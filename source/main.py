from source.systemData import Cells
from systemData import Spot
from utils import loadmat
from systemData import geneSet
import source.config as config
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
df = sa.data

spots = []
for r in zip(df.index, df.x, df.y, df.target):
    spots.append(Spot(r[0], r[1], r[2], r[3]))


geneSet(config.DEFAULT)


print('Done')

