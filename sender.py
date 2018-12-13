import paho.mqtt.client as paho
import ssl
from time import strftime, sleep


class Sender:
    def __init__(self, ca, cert, key, topic, endpoint, port):
        self.ca = ca
        self.cert = cert
        self.key = key
        self.topic = topic
        self.port = port
        self.endpoint = endpoint
        self.mqttc = paho.Client()
        self.mqttc.on_connect = self.onConnect
        self.mqttc.on_message = self.onMessage

        self.mqttc.tls_set(self.ca, certfile=self.cert, keyfile=self.key, cert_reqs=ssl.CERT_REQUIRED,
                           tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

    def connect(self):
        self.mqttc.connect(self.endpoint, self.port, keepalive=60)
        self.mqttc.loop_start()

    def send(self, data):
        self.mqttc.publish(self.topic, data, qos=0)
        print("DEBUG___AWS sent ", data)

    def onConnect(self, client, userdata, flags, rc):
        return True

    def onMessage(self, client, userdata, msg):
        return True
