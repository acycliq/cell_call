import numpy as np
from skimage.measure import regionprops
import scipy.io as spio
from source.systemData import Cell
import os
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = dir_path + '/config.yml'
# yaml = ruamel.yaml.YAML(typ='safe')

logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )



def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects

    from: `StackOverflow <http://stackoverflow.com/questions/7008608/scipy-io-loadmat-nested-structures-i-e-dictionaries>`_
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)


def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict


def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict


def parse(label_image, roi):
    '''
    Read image and calc some statistics
    :return:
    '''

    xRange = roi["x1"] - roi["x0"]
    yRange = roi["y1"] - roi["y0"]
    roiSize = np.array([yRange, xRange]) + 1

    # sanity check
    assert np.all(label_image.shape == roiSize), 'Image is %d by %d but the ROI implies %d by %d' % (label_image.shape[1], label_image.shape[0], xRange, yRange)

    x0 = roi["x0"]
    y0 = roi["y0"]

    rp = regionprops(label_image)
    cellYX = np.array([x.centroid for x in rp]) + np.array([y0, x0])

    logger.info(' Shifting the centroids of the cells one pixel on each dimension')
    cellYX = cellYX + 1.0

    cellArea0 = np.array([x.area for x in rp])
    meanCellRadius = np.mean(np.sqrt(cellArea0 / np.pi)) * 0.5

    relCellRadius = np.sqrt(cellArea0 / np.pi) / meanCellRadius
    relCellRadius = np.append(relCellRadius, 1)

    # logger.info("Rebasing CellYX to match the one-based indexed Matlab object. ")
    # cellYX = cellYX + 1

    cells = []
    for i, val in enumerate(cellYX):
        cells.append(Cell(val[1], val[0], i))

    print('done')

    # self.YX = cellYX
    # self.nC = cellYX.shape[0] + 1
    # self.meanRadius = meanCellRadius
    # self.relativeRadius = relCellRadius

    # nom = np.exp(-self.relativeRadius ** 2 / 2) * (1 - np.exp(ini['InsideCellBonus'])) + np.exp(ini['InsideCellBonus'])
    # denom = np.exp(-0.5) * (1 - np.exp(ini['InsideCellBonus'])) + np.exp(ini['InsideCellBonus'])
    # CellAreaFactor = nom / denom
    # self.areaFactor = CellAreaFactor