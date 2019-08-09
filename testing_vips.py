import os
import pyvips
import logging
import shutil

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

dim = 32768
img_path = 'background_boundaries.tif'
out_dir = str(dim) + 'px'

im = pyvips.Image.new_from_file('background_boundaries.tif', access='sequential')
im = im.colourspace('srgb')
im = im.addalpha()


logger.info('Resising image: %s' % img_path)
factor = dim / max(im.width, im.height)
im = im.resize(factor)

# expand to the nearest power of two larger square ... by default, gravity will
# extend with 0 (transparent) pixels
im = im.gravity('south-west', dim, dim)

logger.info('Started doing the image tiles ')
if os.path.exists(out_dir):
    # remove the dir if it exists
    shutil.rmtree(out_dir)

# now you can create a fresh one and populate it with tiles
im.dzsave(out_dir, layout='google', suffix='.png', background=0, skip_blanks=0)
logger.info('Done. Pyramid of tile saved at: %s' % out_dir)
print('info')

