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


def BindOpenid(database, openid, id, identity_number):
    if None in (openid, id, identity_number):
        return False, None
    
    openid = str(openid)
    id = str(id)
    identity_number = str(identity_number)

    result = database.BindOpenid(openid, id)
    if result == None:
        return False, None 
    return True, result

def UploadRecord(database, openid, room, campus, row, col, _time):
    if None in (openid, room, campus, row, col, _time):
        return False, None
    
    openid = str(openid)
    room = str(room)
    campus = int(campus)
    row = int(row)
    col = int(col)
    _time = int(_time)

    status, _, _, _ = database.CheckBind(openid)
    if status == False:
        return False, None
    level = Stamp2Level(_time)
    late = Stamp2Stdlevel(_time)
    stamp = int(time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S")))
    l, r = Level2Stamp(level)
    startStamp, endStamp = stamp + l, stamp + r
    if not database.CheckSeatAvailable(room, campus, row, col, startStamp, endStamp):
        return False, None

    if not database.CheckStudentAvailable(openid, startStamp, endStamp):
        database.SwitchSeat(openid, room, campus, row, col, startStamp, endStamp)
        return False, None

    result = database.UploadRecord(openid, room, campus, row, col, _time, level, late)
    if result == None:
        return False, None 
    return True, result

def GetStudentHistory(database, openid, startTime):
    if None in (openid, startTime):
        return False, None
    
    openid = str(openid)
    startTime = str(startTime)

    status, _, _, _ = database.CheckBind(openid)
    if status == False:
        return False, None

    endStamp = int(time.time())
    startStamp = int(time.mktime(time.strptime(startTime, "%Y-%m-%d")))
    histories = database.GetStudentHistory(openid, startStamp, endStamp)
    result = []
    for history in histories:
        history["_id"] = str(history["_id"])
        result.append(history)
    return True, {"res": result, "count": len(result)}

def GetRoomHistory(database, room, _time):
    if None in (room, _time):
        return False, None
    
    _time = str(_time)
    room = str(room)

    level = _time.split()[1]
    _time = _time.split()[0]
    stamp = int(time.mktime(time.strptime(_time + " 00:00:00", "%Y-%m-%d %H:%M:%S")))
    l, r = Level2Stamp(level)
    startStamp, endStamp = stamp + l, stamp + r
    logging.debug(startStamp)
    logging.debug(endStamp)

    histories = database.GetRoomHistory(room, startStamp, endStamp)
    result = []
    for history in histories:
        history["_id"] = str(history["_id"])
        result.append(history)
    return True, {"res": result, "count": len(result)}

# def GetTeacherHistory(openid, time):
#     if None in (openid, time):
#         return False, None
#     level = time.split()[1]
#     time = time.split()[0]
#     stamp = int(time.mktime(time.strptime(time, "%Y-%m-%d")))
#     l, r = Level2Stamp(level)
#     startStamp, endStamp = stamp + l, stamp + r

#     # 查表
#     return True, [123, "21r12r"]