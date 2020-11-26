from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import logging
import traceback
import pymysql
import json

import constants
import response
import message

app = Flask(__name__)
logger = logging.getLogger()
CORS(app)


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    error_dict = {
        'code': error.code,
        'description': error.description,
        'stack_trace': traceback.format_exc()
    }
    log_msg = f"HTTPException {error_dict.code}, Description: {error_dict.description}, Stack trace: {error_dict.stack_trace}"
    logger.log(msg=log_msg)
    log_response = jsonify(error_dict)
    log_response.status_code = error.code
    return log_response


@app.route("/")
def route_main():
    return constants.SERVER_NAME


@app.route("/echo", methods=['GET', 'POST'])
def route_echo():
    data = ''
    if request.method == 'GET':
        data = request.args.get('data')
    if request.method == 'POST':
        data = request.form['data']
    return {"type": request.method, "data": data}


@app.route("/connect", methods=['GET', 'POST'])
def route_connect():
    device = ''
    if request.method == 'GET':
        device = request.args.get('device')
    if request.method == 'POST':
        device = request.form['device']
    return response_normal(response.CODE_SUCCESS, None)


@app.route("/users/<device>/packet", methods=['GET', 'POST'])
def route_users_packet(device):
    packet = ''
    if request.method == 'GET':
        response_normal(response.CODE_FAIL, 'REQUEST TYPE MUST BE POST')
    if request.method == 'POST':
        packet = request.form['data']
    return response_normal(response.CODE_SUCCESS, None)


@app.route("/users/<device>/process", methods=['GET', 'POST'])
def route_users_process(device):
    process = ''
    if request.method == 'GET':
        response_normal(response.CODE_FAIL, 'REQUEST TYPE MUST BE POST')
    if request.method == 'POST':
        process = request.form['data']
    return response_normal(response.CODE_SUCCESS, None)


@app.route("/users/<device>/event", methods=['GET', 'POST'])
def route_users_event(device):
    return response_normal(response.CODE_SUCCESS, None)


@app.route("/manage/<password>/monitor", methods=['GET', 'POST'])
def route_manage_monitor(password):
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    return response_normal(response.CODE_SUCCESS, None)


@app.route("/manage/<password>/<device>", methods=['GET', 'POST'])
def route_manage_device(password, device):
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    return response_normal(response.CODE_SUCCESS, None)


@app.route("/manage/<password>/reset", methods=['GET', 'POST'])
def route_manage_reset(password):
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    return response_normal(response.CODE_SUCCESS, None)


def response_normal(response_code, response_error):
    if response_error is None:
        return {"code": response_code}
    else:
        return {"code": response_code, "error": response_error}


def response_message(response_code, messages):
    return {"code": response_code, "messages": messages}


if __name__ == "__main__":
    app.run(host=constants.SERVER_IP, port=constants.SERVER_PORT)

'''
    db = pymysql.connect(
        host=constants.DB_HOST,
        port=constants.DB_PORT,
        user=constants.DB_USER,
        passwd=constants.DB_PASSWD,
        db=constants.DB_NAME,
        charset=constants.DB_CHARSET,
        autocommit=constants.DB_AUTOCOMMIT)
    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    db.close()
    '''