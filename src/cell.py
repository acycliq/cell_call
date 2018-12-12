import numpy as np
import utils
from skimage.measure import regionprops
import numpy_groupies as npg
import time

import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


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

        # matStr = "..\data\CellMap.mat"
        # logger.info("reading CellMap from %s", matStr)
        # logger.info("Do I need that again?? cell map is set inside Iss class I think!")
        # mat = utils.loadmat(matStr)
        # cell_map = mat["CellMap"]

        rp = regionprops(iss.cell_map)
        cellYX = np.array([x.centroid for x in rp]) + np.array([y0, x0])

        cellArea0 = np.array([x.area for x in rp])
        meanCellRadius = np.mean(np.sqrt(cellArea0 / np.pi)) * 0.5;

        relCellRadius = np.sqrt(cellArea0 / np.pi) / meanCellRadius
        relCellRadius = np.append(relCellRadius, 1)

        logger.info("Rebasing CellYX to match the one-based indexed Matlab object. ")
        cellYX = cellYX + 1

        self.YX = cellYX
        self.nC = cellYX.shape[0] + 1
        self.meanRadius = meanCellRadius
        self.relativeRadius = relCellRadius

        nom = np.exp(-self.relativeRadius ** 2 / 2) * (1 - np.exp(iss.InsideCellBonus)) + np.exp(iss.InsideCellBonus)
        denom = np.exp(-0.5) * (1 - np.exp(iss.InsideCellBonus)) + np.exp(iss.InsideCellBonus)
        CellAreaFactor = nom / denom
        self.areaFactor = CellAreaFactor

    def geneCount(self, spots, genes):
        # start = time.time()
        nC = self.nC
        nG = genes.nG
        nN = spots.neighbors["id"].shape[1]
        CellGeneCount = np.zeros([nC, nG]);
        for n in range(nN - 1):
            c = spots.neighbors["id"][:, n]
            group_idx = np.vstack((c[None, :], spots.geneNo[None, :]))
            a = spots.neighbors["prob"][:, n]
            accumarray = npg.aggregate(group_idx, a, func="sum", size=(nC, nG))
            CellGeneCount = CellGeneCount + accumarray
        # end = time.time()
        # print('time in geneCount: ', end - start)
        return CellGeneCount

    def klassAssignment(self, spots, genes, klasses, iss):
        spots.calcGamma(iss, self, genes, klasses)

        ScaledExp = genes.expression * genes.expectedGamma[None, :, None]*self.areaFactor[:, None, None] + iss.SpotReg
        pNegBin = ScaledExp / (iss.rSpot + ScaledExp)
        CellGeneCount = self.geneCount(spots, genes)
        contr = utils.nb_negBinLoglik(CellGeneCount[:,:,None], iss.rSpot, pNegBin)
        # contr = utils.negBinLoglik(CellGeneCount[:, :, None], iss.rSpot, pNegBin)
        # assert np.all(nb_contr == contr)
        wCellClass = np.sum(contr, axis=1) + klasses.logPrior
        pCellClass = utils.softmax(wCellClass)

        self.classProb = pCellClass
        logger.info('cell ---> klass probabilities updated')
        return pCellClass

    def geneCountsPerKlass(self, genes, spots, klasses, iss):
        klassProb = self.classProb.reshape((self.nC, 1, klasses.nK))
        temp = spots.expectedGamma * klassProb * self.areaFactor[..., None, None]
        temp = np.sum(temp, axis=0)
        temp = np.squeeze(temp)
        ClassTotPredicted = temp * (genes.expression + iss.SpotReg)
        ClassTotPredicted = np.squeeze(ClassTotPredicted)
        TotPredicted = np.sum(ClassTotPredicted[:, :-1], axis=1)
        return TotPredicted
