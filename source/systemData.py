import numpy as np
import  pandas as pd
import xarray as xr
from skimage.measure import regionprops
from sklearn.neighbors import NearestNeighbors
import utils
import os
import config
import numpy_groupies as npg
import time
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
        self.yx_coords, self.stats = _parse(label_image, config)

    def nn(self):
        n = config.DEFAULT['nNeighbors']
        # for each spot find the closest cell (in fact the top nN-closest cells...)
        nbrs = NearestNeighbors(n_neighbors=n, algorithm='ball_tree').fit(self.yx_coords.data)
        return nbrs

    def geneCount(self, spots):
        '''
        Produces a matrix numCells-by-numGenes where element at position (c,g) keeps the expected
        number of gene g  in cell c.
        :param spots:
        :return:
        '''
        start = time.time()
        nC = self.yx_coords.shape[0] + 1
        nG = len(spots.geneUniv.gene_name)
        cell_id = self.yx_coords.cell_id.values
        _id = np.append(cell_id, cell_id.max()+1)
        nN = spots.neighborCells["id"].shape[1]
        CellGeneCount = np.zeros([nC, nG])
        geneNames = spots.geneNames()
        [name, ispot, _] = np.unique(geneNames, return_inverse=True, return_counts=True)
        for n in range(nN - 1):
            c = spots.neighborCells["id"][:, n]
            group_idx = np.vstack((c[None, :], ispot[None, :]))
            a = spots.neighborCells["prob"][:, n]
            accumarray = npg.aggregate(group_idx, a, func="sum", size=(nC, nG))
            CellGeneCount = CellGeneCount + accumarray
        end = time.time()
        print('time in geneCount: ', end - start)
        CellGeneCount = xr.DataArray(CellGeneCount, coords=[_id, name], dims=['cell_id', 'gene_name'])
        self.CellGeneCount = CellGeneCount
        return CellGeneCount



class Prior(object):
    def __init__(self, cell_type):
        # list(dict.fromkeys(cell_type_name))
        self.name = cell_type
        self.nK = self.name.shape[0]
        self.value = np.append([.5 * np.ones(self.nK - 1) / self.nK], 0.5)
        self.logvalue = np.log(self.value)



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
        self.neighborCells = dict()
        for r in zip(df.index, df.x, df.y, df.target):
            self.collection.append(Spot(r[0], r[1], r[2], r[3]))
        self.geneUniv = xr.DataArray(np.ones((len(sorted(self.geneUniv())), 1)),
                                     coords={'gene_name': sorted(self.geneUniv()),
                                             'columns': ['expected_gamma']},
                                     dims=['gene_name', 'columns'])

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

    def geneNames(self):
        return list(map(lambda d: d.geneName, self.collection))

    def spotId(self):
        temp = list(map(lambda d: d.Id, self.collection))
        return np.array(temp)

    def _neighborCells(self, cells, cfg):
        spotYX = self.yxCoords()
        n = cfg['nNeighbors']
        numCells = len(cells.yx_coords)
        numSpots = len(spotYX)
        neighbors = np.zeros((numSpots, n+1), dtype=int)
        # for each spot find the closest cell (in fact the top nN-closest cells...)
        nbrs = cells.nn()
        _, _neighbors = nbrs.kneighbors(spotYX)

        # populate temp with the neighbours
        neighbors[:, :-1] = _neighbors
        # last column is for misreads. Id is dummy id and set to the
        # number of cells (which so-far should always be unallocated)
        neighbors[:, -1] = numCells
        logger.info('Populating parent cells')
        for i, d in enumerate(neighbors):
            self.collection[i].parentCell = d
        logger.info('Parent cells filled')

        # finally return
        return neighbors

    def _cellProb(self, label_image, cfg):
        roi = cfg['roi']
        x0 = roi["x0"]
        y0 = roi["y0"]
        yxCoords = self.yxCoords()
        neighbors = self.neighborCells['id']
        nS = len(yxCoords)
        nN = cfg['nNeighbors'] + 1

        idx = np.array(yxCoords) - np.array([y0, x0]) # First move the origin at (0, 0)
        SpotInCell = utils.label_spot(label_image, idx.T)
        # sanity check
        sanity_check = neighbors[SpotInCell > 0, 0] + 1 == SpotInCell[SpotInCell > 0]
        assert ~any(sanity_check), "a spot is in a cell not closest neighbor!"

        pSpotNeighb = np.zeros([nS, nN])
        pSpotNeighb[neighbors + 1 == SpotInCell[:, None]] = 1
        pSpotNeighb[SpotInCell == 0, -1] = 1
        return pSpotNeighb

    def neighCells(self, cells, label_image, config):
        self.neighborCells['id'] = self._neighborCells(cells, config)
        self.neighborCells['prob'] = self._cellProb(label_image, config)
        # self.neighborCells = _neighborCells


class Genes(object):
    def __init__(self, genes):
        self.array = xr.DataArray(np.ones((len(genes), 1)),
                     coords={'gene_name': genes,
                             'columns': ['expected_gamma']},
                     dims=['gene_name', 'columns'])


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

    # logger.info(' Shifting the centroids of the cells one pixel on each dimension')
    # cellYX = cellYX + 1.0

    cellArea0 = np.array([x.area for x in rp])
    meanCellRadius = np.mean(np.sqrt(cellArea0 / np.pi)) * 0.5;

    relCellRadius = np.sqrt(cellArea0 / np.pi) / meanCellRadius

    # append 1 for the misreads
    relCellRadius = np.append(relCellRadius, 1)

    nom = np.exp(-relCellRadius ** 2 / 2) * (1 - np.exp(config['InsideCellBonus'])) + np.exp(config['InsideCellBonus'])
    denom = np.exp(-0.5) * (1 - np.exp(config['InsideCellBonus'])) + np.exp(config['InsideCellBonus'])
    CellAreaFactor = nom / denom
    areaFactor = CellAreaFactor


    # ds = xr.Dataset(
    #     data_vars={'yx_coords': (('cell_id', 'yx'), np.array(cellYX))},
    #     coords={'yx': ['y', 'x'],
    #             'cell_id': list(range(len(cellYX)))}
    # )

    temp = np.vstack((areaFactor, relCellRadius)).T
    stats = xr.DataArray(temp,
                 coords={'cell_id': np.arange(temp.shape[0]),
                         'columns': ['area_factor', 'rel_radius'],
                         'mean_radius': meanCellRadius},
                 dims=['cell_id', 'columns'])

    da = xr.DataArray(cellYX,
                         coords={'cell_id': np.arange(cellYX.shape[0]),
                                 'columns': ['y', 'x']},
                         dims=['cell_id', 'columns'])

    return da, stats


