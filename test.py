import pymongo
db = pymongo.MongoClient('mongodb://server:tdlm_server123@checkin.nuaaweyes.com:27017/')["test"]

mycol = db["user"]
query = {f"_id": "161830312"} 
mydoc = mycol.find_one(query)
print(mydoc)

