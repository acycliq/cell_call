
from iss import Iss
from geneset import GeneSet
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
    def __init__(self, ini):
        print('in systemData.algo')
        # create iss and gSet objects and add them as properties
        self._iss = Iss(ini)
        self._gSet = GeneSet()

    @property
    def iss(self):
        return self._iss

    @property
    def gSet(self):
        return self._gSet

    def getGeneSubset(self, geneNames):
        out = self.gSet.GeneSubset(geneNames).ScaleCell(0)
        return out