#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bt_sensor.services.bt_common import BT_Common
from bt_sensor.models.ble import BLE
from itertools import cycle
from datetime import datetime
import json
import re
import time
import logging
from bluepy.btle import Scanner, DefaultDelegate
from os import kill
from signal import SIGKILL

class ScanDelegate(DefaultDelegate):

	"""ScanDelegate Class needs for logging messages about founded devices"""

	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if isNewDev:
			logging.info("Discovered device %s" % dev.addr)

class BLE_Scan(BT_Common):

	"""BLE_Scan Class is for scanning BLE devices"""

	def __init__(self):
	
		BT_Common.__init__(self)

	def ubertooth_ble_scan(self):
	
		"""ubertooth_ble_scan: discovering of BLE MAC addresses """
	
		logging.info("Ubertooth BLE Scan")
		ble_call = self.call(". `pwd`/ble_scan.sh")
		logging.info(ble_call)
		uber_data = open('uber_info','r').read()
		match_mac = re.findall(r'AdvA:  \w\w\S\w\w\S\w\w\S\w\w\S\w\w\S\w\w', uber_data)
		match_time = re.findall(r'systime=\d+',a)
		ble_device = {}
		
		for str_mac, str_time in zip(match_mac,match_time):
			mac = str_mac.split(':  ')[1].upper()
			time = int(str_time.split('=')[1])
			if not mac in ble_device.keys():
				ble_device[mac] = BLE()
			ble_device[mac].set_ble_pocket_number()
			ble_device[mac].set_ble_time(time.strftime(self._SENSOR_TIME_FORMAT, 
										 time.localtime(time)))
			logging.info("%s: %s" % (mac, pocket_number))
			
		return ble_device
			
	def get_manufaturer(self,mac):
	
		"""get_manufacturer: get manufacurer's name"""
	
		logging.info("Get BLE Manufacturer")
		data = self.call("hcitool leinfo %s" % mac)[1:].split("\\n") 
		
		try:
			for line in data:
				word = line.split(': ') 
				manufacturer = word[1] if "Manufacturer" in word[0] else None
		except Exception:
			manufacturer = None
			
		return manufacturer

	def get_ble_info(self,ble_devices):
	
		"""get_ble_info: collect information from known devices"""
	
		logging.info("Get BLE Info")
		scanner = Scanner().withDelegate(ScanDelegate())
		devices = []
		device_time = []
		addresses = []
		try:
			for i in range(6):
				device = scanner.scan(10.0)
				for dev in device:
					if not dev.addr.upper() in addresses:
						address.append(dev.addr.upper())
						devices.append(dev)
						device_time.append(str(datetime.now()).split('.')[0])
						logging.info("Device Scan Date: %s" % device_time[-1])
						
			for mac in addresses:
				ble_dev.set_ble_addresses(mac)
						
		except Exception as e:
			logging.error("Bluepy Scan Error: %s" % e)
			return False

		for dev in devices:
			mac = dev.addr.upper()
			if not mac in ble_device.keys():
				ble_devices[mac] = BLE()
				ble_devices[mac].set_ble_rssi(dev.rssi)
				ble_devices[mac].set_ble_time(device_time[devices.index(dev)])
				ble_devices[mac].set_ble_pocket_number()
			
			data = {}
			for (adtype, desc, value) in dev.getScanData():
				data[desc] = value
			
			services_data = []
			try:
				for word in data["Complete 16b Services"].split(','):
					uuid = '0x' + word[4:8]
					name = self._name_dict(uuid)
					services_data.append({
										  'uuid' : uuid,
										  'name' : name,
										  'protocol' : None
										  })
			except Exception:
				services_data.append({
									  'uuid' : None,
									  'name' : None,
									  'protocol' : None
									  })
			ble_devices[mac].set_ble_services(services_data)
				
			try:
				ble_devices[mac].set_ble_ssid(data["Complete Local Name"])
			except Exception:
				ble_devices[mac].set_ble_ssid(None)
		return True
				
	def ble_kill(self):
	
		"""ble_kill: kill bluepy_helper process if it doesn't stop after timeout"""

		time.sleep(80)
		command = "ps -aux | grep bluepy-helper | awk '{print $2}'"
		uber_pids = self.call(command)[1:].strip("'").rstrip('\\n').split('\\n')
		logging.info("Bluepy-helper process: %s" % uber_pids)
		if len(uber_pids) > 0:
			for pid in uber_pids:
				try:
					kill(int(pid), SIGKILL)	
					logging.info("Process %s was killed" % pid)		
				except Exception as e:
					logging.warning(e)

	def create_ble_json(self, ble_devices):
	
		"""create_ble_json: create json with information about BLE devices"""
	
		logging.info("Create BLE JSON")
	
		data_of_devices = []
		devices_info = []
		for mac in ble_devices.keys():
			
			devices_info.append({
								 "name:": ble_devices[mac].get_ble_ssid(),
								 "mac": mac,
								 "timestamp": ble_devices[mac].get_ble_time(),
								 "standard": "LE",
								 "deviceClass": "BLE",
								 "level": ble_devices[mac].get_ble_rssi(),
								 "packages": ble_devices[mac].get_ble_pocket_number(),
								 "vendorChip": self.get_manufaturer(mac),
								 "services": ble_devices[mac].get_ble_services()
								 })
		return devices_info

