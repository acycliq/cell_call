import os
import utils
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
        print(self.cell_map)

    def _populate(self, pathStr):
        mat = utils.loadmat(pathStr)
        dictionary = mat["iss"]
        logger.info("reading iss.mat from %s", pathStr)
        toKeep = ['CellMapFile', 'CellCallRegionYX', 'InsideCellBonus', 'GeneNames',
                  'SpotCodeNo', 'SpotGlobalYX', 'SpotCombi', 'SpotScore',
                  'CombiQualThresh', 'SpotIntensity', 'CombiIntensityThresh', 'cAnchorIntensities',
                  'DetectionThresh', 'CombiAnchorsReq', 'CharCodes', 'ExtraCodes',
                  'nNeighbors', 'MisreadDensity', 'CellCallMaxIter', 'Inefficiency',
                  'SpotReg', 'rSpot', 'rGene', 'CellCallTolerance']
        for key in mat["iss"]:
            if key in toKeep:
                setattr(self, key, dictionary[key])
                logger.info("Attribute %s populated.", key)

    def _load_cellMapFile(self, ini):
        try:
            mat = utils.loadmat(self.CellMapFile)
            self.cell_map = mat["CellMap"]
            logger.info("reading CellMap from %s", self.CellMapFile)
        except FileNotFoundError:
            matStr = ini['cellMap']
            logger.info("reading CellMap from %s", matStr)
            mat = utils.loadmat(matStr)
            self.cell_map = mat["CellMap"]





