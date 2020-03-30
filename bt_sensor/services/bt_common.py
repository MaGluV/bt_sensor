#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from configparser import RawConfigParser as RCP
import json
from subprocess import Popen,PIPE,STDOUT
from datetime import datetime
import logging

class BT_Common():

	"""BT_Common class contains functions common to other classes."""
	
	def __init__(self):
		self._DEVICE_MAC = self.read_config("Settings","device_MAC")
		self._DEVICE_NAME_0 = self.read_config("Settings","bt_device_name_0")
		self._DEVICE_NAME_1 = self.read_config("Settings","bt_device_name_1")
		self.__TIME_FORMAT_FROM_SERVER = "%Y-%m-%dT%H:%M:%S.%f"
		self.__SYSTEM_TIME_FORMAT = '%m%d%H%M%Y.%S'
		self._SENSOR_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
		self._get_manufacturers_name = json.loads(self.read_config("Data","manufacturers"))
		self._get_bt_version = json.loads(self.read_config("Data","bt_versions"))
		self._name_dict = self.read_config("Data","service_name")
		self._ubertooth_version = self.read_config("Settings","ubertooth_version")
		self._ubertooth_amplifier = self.read_config("Settings","ubertooth_amplifier")
		self._ubertooth_channel = self.read_config("Settings","ubertooth_channel")
		
	def put_mac_to_server(self):

		"put_mac_to_server(): create JSON to get information about sensor"
		
		return json.dumps({
				 'mac': self._DEVICE_MAC, 
				 'firmwareVersion': self.read_config('Settings','firmware_version')
			   })
		
	def read_config(self,setting,key):
	
		"""read_config: get data from BT.conf"""
		
		config = RCP()
		while True:
			try:
				config_file = '/etc/bt_sensor/BT.conf'
				config.read(config_file)
				value = config.get(setting,key)
				break
			except Exception as e:
				logging.error("Configurations Reading Error: %s" % e)	
		return value
	
	def call(self,cmd):
	
		"""call: execute system process"""
	
		process = Popen(cmd, stdout=PIPE, stderr = STDOUT, shell=True)
		data = process.communicate()[0]
		return str(data)
	
	def reboot_device(self):
	
		"""reboot_device: reboot BT devices"""
		
		hci_data = self.call("rfkill list")[1:].strip("'").split('\\n')
		for line in hci_data:
			if line.count('hci') == 1:
				hci = line.split(': ')[0]
				self.call("rfkill block %s" % hci)
				self.call("rfkill unblock %s" % hci)
				logging.info("Device %s was rebooted" % hci)
			
	def start_device(self):
	
		"""start_device: reset hciuart service if it was failed"""
		
		message = self.call("hcitool dev")
		
		if message.count(self._DEVICE_NAME_0) == 0 or message.count(self._DEVICE_NAME_1) == 0:
			self.call("systemctl start hciuart.service")
			self.call("systemctl reset-failed")
			self.call("systemctl start hciuart.service")
			
	def checkup(self,mac):
	
		"""checkup: check up MAC address on accessebility"""
	
		message = self.call("hcitool cc %s" % mac)[1:].strip("'")
		logging.info("CHECKUP_MESSAGE = %s" % message)
		if len(message) == 0:
			self.call("hcitool dc %s" % mac)
			return True
		else:
			return False
			
	def set_system_date_time(self,date):

		"""set_system_date_time(): change the system date and time to the sensor"""

		date_time = datetime.strptime(date, self.__TIME_FORMAT_FROM_SERVER)
		self.execute_system_process(["date", date_time.strftime(self.__SYSTEM_TIME_FORMAT)])
		
	def ubertooth_init(self):
	
		"""ubertooth_init: set ubertooth parameters """
	
		logging.info("Ubertooth_init")
		i = 0
		while True:
			i += 1
			cmd = "ubertooth-util -U%s -a%s" % (
												 self._ubertooth_version, 
												 self._ubertooth_amplifier
												 ) 
			answer = self.call(cmd)
			if not "usb_claim_interface error -6" in answer[1:].strip("'").split("\\n"):
				break
			if i > 1000:
				self.call("reboot")
