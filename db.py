import pymongo
import logging

class DataBase:
    db = pymongo.MongoClient('mongodb://localhost:27017/')["checkin"]
 
    def CheckBind(self, openid):
        mycol = self.db["user"]
        query = {"_openid": openid} 
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False, 0, None, None
        if mydoc["_openid"] == "null":
            return False, 0, None, None
        if mydoc["_is_student"] == True:
            return True, 1, mydoc["_id"], mydoc["_name"]
        elif mydoc["_is_student"] == False:
            return True, 2, mydoc["_id"], mydoc["_name"]

    def BindOpenid(self, openid, id, identity_number):
        mycol = self.db["user"]
        query = {"_id": id, "_identity_number": identity_number} 
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return None, None, None, None
        if mydoc["_openid"] != "null":
            return None, None, None, None
        
        newvalues = { "$set": { "_openid": openid } }
        mycol.update_one(query, newvalues)
        if mydoc["_is_student"] == True:
            return id, 1, mydoc["_id"], mydoc["_name"]
        elif mydoc["_is_student"] == False:
            return id, 2, mydoc["_id"], mydoc["_name"]



    def UploadRecord(self, openid, room, campus, row, col, time, level, late):
        mycol = self.db["record"]
        newvalues = {"_openid": openid, "_campus": campus, "_room": room, "_row": row, "_col": col, "_time": time, "_level": level, "_late": late}
        result = mycol.insert_one(newvalues)
        return str(result)

    def SwitchSeat(self, openid, room, campus, row, col, startStamp, endStamp):
        mycol = self.db["record"]
        
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], "_campus": campus}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return None
        
        newvalues = { "$set": { "_room": room, "_col": col, "_row": row}}
        mycol.update_one(query, newvalues)
        
        return str(mydoc["_id"])

    def CheckSeatAvailable(self, room, campus, row, col, startStamp, endStamp):
        mycol = self.db["record"]
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_room': room, "_campus": campus, "_row": row, "_col": col}
        mydoc = mycol.find_one(query)
        if not mydoc:
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

    def GetRoomHistory(self, room, startStamp, endStamp):
        mycol = self.db["record"]
        query = { '$and': [ { '_time':{'$gte':startStamp}  }, {'_time':{'$lt':endStamp} } ], '_room': room}
        mydoc = mycol.find(query)
        return mydoc
        
