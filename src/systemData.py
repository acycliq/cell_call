
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
    def __init__(self):
        print('in systemData.algo')
        # create iss and gSet objects and add them as properties
        self._iss = Iss()
        self._gSet = GeneSet()

    @property
    def iss(self):
        return self._iss

    @property
    def gSet(self):
        return self._gSet