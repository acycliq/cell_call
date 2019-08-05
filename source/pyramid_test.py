import sys
import pyvips

im = pyvips.Image.new_from_file(sys.argv[1], access='sequential')

im = im.addalpha()

# expand to the nearest power of two larger square ... by default, gravity will
# extend with 0 (transparent) pixels
size = 1 << int.bit_length(max(im.width, im.height))
im = im.gravity('south-west', size, size)

im.dzsave(sys.argv[2],
          layout='google', suffix='.png', background=0, skip_blanks=0)