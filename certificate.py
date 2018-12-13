import http.client
import json
import urllib.request
from libs import file
from urllib.parse import urlparse


class Certificate:
    def __init__(self, iccid, apiKey, gatewayToken, endPoint):
        self.iccid = iccid
        self.apiKey = apiKey
        self.gatewayToken = gatewayToken
        url = urlparse(endPoint)
        self.host = url.hostname
        self.port = url.port
        self.path = url.path

    def isExisted(self):
        """
            find if in follow order
            1. cache
            2. local
            3. download
        """
        if self._load():
            print("already downloaded")
            return True
        else:
            print("not yet downloaded")
            return self._download()

    def _load(self):
        print("check if already downloaded")
        try:
            file.load("./keys/"+self.iccid + ".crt")
            file.load("./keys/"+self.iccid + ".key")
            file.load("./keys/"+self.iccid + ".json")
            return True
        except FileNotFoundError:
            return False

    def _download(self):
        print("downloading files")
        headers = {"Content-Type": "application/json",
                   "GATEWAY_TOKEN": self.gatewayToken}
        params = {"ICCID": self.iccid, "api_key": self.apiKey}
        body = json.dumps(params)

        print("requesting to", self.host, self.port, self.path)
        conn = http.client.HTTPConnection(self.host, self.port)
        conn.request("POST", self.path, body, headers)

        response = conn.getresponse()
        if response.status == 200:
            resString = response.read().decode('utf-8')
            resJson = json.loads(resString)
            conn.close()

            print("downloaded", resJson)
            print("saving to file")
            file.save('./keys/'+self.iccid+".json", resString)
            urllib.request.urlretrieve(
                resJson["crt"], './keys/%s.crt' % self.iccid)
            urllib.request.urlretrieve(
                resJson["key"], './keys/%s.key' % self.iccid)

            return True
        else:
            print(response.status, response.reason)
            conn.close()

            return False
