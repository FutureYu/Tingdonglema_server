# 增删改查api
import pymongo
import logging

class DataBase:
    db = pymongo.MongoClient('mongodb://localhost:27017/')["checkin"]
 
    def CheckBind(self, openid, id):
        mycol = self.db["user"]
        query = {"_openid": openid} 
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False
        if mydoc["_openid"] == "null":
            return False
        return True

    def BindOpenid(self, openid, id):
        mycol = self.db["user"]
        query = {"_id": id} 
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return None
        if mydoc["_openid"] != "null":
            return None
        
        newvalues = { "$set": { "_openid": openid } }
        mycol.update_one(query, newvalues)
        return id

    def UploadRecord(self, openid, room, campus, row, col, time, level, late):
        mycol = self.db["record"]
        newvalues = {"_openid": openid, "_campus": campus, "_room": room, "_row": row, "_col": col, "_time": time, "_level": level, "_late": late}
        result = mycol.insert_one(newvalues)
        return str(result)

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
        
