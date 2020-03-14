from flask import Flask, request, jsonify
import json
import requests
import logging
import traceback
import os
from classes import *
from pilight import establishConnection
from pprint import pprint

# Create custom logger to use
logger = logging.getLogger('api')
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)
logger.info('Started.')

establishConnection()
logger.info('Pilight connection established.')


app = Flask(__name__)
config_file_path = os.path.dirname(__file__) + "/config.json"

devices = {}

# Hide webserver logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)


def createDevices():
    with open(config_file_path) as f:
        config = json.load(f)
    for accessory in config['accessories']:
        devices[accessory['id']] = Fan(accessory)
        pass
    logger.debug(
        ', '.join([(str(i) + ": " + devices[i].name) for i in devices]))
    pprint(devices)
    pass


def error(msg):
    return {'success': False, 'message': msg}


def getSyncPack(device_id):
    return {
        "light-on": int(devices[device_id].light.getState()),
        "fan-on": int(devices[device_id].getOn()),
        "fan-speed": int(devices[device_id].getSpeed())
    }


def getName(device_id):
    return devices[device_id].name


@app.route("/apiv2/status", methods=["GET"])
def statusComplete():
    data = request.get_json()
    device_id = str(data.get('id', -1))
    response = {'success': True, 'id': device_id}
    status_code = 200

    # Check if we have device with supplied ID
    if device_id in devices:
        try:
            response['sync'] = getSyncPack(device_id)
        except Exception as e:
            response = error("Error in getting status of " +
                             getName(device_id))
            status_code = 500
            logger.error(traceback.format_exc())
    else:
        response = error(
            "Device ID '{}' not found.".format(device_id))
        status_code = 400

    # Log to console
    logger.debug('Received request: ' + str(data))
    logger.debug('Device:{}, Mode:{}, Response:{}'.format(
        getName(device_id),
        'Light' if int(data.get('light', False)) else 'Fan',
        json.dumps(response)
    ))

    return json.dumps(response), status_code


@app.route("/apiv2/update", methods=["GET", "POST"])
def update():
    data = request.get_json()
    device_id = str(data.get('id', -1))
    sync = dict(data.get('sync'))
    response = {'success': True, 'id': device_id}
    status_code = 200

    if device_id in devices:
        try:
            devices[device_id].setState(sync)
        except Exception as e:
            response = error("Error in setting status of " +
                             getName(device_id))
            status_code = 500
            logger.error(traceback.format_exc())

        response['sync'] = getSyncPack(device_id)
    else:
        response = error("Device ID '{}' not found.".format(device_id))
        status_code = 400

    return json.dumps(response), status_code


if __name__ == "__main__":
    createDevices()
    print('\nFlask Startup:')
    app.run(debug=False, host='0.0.0.0', port='5010')
