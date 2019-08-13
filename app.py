import json
import os
from flask import Flask, render_template
import webbrowser
import platform
import random
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


def get_browser(port_num):
    # port = 5000 + random.randint(0, 999)
    url = 'http://127.0.0.1:%s' % str(port_num)
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


def app_start(config):
    template_dir = os.path.abspath('./dashboard')
    port = 5000 + random.randint(0, 999)

    app = Flask(__name__,
                static_url_path='',  # remove the static folder path
                static_folder='./',  # set here the path of the folder to be served
                template_folder='dashboard')  # set here the path to the folder where your html page lives

    @app.route("/")
    def index():
        return render_template("index.html", data=config)

    Timer(1, get_browser, [port]).start()
    app.run(port=port)


def tile_maker(roi):
    dim = 32768

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

    return pixel_dims


def mk_ini(cellData, geneData, pixel_dims):
    ini = {}
    ini['name'] = json.dumps('98 gene panel')
    ini['roi'] = json.dumps(config.DEFAULT['roi'])
    ini['imageSize'] = json.dumps(pixel_dims)
    ini['cellData'] = cellData.to_json(orient='records')
    ini['geneData'] = geneData.to_json(orient='records')
    ini['tiles'] = json.dumps(config.DEFAULT['tiles'])

    return ini


if __name__ == "__main__":
    # 1. run the cell calling algo
    cellData, geneData = varBayes()

    # 2. start the viewer
    if cellData is not None and geneData is not None:
        pixel_dims = tile_maker(config.DEFAULT['roi'])

        # 2a. First make a dict to keep the configuration
        ini = mk_ini(cellData, geneData, pixel_dims)

        # 2b. Now push everything into the viewer
        app_start(ini)
        print('Done')
