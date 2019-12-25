import pymongo
import logging

class DataBase:
    def __init__(self, db_name):
        self.db = pymongo.MongoClient('mongodb://server:tdlm_server123@checkin.nuaaweyes.com/', 27017)[db_name]
 
    def CheckBind(self, openid, qtype="openid"):
        mycol = self.db["user"]
        query = {f"_{qtype}": openid} 
        mydoc = mycol.find_one(query)

        if mydoc == None:
            return False, 0, None, None, None
        if mydoc["_openid"] == "null" or mydoc["_openid"] == "":
            return False, 0, mydoc["_id"], mydoc["_name"], mydoc["_openid"]
        if mydoc["_is_student"] == True:
            return True, 1, mydoc["_id"], mydoc["_name"], mydoc["_openid"]
        elif mydoc["_is_student"] == False:
            return True, 2, mydoc["_id"], mydoc["_name"], mydoc["_openid"]
        else:
            return False, 0, None, None, None

    def BindOpenid(self, openid, id, identity_number):
        mycol = self.db["user"]
        query = {"_id": id} 
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return 13, None, None, None
        if mydoc["_identity_number"] != identity_number:
            return 4, None, None, None
        if mydoc["_openid"] != "null" and mydoc["_openid"] != "" :
            return 12, None, None, None
        
        newvalues = { "$set": { "_openid": openid } }
        mycol.update_one(query, newvalues)
        if mydoc["_is_student"] == True:
            return id, 1, mydoc["_id"], mydoc["_name"]
        elif mydoc["_is_student"] == False:
            return id, 2, mydoc["_id"], mydoc["_name"]

    def UploadRecord(self, openid, room, campus, row, col, time, level, late, courseid, course_name, teacherid, teacher_name, stuid, name, cheat, comment):
        mycol = self.db["record"]
        newvalues = {"_openid": openid, "_campus": campus, "_room": room, "_row": row, "_col": col, "_time": time, "_level": level, "_late": late, "_courseid": courseid, "_teacherid": teacherid, "_course_name": course_name, "_teacher_name": teacher_name, "_stuid": stuid, "_stu_name": name, "_exception": cheat, "_comment": comment}
        mycol.insert_one(newvalues)
        return newvalues

    def SwitchSeat(self, openid, room, campus, row, col, startStamp, endStamp):
        mycol = self.db["record"]
        
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], "_campus": campus, "_room": room, "_openid": openid}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return None
        
        newvalues = { "$set": { "_room": room, "_col": col, "_row": row}}
        mycol.update_one(query, newvalues)
        mydoc = mycol.find_one(query)

        return mydoc

    def CheckException(self, room, campus, row, col, startStamp, endStamp):
        mycol = self.db["record"]
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_room': room, "_campus": campus, "_row": row, "_col": col}
        mydoc = mycol.find(query)
        if mydoc.count() >= 2:
            newvalues = { "$set": { "_exception": True}}
            mycol.update_many(query, newvalues)
            return True
        return False

    def ChangeStudentRecord(self, recordid, exception, late, row, col, comment):
        mycol = self.db["record"]
        query = {"_id": recordid}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False
        if exception == None:
            exception = mydoc["_exception"]
        if late == None:
            late = mydoc["_late"]
        if row == None:
            row = mydoc["_row"]
        if col == None:
            col = mydoc["_col"]
        if comment == None:
            comment = mydoc["_comment"]
        newvalues = { "$set": { "_exception": exception, "_late": late, "_row": row, "_col": col, "_comment": comment}}
        mycol.update_one(query, newvalues)
        return True

    def UnCheckException(self, openid, room, campus, startStamp, endStamp):
        mycol = self.db["record"]
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_room': room, "_campus": campus, "_openid": openid}
        mydoc_old = mycol.find_one(query)
        if mydoc_old == None:
            return False
        row = mydoc_old["_row"]
        col = mydoc_old["_col"]
        logging.debug(f"row, col: {row}, {col}")
        exception = mydoc_old["_exception"]
        if exception == False:
            return False
        newquery = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_room': room, "_campus": campus, "_row": row, "_col": col}
        mydoc = mycol.find(newquery)
        if mydoc.count() > 2:
            newvalues = { "$set": { "_exception": False}}
            mycol.update_one(query, newvalues)
            return False
        else:
            newvalues = { "$set": { "_exception": False}}
            mycol.update_many(newquery, newvalues)
            return True

    def CheckStudentAvailable(self, openid, startStamp, endStamp):
        mycol = self.db["record"]
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_openid': openid}
        mydoc = mycol.find_one(query)
        if not mydoc:
            return True

    def GetStudentHistory(self, openid, startStamp, endStamp):
        mycol = self.db["record"]
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_openid': openid}
        mydoc = mycol.find(query)
        return mydoc

    def GetTeacherHistory(self, teaid, startStamp, endStamp):
        mycol = self.db["course"]
        query = { '$and': [ { '_start_stamp':{'$gte':startStamp}  }, {'_start_stamp':{'$lt':endStamp} } ], '_teacherid': teaid}
        mydoc = mycol.find(query).sort('_start_stamp',pymongo.DESCENDING)
        return mydoc

    def GetRoomHistory(self, room, startStamp, endStamp):
        mycol = self.db["record"]
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_room': room}
        mydoc = mycol.find(query)
        return mydoc
        
    def GetRoomCourse(self, room, startStamp):
        mycol = self.db["course"]
        query = { "_start_stamp": startStamp, '_room': room}
        mydoc = mycol.find_one(query)
        return mydoc

    def TeacherScan(self, room, startStamp):
        mycol = self.db["course"]
        query = { "_start_stamp": startStamp, '_room': room}
        mydoc = mycol.find_one(query)
        newvalues = { "$set": { "_scan": True}}
        mycol.update_one(query, newvalues)
        return mydoc

    def GetStudentCourse(self, stuid, startStamp):
        mycol = self.db["course"]
        query = { "_start_stamp": {'$gte': startStamp}, '_stus': stuid}
        mydoc = mycol.find(query).sort('_start_stamp', pymongo.ASCENDING).limit(1)  
        if mydoc.count() == 0:
            return None
        return mydoc[0]

    def GetStudentLocation(self, stuid, startStamp, endStamp):
        mycol = self.db["record"]
        query = {  '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_stuid': stuid}
        mydoc = mycol.find_one(query)
        return mydoc

    def GetTeacherCourse(self, teaid, startStamp):
        mycol = self.db["course"]
        query = { "_start_stamp": {'$gte': startStamp}, '_teacherid': teaid}
        mydoc = mycol.find(query).sort('_start_stamp', pymongo.ASCENDING).limit(1)  
        if mydoc.count() == 0:
            return None
        return mydoc[0]


    def ChangeCourseStatus(self, room, startStamp, level, late, isSwitchSeat):
        mycol = self.db["course"]
        query = { "_start_stamp": startStamp, '_room': room}
        mydoc = mycol.find_one(query)
        if isSwitchSeat:
            return mydoc
    
        if mydoc == None:
            return None
        newabsent =  mydoc["_absent"] - 1
        if late == -1:
            newlate = mydoc["_late"] + 1
            newvalues = { "$set": { "_late": newlate, "_absent": newabsent}}
        else:
            newintime = mydoc["_intime"] + 1
            newvalues = { "$set": { "_intime": newintime, "_absent": newabsent}}
        mycol.update_one(query, newvalues)
        
        return mydoc

    def InsertAskForLeave(self, stuid, teaid, room, startStamp):
        mycol = self.db["course"]
        query = { "_start_stamp": startStamp, '_room': room, '_teacherid': teaid}
        mydoc = mycol.find_one(query)
        logging.info(mydoc)
        if mydoc == None:
            return None
        if stuid not in mydoc['_stus']:
            return None
        if '_askforleave' not in mydoc:
            mycol.update_one(query, {"$set": {"_askforleave": []}})
            mydoc = mycol.find_one(query)
        orig_list = mydoc['_askforleave']
        if stuid not in orig_list:
            orig_list.append(stuid)
        newvalues = {"$set": {"_askforleave": orig_list}}
        mycol.update_one(query, newvalues)
        return mydoc


def GetStudentData(self, teaid, campus, room, level, late, courseid, stuid, exception, startStamp, endStamp):
    mycol = self.db["record"]
    query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], "_teacherid": teaid}
    if campus != None:
        query["_campus"] = campus
    if room != None:
        query["_room"] = room
    if level != None:
        query["_level"] = level
    if late != None:
        query["_late"] = late
    if courseid != None:
        query["_courseid"] = courseid
    if stuid != None:
        query["_stuid"] = stuid
    if exception != None:
        query["_exception"] = exception
    
    mydoc = mycol.find(query).sort('_time', pymongo.ASCENDING).limit(1)  
    if mydoc.count() == 0:
        return None
    for doc in mydoc:
        doc["_id"] = str(doc["_id"])
    return mydoc
