import numpy as np
import pandas as pd
import os
import xarray as xr
from source.utils import loadmat
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = dir_path + '/config.yml'


logger = logging.getLogger()
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s:%(levelname)s:%(message)s"
#     )


def _load_geneset(config):
    '''
    :param config:
    :return:
    '''
    genesetPath = os.path.join(dir_path, config['geneset'])
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


def geneSet(spots, config):
    genes = spots.gene_panel.gene_name.values
    ge = _load_geneset(config)

    # make a dataframe from the xarray
    logger.info('Renaming subclasses PC.CA2 and PC.CA3 to be PC.Other1 and PC.Other2')
    class_name = ['PC.Other1' if x == 'PC.CA2' else x for x in ge.Class.values]
    class_name = ['PC.Other2' if x == 'PC.CA3' else x for x in class_name]
    df = pd.DataFrame(ge.data, index=ge.GeneName.values, columns=class_name, dtype='float64')
    df = df.loc[genes]

    df = _normalise(df)

    # take the transpose, ie classes-by-genes
    dft = df.T

    # loop over genes and calc the mean expression within each cell type
    mean_expression = config['Inefficiency'] * dft.groupby(level=0, sort=False).mean().T

    # sort the dataframe (the index only)
    mean_expression = mean_expression.sort_index(axis=0)

    # append the zero cell
    mean_expression['Zero'] = np.zeros([mean_expression.shape[0], 1])

    log_mean_expression = np.log(mean_expression + config['SpotReg'])

    ds = xr.Dataset(
        data_vars={'mean_expression': (('gene_name', 'class_name'), mean_expression),
                   'log_mean_expression': (('gene_name', 'class_name'), log_mean_expression)},
        coords={'gene_name': mean_expression.index.values,
                'class_name': mean_expression.columns.values}
    )

    return ds
