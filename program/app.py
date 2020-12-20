from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import traceback
import pymysql
import json
import datetime

import constants
import response
import message

app = Flask(__name__)
logger = logging.getLogger()
CORS(app)


def json_default(value):
    if isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')
    raise TypeError('not JSON serializable')


def sql_fetch_json(cursor: pymysql.cursors.Cursor):
    """
    Convert the pymysql SELECT result to json format
    :param cursor:
    :return:
    """
    keys = []
    for column in cursor.description:
        keys.append(column[0])
    key_number = len(keys)

    json_data = []
    for row in cursor.fetchall():
        item = dict()
        for q in range(key_number):
            item[keys[q]] = row[q]
        json_data.append(item)

    return json_data


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    error_dict = {
        'code': error.code,
        'description': error.description,
        'stack_trace': traceback.format_exc()
    }
    log_msg = f"HTTPException {error_dict['code']}, Description: {error_dict['description']}, Stack trace: {error_dict['stack_trace']}"
    logger.log(level=5, msg=log_msg)
    log_response = jsonify(error_dict)
    log_response.status_code = error.code
    return log_response


def connect_database():
    db = pymysql.connect(
        host=constants.DB_HOST,
        port=constants.DB_PORT,
        user=constants.DB_USER,
        passwd=constants.DB_PASSWD,
        db=constants.DB_NAME,
        charset=constants.DB_CHARSET,
        autocommit=constants.DB_AUTOCOMMIT)
    return db


def monitor_network():
    print("CHECKING NETWORKS")
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT CURRENT_TIMESTAMP()")
        current_time = cursor.fetchone()
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM `networks` WHERE `network_status` = 0 AND `network_end` <= (%s - interval '60' second)", current_time)
        results = cursor.fetchall()
        result_count = cursor.rowcount
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    for network_item in results:
        print("MACHINE-LEARNING")
        # send to machine-learning
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE `networks` SET `network_status` = 1 WHERE `network_status` = 0 AND `network_end` <= (%s - interval '60' second)", current_time)
        results = cursor.fetchall()
        result_count = cursor.rowcount
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()


def handle_packet(device, raw_data):
    try:
        data = json.loads(raw_data)
        packet = data['packet']
        process = data['process']
        if packet.get("Ethernet") is not None:
            packet_ethernet = packet['Ethernet']
            packet_ethernet_dst = packet_ethernet['dst']
            packet_ethernet_src = packet_ethernet['src']
        if packet.get("IP") is not None:
            packet_ip = packet['IP']
            packet_ip_len = packet_ip['len']
            packet_ip_proto = packet_ip['proto']
            packet_ip_src = packet_ip['src']
            packet_ip_dst = packet_ip['dst']
        if packet.get("TCP") is not None:
            packet_tcp = packet['TCP']
            packet_tcp_sport = packet_tcp['sport']
            packet_tcp_dport = packet_tcp['dport']
        if packet.get("UDP") is not None:
            packet_udp = packet['UDP']
            packet_udp_sport = packet_udp['sport']
            packet_udp_dport = packet_udp['dport']
        process_name = process['name']
        process_status = process['status']
        process_local_ip = process['local_ip']
        process_local_port = process['local_port']
        process_remote_ip = process['remote_ip']
        process_remote_port = process['remote_port']
        protocol_type = 0
        packet_port_src = 0
        packet_port_dst = 0
        if packet_ip_proto == 'tcp':
            protocol_type = 1
            packet_port_src = packet_tcp_sport
            packet_port_dst = packet_tcp_dport
        if packet_ip_proto == 'udp':
            protocol_type = 2
            packet_port_src = packet_udp_sport
            packet_port_dst = packet_udp_dport
        if packet_port_src == 'http':
            packet_port_src = 80
        if packet_port_dst == 'http':
            packet_port_dst = 80
        if packet_port_src == 'https':
            packet_port_src = 443
        if packet_port_dst == 'https':
            packet_port_dst = 443
        # check process is packet owner
    except ValueError as error:
        return response_normal(response.CODE_ERROR, error)
    # get process by name
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM `processes` WHERE `process_name` = %s", process_name)
        results = cursor.fetchall()
        result_count = cursor.rowcount
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    if result_count == 0:
        db = connect_database()
        try:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO `processes` (`process_name`, `process_type`, `process_level`)  VALUES (%s, 0, 0)", process_name)
            db.commit()
            process_index = cursor.lastrowid
        except RuntimeError as error:
            return response_normal(response.CODE_ERROR, error)
        finally:
            db.close()
    else:
        process_index = results[0][0]
    # check is part of existing network
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM `networks` WHERE `network_status` = 0 AND `network_device` = %s AND `network_process` = %s ORDER BY `network_index` DESC LIMIT 1",
            (str(device), int(process_index)))
        results = cursor.fetchall()
        result_count = cursor.rowcount
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    if result_count == 0:
        db = connect_database()
        try:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO `networks` (`network_device`, `network_process`, `network_status`, `network_start`, `network_end`, `network_type`, `network_srcip`, `network_dstip`, `network_srcdevice`, `network_dstdevice`, `network_protocol`, `network_srcport`, `network_dstport`, `network_srcpackets`, `network_dstpackets`, `network_srcbytes`, `network_dstbytes`) "
                "VALUES (%s, %s, %s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (str(device), int(process_index), 0, 0, packet_ip_src, packet_ip_dst, packet_ethernet_src, packet_ethernet_dst, int(protocol_type), packet_port_src, packet_port_dst, 1, 0, int(packet_ip_len), 0))
            db.commit()
            network_index = cursor.lastrowid
        except RuntimeError as error:
            return response_normal(response.CODE_ERROR, error)
        finally:
            db.close()
    else:
        network_index = results[0][0]
        #print("network_srcip : "+results[0][7])
        #print("network_dstip : "+results[0][8])
        #print("packet src ip : "+packet_ip_src)
        #print("packet dst ip : "+packet_ip_dst)
        if results[0][7] == packet_ip_src:
            packet_src_add = 1
            packet_dst_add = 0
            byte_src_add = packet_ip_len
            byte_dst_add = 0
        if results[0][7] == packet_ip_dst:
            packet_src_add = 0
            packet_dst_add = 1
            byte_src_add = 0
            byte_dst_add = packet_ip_len
        #print("packet_src_add : "+str(packet_src_add))
        #print("packet_dst_add : "+str(packet_dst_add))
        #print("byte_src_add : "+str(byte_src_add))
        #print("byte_dst_add : "+str(byte_dst_add))
        db = connect_database()
        try:
            cursor = db.cursor()
            cursor.execute(
                "UPDATE `networks` SET `network_end` = CURRENT_TIMESTAMP(), `network_srcpackets` = `network_srcpackets` + %s, `network_dstpackets` = `network_dstpackets` + %s, `network_srcbytes` = `network_srcbytes` + %s, `network_dstbytes` = `network_dstbytes` + %s WHERE `network_index` = %s",
                (packet_src_add, packet_dst_add, byte_src_add, byte_dst_add, network_index))
            db.commit()
        except RuntimeError as error:
            return response_normal(response.CODE_ERROR, error)
        finally:
            db.close()
    # insert packet to database
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO `packets` (`packet_device`, `packet_process`, `packet_network`, `packet_type`, `packet_srcip`, `packet_dstip`, `packet_srcdevice`, `packet_dstdevice`, `packet_protocol`, `packet_srcport`, `packet_dstport`, `packet_length`) "
            "VALUES (%s, %s, %s, 0, %s, %s, %s, %s, %s, %s, %s, %s)",
            (str(device), int(process_index), int(network_index), packet_ip_src, packet_ip_dst, packet_ethernet_src, packet_ethernet_dst, int(protocol_type), packet_port_src, packet_port_dst, int(packet_ip_len)))
        db.commit()
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()


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
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO `devices` (`device_index`, `device_id`, `device_created`) VALUES (NULL, %s, current_timestamp())",
            (str(device)))
        db.commit()
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    return response_normal(response.CODE_SUCCESS)


@app.route("/users/<device>/packet", methods=['GET', 'POST'])
def route_users_packet(device):
    raw_data = ''
    if request.method == 'GET':
        # response_normal(response.CODE_FAIL, 'REQUEST TYPE MUST BE POST')
        raw_data = request.args.get('data')
    if request.method == 'POST':
        raw_data = request.form['data']
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM `devices` WHERE `device_id` = %s", (str(device)))
        results = cursor.fetchall()
        result_count = cursor.rowcount
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    if result_count == 0:
        return response_normal(response.CODE_FAIL, "CONNECT DEVICE FIRST")
    handle_packet(device, raw_data)

    return response_normal(response.CODE_SUCCESS)


@app.route("/users/<device>/process", methods=['GET', 'POST'])
def route_users_process(device):
    process = ''
    if request.method == 'GET':
        response_normal(response.CODE_FAIL, 'REQUEST TYPE MUST BE POST')
    if request.method == 'POST':
        process = request.form['data']
    return response_normal(response.CODE_SUCCESS)


@app.route("/users/<device>/event", methods=['GET', 'POST'])
def route_users_event(device):
    raw_data = ''
    if request.method == 'GET':
        # response_normal(response.CODE_FAIL, 'REQUEST TYPE MUST BE POST')
        raw_data = request.args.get('data')
    if request.method == 'POST':
        raw_data = request.form['data']
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM `devices` WHERE `device_id` = %s", (str(device)))
        results = cursor.fetchall()
        result_count = cursor.rowcount
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    if result_count == 0:
        return response_normal(response.CODE_FAIL, "CONNECT DEVICE FIRST")
    device_index = results[0][0]
    print("DEVICE " + str(device) + "(" + str(device_index) + ")" + "GETS EVENT")
    # check unread message
    db = connect_database()
    try:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM `messages` WHERE `message_device` = %s AND `message_sent` = 0", (device_index))
        results = cursor.fetchall()
        result_count = cursor.rowcount
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    messages = json.dumps(results, default=json_default)
    # update to read message
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE `messages` SET `message_sent` = 1 WHERE `message_device` = %s AND `message_sent` = 0", (device_index))
        db.commit()
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    return response_message(response.CODE_SUCCESS, messages)


@app.route("/manage/<password>/monitor", methods=['GET', 'POST'])
def route_manage_monitor(password):
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    return response_normal(response.CODE_SUCCESS)


@app.route("/manage/<password>/<device>", methods=['GET', 'POST'])
def route_manage_device(password, device):
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    return response_normal(response.CODE_SUCCESS)


@app.route("/manage/<password>/reset", methods=['GET', 'POST'])
def route_manage_reset(password):
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    return response_normal(response.CODE_SUCCESS)


@app.route("/manage/<password>/test-message", methods=['GET', 'POST'])
def route_manage_test_message(password):
    if request.method == 'GET':
        message_type = request.args.get('type')
        message_title = request.args.get('title')
        message_content = request.args.get('content')
        message_data = request.args.get('data')
    if request.method == 'POST':
        message_type = request.form['type']
        message_title = request.form['title']
        message_content = request.form['content']
        message_data = request.form['data']
    if message_type is None:
        message_type = 0
    if message_title is None:
        message_title = "test message title"
    if message_content is None:
        message_content = "test message content"
    if message_data is None:
        message_data = "test message data"
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    db = connect_database()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM `devices`")
        results = cursor.fetchall()
    except RuntimeError as error:
        return response_normal(response.CODE_ERROR, error)
    finally:
        db.close()
    for result_object in results:
        db = connect_database()
        try:
            cursor = db.cursor(pymysql.cursors.DictCursor)
            cursor.execute("INSERT INTO `messages` (`message_device`, `message_sent`, `message_type`, `message_title`, `message_content`, `message_data`) VALUES (%s, 0, %s, %s, %s, %s)", (result_object[0], message_type, message_title, message_content, message_data))
            db.commit()
        except RuntimeError as error:
            return response_normal(response.CODE_ERROR, error)
        finally:
            db.close()
    return response_normal(response.CODE_SUCCESS)


@app.route("/manage/<password>/test-warning", methods=['GET', 'POST'])
def route_manage_test_warning(password):
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    return response_normal(response.CODE_SUCCESS)


@app.route("/manage/<password>/test-error", methods=['GET', 'POST'])
def route_manage_test_error(password):
    if password != constants.MANAGE_PASSWORD:
        return response_normal(response.CODE_FAIL, "PASSWORD NOT MATCH")
    return response_normal(response.CODE_SUCCESS)


def response_normal(response_code, response_error=None):
    if response_error is None:
        return {"code": response_code}
    else:
        return {"code": response_code, "error": response_error}


def response_message(response_code, messages):
    return {"code": response_code, "messages": messages}


if __name__ == "__main__":
    print("SERVER START")
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitor_network, 'interval', seconds=1)
    scheduler.start()
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
