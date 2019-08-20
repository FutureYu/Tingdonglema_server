from flask import Flask, request, jsonify, make_response, abort
import data
from db import DataBase
import logging
logging.basicConfig(filename="main.log", level=logging.DEBUG)

app = Flask(__name__)
database = DataBase()
logging.debug("HelloWorld")

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index():
    return "Hello, Nuaaer"

@app.route('/api/BindOpenid', methods=['POST'])
def BindOpenid():
    openid = request.json.get('openid')
    id = request.json.get('id')
    status, recordid = data.BindOpenid(database, openid, id)
    if not status:
        abort(400)
    res = {"status": "success", "recordid": recordid}
    return jsonify(res)

@app.route('/api/UploadRecord', methods=['POST'])
def UploadRecord():
    openid = request.json.get('openid')    
    room = request.json.get('room')    
    campus = request.json.get('campus')    
    row = request.json.get('row')    
    col = request.json.get('col')    
    time = request.json.get('time')   
    logging.debug(openid, room, campus, row, col, time) 

    status, recordid = data.UploadRecord(database, openid, room, campus, row, col, time)
    if not status:
        abort(400)
    res = {"status": "success", "recordid": recordid , "openid": openid}
    return jsonify(res)

@app.route('/api/GetStudentHistory', methods=['GET'])
def GetStudentHistory():
    openid = request.args.get('openid')
    startTime = request.args.get('startTime')

    status, records = data.GetStudentHistory(database, openid, startTime)
    if not status:
        abort(400)
    res = {"status": "success", "records": records}
    return jsonify(res)

@app.route('/api/GetRoomHistory', methods=['GET'])
def GetRoomHistory():
    room = request.args.get('room')
    time = request.args.get('time')

    status, record = data.GetRoomHistory(database, room, time)
    if not status:
        abort(400)
    res = {"status": "success", "record": record}
    return jsonify(res)

# @app.route('/api/GetTeacherHistory', methods=['GET'])
# def GetTeacherHistory():
#     openid = request.args.get('openid')
#     time = request.args.get('time')

#     status, record = data.GetTeacherHistory(openid, time)
#     if not status:
#         abort(400)
#     res = {"status": "success", "record": record}
#     return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True)