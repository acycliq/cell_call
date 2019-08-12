import json
import os
from flask import Flask, render_template
import pandas as pd
import webbrowser
import platform
from threading import Timer
import logging

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

template_dir = os.path.abspath('./dashboard')
app = Flask(__name__,
            static_url_path='',  # remove the static folder path
            static_folder='./',  # set here the path of the folder to be served
            template_folder='dashboard')  # set here the path to the folder where your html page lives

cellData = pd.read_json('iss.json').to_dict(orient='records')
geneData = pd.read_json('genes.json').to_dict(orient='records')
data = {'cellData': cellData,
        'geneData': geneData,
        'name': '98 gene panel',
        'roi': '{x0: 6150, x1: 13751, y0: 12987, y1: 18457}',
        'imageSize': '[16384, 11791]',
        'tiles': '"./dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png"',
        # Needs to be like that, ie single quote, then double quote
        'someText': 'this is some text'
        }


@app.route("/")
def index():
    return render_template("index.html", data=data)


def get_browser():
    url = 'http://127.0.0.1:5000/'
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


if __name__ == "__main__":
    # Timer(1, open_browser).start()
    Timer(1, get_browser).start()
    app.run(port=5000)
    print('Done')
