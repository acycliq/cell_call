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
        eg, elg = self.calcGamma(spots, cells, genes, klasses)

        print('in algo:callCells')

    def callSpots(self):
        '''
        Assign spots to the neighbouring cells
        '''
        print('in algo:callSpots')

    def calcGamma(self, spots, cells, genes, klasses):
        scaledMean = np.transpose(np.dstack([klasses.expression.T] * len(cells.areaFactor)) * cells.areaFactor, (2, 1, 0))
        cellGeneCount = cells.geneCount(spots, genes)
        rho = self.iss.rSpot + np.reshape(cellGeneCount, (cells.nC, 1, genes.nG), order='F')
        beta = self.iss.rSpot + scaledMean
        eg = utils.expectedGamma(rho, beta)
        elg = utils.expectedLogGamma(rho, beta)
        return eg, elg




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

    klasses = systemData.Klass(algo.iss, algo.gSet, genes)

    algo.callCells(spots, cells, genes, klasses)


    print("done")