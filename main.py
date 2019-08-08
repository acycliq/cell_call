from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
    data = {'username': 'Pang', 'site': 'stackoverflow.com'}
    return render_template('settings.html', data=data)


app.run()
