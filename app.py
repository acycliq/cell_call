import json
import os
from flask import Flask, render_template
import pandas as pd
import webbrowser
import platform
import threading

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
    elif my_os == 'Darwin':
        chrome_path = 'open -a /Applications/Google\ Chrome.app'
    elif my_os == 'Linux':
        chrome_path = '/usr/bin/google-chrome'
    else:
        chrome_path = None

    if os.path.isfile(chrome_path):
        webbrowser.get(chrome_path).open_new(url)
    else:
        webbrowser.open_new(url)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == "__main__":
    # threading.Timer(1.25, lambda: get_browser('index.html')).start()
    # # get_browser('./dashboard/index.html')
    # webbrowser.open_new('http://127.0.0.1:5000/')
    # app.run(debug=True)

    # threading.Timer(1, open_browser).start();
    threading.Timer(1, get_browser).start();
    app.run(port=5000)
    print('Done')