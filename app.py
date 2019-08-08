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
    df = pd.read_csv('data.csv').drop('Open', axis=1)
    # chart_data = df.to_dict(orient='records')
    # chart_data = json.dumps(chart_data, indent=2)
    chart_data = df.to_json(orient='records')
    data = {'chart_data': chart_data}
    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
