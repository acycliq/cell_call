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
roi = {"x0": 6150, "x1": 13751, "y0": 12987, "y1": 18457}
# roi = {"y0": 6150, "y1": 13751, "x0": 12987, "x1": 18457}

img_path = os.path.join('demo_data', 'background_boundaries.tif')
out_dir = str(dim) + 'px'
# remove the dir if it exists
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)

im = pyvips.Image.new_from_file(img_path, access='sequential')

# The following two lines add an alpha component to rgb which allows for transparency.
# Is this worth it? It adds quite a bit on the execution time, about x2 increase
# im = im.colourspace('srgb')
# im = im.addalpha()

assert im.width == roi['x1']-roi['x0']+1 and im.height == roi['y1']-roi['y0']+1, \
    "The size of the image is %d by %d but the ROI implies that the size is %d by %d" % (im.width, im.height, roi['x1']-roi['x0']+1, roi['y1']-roi['y0']+1)


logger.info('Resising image: %s' % img_path)
factor = dim / max(im.width, im.height)
im = im.resize(factor)

# expand to the nearest power of two larger square ... by default, gravity will
# extend with 0 (transparent) pixels
im = im.gravity('south-west', dim, dim)

# now you can create a fresh one and populate it with tiles
logger.info('Started doing the image tiles ')
im.dzsave(out_dir, layout='google', suffix='.png', background=0, skip_blanks=0)
logger.info('Done. Pyramid of tiles saved at: %s' % out_dir)
print('info')

