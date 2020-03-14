import json
import requests
import logging
import os
from classes_old import *
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


from flask import Flask, request, jsonify

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
    logger.debug(', '.join([(str(i) + ": " + devices[i].name) for i in devices]))
    pprint(devices)
    pass


def dict_merge(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


@app.route("/api/status", methods=["GET"])
def status():
    data = request.get_json()  # request.args
    response = {'success': True}

    def error(msg):
        return {'success': False, 'message': msg}

    id = str(data.get('id', -1))

    # Check if we have device with supplied ID
    if id in devices:
        # Check if asking for light
        if int(data.get('light', False)):
            # Check if the device has a light
            if devices.get(id).hasLight():
                response['on'] = int(devices[id].light.getState())
            else:
                response = error('Device ID {} does not have a light.'.format(id))

        else:
            response['speed'] = int(devices[id].getState())
    else:
        response = error('Device ID of {} not found.'.format(id))

    # Log to console
    logger.debug('Received request: ' + str(data))
    logger.debug('Device:{}, Mode:{}, Response:{}'.format(
        data.get('id', 'null'),
        'Light' if int(data.get('light', False)) else 'Fan',
        json.dumps(response)
    ))

    return json.dumps(response)


@app.route("/api/update", methods=["GET", "POST"])
def update():
    data = request.get_json()  # dict_merge(request.args, request.form) #{**request.args, **request.form}
    response = {'success': True}
    output = ''
    id = str(data.get('id', -1))

    def error(msg):
        return {'success': False, 'message': msg}

    # Check if we have device with supplied ID
    if id in devices and data.get('state') != None:
        # Check if asking for light
        if int(data.get('light', False)):
            # Check if the device has a light
            if devices.get(id).hasLight():
                if not devices[id].light.setState(data.get('state')):
                    response = error('Invalid state value provided.')
            else:
                response = error('Device ID {} does not have a light.'.format(data['id']))

        else:
            if not devices[id].setState(data.get('state')):
                response = error('Invalid state value provided.')
    else:
        response = error('Device ID of {} not found or state not provided.'.format(id))

    # Log to console
    logger.debug('Received request: ' + str(data))
    logger.debug('Device:{}, Mode:{}, Response:{}'.format(
        data.get('id', 'null'),
        'Light' if int(data.get('light', False)) else 'Fan',
        json.dumps(response)
    ))

    return json.dumps(response)


if __name__ == "__main__":
    createDevices()
    print('\nFlask Startup:')
    app.run(debug=False, host='0.0.0.0', port='5010')
