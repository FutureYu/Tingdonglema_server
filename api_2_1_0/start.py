from flask import Flask, request, jsonify, make_response, abort

import logging
import requests
import markdown
import time
from . import api

from . import database
from . import data

from bson.json_util import dumps

errmsgs = [
    "Success", # 0
    "Can't get openid from wechat server", # 1
    "The user has not been bound", # 2
    "Missing parameters", # 3
    "Wrong school or ID number", # 4
    "The seat is not available", # 5
    "Upload fail", # 6
    "No course", # 7
    "Switch seat success", # 8
    "No Course and Switch Seat", # 9
    "No results in database", # 10
    "Get future course", # 11
    "The user has been bound", #12
    "The user is not on the list", #13
    "",
    "",
    "",
    ""]


logging.info("V2.1.0!")

@api.route('/GetStudentInfo', methods=['GET'])
def GetStudentInfo():
    openid = request.args.get('openid')
    id = request.args.get('id')
    logging.info("Get openid: " + str(openid))
    logging.info("Get id: " + str(id))
    errcode, identity, id, name = data.GetStudentInfo(database, openid, id)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "identity": identity, "id": id, "name": name}
    logging.info("Return: " + str(res))
    return jsonify(res)

@api.route('/GetOpenid', methods=['GET'])
def GetOpenid():
    appid = request.args.get('appid')
    secret = request.args.get('secret')
    js_code = request.args.get('js_code')
    logging.info("Get appid: " + str(appid))
    logging.info("Get secret: " + str(secret))
    logging.info("Get js_code: " + str(js_code))

    errcode, identity, id, name, openid = data.GetOpenid(database, appid, secret, js_code)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "identity": identity, "id": id, "openid": openid, "name": name}
    logging.info("Return: " + str(res))
    return jsonify(res)

@api.route('/BindOpenid', methods=['POST'])
def BindOpenid():
    openid = request.json.get('openid')
    id = request.json.get('id')
    identity_number = request.json.get('identity_number')
    logging.info("Get openid: " + str(openid))
    logging.info("Get id: " + str(id))
    logging.info("Get identity_number: " + str(identity_number))
    errcode, recordid, identity, id, name = data.BindOpenid(database, openid, id, identity_number)
    logging.debug(errcode)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "recordid": recordid, "identity": identity, "id": id, "openid": openid, "name": name}
    logging.info("Return: " + str(res))
    return jsonify(res)

@api.route('/TeacherScan', methods=['POST'])
def TeacherScan():
    room = request.json.get('room')
    _time = request.json.get('time')
    logging.info("Get room: " + str(room))
    logging.info("Get _time: " + str(_time))
    errcode, recordid = data.TeacherScan(database, room, _time)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "recordid": recordid}
    logging.info("Return: " + str(res))
    return jsonify(res)

@api.route('/UploadRecord', methods=['POST'])
def UploadRecord():
    openid = request.json.get('openid')    
    room = request.json.get('room')    
    campus = request.json.get('campus')    
    row = request.json.get('row')    
    col = request.json.get('col')    
    _time = request.json.get('time')   
    logging.info("Get openid: " + str(openid))
    logging.info("Get room: " + str(room))
    logging.info("Get campus: " + str(campus))
    logging.info("Get row: " + str(row))
    logging.info("Get col: " + str(col))
    logging.info("Get time: " + str(_time))
    errcode, record = data.UploadRecord(database, openid, room, campus, row, col, _time)
    if "_id" in str(record):
        record["_id"] = str(record["_id"])
    res = {"errcode": errcode, "errmsg": errmsgs[errcode] , "record": record}
    logging.info("Return: " + str(res))
    return jsonify(res)


@api.route('/ChangeStudentRecord', methods=['POST'])
def ChangeStudentRecord():
    recordid = request.json.get('recordid')
    exception = request.json.get('exception')
    late = request.json.get('late')
    col = request.json.get('col')
    row = request.json.get('row')
    comment = request.json.get('comment')
    logging.info("Get recordid: " + str(recordid))
    logging.info("Get exception: " + str(exception))
    logging.info("Get late: " + str(late))
    logging.info("Get col: " + str(col))
    logging.info("Get row: " + str(row))
    logging.info("Get comment: " + str(comment))
    errcode = data.ChangeStudentRecord(database, recordid, exception, late, row, col, comment)

    res = {"errcode": errcode, "errmsg": errmsgs[errcode]}
    logging.info("Return: " + str(res))
    return jsonify(res)

@api.route('/GetStudentHistory', methods=['GET'])
def GetStudentHistory():
    openid = request.args.get('openid')
    startTime = request.args.get('startTime')
    stamp = request.args.get('stamp')
    stuid = request.args.get('stuid')
    logging.info("Get openid: " + str(openid))
    logging.info("Get startTime: " + str(startTime))
    logging.info("Get stamp: " + str(stamp))
    logging.info("Get stuid: " + str(stuid))
    errcode, records = data.GetStudentHistory(database, openid, startTime, stamp, stuid)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "records": records}
    logging.info("Return: " + str(res))
    return jsonify(res)

@api.route('/GetRoomHistory', methods=['GET'])
def GetRoomHistory():
    room = request.args.get('room')
    _time = request.args.get('time')
    logging.info("Get room: " + str(room))
    logging.info("Get time: " + str(_time))
    errcode, record = data.GetRoomHistory(database, room, _time)
    res = {"errcode": errcode, "record": record}
    logging.info("Return: " + str(res))
    return jsonify(res)


@api.route('/GetRoomCourse', methods=['GET'])
def GetRoomCourse():
    room = request.args.get('room')
    _time = request.args.get('time')
    logging.info("Get room: " + str(room))
    logging.info("Get time: " + str(_time))

    errcode, record = data.GetRoomCourse(database, room, _time)

    res = {"errcode": errcode, "record": record}
    logging.info("Return: " + str(res))
    return jsonify(res)


@api.route('/GetStudentCourse', methods=['GET'])
def GetStudentCourse():
    stuid = request.args.get('stuid')
    _time = request.args.get('time')
    logging.info("Get stuid: " + str(stuid))
    logging.info("Get time: " + str(_time))

    errcode, record = data.GetStudentCourse(database, stuid, _time)

    res = {"errcode": errcode, "record": record}
    logging.info("Return: " + str(res))
    return jsonify(res)


@api.route('/GetStudentLocation', methods=['GET'])
# 废弃
def GetStudentLocation():
    stuid = request.args.get('stuid')
    _time = request.args.get('time')
    logging.info("Get stuid: " + str(stuid))
    logging.info("Get time: " + str(_time))

    errcode, record = data.GetStudentLocation(database, stuid, _time)

    res = {"errcode": errcode, "record": record}
    logging.info("Return: " + str(res))
    abort(404)

@api.route('/GetTeacherCourse', methods=['GET'])
def GetTeacherCourse():
    teaid = request.args.get('teaid')
    _time = request.args.get('time')
    logging.info("Get teaid: " + str(GetTeacherCourse))
    logging.info("Get time: " + str(_time))

    errcode, record = data.GetTeacherCourse(database, teaid, _time)

    if record == None:
        res = {"errcode": errcode, "errmsg": errmsgs[errcode], "record": None}
        logging.info("Return: " + str(res))
        return jsonify(res)
    _, scans = data.GetRoomHistory(database, record["_room"], _time)
    details = {"total": [], "absent": [], "late": [], "intime": [], "exception": [], "off": []}

    for rec in record["_stus"]:
        _, _, id, name = data.GetStudentInfo(database, None, rec)
        details["total"].append({"id": id, "name": name})
        if '_askforleave' in record and id in record["_askforleave"]:
            details['off'].append({"id": id, "name": name})
        else:
            details["absent"].append({"id": id, "name": name})
    for scan in scans["res"]:
        if scan["_exception"] == True:
            details["exception"].append(scan)
            details["absent"].remove({"id": scan["_stuid"], "name": scan["_stu_name"]})
        elif scan["_late"] == -1:
            details["late"].append(scan)
            details["absent"].remove({"id": scan["_stuid"], "name": scan["_stu_name"]})
        else:
            details["intime"].append(scan)
            details["absent"].remove({"id": scan["_stuid"], "name": scan["_stu_name"]})

    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "record": record, "details": details}
    logging.info("Return: " + str(res))
    return jsonify(res)


@api.route('/GetTeacherHistory', methods=['GET'])
def GetTeacherHistory():
    teaid = request.args.get('teaid')
    startTime = request.args.get('startTime')
    logging.info("Get teaid: " + str(teaid))
    logging.info("Get startTime: " + str(startTime))

    errcode, records = data.GetTeacherHistory(database, teaid, startTime)

    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "records": records}
    logging.info("Return: " + str(res))
    return jsonify(res)

@api.route('/GetStudentData', methods=['GET'])
def GetStudentData():
    teaid = request.args.get('teaid')
    campus = request.args.get('campus')
    room = request.args.get('room')
    level = request.args.get('level')
    late = request.args.get('late')
    courseid = request.args.get('courseid')
    stuid = request.args.get('stuid')
    exception = request.args.get('exception')
    startTime = request.args.get('startTime')
    endTime = request.args.get('endTime')
    logging.info("Get teaid: " + str(teaid))
    logging.info("Get campus: " + str(campus))
    logging.info("Get room: " + str(room))
    logging.info("Get level: " + str(level))
    logging.info("Get late: " + str(late))
    logging.info("Get courseid: " + str(courseid))
    logging.info("Get stuid: " + str(stuid))
    logging.info("Get exception: " + str(exception))
    logging.info("Get startTime: " + str(startTime))
    logging.info("Get endTime: " + str(endTime))

    errcode, records = data.GetStudentData(database, teaid, campus, room, level, late, courseid, stuid, exception, startTime, endTime)

    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "records": records}
    logging.info("Return: " + str(res))
    return jsonify(res)

@api.route('/SetStudentOff', methods=['GET'])
def SetStudentOff():
    stuid = request.args.get('stuid')
    room = request.args.get('room')
    startTime = request.args.get('startTime')
    teaid = request.args.get('teaid')
    errcode, records = data.SetStudentOff(database, stuid, teaid, room, startTime)
    res = {"errcode": errcode, "errmsg": errmsgs[errcode], "records": records}
    logging.info("Return: " + str(res))
    return dumps(res)

@api.route('/doc', methods=['GET'])
def doc():
    with open("api_2_1_0/doc.md", "r") as f:
        text = f.read()
        html = markdown.markdown(text)
    return html
