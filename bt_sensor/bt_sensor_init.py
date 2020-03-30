#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bt_sensor.services.bt_scan import BT_Scan
from bt_sensor.services.ble_scan import BLE_Scan
from bt_sensor.services.Request import Request
from multiprocessing.pool import ThreadPool
import time
import json
import logging
import os

class Init(BT_Scan,BLE_Scan,Request):

	"""Class Init manage scan BT classic and BLE devices and
	   send information about them to server"""
	
	def __init__(self):
		
		BT_Scan.__init__(self)
		BLE_Scan.__init__(self)
		time.sleep(2)
		Request.__init__(self)
		logging.basicConfig(
							filename='bt_sensor.log',
							filemode='w',
							level=logging.DEBUG,
							format='%(asctime)s %(message)s', 
							datefmt='%m/%d/%Y %I:%M:%S %p'
							)
		
	def access_check(self):

		"""access_check: check accessibility """

		while True:	
			device_info = self.get_device_info()

			if (device_info == ""):
				logging.warning("JSON wasn't got")
				

			if device_info["success"]:
				return device_info

			elif not device_info["success"]:
				logging.warning("This MAC-address doesn't exist!")
		
	def start_sensor(self):

		"""start_sensor: get data from device """

		device_date_time = self.access_check()
		self.set_system_date_time(device_date_time["deviceInfo"]["date"])
		
	def start_bt(self, devices):
	
		"""start_bt: start BT Classic devices scanning"""

		self.get_bt_info(devices)
		get_info = self.create_bt_json(devices)
		return get_info
		
	def start_ble(self,devices):
	
		"""start_ble: start BLE devices scanning"""
		
		pool = ThreadPool(processes=2)
		ble_scan = pool.apply_async(self.get_ble_info, (deivces,))
		kill = pool.apply_async(self.ble_kill, ())
		if ble_scan.get():
			get_info = self.create_ble_json(devices)
			pool.close()
			return get_info
		else:
			pool.close()
			return []
		
	def run_sensor(self):
	
		"""run_sensor: collect all infornation from both types of BT devices, 
					   then create JSON message and send it to server"""
		
		self.start_device()
		while True:
			pool = ThreadPool(processes=2)
			self.ubertooth_init()
			self.reboot_device()
			time.sleep(7)
			
			try:
				ble_devices = self.ubertooth_ble_scan()
				time.sleep(5)
				bt_devices = self.ubertooth_scan(60,60)
				if len(bt_devices.keys()) != 0:
					async_result_bt = pool.apply_async(self.start_bt, (bt_devices,))
				async_result_ble = pool.apply_async(self.start_ble, (ble_devices,))
			except Exception as e:
				logging.error("Scan Error: %s" % e)
				continue
			
			if len(bt_devices.keys()) == 0:
				logging.warning("There is no information about BT devices")
				devices_info = []
			else:
				devices_info = async_result_bt.get()
				
			for device in async_result_ble.get():
				devices_info.append(device)
				
			pool.close()
				
			if len(devices_info) == 0:
				continue
				
			data_of_devices = {
								"sensorMac": self._DEVICE_MAC,
								"deviceInfo": devices_info
								}
								
			for device in devices_info:
				logging.info("DEVICE INFO: %s" % device)
			api = self.read_config("Settings", "api_set_bluetooth")
			send_data = self.send(api, json.dumps(data_of_devices),"POST")
			logging.info("Request return %s" % send_data)
			BLE_Scan.__init__(self)
			BT_Scan.__init__(self)
			
if __name__ == '__main__':

	service = Init()
	service.start_sensor()
	service.run_start()
	
