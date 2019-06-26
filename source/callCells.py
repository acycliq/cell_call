import os
import utils
import numpy as np
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
    scaled_mean = cells.stats.sel(columns='area_factor') * ds.mean_expression
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

    expected_gamma = spots.geneUniv.sel(columns='expected_gamma')
    ScaledExp = cells.stats.sel(columns='area_factor') * expected_gamma * ds.mean_expression + cfg['SpotReg']
    pNegBin = ScaledExp / (cfg['rSpot'] + ScaledExp)
    # contr = utils.nb_negBinLoglik(CellGeneCount[:,:,None], ini['rSpot'], pNegBin)
    gc = cells.geneCount(spots)
    # x * log(p) + r * log(1 - p)
    contr = utils.negBinLoglik(gc, cfg['rSpot'], pNegBin)
    # assert np.all(nb_contr == contr)
    wCellClass = np.sum(contr, axis=1) + prior.logvalues
    pCellClass = utils.softmax(wCellClass)

    cells.classProb = pCellClass
    logger.info('Cell 0 is classified as %s with prob %4.8f' % (
        prior.name[np.argmax(wCellClass[0, :])], pCellClass[0, np.argmax(wCellClass[0, :])]))
    logger.info('cell ---> klass probabilities updated')
    return pCellClass


def cell_assignment(spots, cells, genes, klasses):
    # spot to cell assignment
    nN = spots.neighbors['id'].shape[1]
    nS = spots.nS
    nK = klasses.nK
    aSpotCell = np.zeros([nS, nN])
    for n in range(nN - 1):
        c = spots.neighbors['id'][:, n]
        # logger.info('genes.spotNo should be something line spots.geneNo instead!!')
        meanLogExpression = np.squeeze(genes.logExpression[:, spots.geneNo, :])
        classProb = cells.classProb[c, :]
        term_1 = np.sum(classProb * meanLogExpression, axis=1)
        expectedLog = utils.bi2(spots.expectedLogGamma, [nS, nK], c[:, None], spots.geneNo[:, None])
        term_2 = np.sum(cells.classProb[c, :] * expectedLog, axis=1)
        aSpotCell[:, n] = term_1 + term_2
    wSpotCell = aSpotCell + spots.D

    # update the prob a spot belongs to a neighboring cell
    pSpotNeighb = utils.softmax(wSpotCell)
    spots.neighbors['prob'] = pSpotNeighb
    logger.info('spot ---> cell probabilities updated')