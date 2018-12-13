#!/usr/bin/python3
import time
import serial
import certificate
import sensor
import sender
import subprocess
from config import Config
from libs import file
import json
from SimManager2 import SimManager
import queue
import boto3
import os
import sys
from OTA import DownloadSource

#from dotenv import Dotenv
#dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))
#os.environ.update(dotenv)

SerialBaud = 9600

# ser = serial.Serial(
#             port='/dev/ttyS0',
#             baudrate=9600,
#             parity=serial.PARITY_NONE,
#             stopbits=serial.STOPBITS_ONE,
#             bytesize=serial.EIGHTBITS,
#             timeout=1
#         )
exitFlag = False
simReady = queue.Queue(1)
ready = False
isInit = False

def run(simManager):
    # load iccid
    print("DEBUG___get sim iccid")
    idicc = simManager.read("AT+CCID\r\n")    
    # if iccid.find("AT+CCID") != -1:    
    idicc = idicc.replace("AT+CCID","")
    print('DEBUG___get iccid success : ', idicc)
    with open("env.json", "r+") as jsonFile:
        data_json = json.load(jsonFile)
        jsonFile.close()  # Close the JSON file

    #load OTA
    downLoad = DownloadSource("DOWNLOAD", data_json["OTA_Server"], data_json["OTA_path"])
    # load certificate
    print("DEBUG___load ca, path")
    cert = certificate.Certificate(
        idicc, data_json["API_key"], data_json["API_gatewaytoken"], data_json["API_endpoint"])
    if cert.isExisted():
        print('DEBUG___ca, key available')
    else:
        print("DEBUG___Cannot locate ca and key files")

    print("DEBUG___init sensor")
    ss = sensor.Sensor(data_json["SENSOR_pin"], data_json["SENSOR_type"])
    print("DEBUG___sensor pin, type, each: ", data_json["SENSOR_pin"], data_json["SENSOR_type"], data_json["SENSOR_intervaltime"])

    awsConf = json.loads(file.load("./keys/"+idicc+".json"))
    print('DEBUG___init sender')
    sd = sender.Sender("./keys/rootca.crt", "./keys/"+idicc +
                       ".crt", "./keys/"+idicc+".key",  awsConf.get("topic"), awsConf.get("endpoint"), int(awsConf.get("port")))
    sd.connect()
    print('DEBUG___inited sender')
    sms = simManager.read("AT+CMGR=12\r\n")
    # sms = converter.pdu_to_text(sms.replace("AT+CMGR=12+CMGR: 1,,100", ""))
    print('DEBUG___Receive OTA SMS success : ', sms)
    log(idicc)
    # send data
    while ready:
        simStateChange()
        newData = ss.get()
        newData["ICCID"] = idicc
        newData["location"] = "demo"
        newData = json.dumps(newData)
        sd.send(newData)        
        time.sleep(data_json["SENSOR_intervaltime"])
        if sms != "":
            print('DEBUG________________OTA BEGIN')
            downLoad.download()
            downLoad.backup()
            #downLoad.remove()
            downLoad.extract()
            #downLoad.resetService()
            time.sleep(10)
            os.system('sudo chmod 666 /dev/ttyS0')
            print("DEBUG__________Restart")
            os.system('cd ..')        
            os.system('cd /home/pi/workspace/singtel/Singtel_VNSIM/')        
            os.system('sudo chmod a+x /home/pi/workspace/singtel/Singtel_VNSIM/main.py')        
            os.execv(__file__, sys.argv)    

def simStateChange():
    global ready
    print("DEBUG___simStateChange ok?", ready)
    if not simReady.empty():
        simReady.get()
        ready = not ready


def log(iccid):
    dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-1")

    sensor_log_table = dynamodb.Table('dev_sensor_logs')
    timestamp = int(time.time() * 1000)
    log = " " + iccid + " is online"
    sensor_log_table.put_item(Item={
        'sensor_id': iccid,
        'timestamp': timestamp,
        'log': log
    })
def doWhile(ser1, code):
    #while ser1.is_open:
    #print(code)
    ser1.write(code.encode())
    ser1.flush()
    time.sleep(1)
    response1 =  ser1.readline().decode()
    print(response1)
    ser1.flush()
    time.sleep(0.1)
    #print(response1)
    #if response1 == 'OK\n':
    #    break
        
def _onload():
    with open("env.json", "r+") as jsonFile:
        data_json = json.load(jsonFile)
        jsonFile.close()  # Close the JSON file
    print("----------SOFTWARE VERSION: ", data_json["software_version"])
    print('DEBUG__Power ON Init')
    ser1 = serial.Serial('/dev/ttyS0', 9600, timeout = 1)
    print('DEBUG__AT')
    doWhile(ser1, "AT\r\n")
    print('DEBUG__AT+CNSMOD=1')
    doWhile(ser1, "AT+CNSMOD=1\r\n")
    print('DEBUG__AT+CMNB=1')
    doWhile(ser1, "AT+CMNB=1\r\n")
    print('DEBUG__AT+CAPNMODE=1')
    doWhile(ser1, "AT+CAPNMODE=1\r\n")
    print('DEBUG__AT+CNACT=1')
    doWhile(ser1, "AT+CNACT=1,\""+data_json["APN_name"]+"\"\r\n")
    print('DEBUG__AT+CNMI=2,1')
    doWhile(ser1, "AT+CNMI=2,1\r\n")
    print('DEBUG__AT+CMGF=1')
    doWhile(ser1, "AT+CMGF=1\r\n")
    #doWhile(ser1, "AT+CMGL=\"REC UNREAD\"\r\n")
    ser1.close()
    print("DEBUG___MAIN___onload finish")

if __name__ == '__main__':    
    _onload()
    while True:
        global ready
        flag_ = True
        sm = SimManager("sim manager", simReady)
        sm.start()
        
        while flag_:
            print("DEBUG3___is sim ready ?")            
            while not ready:
                simStateChange()
                print("DEBUG___sim not ready yet, change state")
                time.sleep(2)
            run(sm)
            sm.stop()
            flag_ = False    
