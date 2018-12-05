import numpy as np
import utils
from sklearn.neighbors import NearestNeighbors
from time import time
import gene
import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


class Spot(object):
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
        self.expectedGamma = None
        self.expectedLogGamma = None
        self.cellProb = None
        self.zeroProb = None
        self._TotPredictedB = None
        # 1) filter the spots
        self._filter_spots(iss)

    @property
    def TotPredictedB(self):
        try:
            self._TotPredictedB = np.bincount(self.geneNo, self.neighbors['prob'][:, -1])
        except:
            pass # swallow the exception (are you sure you wanna keep that??)
        return self._TotPredictedB

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
        logger.info("Rebasing SpotYX to match the one-based indexed Matlab object. Not sure this is needed!!")
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
        g = gene.Gene()
        #populate it
        [GeneNames, SpotGeneNo, TotGeneSpots] = np.unique(self.name, return_inverse=True, return_counts=True)
        g.names = GeneNames
        self.geneNo = SpotGeneNo
        g.totalSpots = TotGeneSpots
        g.nG = GeneNames.shape[0]
        g.expectedGamma = np.ones(g.nG)
        return g

    def calcGamma(self, iss, cells, genes, klasses):
        scaledMean = genes.expression * cells.areaFactor[:, None, None]
        cellGeneCount = cells.geneCount(self, genes)
        rho = iss.rSpot + cellGeneCount
        beta = iss.rSpot + scaledMean
        self.expectedGamma = utils.gammaExpectation(rho[:,:,None], beta)
        self.expectedLogGamma = utils.logGammaExpectation(rho[:,:,None], beta)

    def cellAssignment(self, cells, genes, klasses):
        nN = self.neighbors['id'].shape[1]
        nS = self.nS
        nK = klasses.nK
        aSpotCell = np.zeros([nS, nN])
        for n in range(nN - 1):
            c = self.neighbors['id'][:, n]
            # logger.info('genes.spotNo should be something line spots.geneNo instead!!')
            meanLogExpression = np.squeeze(genes.logExpression[:, self.geneNo, :])
            classProb = cells.classProb[c, :]
            term_1 = np.sum(classProb * meanLogExpression, axis=1)
            expectedLog = utils.bi2(self.expectedLogGamma, [nS, nK], c[:, None], self.geneNo[:, None])
            term_2 = np.sum(cells.classProb[c, :] * expectedLog, axis=1)
            aSpotCell[:, n] = term_1 + term_2
        wSpotCell = aSpotCell + self.D

        # update the prob a spot belongs to a neighboring cell
        pSpotNeighb = utils.softmax(wSpotCell)
        self.neighbors['prob'] = pSpotNeighb
        logger.info('spot ---> cell probabilities updated')

    def zeroKlassProb(self, klasses, cells):
        nK = klasses.nK
        nN = self.neighbors['id'].shape[1]
        klassProb = cells.classProb[:, nK-1]
        neighbourProb = self.neighbors['prob']

        neighbourProb[:, 0: nN - 1] * klassProb[self.neighbors['id'][:, 0: nN - 1]]
        temp = neighbourProb[:, 0: nN - 1] * klassProb[self.neighbors['id'][:, 0: nN - 1]]
        #temp = neighbourProb * klassProb
        pSpotZero = np.sum(temp, 1)
        out = pSpotZero
        #self.zeroProb = pSpotZero
        return out

    def TotPredictedZ(self, geneNo, pCellZero):
        '''
        ' given a vector
        :param spots:
        :return:
        '''
        spotNeighbours = self.neighbors['id'][:, :-1]
        neighbourProb = self.neighbors['prob'][:, :-1]
        pSpotZero = np.sum(neighbourProb * pCellZero[spotNeighbours], axis=1)
        TotPredictedZ = np.bincount(geneNo, pSpotZero)
        return TotPredictedZ
