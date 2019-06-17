import numpy as np
import pandas as pd
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


def geneSet(genes, config):
    ge = _load_geneset(config)

    # make a dataframe from the xarray
    df = pd.DataFrame(ge.data, index=ge.GeneName, columns=ge.Class, dtype='float64')
    df = df.loc[genes]

    df = _normalise(df)

    # take the transpose, ie classes-by-genes
    dft = df.T

    # loop over genes and calc the mean expression within each cell type
    mean_expression = config['Inefficiency'] * dft.groupby(level=0).mean().T

    # sort the dataframe
    mean_expression = mean_expression.sort_index(axis=1).sort_index(axis=0)

    # append the zero cell
    mean_expression['Zero'] = np.zeros([mean_expression.shape[0], 1])

    log_mean_expression = np.log(mean_expression + config['SpotReg'])

    return mean_expression, log_mean_expression
