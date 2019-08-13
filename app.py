import json
import os
from flask import Flask, render_template
import pandas as pd
import webbrowser
import platform
from threading import Timer
from source.run import varBayes
import pyvips
import shutil
import logging
import config

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

dir_path = os.path.dirname(os.path.realpath(__file__))

def get_browser():
    url = 'http://127.0.0.1:5005/'
    my_os = platform.system()

    if my_os == 'Windows':
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
    elif my_os == 'Darwin':  # Is this always the case for MacOS?
        chrome_path = 'open -a /Applications/Google\ Chrome.app'
    elif my_os == 'Linux':
        chrome_path = '/usr/bin/google-chrome'
    else:
        chrome_path = None

    logger.info('Platform is %s' % my_os)
    if chrome_path:
        logger.info('Chrome path: %s' % chrome_path)

    if chrome_path and os.path.isfile(chrome_path):
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path), 1)
        webbrowser.get('chrome').open_new_tab(url)
    else:
        webbrowser.open_new(url)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


def app_start(cellData, geneData, pixel_dims, roi):
    template_dir = os.path.abspath('./dashboard')
    # image_size = ",".join([str(x) for x in pixel_dims])
    image_size = '[' + str(pixel_dims[0]) + "," + str(pixel_dims[1]) + ']'

    app = Flask(__name__,
                static_url_path='',  # remove the static folder path
                static_folder='./',  # set here the path of the folder to be served
                template_folder='dashboard')  # set here the path to the folder where your html page lives

    # cellData = pd.read_json('iss.json').to_dict(orient='records')
    # geneData = pd.read_json('genes.json').to_dict(orient='records')
    cellData = cellData.to_json(orient='records')
    geneData = geneData.to_json(orient='records')
    data = {'cellData': cellData,
            'geneData': geneData,
            'name': 'default',
            'roi': roi,
            'imageSize': image_size,
            'tiles': '"./dashboard/data/img/default/32768px/{z}/{y}/{x}.png"',
            # Needs to be like that, ie single quote, then double quote
            'someText': 'this is some text'
            }

    @app.route("/")
    def index():
        return render_template("index.html", data=data)

    Timer(1, get_browser).start()
    app.run(port=5005)


def tile_maker(roi):
    dim = 32768  # DO NOT change this!
    # roi = {"x0": 6150, "x1": 13751, "y0": 12987, "y1": 18457}
    # roi = {"y0": 6150, "y1": 13751, "x0": 12987, "x1": 18457}

    img_path = os.path.join(dir_path, 'demo_data', 'background_boundaries.tif')
    out_dir = os.path.join(dir_path, 'dashboard', 'data', 'img', 'default', str(dim) + 'px')
    # remove the dir if it exists
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    im = pyvips.Image.new_from_file(img_path, access='sequential')

    # The following two lines add an alpha component to rgb which allows for transparency.
    # Is this worth it? It adds quite a bit on the execution time, about x2 increase
    # im = im.colourspace('srgb')
    # im = im.addalpha()

    assert im.width == roi['x1'] - roi['x0'] + 1 and im.height == roi['y1'] - roi['y0'] + 1, \
        "The size of the image is %d by %d but the ROI implies that the size is %d by %d" % (
        im.width, im.height, roi['x1'] - roi['x0'] + 1, roi['y1'] - roi['y0'] + 1)

    logger.info('Resizing image: %s' % img_path)
    factor = dim / max(im.width, im.height)
    im = im.resize(factor)
    logger.info('Done! Image is now %d by %d' % (im.width, im.height))
    pixel_dims = [im.width, im.height]

    # sanity check
    assert max(im.width, im.height) == dim, 'Something went wrong. Image isnt scaled up properly. ' \
                                            'It should be %d pixels in its longest side' % dim

    # expand to the nearest power of two larger square ... by default, gravity will
    # extend with 0 (transparent) pixels
    im = im.gravity('south-west', dim, dim)

    # now you can create a fresh one and populate it with tiles
    logger.info('Started doing the image tiles ')
    im.dzsave(out_dir, layout='google', suffix='.png', background=0, skip_blanks=0)
    logger.info('Done. Pyramid of tiles saved at: %s' % out_dir)

    return pixel_dims, roi


if __name__ == "__main__":
    # Timer(1, open_browser).start()
    cellData, geneData = varBayes()
    roi = config.DEFAULT['roi']
    ini = {}
    ini['cellData'] = cellData.to_json(orient='records')
    ini['geneData'] = geneData.to_json(orient='records')
    ini['roi'] = json.dumps(roi)
    ini['tiles'] = '"./dashboard/data/img/default/32768px/{z}/{y}/{x}.png"'
    if cellData is not None and geneData is not None:
        pixel_dims, roi = tile_maker(roi)
        ini['imageSize']: json.dumps(pixel_dims)
        app_start(cellData, geneData, pixel_dims, roi)
        print('Done')
