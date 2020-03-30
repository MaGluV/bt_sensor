#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
from bt_sensor.services.bt_common import BT_Common
import logging

class Request(BT_Common):

	"""Class Data_Exchange realize data exchange between server and sensor"""

	def __init__(self):
		BT_Common.__init__(self)
		self.__HEADER = {'Content-type': 'application/json'}

	def send(self, api, data, request_type):

		"""send(): Send POST and GET requests to server, 
				which address was described in settings.conf."""

		server = self.read_config("Settings","server")
		login = self.read_config("Settings","login")
		password = self.read_config("Settings","password")

		while True:
			try:
				if(request_type == "POST"):
					url = 'http://{0}/{1}'.format(server, api)
					read_request = requests.post(url, data=data, auth=(login, password), headers=self.__HEADER, timeout=30)

				elif(request_type == "PUT"):
					url = 'http://{0}/{1}'.format(server, api)
					read_request = requests.put(url, data=data, auth=(login, password), headers=self.__HEADER, timeout=30)

				elif(request_type == "GET"):
					#TODO : implement this request
					return ""

				else:
					logging.error("Incorrect request!")
					return ""

				logging.info("%s %s" % (request_type,read_request))
				if (read_request.status_code == 200):
					try:
						return json.loads(read_request.text)
					except Exception:
						return ""

				else:
					logging.warning((read_request.text))
					time.sleep(10)
					continue

			except Exception as e:
				logging.error("Data Sending Error: %s" % e)
				time.sleep(10)
				continue

	def get_device_info(self):

		"""get_device_info(): get server time"""

		api = self.read_config("Settings","api_access") 
		data = self.put_mac_to_server()
		device_info = self.send(api, data, "PUT")
		return device_info
