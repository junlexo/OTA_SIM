import threading
import time
import serial
import queue
import subprocess
import SMS
import json
class SimManager(threading.Thread):
    def __init__(self, name, readyFlag, options={}):
        threading.Thread.__init__(self)
        self.name = name
        self.exitFlag = False
        self.readyFlag = readyFlag

    def run(self):

        self._start()

    def _start(self):
        print("DEBUG___starting SimManager.....")
        self.listenerQueue = queue.Queue()
        self.readQueue = queue.Queue()
        self.simThread = SimThread(
            "Sim Thread", self.readQueue, self.listenerQueue)
        self.wvdialThread = WvdialThread("WvdialThread")

        self.simThread.start()
        #self.resetSim()
        # check sim
        self.checkSim()

        self.wvdialThread.start()
        self.readyFlag.put(True)

        # wait untill inserted
        self._monitoring()

    def onEjectSim(self, value):
        self.listenerQueue.put(value)

    def onInsertedSim(self, value):
        self.listenerQueue.put(value)

    def _onEjectSim(self):
        print("sim is ejected")
        self.readyFlag.put(False)
        self.wvdialThread.stop()
        self.checkSim()
        self.simThread.stop()
        self._start()

    def _clean(self):
        return True

    def read(self, command):
        return self.simThread.read(command)

    def _monitoring(self):
        print("DEBUG___SimManager monitoring")
        #for SMS
        sms = SMS.SMSManager()
        # anyone want to read
        # are there any problem
        while True:
            if not self.listenerQueue.empty():
                value = self.listenerQueue.get()
                print(value)
                if value == "+CPIN: READY":
                    #self._onInsertedSim()
                    #break
                    print("DEBUG___+CPIN: ready----------------")
                    pass
                elif value == "+CPIN: NOT READY":
                    print("DEBUG___+CPIN: NOT ready----------------")
                    self._onEjectSim()
                    break
                #SMS check
                elif value.find("CMTI") != -1:
                    print("DEBUG___Received new Message")
                    smsindex = sms.read_index(value)
                    smscontent = self.read_SMS(smsindex[1])
                    if "\"$\"" in smscontent:
                        #finish receive SMS
                        print("DEBUG___finish read SMS")
                    else:
                        #wait for finish
                        print("DEBUG___read next SMS")
                else:
                    print("DEBUG___no such command : ", value)
            #else:
                #print("DEBUG___Queue is empty")

    def checkSim(self):
        print("DEBUG___running on thread : ", threading.current_thread().name)
        lastRead = self.simThread.read("AT+CCID\r\n")
        print("DEBUG___check sim is inserted : ", lastRead)
        while lastRead == "ERROR":
            self.resetSim()
            lastRead = self.simThread.read("AT+CCID\r\n")
            print("DEBUG___check sim is inserted again : ", lastRead)

    def resetSim(self):
        with open("env.json", "r+") as jsonFile:
            data_json = json.load(jsonFile)
            jsonFile.close()  # Close the JSON file
        print("DEBUG___reset sim_________")
        self.simThread.read("AT+CFUN=6\r\n")
        time.sleep(15)
        self.simThread.read("AT+CNSMOD=1\r\n")
        self.simThread.read("AT+CMNB=1\r\n")
        self.simThread.read("AT+CAPNMODE=1\r\n")
        self.simThread.read("AT+CNACT=1,\""+data_json["APN_name"]+"\"\r\n")
        self.simThread.read("AT+CNMI=2,1\r\n")
        self.simThread.read("AT+CMGF=1\r\n")
        #self.simThread.read("AT+CMGL=\"REC UNREAD\"\r\n")
        print("DEBUG___reset sim ok_____________")

    #SMS read
    def read_SMS(self,index):
        print("DEBUG___Read SMS from : ", index)
        strsms = self.simThread.read("AT+CMGR=%s\r\n", index)

        return strsms

class WvdialThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        subprocess.call(['sudo', 'wvdial'])

    def stop(self):
        subprocess.call(['sudo', 'killall', 'wvdial'])


class SimThread (threading.Thread):
    def __init__(self, name, readQueue, notifyQueue, options={}):
        threading.Thread.__init__(self)
        self.name = name
        self.exitFlag = False

        # shoud use option or DI here
        self.ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        self.readQueue = readQueue
        self.notifyQueue = notifyQueue
        self.commandQueue = queue.Queue(1)

    def run(self):
        print("DEBUG___Start reading : " + self.name)
        while not self.exitFlag:
            # run command and get result
            if not self.commandQueue.empty():
                command = self.commandQueue.get()
                self._send(command)
                # wait until result is available
                # TODO: check if command is wrong
                while True:
                    result = ""
                    lastRead = self._recv()
                    if lastRead == command.rstrip():
                        print("                     replied")
                        result = lastRead
                        lastRead = self._recv()
                        # read until command is end
                        while not lastRead == "OK":
                            if lastRead == "ERROR":
                                result = "ERROR"
                                break
                            result += lastRead
                            lastRead = self._recv()
                            time.sleep(0.1)
                            print("DEBUG___")
                        self.readQueue.put(result)
                        break
                    else:
                        if lastRead:
                            self.notifyQueue.put(result)
            # get notification
            else:
                result = self._recv()
                if result:
                    self.notifyQueue.put(result)

            time.sleep(0.1)
        print("DEBUG___Exit reading : " + self.name)

    def stop(self):
        self.exitFlag = True

    def _send(self, command):
        print("    > ", command)
        self.ser.write(command.encode())
        self.ser.flush()

    def _recv(self):
        s = self.ser.readline()
        data = s.decode()   #'utf-8'
        data = data.rstrip()
        print("    < ", data)
        return data

    def read(self, command):
        self.commandQueue.put(command)
        while self.readQueue.empty():
            time.sleep(1)
        return self.readQueue.get()
