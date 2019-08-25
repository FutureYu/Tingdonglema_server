from flask import Flask, request, jsonify, make_response, abort
import data
from db import DataBase
import logging
import time 

errmsgs = [
    "Success",
    "Can't get openid from wechat server",
    "The user has not been bound",
    "Missing parameters",
    "Wrong school or ID number",
    "The seat is not available",
    "Upload fail"]

logging.basicConfig(filename="main.log",format='[%(asctime)s] [%(filename)s] [line:%(lineno)d] %(levelname)s %(message)s', level=logging.DEBUG)

app = Flask(__name__)
database = DataBase()
logging.info("Starting server!")

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index():
    return "Hello, Nuaaer"

@app.route('/api/GetOpenid', methods=['POST'])
def GetOpenid():
    appid = request.json.get('appid')
    secret = request.json.get('secret')
    js_code = request.json.get('js_code')
    logging.info("Get: appid" + str(appid))
    logging.info("Get: secret" + str(secret))
    logging.info("Get: js_code" + str(js_code))

    errcode, identity, id, name, openid = data.GetOpenid(database, appid, secret, js_code)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "identity": identity, "id": id, "openid": openid, "name": name}
    logging.info("Return: " + str(res))
    return jsonify(res)

@app.route('/api/BindOpenid', methods=['POST'])
def BindOpenid():
    openid = request.json.get('openid')
    id = request.json.get('id')
    identity_number = request.json.get('identity_number')
    logging.info("Get: openid" + str(openid))
    logging.info("Get: id" + str(id))
    logging.info("Get: identity_number" + str(identity_number))
    errcode, recordid, identity, id, name = data.BindOpenid(database, openid, id, identity_number)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "recordid": recordid, "identity": identity, "id": id, "openid": openid, "name": name}
    logging.info("Return: " + str(res))
    return jsonify(res)

@app.route('/api/UploadRecord', methods=['POST'])
def UploadRecord():
    openid = request.json.get('openid')    
    room = request.json.get('room')    
    campus = request.json.get('campus')    
    row = request.json.get('row')    
    col = request.json.get('col')    
    time = request.json.get('time')   
    logging.info("Get: openid" + str(openid))
    logging.info("Get: room" + str(room))
    logging.info("Get: openid" + str(openid))
    logging.info("Get: campus" + str(campus))
    logging.info("Get: row" + str(row))
    logging.info("Get: col" + str(col))
    logging.info("Get: time" + str(time))
    errcode, recordid = data.UploadRecord(database, openid, room, campus, row, col, time)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode] , "recordid": recordid}
    logging.info("Return: " + str(res))
    return jsonify(res)

@app.route('/api/GetStudentHistory', methods=['GET'])
def GetStudentHistory():
    openid = request.args.get('openid')
    startTime = request.args.get('startTime')
    logging.info("Get: openid" + str(openid))
    logging.info("Get: startTime" + str(startTime))

    errcode, records = data.GetStudentHistory(database, openid, startTime)

    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "records": records}
    logging.info("Return: " + str(res))
    return jsonify(res)

@app.route('/api/GetRoomHistory', methods=['GET'])
def GetRoomHistory():
    room = request.args.get('room')
    _time = request.args.get('time')
    logging.info("Get: room" + str(room))
    logging.info("Get: time" + str(time))

    errcode, record = data.GetRoomHistory(database, room, _time)

    res = {"errcode": errcode, "record": record}
    logging.info("Return: " + str(res))
    return jsonify(res)

@app.route('/api/GetRoomHistoryByStamp', methods=['GET'])
def GetRoomHistoryByStamp():
    room = request.args.get('room')
    _time = request.args.get('time')
    logging.info("Get: room" + str(room))
    logging.info("Get: time" + str(time))

    errcode, record = data.GetRoomHistoryByStamp(database, room, _time)

    res = {"errcode": errcode, "record": record}
    logging.info("Return: " + str(res))
    return jsonify(res)


@app.route('/api/GetRoomCourse', methods=['GET'])
def GetRoomCourse():
    room = request.args.get('room')
    _time = request.args.get('time')
    logging.info("Get: room" + str(room))
    logging.info("Get: time" + str(time))

    errcode, record = data.GetRoomCourse(database, room, _time)

    res = {"errcode": errcode, "record": record}
    logging.info("Return: " + str(res))
    return jsonify(res)

@app.route('/api/GetRoomCourseByStamp', methods=['GET'])
def GetRoomCourseByStamp():
    room = request.args.get('room')
    _time = request.args.get('time')
    logging.info("Get: room" + str(room))
    logging.info("Get: time" + str(time))

    errcode, record = data.GetRoomCourseByStamp(database, room, _time)

    res = {"errcode": errcode, "record": record}
    logging.info("Return: " + str(res))
    return jsonify(res)



# @app.route('/api/GetTeacherHistory', methods=['GET'])
# def GetTeacherHistory():
#     openid = request.args.get('openid')
#     time = request.args.get('time')

#     status, record = data.GetTeacherHistory(openid, time)
#     if not status:
#         abort(400)
#     res = {"status": "success", "record": record}
#     return jsonify(res)'



@app.route('/test/log', methods=['GET'])
def log():
    with open("main.log", "r") as f:
        text = f.read()
    return text

@app.route('/test/doc', methods=['GET'])
def doc():
    with open("doc.md", "r") as f:
        text = f.read()
    return text



if __name__ == '__main__':
    app.run()