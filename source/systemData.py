import numpy as np
from skimage.measure import regionprops
from sklearn.neighbors import NearestNeighbors
import utils
import os
import config
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

    def yxCoords(self):
        def yx(d): return d.y, d.x
        return list(map(yx, self.collection))

    def icoords(self):
        return ((d.x, d.y) for d in self.collection)

    def nn(self):
        n = config.DEFAULT['nNeighbors']
        # for each spot find the closest cell (in fact the top nN-closest cells...)
        nbrs = NearestNeighbors(n_neighbors=n, algorithm='ball_tree').fit(self.yxCoords())
        return nbrs



class Spot(object):
    def __init__(self, Id, x, y, geneName):
        self._Id = Id
        self._x = x
        self._y = y
        self._geneName = geneName
        self._cellAssignment = None
        self._parentCell = None

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

    @property
    def parentCell(self):
        return self._parentCell

    @parentCell.setter
    def parentCell(self, value):
        self._parentCell = value

    def closestCell(self, nbrs):
        _, neighbors = nbrs.kneighbors([[self.x, self.y]])

        return neighbors


class Spots(object):
    def __init__(self, df):
        self._neighbors = None
        self.collection = []
        for r in zip(df.index, df.x, df.y, df.target):
            self.collection.append(Spot(r[0], r[1], r[2], r[3]))

    @property
    def neighbors(self):
        return self._neighbors

    @neighbors.setter
    def neighbors(self, value):
        self._neighbors = value

    def yxCoords(self):
        def yx(d): return d.y, d.x
        return list(map(yx, self.collection))

    def icoords(self):
        return ((d.x, d.y) for d in self.collection)

    def geneUniv(self):
        _map = map(lambda d: d.geneName, self.collection)
        return set(_map)

    def neighborCells(self, cells, config):
        n = config['nNeighbors']
        spotYX = self.yxCoords()
        # for each spot find the closest cell (in fact the top nN-closest cells...)
        nbrs = cells.nn()
        _, neighbors = nbrs.kneighbors(spotYX)

        logger.info('Populating parent cells')
        for i, d in enumerate(neighbors):
            self.collection[i].parentCell = d
        logger.info('Parent cells filled')
        self._neighbors = neighbors

    def cellProb(self, label_image, config):
        roi = config['roi']
        x0 = roi["x0"]
        y0 = roi["y0"]
        yxCoords = self.yxCoords()
        nS = len(yxCoords)
        nN = config['nNeighbors'] + 1
        idx = np.array(yxCoords) - np.array([y0, x0])  # First move the origin at (0, 0)

        SpotInCell = utils.label_spot(label_image, idx.T)
        neighbors = self.neighbors
        pSpotNeighb = np.zeros([nS, nN])
        pSpotNeighb[neighbors + 1 == SpotInCell[:, None]] = 1
        pSpotNeighb[SpotInCell == 0, -1] = 1
        return pSpotNeighb



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


