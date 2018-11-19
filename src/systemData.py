
import numpy as np
import pandas as pd
from skimage.measure import regionprops
from sklearn.neighbors import NearestNeighbors
import utils
import numpy_groupies as npg
from time import time
import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


class Spots(object):
    '''
    keeps the spots neighbors and the spot containing cell
    neighbors is a dict. Key is the neighbor cell id and val is the probability
    the spot belongs to that neighbor
    '''
    def __init__(self, iss):
        # creates a spot object
        self.neighbors = None  # neighbors is a dict (top3 plus last one which is a dummy)
        self.D = None
        self.inCell = None
        self.YX = None
        self.nS = None
        self.name = None
        self.geneNo = None
        # 1) filter the spots
        self._filter_spots(iss)

    def loglik(self, cellObj, iss):
        cellYX = cellObj.YX
        spotYX = self.YX
        meanCellRadius = cellObj.meanRadius
        nC = cellYX.shape[0] + 1
        nN = iss.nNeighbors + 1
        nS = spotYX.shape[0]

        # for each spot find the closest cell (in fact the top nN-closest cells...)
        nbrs = NearestNeighbors(n_neighbors=nN, algorithm='ball_tree').fit(cellYX)
        Dist, Neighbors = nbrs.kneighbors(spotYX)

        # Assign the nN-closest neighbour to an out-of-bounds value. (I would use -1 here instead of nC, anyways...)
        Neighbors[:, -1] = nC

        # Assume a bivariate normal and calc the likelihood
        D = -Dist ** 2 / (2 * meanCellRadius ** 2) - np.log(2 * np.pi * meanCellRadius ** 2)

        # last column (nN-closest) keeps the misreads,
        D[:, -1] = np.log(iss.MisreadDensity)

        y0 = iss.CellCallRegionYX[:, 0].min()
        x0 = iss.CellCallRegionYX[:, 1].min()
        logger.info("Rebasing SpotYX to match the one-based indexed Matlab object.")
        spotyx = spotYX - 1  # I DO NOT THINK THIS IS NEEDED!! REMOVE IT!
        logger.info(
            "Rebasing Neighbors to match the one-based indexed Matlab object. Not sure this is needed! REMOVE IT")

        # Lookup cell_map and infer which spot belongs to which cell.
        # This is kinda using the empirical....
        idx = spotyx - [y0, x0]  # First move the origin at (0, 0)
        SpotInCell = utils.IndexArrayNan(iss.cell_map, idx.T)  # Now get the allocation of spots to cells
        sanity_check = Neighbors[SpotInCell > 0, 0] + 1 == SpotInCell[SpotInCell > 0]
        assert ~any(sanity_check), "a spot is in a cell not closest neighbor!"

        D[SpotInCell > 0, 0] = D[SpotInCell > 0, 0] + iss.InsideCellBonus

        # set now some probabilities (spot to cell)
        pSpotNeighb = np.zeros([nS, nN])
        pSpotNeighb[Neighbors + 1 == SpotInCell[:, None]] = 1
        pSpotNeighb[SpotInCell == 0, -1] = 1


        neighborsDict = dict()
        neighborsDict['id'] = Neighbors
        neighborsDict['prob'] = pSpotNeighb
        self.D = D
        self.neighbors = neighborsDict
        self.inCell = SpotInCell

    def _filter_spots(self, iss):
        excludeGenes = ['Vsnl1', 'Atp1b1', 'Slc24a2', 'Tmsb10', 'Calm2', 'Gap43', 'Fxyd6']
        allGeneNames = iss.GeneNames[iss.SpotCodeNo - 1]  # -1 is needed because Matlab is 1-based
        cond1 = ~np.isin(allGeneNames, excludeGenes)
        start_time = time()
        cond2 = utils.inpolygon(iss.SpotGlobalYX, iss.CellCallRegionYX)
        print('Elapsed time: ' + str(time() - start_time))

        cond3 = utils.qualityThreshold(iss)

        includeSpot = cond1 & cond2 & cond3
        spotYX = iss.SpotGlobalYX[includeSpot, :].round()
        spotGeneName = allGeneNames[includeSpot]

        # [GeneNames, SpotGeneNo, TotGeneSpots] = np.unique(spotGeneName, return_inverse=True, return_counts=True)

        self.YX = spotYX
        self.nS = spotYX.shape[0]
        self.name = spotGeneName
        # self._name = GeneNames
        # self._geneNo = SpotGeneNo
        # self._nG = GeneNames.shape[0]

    def getGenes(self):
        #make a gene object
        g = Genes()
        #populate it
        [GeneNames, SpotGeneNo, TotGeneSpots] = np.unique(self.name, return_inverse=True, return_counts=True)
        g.names = GeneNames
        g.spotNo = SpotGeneNo
        g.totalSpots = TotGeneSpots
        g.nG = GeneNames.shape[0]
        return g


class Cell(object):
    def __init__(self, iss):
        # creates a cell object
        self.YX = None
        self.nC = None
        self.meanRadius = None
        self.relativeRadius = None
        self.areaFactor = None
        self.classProb = None
        self._cell_info(iss)

    def _cell_info(self, iss):
        '''
        Read image and calc some statistics
        :return:
        '''
        y0 = iss.CellCallRegionYX[:, 0].min()
        x0 = iss.CellCallRegionYX[:, 1].min()

        matStr = "..\data\CellMap.mat"
        logger.info("reading CellMap from %s", matStr)
        mat = utils.loadmat(matStr)
        # cell_map = mat["CellMap"]

        rp = regionprops(mat["CellMap"])
        cellYX = np.array([x.centroid for x in rp]) + np.array([y0, x0])

        cellArea0 = np.array([x.area for x in rp])
        meanCellRadius = np.mean(np.sqrt(cellArea0 / np.pi)) * 0.5;

        relCellRadius = np.sqrt(cellArea0 / np.pi) / meanCellRadius
        relCellRadius = np.append(relCellRadius, 1)

        logger.info("Rebasing CellYX to match the one-based indexed Matlab object. ")
        cellYX = cellYX + 1

        self.YX = cellYX
        self.nC = cellYX.shape[0]
        self.meanRadius = meanCellRadius
        self.relativeRadius = relCellRadius

        nom = np.exp(-self.relativeRadius ** 2 / 2) * (1 - np.exp(iss.InsideCellBonus)) + np.exp(iss.InsideCellBonus)
        denom = np.exp(-0.5) * (1 - np.exp(iss.InsideCellBonus)) + np.exp(iss.InsideCellBonus)
        CellAreaFactor = nom / denom
        self.areaFactor = CellAreaFactor

    def geneCounts(self, spots, genes):
        nC = self.nC
        nG = genes.nG
        nN = spots.neighbors["id"].shape[1]
        CellGeneCount = np.zeros([nC, nG]);
        for n in range(nN - 1):
            c = spots.neighbors["id"][:, n]
            group_idx = np.vstack((c[None, :], genes.spotNo[None, :]))
            a = spots.neighbors["prob"][:, n]
            accumarray = npg.aggregate(group_idx, a, func="sum", size=(nC, nG))
            CellGeneCount = CellGeneCount + accumarray
        return CellGeneCount


class Genes(object):
    def __init__(self):
        self.names = None
        self.spotNo = None
        self.totalSpots = None


class Klass(object):
    def __init__(self, iss, gSet, genes):
        self.expression = None
        self.logExpression = None
        self.nK = None
        self.name = None
        self._populate(iss, gSet, genes)

    def _populate(self, iss, gSet, genes):
        self.name = np.append(pd.unique(gSet.Class), 'Zero')
        self.nK = self.name.shape[0]

        MeanClassExp = np.zeros([self.nK, genes.nG])
        temp = gSet.GeneSubset(genes.names).ScaleCell(0)
        for k in range(self.nK - 1):
            val = iss.Inefficiency * np.mean(temp.CellSubset(self.name[k]).GeneExp, 1);
            MeanClassExp[k, :] = val
        self.expression = MeanClassExp
        self.logExpression = np.log(MeanClassExp + iss.SpotReg)



