import time
import logging
import requests
import json
import bson
import openpyxl

def Level2Stamp(l):    
    l = int(l)
    if l == 1:
        return (7 * 60 + 30) * 60, (9 * 60 + 45) * 60
    elif l == 2:
        return (9 * 60 + 45) * 60, (12 * 60) * 60
    elif l == 3:
        return (13 * 60 + 30) * 60, (15 * 60 + 45) * 60
    elif l == 4:
        return (15 * 60 + 45) * 60, (18 * 60) * 60
    elif l == 5:
        return (18 * 60 + 15) * 60, (20 * 60 + 30) * 60
    else:
        return (23 * 60 + 59) * 60, (23 * 60 + 59) * 60

def Stdlevel2Stamp(l):
    l = int(l)
    if l == 1:
        return 0, (8 * 60) * 60
    elif l == 2:
        return (9 * 60 + 45) * 60, (10 * 60 + 15) * 60
    elif l == 3:
        return (12 * 60) * 60, (14 * 60) * 60
    elif l == 4:
        return (15 * 60 + 45) * 60, (16 * 60 + 15) * 60
    elif l == 5:
        return (18 * 60) * 60, (18 * 60 + 15) * 60
    else:
        return (23 * 60 + 59) * 60, (23 * 60 + 59) * 60

def Stamp2Level(s):
    s = int(s) - (((int(s) + 28800) // 86400 * 86400) - 28800)
    if (7 * 60 + 30) * 60 <= s < (9 * 60 + 45) * 60:
        return 1
    elif (9 * 60 + 45) * 60 <= s < (12 * 60) * 60:
        return 2
    elif (13 * 60 + 30) * 60 <= s < (15 * 60 + 45) * 60:
        return 3
    elif (15 * 60 + 45) * 60 <= s < (18 * 60) * 60:
        return 4
    elif (18 * 60 + 15) * 60 <= s < (20 * 60 + 30) * 60:
        return 5
    else:
        return -1

def Stamp2Stdlevel(s):
    s = int(s) - (((int(s) + 28800) // 86400 * 86400) - 28800)
    if 0 <= s < (8 * 60) * 60:
        return 1
    elif (9 * 60 + 45) * 60 <= s < (10 * 60 + 15) * 60:
        return 2
    elif (12 * 60) * 60 <= s < (14 * 60) * 60:
        return 3
    elif (15 * 60 + 45) * 60 <= s < (16 * 60 + 15) * 60:
        return 4
    elif (18 * 60 + 45) * 60 <= s < (20 * 60 + 30) * 60:
        return 5
    else:
        return -1

def GetStudentInfo(database, openid, id):
    if openid != None:
        openid = str(openid)
        status, identity, id, name, _ = database.CheckBind(openid, qtype="openid")
    elif id != None:
        id = str(id)
        status, identity, id, name, _ = database.CheckBind(id, qtype="id")
    if status:
        return 0, identity, id, name
    else:
        return 2, identity, id, name

def GetOpenid(database, appid, secret, js_code):
    if None in (appid, secret, js_code):
        return 3, None, None, None, None
    text = requests.get(f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={js_code}&grant_type=authorization_code").text
    jtext = json.loads(text)
    if not "openid" in str(text):
        return 1, None, None, None, None
    openid = jtext["openid"]
    errcode, identity, id, name, _ = CheckBind(database, openid)
    return errcode, identity, id, name, openid

def CheckBind(database, openid):
    status, identity, id, name, _openid = database.CheckBind(openid)
    if status:
        return 0, identity, id, name, _openid
    else:
        return 2, identity, None, None, _openid

def BindOpenid(database, openid, id, identity_number):
    if None in (openid, id, identity_number):
        return 3, None, None, None, None  
    
    openid = str(openid)
    id = str(id)
    identity_number = str(identity_number)

    result, identity, id, name = database.BindOpenid(openid, id, identity_number)
    if result == 13 or result == 12 or result == 4:
        return result, None, None, None, None  
    
    return 0, result, identity, id, name

def TeacherScan(database, room, _time):
    if None in (room, _time):
        return 3, None
    room = str(room)
    _time = int(_time)
    level = Stamp2Level(_time)
    stamp = int(_time // 86400 * 86400 - 28800)
    l, _ = Level2Stamp(level)
    startStamp = stamp + l
    result = database.TeacherScan(room, startStamp)
    if result == None:
        return 6, None 
    result["_id"] = str(result["_id"])
    return 0, result

def CheckException(database, room, campus, row, col, startStamp, endStamp):
    result = database.CheckException(room, campus, row, col, startStamp, endStamp)
    return result

def UnCheckException(database, openid, room, campus, row, col, startStamp, endStamp):
    result = database.UnCheckException(openid, room, campus, startStamp, endStamp)
    return result

def ChangeStudentRecord(database, recordid, exception, late, row, col, comment):
    if recordid == None:
        return 3, None

    recordid = bson.ObjectId(recordid)
    database.ChangeStudentRecord(recordid, exception, late, row, col, comment)
    return 0
    
    

def UploadRecord(database, openid, room, campus, row, col, _time):
    if None in (openid, room, campus, row, col, _time):
        return 3, None
    
    openid = str(openid)
    room = str(room)
    campus = int(campus)
    row = int(row)
    col = int(col)
    _time = int(_time)

    status, _, id, name, _ = database.CheckBind(openid)
    if status == False:
        return 2, None
    level = Stamp2Level(_time)
    late = Stamp2Stdlevel(_time)
    stamp = int(_time // 86400 * 86400 - 28800)

    l, r = Level2Stamp(level)
    stdl, _ = Stdlevel2Stamp(level)
    stdStartStamp = stamp + stdl
    startStamp, endStamp = stamp + l, stamp + r

    UnCheckException(database, openid, room, campus, row, col, startStamp, endStamp)

    isSwitchSeat = False
    if not database.CheckStudentAvailable(openid, startStamp, endStamp):
        isSwitchSeat = True
        result = database.SwitchSeat(openid, room, campus, row, col, startStamp, endStamp)

    course = database.ChangeCourseStatus(room, startStamp, level, late, isSwitchSeat)
    logging.debug("course: " + str(course))
    isNoCourse = False
    if course == None and not isSwitchSeat:
        isNoCourse = True
        logging.debug("isNoCourse true")
        
        # result = database.UploadRecord(openid, room, campus, row, col, _time, level, late, "", "", "", "", id, name, False)
        result = None
    elif course != None and not isSwitchSeat:
        isNoCourse = False
        logging.debug("isNoCourse false")
        if row == col == 0:
            result = database.UploadRecord(openid, room, campus, row, col, stdStartStamp, level, late, course["_courseid"], course["_name"], course["_teacherid"], course["_teacher"], id, name, False, "请假")
        else:
            result = database.UploadRecord(openid, room, campus, row, col, _time, level, late, course["_courseid"], course["_name"], course["_teacherid"], course["_teacher"], id, name, False, "")
    
    if not row == col == 0:
        CheckException(database, room, campus, row, col, startStamp, endStamp)

    if result == None:
        return 6, None 

    if isNoCourse and not isSwitchSeat:
        return 7, result
    elif isNoCourse and isSwitchSeat:
        return 9, result
    elif not isNoCourse and isSwitchSeat:
        return 8, result
    else:
        return 0, result



def GetStudentHistory(database, openid, startTime, stamp, stuid):
    if None == openid and None == stuid:
        return 3, None
    if startTime != None:
        startTime = str(startTime)
        endStamp = int(time.time())
        startStamp = int(time.mktime(time.strptime(startTime, "%Y-%m-%d")))

    elif stamp != None:
        stamp = int(stamp)
        level = Stamp2Level(stamp)
        baseStamp = int((stamp + 28800) // 86400 * 86400 - 28800)
        l, r = Level2Stamp(level)
        startStamp, endStamp = l + baseStamp, r + baseStamp

    else:
        return 3, None

    if openid != None:
        status, _, _, _, _ = database.CheckBind(openid)
    else:
        status, _, _, _, openid = database.CheckBind(stuid, qtype="id")

    if status == False:
        return 2, None


    logging.debug(openid)
    histories = database.GetStudentHistory(openid, startStamp, endStamp)
    result = []
    for history in histories:
        logging.debug("hasduihu")
        history["_id"] = str(history["_id"])
        result.append(history)
    return 0, {"res": result, "count": len(result)}


def GetTeacherHistory(database, teaid, startTime):
    if None in (teaid, startTime):
        return 3, None
    
    teaid = str(teaid)
    startTime = str(startTime)

    endStamp = int(time.time())
    startStamp = int(time.mktime(time.strptime(startTime, "%Y-%m-%d")))
    logging.debug(startStamp, endStamp)
    histories = database.GetTeacherHistory(teaid, startStamp, endStamp)
    result = []
    for history in histories:
        history["_id"] = str(history["_id"])
        logging.debug(f'history["_id"], {history["_id"]}')
        result.append(history)
    return 0, {"res": result, "count": len(result), "startStamp": startStamp} 


def GetRoomHistory(database, room, _time):
    if None in (room, _time):
        return 3, None
    room = str(room)
    if "-" in str(_time):
        _time = str(_time)
        level = _time.split()[1]
        _time = _time.split()[0]
        stamp =  time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    else:
        _time = int(_time)
        stamp = int((_time + 28800) // 86400 * 86400 - 28800)
        level = Stamp2Level(_time)
    l, r = Level2Stamp(level)
    startStamp, endStamp = stamp + l, stamp + r

    histories = database.GetRoomHistory(room, startStamp, endStamp)
    result = []
    for history in histories:
        history["_id"] = str(history["_id"])
        result.append(history)
    return 0, {"res": result, "count": len(result)}

    

def GetRoomCourse(database, room, _time):
    if None in (room, _time):
        return 3, None
    room = str(room)
    if "-" in str(_time):
        _time = str(_time)
        level = _time.split()[1]
        _time = _time.split()[0]
        stamp =  time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    else:
        _time = int(_time)
        stamp = int((_time + 28800) // 86400 * 86400 - 28800)
        level = Stamp2Level(_time)
    l, _ = Level2Stamp(level)
    startStamp = stamp + l

    result = database.GetRoomCourse(room, startStamp)
    if result == None:
        return 10, None 
    result["_id"] = str(result["_id"])
    return 0, result


def GetStudentCourse(database, stuid, _time):
    if None in (stuid, _time):
        return 3, None
    
    stuid = str(stuid)
    if "-" in str(_time):
        _time = str(_time)
        level = _time.split()[1]
        _time = _time.split()[0]
        stamp =  time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    else:
        _time = int(_time)
        stamp = int((_time + 28800) // 86400 * 86400 - 28800)
        level = Stamp2Level(_time)
    l, _ = Level2Stamp(level)
    startStamp = stamp + l
    
    result = database.GetStudentCourse(stuid, startStamp)
    if result == None:
        return 10, None 
    result["_id"] = str(result["_id"])
    logging.debug(startStamp)
    if result["_start_stamp"] == startStamp:
        return 0, result
    else:
        return 11, result

def GetStudentLocation(database, stuid, _time):
    if None in (stuid, _time):
        return 3, None
    
    stuid = str(stuid)
    if "-" in str(_time):
        _time = str(_time)
        level = _time.split()[1]
        _time = _time.split()[0]
        stamp =  time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    else:
        _time = int(_time)
        stamp = int((_time + 28800) // 86400 * 86400 - 28800)
        level = Stamp2Level(_time)
    l, r = Level2Stamp(level)
    startStamp = stamp + l
    endStamp = stamp + r
    
    result = database.GetStudentLocation(stuid, startStamp, endStamp)
    if result == None:
        return 10, None 
    return 0, result


def GetTeacherCourse(database, teaid, _time):
    if None in (teaid, _time):
        return 3, None
    if "-" in str(_time):
        level = _time.split()[1]
        _time = _time.split()[0]
        stamp =  time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    else:
        try:
            _time = int(_time)
        except:
            _time = 0
        level = Stamp2Level(_time)
        stamp = int((_time + 28800) // 86400 * 86400 - 28800)
    teaid = str(teaid)
    l, _ = Level2Stamp(level)
    startStamp = stamp + l
    result = database.GetTeacherCourse(teaid, startStamp)
    if result == None:
        return 10, None 
    result["_id"] = str(result["_id"])
    logging.info(f"get teacher course _startstamp: {startStamp}, result['_start_stamp']: {result['_start_stamp']}")
    if result["_start_stamp"] == startStamp:
        return 0, result
    else:
        return 11, result

def GetStudentData(database, teaid, campus, room, level, late, courseid, stuid, exception, startTime, endTime):
    if None in (teaid, startTime, endTime):
        return 3, None
    if "-" in startTime:
        startStamp =  time.mktime(time.strptime(startTime + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    else:
        startStamp = int(startTime)
    if "-" in endTime:
        endStamp =  time.mktime(time.strptime(endTime + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    else:
        endStamp = int(endTime)
    
    if teaid != None:
        teaid = str(teaid)
    if room != None:
        room = str(room)
    if courseid != None:
        courseid = str(courseid)
    if stuid != None:
        stuid = str(stuid)
    if campus != None:
        campus = int(campus)
    if level != None:
        level = int(level)
    if late != None:
        late = int(late)
    if exception != None:
        exception = bool(exception)
    records = database.GetStudentData(teaid, campus, room, level, late, courseid, stuid, exception, startStamp, endStamp)
    #excel = openpyxl.Workbook()    

      
    #excel.save('RercordDatas/answer.xlsx') 
    return 0, records

def SetStudentOff(database, stuid, teaid, room, startTime):
    if None in (room, startTime, stuid, teaid):
        return 3, None
    stuid = str(stuid)
    room = str(room)
    startTime = int(startTime)
    teaid = str(teaid)
    res = database.InsertAskForLeave(stuid, teaid, room, startTime)
    if not res:
        return 10, res
    else:
        return 0, res

