from iss import Iss
from geneset import GeneSet
from preprocess import preprocess

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


if __name__ == "__main__":
    algo = algo()
    preprocess(algo.iss, algo.gSet)
    print("done")