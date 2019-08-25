import time
import logging

def Level2Stamp(l):    
    l = int(l)
    if l == 1:
        return 0, (9 * 60 + 45) * 60
    elif l == 2:
        return (9 * 60 + 45) * 60, (12 * 60) * 60
    elif l == 3:
        return (12 * 60) * 60, (15 * 60 + 45) * 60
    elif l == 4:
        return (15 * 60 + 45) * 60, (18 * 60) * 60
    elif l == 5:
        return (18 * 60) * 60, (20 * 60 + 30) * 60

import requests
import json
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

def Stamp2Level(s):
    s = int(s) - (int(s) // 86400 * 86400 - 28800)
    logging.debug(s)
    if 0 <= s < (9 * 60 + 45) * 60:
        return 1
    elif (9 * 60 + 45) * 60 <= s < (12 * 60) * 60:
        return 2
    elif (12 * 60) * 60 <= s < (15 * 60 + 45) * 60:
        return 3
    elif (15 * 60 + 45) * 60 <= s < (18 * 60) * 60:
        return 4
    elif (18 * 60) * 60 <= s < (20 * 60 + 30) * 60:
        return 5
    else:
        return -1

def Stamp2Stdlevel(s):
    s = int(s) - (int(s) // 86400 * 86400 - 28800)
    if 0 <= s < (8 * 60) * 60:
        return 1
    elif (9 * 60 + 45) * 60 <= s < (10 * 60 + 15) * 60:
        return 2
    elif (12 * 60) * 60 <= s < (14 * 60) * 60:
        return 3
    elif (15 * 60 + 45) * 60 <= s < (16 * 60 + 15) * 60:
        return 4
    elif (18 * 60) * 60 <= s < (18 * 60 + 15) * 60:
        return 5
    else:
        return -1

def GetOpenid(database, appid, secret, js_code):
    if None in (appid, secret, js_code):
        return 3, None, None, None, None
    text = requests.get(f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={js_code}&grant_type=authorization_code").text
    jtext = json.loads(text)
    if not "openid" in str(text):
        return 1, None, None, None, None
    openid = jtext["openid"]
    errcode, identity, id, name = CheckBind(database, openid)
    return errcode, identity, id, name, openid

def CheckBind(database, openid):
    status, identity, id, name = database.CheckBind(openid)
    if status:
        return 0, identity, id, name
    else:
        return 2, identity, None, None

def BindOpenid(database, openid, id, identity_number):
    if None in (openid, id, identity_number):
        return 3, None
    
    openid = str(openid)
    id = str(id)
    identity_number = str(identity_number)

    result, identity, id, name = database.BindOpenid(openid, id, identity_number)
    if result == None:
        return 4, None, None, None, None  
    
    return 0, result, identity, id, name

def UploadRecord(database, openid, room, campus, row, col, _time):
    if None in (openid, room, campus, row, col, _time):
        return 3, None
    
    openid = str(openid)
    room = str(room)
    campus = int(campus)
    row = int(row)
    col = int(col)
    _time = int(_time)

    status, _, _, _ = database.CheckBind(openid)
    if status == False:
        return 2, None
    level = Stamp2Level(_time)
    late = Stamp2Stdlevel(_time)
    stamp = int(_time // 86400 * 86400 - 28800)

    l, r = Level2Stamp(level)
    startStamp, endStamp = stamp + l, stamp + r
    if not database.CheckSeatAvailable(room, campus, row, col, startStamp, endStamp):
        return 5, None

    if not database.CheckStudentAvailable(openid, startStamp, endStamp):
        result = database.SwitchSeat(openid, room, campus, row, col, startStamp, endStamp)
        return 0, result

    result = database.UploadRecord(openid, room, campus, row, col, _time, level, late)
    if result == None:
        return 6, None 
    return 0, result

def GetStudentHistory(database, openid, startTime):
    if None in (openid, startTime):
        return 3, None
    
    openid = str(openid)
    startTime = str(startTime)

    status, _, _, _ = database.CheckBind(openid)
    if status == False:
        return 2, None

    endStamp = int(time.time())
    startStamp = int(time.mktime(time.strptime(startTime, "%Y-%m-%d")))
    histories = database.GetStudentHistory(openid, startStamp, endStamp)
    result = []
    for history in histories:
        history["_id"] = str(history["_id"])
        result.append(history)
    return 0, {"res": result, "count": len(result)}

def GetRoomHistory(database, room, _time):
    if None in (room, _time):
        return 3, None
    
    _time = str(_time)
    room = str(room)
    level = _time.split()[1]
    _time = _time.split()[0]
    stamp =  time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    l, r = Level2Stamp(level)
    startStamp, endStamp = stamp + l, stamp + r

    histories = database.GetRoomHistory(room, startStamp, endStamp)
    result = []
    for history in histories:
        history["_id"] = str(history["_id"])
        result.append(history)
    return 0, {"res": result, "count": len(result)}

def GetRoomHistoryByStamp(database, room, _time):
    if None in (room, _time):
        return 3, None
    
    _time = str(_time)
    room = str(room)
    stamp = int(_time // 86400 * 86400 - 28800)
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
    
    r = [{"res": {"_name": "数据结构", "_teacher": "高航"}, "count": 1}, {"res": None, "count": 0}]
    return 0, r[int(time.time() % 2)]
    # _time = str(_time)
    # room = str(room)
    # level = _time.split()[1]
    # _time = _time.split()[0]
    # stamp =  time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S"))
    # l, r = Level2Stamp(level)
    # startStamp, endStamp = stamp + l, stamp + r

    # histories = database.GetRoomCourse(room, startStamp, endStamp)
    # result = []
    # for history in histories:
    #     history["_id"] = str(history["_id"])
    #     result.append(history)
    # return 0, {"res": result, "count": len(result)}

def GetRoomCourseByStamp(database, room, _time):
    if None in (room, _time):
        return 3, None

    r = [{"res": {"_name": "数据结构", "_teacher": "高航"}, "count": 1}, {"res": None, "count": 0}]

    return 0, r[int(time.time() % 2)]
    # _time = str(_time)
    # room = str(room)
    # stamp = int(_time // 86400 * 86400 - 28800)
    # level = Stamp2Level(_time)
    # l, r = Level2Stamp(level)
    # startStamp, endStamp = stamp + l, stamp + r

    # histories = database.GetRoomCourse(room, startStamp, endStamp)
    # result = []
    # for history in histories:
    #     history["_id"] = str(history["_id"])
    #     result.append(history)
    # return 0, {"res": result, "count": len(result)}


# def GetTeacherHistory(openid, time):
#     if None in (openid, time):
#         return False, None
#     level = time.split()[1]
#     time = time.split()[0]
#     stamp = int(time.mktime(time.strptime(time, "%Y-%m-%d")))
#     l, r = Level2Stamp(level)
#     startStamp, endStamp = stamp + l, stamp + r

#     return True, [123, "21r12r"]