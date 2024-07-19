"""A Python Flask REST API BoilerPlate (CRUD) Style"""
import argparse
import os
from flask import Flask, jsonify, make_response, render_template, redirect, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from routes import request_api, traffic_monitor_apis, docker_api
import json
import mimetypes
mimetypes.add_type('application/javascript', '.js')
APP = Flask(__name__)
APP.app_context().push()
CORS(APP)
### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Blockchain-Benchmarking-Framework-Flask-API"
    }
)
'''
def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)
'''

@APP.route("/", methods=["GET", "POST"])
def init():
    return redirect('home')

@APP.route("/home", methods=["GET"])
def home():
    return render_template('home.html')


@APP.route("/management", methods=["GET"])
def management():
    return render_template('management.html')

@APP.route("/benchmarking_engine", methods=["GET", "POST"])
def benchmarking_engine():
    li=[]
    li=json.loads(request_api.show_list())

    return render_template('benchmarking_engine.html', li=list(li[2:]))



@APP.route("/available_networks", methods=["GET"])
def available_networks():
    
    li=json.loads(request_api.show_list())
    return render_template('available_networks.html', li=list(li[2:]))


@APP.route("/monitoring", methods=["GET"])
def monitoring():
    return render_template('monitoring.html')

@APP.route("/dozzle", methods=["GET", "POST"])
def dozzle():
    return render_template('dozzle.html') 

@APP.route("/grafana", methods=["GET"])
def grafana():
    return render_template('grafana.html')      

    

APP.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


APP.register_blueprint(request_api.get_blueprint())
APP.register_blueprint(traffic_monitor_apis.get_blueprint())
APP.register_blueprint(docker_api.get_blueprint())

@APP.errorhandler(400)
def handle_400_error(_error):
    """Return a http 400 error to client"""
    
    return make_response(jsonify({'error': 'Misunderstood'}), 400)


@APP.errorhandler(401)
def handle_401_error(_error):
    """Return a http 401 error to client"""
    return make_response(jsonify({'error': 'Unauthorised'}), 401)


@APP.errorhandler(404)
def handle_404_error(_error):
    """Return a http 404 error to client"""
    return make_response(jsonify({'error': 'Not found'}), 404)


@APP.errorhandler(500)
def handle_500_error(_error):
    """Return a http 500 error to client"""
    return make_response(jsonify({'error': 'Server error'}), 500)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description="Blockchain Benchmarking Framework Flask API")

    PARSER.add_argument('--debug', action='store_true',
                        help="Use flask debug/dev mode with file change reloading")
    ARGS = PARSER.parse_args()

    PORT = int(os.environ.get('PORT', 443))

    APP.run(host='0.0.0.0', port=443, debug=True, extra_files=['./static/swagger.json'])
