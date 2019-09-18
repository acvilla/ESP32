
from client import Client 
import random
import time

def makeId(length):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    result = ''
    for i in range(length):
        result += random.choice(characters)

    return result

def searchId(fn):
    try:
        with open(fn, "r") as idFile:
            c_id = idFile.read()
            idFile.close()
            if (len(c_id) != 32):
                with open(fn, "rw") as IdFile:
                    idFile.write(makeId(32))
                    idFile.close()
            return c_id
    except Exception:
        idFile = open(fn, "rw")
        idFile.write(makeId(32))
        idFile.close()
        with open(fn, "r") as IdFile:
            c_id = idFile.read()
            idFile.close()
            return c_id

c_id = searchId('c_id.txt')
c = Client(c_id, "broker.mqttdashboard.com", topic="ebike/" + c_id) # Initialize mqtt client

while True:
    c.start()
    time.sleep(1)
    c.read_data()
    time.sleep(1)




