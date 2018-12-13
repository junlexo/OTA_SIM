import threading
import time
import re
from curses import ascii
import json

is_Receive_SMS = False

class SMSManager:
    def __init__(self):
        return

    def read_index(self, data):
        print("DEBUG___receive new SMS from: ", data)
        index_list = []
        strtmp = re.compile("(\s?\d)|:")
        index_list += strtmp.sub("", data).split(",")
        return index_list

    def split_sms(self, data):
        print("DEBUG___the SMS content is : ", data)
        a = data
        z = []
        y = []
        for x in a:
            if x.startswith("+CMGR:"):
                r = a.index(x)
                t = r + 1
                z.append(r)
                z.append(t)
        for x in z:
            y.append(a[x])

        return y

    def action_sms(self,data):
        if data[0] == "1":
            #Change APN
            with open("env.json", "r+") as jsonFile:
                data_json = json.load(jsonFile)
                jsonFile.close()  # Close the JSON file
            ## Working with buffered content
            tmp = data_json["APN_name"]
            data_json["APN_name"] = data[1]
            data_json["APN_user"] = data[2]
            data_json["APN_pass"] = data[3]
            ## Save our changes to JSON file
            jsonFile = open("env.json", "w+")
            jsonFile.write(json.dumps(data_json))
            jsonFile.close()
            print("DEBUG___Changed APN and restart ", data[1])
        elif data[0] == "2":
            #Change Endpoint, token
            with open("env.json", "r+") as jsonFile:
                data_json = json.load(jsonFile)
                jsonFile.close()  # Close the JSON file
            ## Working with buffered content
            tmp = data_json["API_key"]
            data_json["API_key"] = data[1]
            data_json["API_gatewaytoken"] = data[2]
            data_json["API_endpoint"] = data[3]
            ## Save our changes to JSON file
            jsonFile = open("env.json", "w+")
            jsonFile.write(json.dumps(data_json))
            jsonFile.close()
            print("DEBUG___Changed Endpoint and restart ", data[1])
        elif data[0] == "3":
            #Change Sensor
            with open("env.json", "r+") as jsonFile:
                data_json = json.load(jsonFile)
                jsonFile.close()  # Close the JSON file
            ## Working with buffered content
            tmp = data_json["SENSOR_type"]
            data_json["SENSOR_type"] = data[1]
            data_json["SENSOR_pin"] = data[2]
            data_json["SENSOR_intervaltime"] = data[3]
            ## Save our changes to JSON file
            jsonFile = open("env.json", "w+")
            jsonFile.write(json.dumps(data_json))
            jsonFile.close()
            print("DEBUG___Changed Sensor and restart ", data[1])
        elif data[0] == "4":
            #Update new software
            with open("env.json", "r+") as jsonFile:
                data_json = json.load(jsonFile)
                jsonFile.close()  # Close the JSON file
            ## Working with buffered content
            tmp = data_json["OTA_Server"]
            data_json["OTA_Server"] = data[1]
            data_json["OTA_port"] = data[2]
            data_json["OTA_path"] = data[3]
            ## Save our changes to JSON file
            jsonFile = open("env.json", "w+")
            jsonFile.write(json.dumps(data_json))
            jsonFile.close()
            print("DEBUG___Updated new software and restart", data[1])
        elif data[0] == "5":
            print("DEBUG___the SMS format is invalid")
        else:
            print("DEBUG___the SMS format is invalid")