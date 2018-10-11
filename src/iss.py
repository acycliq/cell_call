import numpy as np
import pandas as pd
import os
import src.utils as utils
from skimage.measure import regionprops
import logging


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


class Iss:
    def __init__(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        self._populate(os.path.join(my_path, "../data/iss.mat"))
        self._load_cellMapFile()
        print(self.cell_map)

    def _populate(self, path_str):
        mat = utils.loadmat(path_str)
        dictionary = mat["iss"]
        for key in mat["iss"]:
            setattr(self, key, dictionary[key])

    def _load_cellMapFile(self):
        mat = utils.loadmat(self.CellMapFile)
        self.cell_map = mat["CellMap"]




