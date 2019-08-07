from flask import Flask, render_template

app = Flask(__name__)

# faking datasets that can be returned from a api or database
swarm_services = ['my-web-service', 'my-api-service']
swarm_tasks = {
    "my-web-service": {
        "container_names": [
            "my-web-service.1.alfjshoehfosfn",
            "my-web-service.2.fuebchduehakjdu"
        ]
    },
    "my-api-service": {
        "container_names": [
            "my-api-service.1.oprudhyuythvbzx",
            "my-api-service.2.sjduebansifotuf"
        ]
    }
}

def get_container_name(app_name):
    data = []
    response = swarm_tasks[app_name]
    for container in response['container_names']:
        data.append(container)
    return render_template('index.html', app_name=app_name, number=len(data), data=data)

@app.route('/')
def list():
    return render_template('list.html', number=len(swarm_services), apps=swarm_services, aws_region='eu-west-1', cloudwatch_log_stream='docker-swarm-lg')

@app.route('/describe/<string:app_name>')
def get_app(app_name):
    app = get_container_name(app_name)
    return app

if __name__ == '__main__':
    app.run()

# default is 63342