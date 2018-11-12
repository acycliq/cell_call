from iss import Iss
from geneset import GeneSet
from preprocess import preprocess
import numpy as np
import numpy_groupies as npg

import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )



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

    def callCells(self):
        '''
        Assign cells to classes
        '''
        print('in algo:callCells')

    def callSpots(self):
        '''
        Assign spots to the neighbouring cells
        '''
        print('in algo:callSpots')

    def calcRNAcounts(ini):
        '''
        Calc expected RNA counts
        '''
        print('in algo:calcRNAcounts')
        CellGeneCount = np.zeros([nC, nG]);
        for n in range(nN - 1):
            c = ini.Neighbors[:, n]
            group_idx = np.vstack((c[None, :], ini.SpotGeneNo[None, :]))
            a = pSpotNeighb[:, n]
            accumarray = npg.aggregate(group_idx, a, func="sum", size=(nC, nG))
            CellGeneCount = CellGeneCount + accumarray




if __name__ == "__main__":
    algo = algo()
    ini = preprocess(algo.iss, algo.gSet)
    print("done")