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


class Cells(object):
    def __init__(self, label_image, config):
        self.ds = _parse(label_image, config)

    @property
    def yx_coords(self):
        y_nan = np.argwhere(~np.isnan(self.ds.y.values))
        x_nan = np.argwhere(~np.isnan(self.ds.x.values))

        # coords = [self.ds.y.values, self.ds.x.values]
        coords = [d for d in zip(self.ds.y.values, self.ds.x.values) if not np.isnan(d).any()]
        # coords = np.array([self.ds.y.values, self.ds.x.values]).T

        return np.array(coords)

    @property
    def cell_id(self):
        mask = ~np.isnan(self.ds.y.values) & ~np.isnan(self.ds.x.values)
        return self.ds.cell_id.values[mask]

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
        cell_id = self.cell_id
        _id = np.append(cell_id, cell_id.max()+1)
        nN = spots.neighboring_cells["id"].shape[1]
        CellGeneCount = np.zeros([nC, nG])
        geneNames = spots.gene_name
        [name, ispot, _] = np.unique(geneNames, return_inverse=True, return_counts=True)
        name = spots.geneUniv.gene_name.values
        ispot = spots.geneUniv.ispot.values
        for n in range(nN - 1):
            c = spots.neighboring_cells["id"][n].values
            group_idx = np.vstack((c[None, :], ispot[None, :]))
            a = spots.neighboring_cells["prob"][:, n]
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
        # Check this....maybe you should divide my K-1
        self.value = np.append([.5 * np.ones(self.nK - 1) / self.nK], 0.5)
        self.logvalue = np.log(self.value)


class Spots(object):
    def __init__(self, df):
        self._neighbors = None
        self.collection = []
        self.neighboring_cells = dict()
        self.data = df.to_xarray().rename({'target': 'gene_name'})

        [gn, ispot, _] = np.unique(self.data.gene_name.data, return_inverse=True, return_counts=True)
        gamma = np.ones((len(gn), 1))
        da = xr.DataArray(np.ones(gn.shape), dims=('gene_name'), coords={'gene_name': gn})
        self.geneUniv = xr.Dataset({'gene_gamma': da,
                                    'ispot': ispot,})
        self.yxCoords = self.data[['y', 'x']].to_array().values.T

    @property
    def neighbors(self):
        return self._neighbors

    @neighbors.setter
    def neighbors(self, value):
        self._neighbors = value

    def gene_name(self):
        return self.data.gene_name.values

    def spotId(self):
        temp = list(map(lambda d: d.Id, self.collection))
        return np.array(temp)

    def _neighborCells(self, cells, cfg):
        spotYX = self.yxCoords
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
        # logger.info('Populating parent cells')
        # for i, d in enumerate(neighbors):
        #     self.collection[i].parentCell = d
        # logger.info('Parent cells filled')

        # finally return
        return pd.DataFrame(neighbors)

    def _cellProb(self, label_image, cfg):
        roi = cfg['roi']
        x0 = roi["x0"]
        y0 = roi["y0"]
        yxCoords = self.yxCoords
        neighbors = self.neighboring_cells['id'].values
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

    def get_neighbors(self, cells, label_image, config):
        self.neighboring_cells['id'] = self._neighborCells(cells, config)
        self.neighboring_cells['prob'] = self._cellProb(label_image, config)
        # self.neighborCells = _neighborCells


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

    num_cells = cellYX.shape[0]
    af = xr.DataArray(areaFactor,    dims='cell_id', coords={'cell_id': np.arange(num_cells + 1)})
    rr = xr.DataArray(relCellRadius, dims='cell_id', coords={'cell_id': np.arange(num_cells + 1)})
    x = xr.DataArray(cellYX[:, 1],   dims='cell_id', coords={'cell_id': np.arange(num_cells)})
    y = xr.DataArray(cellYX[:, 0],   dims='cell_id', coords={'cell_id': np.arange(num_cells)})

    ds = xr.Dataset({'area_factor': af,
                        'rel_radius': rr,
                        'mean_radius': meanCellRadius,
                        'x': x,
                        'y': y})

    # stats = xr.DataArray(temp,
    #              coords={'cell_id': np.arange(temp.shape[0]),
    #                      'columns': ['area_factor', 'rel_radius'],
    #                      'mean_radius': meanCellRadius},
    #              dims=['cell_id', 'columns'])

    # da = pd.DataFrame(cellYX, columns=['y', 'x']).to_xarray()

    da = xr.DataArray(cellYX,
                         coords={'cell_id': np.arange(cellYX.shape[0]),
                                 'columns': ['y', 'x']},
                         dims=['cell_id', 'columns'])

    return ds


