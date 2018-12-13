import http.client
import json
import urllib
import urllib.request
import time
from urllib.parse import urlparse
import zipfile
import shutil
import os

class DownloadSource():
	"""docstring for ClassName"""
	def __init__(self, name, address, path):
		self.name = name
		self.address = address
		self.path = path

	def download(self):			
		urllib.request.urlretrieve(self.address, self.path)
		print("DEBUG--------Download finished")
		time.sleep(5)
		pass	
	def backup(self):	
		os.system('rm -rf /home/pi/workspace/singtel/Singtel_VNSIM.backup')
		shutil.copytree('/home/pi/workspace/singtel/Singtel_VNSIM','/home/pi/workspace/singtel/Singtel_VNSIM.backup')
		print("DEBUG--------backup finished")
		pass	
	def remove(self):	
		os.system('rm -rf /home/pi/workspace/singtel/Singtel_VNSIM/')
		print("DEBUG--------remove finished")
		pass	
	def extract(self):
		fantasy_zip = zipfile.ZipFile(self.path)
		fantasy_zip.extractall('/home/pi/workspace/singtel')
		fantasy_zip.close()	
		print("DEBUG--------extract finished")
		pass	
	def resetService(self):	
		os.system('sudo systemctl restart dummy.service')
		os.system('sudo systemctl status dummy.service')	
		print("DEBUG--------resetService finished")
		pass		
		