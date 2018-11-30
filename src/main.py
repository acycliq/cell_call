from iss import Iss
from geneset import GeneSet
import preprocess
import numpy as np
import utils
import systemData

import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


# def expectedGamma(r, b):
#     return r/b
#
#
# def expectedLogGamma(r, b):
#     return scipy.special.psi(r) - np.log(b)


class algo:
    '''
    Main routine. More to add here!
    '''
    def __init__(self):
        print('in algo')
        # create iss and gSet objects and add them as properties
        self._iss = Iss()
        self._gSet = GeneSet()

    @property
    def iss(self):
        return self._iss

    @property
    def gSet(self):
        return self._gSet

    def callCells(self, spots, cells, genes, klasses):
        '''
        Assign cells to classes
        '''
        spots.calcGamma(self.iss, cells, genes, klasses)

        nK = klasses.nK
        nG = genes.nG
        nC = cells.nC
        ScaledExp = genes.expression * genes.expectedGamma[None, :, None] * cells.areaFactor[:, None, None] + self.iss.SpotReg
        pNegBin = ScaledExp / (self.iss.rSpot + ScaledExp)
        CellGeneCount = cells.geneCount(spots.neighbors, genes)
        wCellClass = np.sum(CellGeneCount[:,:,None] * np.log(pNegBin) + self.iss.rSpot*np.log(1-pNegBin), axis=1) + klasses.logPrior
        pCellClass = utils.LogLtoP(wCellClass)
        pCellClass2 = utils.softmax(wCellClass)

        print('in algo:callCells')

    def callSpots(self, spots, cells, genes, klasses, pCellClass):
        '''
        Assign spots to the neighbouring cells
        '''
        nS = spots.nS
        nN = spots.neighbors["id"].shape[1]
        nK = klasses.nK
        aSpotCell = np.zeros([nS, nN])
        for n in range(nN - 1):
            c = spots.Neighbors[:, n]
            term_1 = np.sum(pCellClass[c, :] * self.lMeanClassExp[:, self.SpotGeneNo].T, axis=1)
            temp = utils.bi(spots.expectedLogGamma, c[:, None], np.arange(0, nK), self.SpotGeneNo[:, None])
            term_2 = np.sum(pCellClass[c, :] * temp, axis=1)
            aSpotCell[:, n] = term_1 + term_2
        wSpotCell = aSpotCell + spots.D

        pSpotNeighb = utils.LogLtoP(wSpotCell)
        MeanProbChanged = np.max(np.abs(pSpotNeighb - pSpotNeighbOld))
        # logger.info('Iteration %d, mean prob change %f' % (i, MeanProbChanged))
        Converged = (MeanProbChanged < self.iss.CellCallTolerance)
        pSpotNeighbOld = pSpotNeighb
        print('in algo:callSpots')

    # def calcGamma(self, spots, cells, genes, klasses):
    #     scaledMean = np.transpose(np.dstack([klasses.expression.T] * len(cells.areaFactor)) * cells.areaFactor, (2, 1, 0))
    #     cellGeneCount = cells.geneCount(spots.neighbors, genes)
    #     rho = self.iss.rSpot + np.reshape(cellGeneCount, (cells.nC, 1, genes.nG), order='F')
    #     beta = self.iss.rSpot + scaledMean
    #     eg = utils.expectedGamma(rho, beta)
    #     elg = utils.expectedLogGamma(rho, beta)
    #     return eg, elg




if __name__ == "__main__":
    algo = algo()

    # make a cell object
    cells = systemData.Cell(algo.iss)

    # make a spots object
    spots = systemData.Spot(algo.iss)

    # calc the loglik and populate some of the object's properties
    spots.loglik(cells, algo.iss)

    # make now a genes object
    genes = spots.getGenes()

    cells.geneCount(spots, genes)

    klasses = systemData.Klass(algo.gSet)

    #now you can set expressions and logexpressions (as the mean expession over klass)
    genes.setKlassExpressions(klasses, algo.iss, algo.gSet)

    # algo.callCells(spots, cells, genes, klasses)

    cells.klassAssignment(spots, genes, klasses, algo.iss)

    spots.cellAssignment(cells, genes, klasses)

    genes.updateGamma(cells, spots, klasses, algo.iss)



    print("done")