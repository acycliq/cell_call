import json
import os
from flask import Flask, render_template
import pandas as pd

template_dir = os.path.abspath('./dashboard')
app = Flask(__name__,
            static_url_path='',  # remove the static folder path
            static_folder='./',  # set here the path of the folder to be served
            template_folder='dashboard')  # set here the path to the folder where your html page lives

@app.route("/")
def index():
    cellData = pd.read_json('iss.json').to_dict(orient='records')
    geneData = pd.read_json('genes.json').to_dict(orient='records')
    data = {'cellData': cellData,
            'geneData': geneData,
            'name': '98 gene panel',
            'roi': '{x0: 6150, x1: 13751, y0: 12987, y1: 18457}',
            'imageSize': '[16384, 11791]',
            'tiles': '"./dashboard/data/img/default_98genes/16384px/{z}/{x}/{y}.png"', # Needs to be like that, ie single quote, then double quote
            'someText': 'this is some text'
            }
    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
