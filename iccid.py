#!/usr/bin/python3
import serial
import time


class ICCID:
    def __init__(self, command="AT+CCID\r\n", options={}):
        self.ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        self.command = command

    def get(self):
        self._send()
        time.sleep(1)

        while True:
            # ignore first result
            self._recv()
            time.sleep(1)

            result = ""
            lastRead = self._recv()
            while lastRead != 'OK':
                time.sleep(1)
                result += lastRead
                lastRead = self._recv()
                time.sleep(1)
            return result

    def _send(self):
        print("> ", self.command)
        self.ser.write(self.command.encode())
        self.ser.flush()

    def _recv(self):
        s = self.ser.readline()
        data = s.decode()
        data = data.rstrip()
        print("< ", data)
        return data
