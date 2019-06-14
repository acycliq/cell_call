import numpy as np
import pandas as pd
from skimage.measure import regionprops
import os
import xarray as xr
from source.utils import loadmat
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = dir_path + '/config.yml'


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


class Cell(object):
    def __init__(self, x, y, Id):
        self._Id = Id
        self._x = x
        self._y = y
        self._spots = None
        self._cellType = None
        self._areaFactor = None
        self._relativeRadius = None

    @property
    def Id(self):
        return self._Id

    @Id.setter
    def Id(self, value):
        self._Id = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def spots(self):
        return self._spots

    @spots.setter
    def spots(self, value):
        self._spots = value

    @property
    def cellType(self):
        return self._cellType

    @cellType.setter
    def cellType(self, value):
        self._cellType = value

    @property
    def areaFactor(self):
        return self._areaFactor

    @areaFactor.setter
    def areaFactor (self, value):
        self._areaFactor = value

    @property
    def relativeRadius(self):
        return self._relativeRadius

    @relativeRadius.setter
    def relativeRadius(self, value):
        self._relativeRadius = value


class Cells(object):
    def __init__(self, label_image, config):
        self._collection, _stats = _parse(label_image, config)
        self._areaFactor = _stats['areaFactor']
        self._meanRadius = _stats['meanRadius']
        self._relativeRadius = _stats['relativeRadius']

    @property
    def areaFactor(self):
        return self._areaFactor

    @property
    def meanRadius(self):
        return self._meanRadius

    @property
    def relativeRadius(self):
        return self._relativeRadius

    @property
    def collection(self):
        return self._collection


class Spot(object):
    def __init__(self, Id, x, y, geneName):
        self._Id = Id
        self._x = x
        self._y = y
        self._geneName = geneName
        self._cellAssignment = None

    @property
    def Id(self):
        return self._Id

    @Id.setter
    def Id(self, value):
        self._Id = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def geneName(self):
        return self._geneName

    @geneName.setter
    def geneName(self, value):
        self._geneName = value


def _parse(label_image, config):
    '''
    Read image and calc some statistics
    :return:
    '''

    roi = config['roi']
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
    meanCellRadius = np.mean(np.sqrt(cellArea0 / np.pi)) * 0.5;

    relCellRadius = np.sqrt(cellArea0 / np.pi) / meanCellRadius
    relCellRadius = np.append(relCellRadius, 1)

    nom = np.exp(-relCellRadius ** 2 / 2) * (1 - np.exp(config['InsideCellBonus'])) + np.exp(config['InsideCellBonus'])
    denom = np.exp(-0.5) * (1 - np.exp(config['InsideCellBonus'])) + np.exp(config['InsideCellBonus'])
    CellAreaFactor = nom / denom
    areaFactor = CellAreaFactor

    my_list = []
    for i, val in enumerate(cellYX):
        c = Cell(val[1], val[0], i)
        c.relativeRadius = relCellRadius[i]
        c.areaFactor = areaFactor[i]

        my_list.append(c)

    stats = dict()
    stats['areaFactor'] = areaFactor
    stats['meanRadius'] = meanCellRadius
    stats['relativeRadius'] = relCellRadius
    return my_list, stats


def _load_geneset(config):
    '''
    :param config:
    :return:
    '''
    genesetPath = config['geneset']
    gs = loadmat(genesetPath)
    logger.info('Loading geneset from %s' % genesetPath)
    ge = gs["GeneSet"]["GeneExp"]
    GeneName = gs["GeneSet"]["GeneName"]
    Class = gs["GeneSet"]["Class"]

    gene_expression = xr.DataArray(ge, coords=[GeneName, Class], dims=['GeneName', 'Class'])
    return gene_expression


def _normalise(df):
    '''
    removes columns with zero mean (ie all zeros) and then rescales so that
    total counts remain the same.
    :param df:
    :return:
    '''

    # find the mean for each column
    col_mean = df.mean(axis=0)

    isZero = col_mean == 0.0

    # remove column if its mean is zero
    df2 = df.loc[:, ~isZero]

    total = df.sum().sum()
    total2 = df2.sum().sum()

    # rescale df2 so that the total counts are the same
    df2 = df2 * total/total2

    # sanity check
    assert df.sum().sum() == df2.sum().sum()

    return df2



def geneSet(config, genes):
    ge = _load_geneset(config)

    # make a dataframe from the xarray
    df = pd.DataFrame(ge.data, index=ge.GeneName, columns=ge.Class)
    df = df.loc[genes]

    df = _normalise(df)

    # take the transpose, ie classes-by-genes
    dft = df.T

    # loop over genes and calc the mean expression within each cell type
    mean_expression = dft.groupby(level=0).mean().T

    # add the zero cell type
    mean_expression['Zero'] = np.zeros([mean_expression.shape[0], 1])

    # sort the dataframe
    mean_expression = mean_expression.sort_index(axis=1).sort_index(axis=0)

    log_mean_expression = np.log(mean_expression + config['SpotReg'])

    return mean_expression


