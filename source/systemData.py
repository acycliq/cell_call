import numpy as np
import  pandas as pd
import xarray as xr
from skimage.measure import regionprops
from sklearn.neighbors import NearestNeighbors
import source.utils as utils
import os
import config
import numpy_groupies as npg
import time
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = dir_path + '/config.yml'


logger = logging.getLogger()
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s:%(levelname)s:%(message)s"
#     )


class Cells(object):
    # Get rid of the properties where not necessary!!
    def __init__(self, label_image, config):
        self.ds = _parse(label_image, config)
        self.classProb = None

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
        n = config.DEFAULT['nNeighbors'] + 1
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
        nG = len(spots.gene_panel.gene_name)
        cell_id = self.cell_id
        _id = np.append(cell_id, cell_id.max()+1)
        nN = spots.call.neighbors.shape[1]
        CellGeneCount = np.zeros([nC, nG])

        name = spots.gene_panel.gene_name.values
        ispot = spots.gene_panel.ispot.values
        for n in range(nN - 1):
            c = spots.call.neighbors.loc[:, n].values
            # c = spots.neighboring_cells['id'].sel(neighbor=n).values
            group_idx = np.vstack((c[None, :], ispot[None, :]))
            a = spots.call.cell_prob.loc[:, n]
            accumarray = npg.aggregate(group_idx, a, func="sum", size=(nC, nG))
            CellGeneCount = CellGeneCount + accumarray
        end = time.time()
        print('time in geneCount: ', end - start)
        CellGeneCount = xr.DataArray(CellGeneCount, coords=[_id, name], dims=['cell_id', 'gene_name'])
        # self.CellGeneCount = CellGeneCount
        return CellGeneCount

    def geneCountsPerKlass(self, single_cell_data, egamma, ini):
        temp = self.classProb * self.ds.area_factor * egamma
        temp = temp.sum(dim='cell_id')
        ClassTotPredicted = temp * (single_cell_data.mean_expression + ini['SpotReg'])
        TotPredicted = ClassTotPredicted.drop('Zero', dim='class_name').sum(dim='class_name')
        return TotPredicted

    def iss_summary(self, spots):
        '''
        returns a datafram summarising the main feaures of each cell, ie gene counts and cell types
        :param spots:
        :return:
        '''
        x = self.ds.x.values
        y = self.ds.y.values
        cell_id = self.ds.cell_id.values

        gene_count = self.geneCount(spots)
        class_prob = self.classProb
        gene_names = gene_count.gene_name.values
        class_names = class_prob.class_name.values

        tol = 0.001

        logger.info('starting collecting data (alt)...')
        N = len(cell_id)
        isCount_nonZero = [gene_count.values[n, :] > tol for n in range(N)]
        name_list = [gene_names[isCount_nonZero[n]] for n in range(N)]
        count_list = [gene_count[n, isCount_nonZero[n]].values for n in range(N)]

        isProb_nonZero = [class_prob.values[n, :] > tol for n in range(N)]
        class_name_list = [class_names[isProb_nonZero[n]] for n in range(N)]
        prob_list = [class_prob.values[n, isProb_nonZero[n]] for n in range(N)]

        iss_df = pd.DataFrame({'Cell_Num': self.ds.cell_id.values,
                                'x': self.ds.x.values,
                                'y': self.ds.y.values,
                                'Genenames': name_list,
                                'CellGeneCount': count_list,
                                'ClassName': class_name_list,
                                'Prob': prob_list
                                },
                               columns=['Cell_Num', 'x', 'y', 'Genenames', 'CellGeneCount', 'ClassName', 'Prob']
                               )
        iss_df.set_index(['Cell_Num'])
        logger.info('finished!')

        return iss_df



class Prior(object):
    def __init__(self, cell_type):
        # list(dict.fromkeys(cell_type_name))
        self.name = cell_type
        self.nK = self.name.shape[0]
        # Check this....maybe you should divide my K-1
        self.value = np.append([.5 * np.ones(self.nK - 1) / self.nK], 0.5)
        self.logvalue = np.log(self.value)


class Genes(object):
    def __init__(self, spots):
        [gn, ispot, total_spots] = np.unique(spots.data.gene_name.data, return_inverse=True, return_counts=True)
        self.panel = xr.Dataset({'gene_gamma': xr.DataArray(np.ones(gn.shape), coords=[('gene_name', gn)]),
                                 'total_spots': xr.DataArray(total_spots, [('gene_name', gn)]),
                                 'ispot': ispot,
                                 },)

    def update_gamma(self, cells, spots, single_cell_data, egamma, ini):
        nK = single_cell_data.class_name.shape[0]

        # pSpotZero = spots.zeroKlassProb(klasses, cells)
        TotPredictedZ = spots.TotPredictedZ(self.panel.ispot.data,
                                                cells.classProb.sel({'class_name': 'Zero'}).data)

        TotPredicted = cells.geneCountsPerKlass(single_cell_data, egamma, ini)
        TotPredictedB = np.bincount(spots.geneUniv.ispot.data, spots.neighboring_cells['prob'][:, -1])

        nom = ini['rGene'] + spots.geneUniv.total_spots - TotPredictedB - TotPredictedZ
        denom = ini['rGene'] + TotPredicted
        self.panel.gene_gamma.data = nom / denom



class Spots(object):
    def __init__(self, df):
        self.data = df.rename(columns={'target': 'gene_name'})
        self.call = None
        self._genes = Genes(self)
        self.gene_panel = self._genes.panel
        self.yxCoords = self.data[['y', 'x']].values

    def _neighborCells(self, cells, cfg):
        # this needs some clean up.
        spotYX = self.yxCoords
        numCells = len(cells.yx_coords)

        # for each spot find the closest cell (in fact the top nN-closest cells...)
        nbrs = cells.nn()
        self.Dist, neighbors = nbrs.kneighbors(spotYX)

        # last column is for misreads. Id is dummy id and set to the
        # number of cells (which so-far should always be unallocated)
        neighbors[:, -1] = numCells

        # finally return
        rows = neighbors.shape[0]
        cols = neighbors.shape[1]
        out = xr.DataArray(neighbors, coords=[('spot_id', range(rows)), ('neighbor', range(cols))])
        return out

    def _cellProb(self, label_image, neighbors, cells, cfg):
        roi = cfg['roi']
        x0 = roi["x0"]
        y0 = roi["y0"]
        yxCoords = self.yxCoords
        # neighbors = self.neighboring_cells['id'].values
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

        da_1 = xr.DataArray(pSpotNeighb, coords=[('spot_id', range(nS)), ('neighbor', range(nN))])
        da_2 = xr.DataArray(SpotInCell, coords=[('spot_id', range(nS))])
        out = xr.Dataset({'cell_prob': da_1, 'label': da_2})
        return out

    def init_call(self, cells, label_image, config):
        neighbors = self._neighborCells(cells, config)
        my_ds = self._cellProb(label_image, neighbors, cells, config)
        my_ds['neighbors'] = neighbors
        self.call = my_ds

    def loglik(self, cells, cfg):
        meanCellRadius = cells.ds.mean_radius

        # Assume a bivariate normal and calc the likelihood
        mcr = meanCellRadius.data
        D = -self.Dist ** 2 / (2 * mcr ** 2) - np.log(2 * np.pi * mcr ** 2)

        # last column (nN-closest) keeps the misreads,
        D[:, -1] = np.log(cfg['MisreadDensity'])

        D[self.call.label.values > 0, 0] = D[self.call.label.values > 0, 0] + cfg['InsideCellBonus']
        print('in loglik')
        return D

    def TotPredictedZ(self, geneNo, pCellZero):
        '''
        ' given a vector
        :param spots:
        :return:
        '''
        spotNeighbours = self.call.neighbors.loc[:, [0, 1, 2]].values
        neighbourProb = self.call.cell_prob.loc[:, [0, 1, 2]].values
        pSpotZero = np.sum(neighbourProb * pCellZero[spotNeighbours], axis=1)
        TotPredictedZ = np.bincount(geneNo, pSpotZero)
        return TotPredictedZ

    def summary(self):
        # check for duplicates (ie spots with the same coordinates with or without the same gene name).
        # I dont know why but it can happen. Misfire during spot calling maybe?
        is_duplicate = self.data.duplicated(subset=['x', 'y'])

        p = []
        nbrs = []
        max_nbrs = []
        num_rows = self.data.shape[0]
        # for i in range(num_rows):
        #     if i%1000 == 0:
        #         logger.info('Spot %d out of %d' % (i, num_rows))
        #     _cp = self.call.cell_prob.loc[i, :].values
        #     _nbrs = self.call.neighbors.loc[i, :].values
        #     p.append(_cp)
        #     nbrs.append(_nbrs)
        #     max_nbrs.append(_nbrs[np.argmax(_cp)])

        cell_prob = self.call.cell_prob.values
        neighbors = self.call.neighbors.values
        logger.info('One')
        p = [cell_prob[i, :] for i in range(num_rows)]
        logger.info('Two')
        nbrs = [neighbors[i, :] for i in range(num_rows)]
        logger.info('Three')
        max_nbrs = [neighbors[i, idx] for i in range(num_rows) for idx in [np.argmax(cell_prob[i, :])]]
        logger.info('ok')

        out = pd.DataFrame()
        out['Gene'] = self.data.gene_name
        out['Expt'] = self.gene_panel.ispot
        out['x'] = self.data.x
        out['y'] = self.data.y
        out['neighbour'] = max_nbrs
        out['neighbour_array'] = nbrs
        out['neighbour_prob'] = p

        return out





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

    # sanity check
    assert ds.x.shape[0] == num_cells + 1 & ds.y.shape[0] == num_cells + 1, 'Dataset should have one extra (dummy) cell'
    assert np.isnan(ds.x[-1].values) & np.isnan(ds.y[-1].values), 'Last cell is a dummy cell, assigned to misreads. Should have nan coordinates!'

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


