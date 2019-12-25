import pymongo
import os
import threading
import time
# db = pymongo.MongoClient('mongodb://server:tdlm_server123@checkin.nuaaweyes.com:27017/')["test"]

# mycol = db["user"]
# query = {f"_id": "161830312"} 
# mydoc = mycol.find_one(query)
# print(mydoc)

def ClearLogs():
    while True:
        oldlogtime = time.strftime("%Y-%m-%d", time.localtime(int(time.time())  - 10 * 24 * 60 * 60)) 
        print(f"clear log: {oldlogtime}")
        if os.path.exists(f"/var/www/class-register/logs/{oldlogtime}.log"):
            os.remove(f"/var/www/class-register/logs/{oldlogtime}.log")
        time.sleep(10)


if __name__ == '__main__':
    threading.Thread(target=ClearLogs).start()
    while True:
        print("hello world! ")
        time.sleep(1)