import os
import src.utils
import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


class Iss:
    def __init__(self, ini):
        my_path = os.path.abspath(os.path.dirname(__file__))
        issPath = os.path.join(my_path, ini['issPath'])
        self._populate(issPath)
        self._load_cellMapFile(ini)
        print(self.label_image)

    def _populate(self, pathStr):
        mat = src.utils.loadmat(pathStr)
        dictionary = mat["iss"]
        logger.info("reading iss.mat from %s", pathStr)
        toKeep = ['CellMapFile', 'CellCallRegionYX', 'InsideCellBonus',
                  'nNeighbors', 'MisreadDensity', 'Inefficiency',
                  'SpotReg', 'CellCallMaxIter', 'rSpot', 'rGene', 'CellCallTolerance']
        for key in mat["iss"]:
            if key in toKeep:
                setattr(self, key, dictionary[key])
                logger.info("Attribute %s populated.", key)

    def _load_cellMapFile(self, ini):
        try:
            mat = src.utils.loadmat(self.CellMapFile)
            self.label_image = mat["CellMap"]
            logger.info("reading CellMap from %s", self.CellMapFile)
        except FileNotFoundError:
            matStr = ini['label_image']
            logger.info("reading CellMap from %s", matStr)
            mat = src.utils.loadmat(matStr)
            self.label_image = mat["CellMap"]





