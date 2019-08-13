from source.systemData import Cells, Spots, Prior
from source.utils import loadmat
from source.singleCell import geneSet
import config
import source.common as common
import starfish as sf
import pandas as pd
import source.utils as utils
import os
import logging


dir_path = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger()


def varBayes():
    roi = config.DEFAULT['roi']
    label_image_path = os.path.join(dir_path, config.DEFAULT['label_image'])
    logger.info("reading CellMap from %s" % label_image_path)
    label_image = loadmat(os.path.join(label_image_path))
    label_image = label_image["CellMap"]
    saFile = os.path.join(dir_path, config.DEFAULT['saFile'])

    cells = Cells(label_image, config.DEFAULT)

    logger.info('********* Getting spot attributes from %s **********', saFile)
    sa_df = pd.read_csv(saFile)
    sa_df = sa_df.rename(columns={'xc': 'x',
                          'yc': 'y',
                          'zc': 'z',
                          'Gene': 'target'}
                 )
    sa = sf.types.SpotAttributes(sa_df)

    logger.warning('*******************************')
    logger.warning('** WARNING WARNING WARNING ***')
    logger.warning('** Spot coordinates are populated from a matlab file (ie 1-based) ***')
    logger.warning('** Removing one pixel from both X and Y coordinates ***')
    sa.data['x'] = sa.data.x - 1
    sa.data['y'] = sa.data.y - 1
    logger.warning('** REMOVE this adjustment in the LIVE CODE ***')
    logger.warning('*******************************')

    spots = Spots(sa.data)
    single_cell_data = geneSet(spots, config.DEFAULT)
    prior = Prior(single_cell_data.coords['class_name'].values)
    spots.init_call(cells, label_image, config.DEFAULT)


    p0 = None
    iss_df = None
    gene_df = None
    for i in range(100):
        # 1. call cell gammas
        egamma, elgamma = common.expected_gamma(cells, spots, single_cell_data, config.DEFAULT)

        # 2 call cells
        common.celltype_assignment(cells, spots, prior, single_cell_data, config.DEFAULT)

        # 3 call spots
        common.call_spots(spots, cells, single_cell_data, prior, elgamma, config.DEFAULT)

        # 4 update gamma
        common.updateGamma(cells, spots, single_cell_data, egamma, config.DEFAULT)

        converged, delta = utils.isConverged(spots, p0, config.DEFAULT['CellCallTolerance'])
        logger.info('Iteration %d, mean prob change %f' % (i, delta))

        # replace p0 with the latest probabilities
        p0 = spots.call.cell_prob.values

        if converged:
            # cells.iss_summary(spots)
            # spots.summary()
            iss_df, gene_df = common.collect_data(cells, spots)
            print("Success!!")
            break

    return iss_df, gene_df



logger.info('Done')

