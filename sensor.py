import Adafruit_DHT


class Sensor:
    def __init__(self, pin, type):
        self.pin = pin
        self.type = type
        self.sensor = self.type if Adafruit_DHT.DHT11 else Adafruit_DHT.DHT22

    def get(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        '''
        result = {
            "humidity": humidity,
            "temperature": temperature,
            "type": "temp_humidity"
        }
        '''
        result = {
            "humidity": 50,
            "temperature": 20,
            "type": "temp_humidity"
        }

        return result
