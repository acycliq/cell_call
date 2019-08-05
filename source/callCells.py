import os
import utils
import numpy as np
import xarray as xr
from sklearn.neighbors import NearestNeighbors
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = dir_path + '/config.yml'


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


def expected_gamma(cells, spots, ds, ini):
    scaled_mean = cells.ds.area_factor * ds.mean_expression
    rho = ini['rSpot'] + cells.geneCount(spots)
    beta = ini['rSpot'] + scaled_mean

    expected_gamma = utils.gammaExpectation(rho, beta)
    expected_loggamma = utils.logGammaExpectation(rho, beta)

    return expected_gamma, expected_loggamma


def celltype_assignment(cells, spots, prior, ds, cfg):
    '''
    return a an array of size numCells-by-numCellTypes where element in position [i,j]
    keeps the probability that cell i has cell type j
    :param spots:
    :param config:
    :return:
    '''

    gene_gamma = spots.gene_panel.gene_gamma
    ScaledExp = cells.ds.area_factor * gene_gamma * ds.mean_expression + cfg['SpotReg']
    pNegBin = ScaledExp / (cfg['rSpot'] + ScaledExp)
    # contr = utils.nb_negBinLoglik(CellGeneCount[:,:,None], ini['rSpot'], pNegBin)
    gc = cells.geneCount(spots)
    # x * log(p) + r * log(1 - p)
    contr = utils.negBinLoglik(gc, cfg['rSpot'], pNegBin)
    # assert np.all(nb_contr == contr)
    wCellClass = np.sum(contr, axis=1) + prior.logvalue
    pCellClass = utils.softmax(wCellClass)

    cells.classProb = pCellClass
    logger.info('Cell 0 is classified as %s with prob %4.8f' % (
        prior.name[np.argmax(wCellClass[0, :])], pCellClass[0, np.argmax(wCellClass[0, :])]))
    logger.info('cell ---> klass probabilities updated')
    return pCellClass



def call_spots(spots, cells, single_cell_data, prior, elgamma, cfg):
    # spot to cell assignment
    nN = spots.call.neighbors.shape[1]
    nS = spots.data.gene_name.shape[0]
    nK = prior.nK
    aSpotCell = np.zeros([nS, nN])
    gn = spots.data.gene_name.values
    expected_spot_counts = single_cell_data['log_mean_expression'].sel({'gene_name': gn}).data
    for n in range(nN - 1):
        spots_name = spots.gene_panel.gene_name.values[spots.gene_panel.ispot.values]
        single_cell_data['log_mean_expression'].sel({'gene_name': spots_name})

        # get the spots' nth-closest cell
        sn = spots.call.neighbors.loc[:, n].values

        # get the respective cell type probabilities
        cp = cells.classProb.sel({'cell_id': sn}).data

        # multiply and sum over cells
        term_1 = (expected_spot_counts * cp).sum(axis=1)


        # logger.info('genes.spotNo should be something line spots.geneNo instead!!')
        expectedLog = utils.bi2(elgamma.data, [nS, nK], sn[:, None], spots.gene_panel.ispot.data[:,None])
        term_2 = np.sum(cp * expectedLog, axis=1)
        aSpotCell[:, n] = term_1 + term_2
    wSpotCell = aSpotCell + spots.loglik(cells, cfg)

    # update the prob a spot belongs to a neighboring cell
    pSpotNeighb = utils.softmax2(wSpotCell)
    spots.call.cell_prob.data = pSpotNeighb
    logger.info('spot ---> cell probabilities updated')


def updateGamma(cells, spots, single_cell_data, egamma, ini):
    nK = single_cell_data.class_name.shape[0]

    # pSpotZero = spots.zeroKlassProb(klasses, cells)
    TotPredictedZ = spots.TotPredictedZ(spots.gene_panel.ispot.data, cells.classProb.sel({'class_name': 'Zero'}).data)

    TotPredicted = cells.geneCountsPerKlass(single_cell_data, egamma, ini)

    TotPredictedB = np.bincount(spots.gene_panel.ispot.data, spots.call.cell_prob.loc[:, 3].data)

    nom = ini['rGene'] + spots.gene_panel.total_spots - TotPredictedB - TotPredictedZ
    denom = ini['rGene'] + TotPredicted
    spots.gene_panel.gene_gamma.data = nom / denom
    # cells.expectedGamma = nom / denom


def geneCountsPerKlass(cells, single_cell_data, egamma, ini):
    temp = cells.classProb * cells.ds.area_factor * egamma
    temp = temp.sum(dim='cell_id')
    ClassTotPredicted = temp * (single_cell_data.mean_expression + ini['SpotReg'])
    TotPredicted = ClassTotPredicted.drop('Zero', dim='class_name').sum(dim='class_name')
    return TotPredicted
