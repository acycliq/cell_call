from source.systemData import Cells
from systemData import Spots
from utils import loadmat
from singleCell import geneSet
import source.config as config
import callCells
import starfish as sf
import xarray as xr
import os
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )


roi = config.DEFAULT['roi']

label_image_path = config.DEFAULT['label_image']
print("reading CellMap from %s" % label_image_path)
label_image = loadmat(os.path.join(label_image_path))
label_image = label_image["CellMap"]

saFile = "../data_preprocessed/spot_attributes.nc"



cells = Cells(label_image, config.DEFAULT)
c = cells.collection[0]


logger.info('********* Getting spotattributes from %s **********', saFile)
sa = sf.types.SpotAttributes(xr.open_dataset(saFile).to_dataframe())

logger.warning('*******************************')
logger.warning('** WARNING WARNING WARNING ***')
logger.warning('** Spot coordinates are populated from a matlab file (ie 1-based) ***')
logger.warning('** Removing one pixel from both X and Y coordinates ***')
sa.data['x'] = sa.data.x - 1
sa.data['y'] = sa.data.y - 1
logger.warning('** REMOVE this adjustment in the LIVE CODE ***')
logger.warning('*******************************')

spots = Spots(sa.data)

geneUniv = spots.geneUniv()
mean_expression, log_mean_expression = geneSet(geneUniv, config.DEFAULT)
classNames = mean_expression.columns.values
geneNames = mean_expression.index.values
ds = xr.Dataset(
    data_vars={'mean_expression': (('geneName', 'className'), mean_expression)},
    coords={'geneName': geneNames,
            'classname': classNames}
)

logger.info('step1')
spots.collection[0].closestCell(cells.nn())
# spots.closestCell(cells.coords())


logger.info('step2')
# spots._neighborCells(cells, config.DEFAULT)
# spots._cellProb(label_image, config.DEFAULT)
# cells.geneCount(spots)
spots.neighCells(cells, label_image, config.DEFAULT)
CellGeneCount = cells.geneCount(spots)

# cells.cellTypeProb(spots, meanExpression, config)
print(spots.collection[0].parentCell)
logger.info('Done')

