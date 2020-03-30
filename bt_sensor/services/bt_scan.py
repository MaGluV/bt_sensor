#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#For MINT:
# sudo apt-get install libbluetooth-dev
# sudo apt-get install python3-dev
#
#For FEDORA:
# sudo dnf install python3-devel
# sudo dnf install bluez-libs-devel
#
#Common libs:
# python3 -m pip install pybluez
# python3 -m pip install bluepy
#
#

from bluetooth import *
from bluetooth import _bluetooth as _bt
from bt_sensor.services.discoverer import InfoDiscoverer
from bt_sensor.services.bt_common import BT_Common
from bt_sensor.models.bt_classic import BT_Classic 
from multiprocessing.pool import ThreadPool
from datetime import datetime
from signal import SIGKILL
from select import *
from os import kill 
import logging
import json
import time
import re

class BT_Scan(BT_Common):

	"""Class BT_Scan search BT devices and collect information about them"""

	def __init__(self):
		BT_Common.__init__(self)

	def ubertooth_discovery(self, time_scan):
	
		"""ubertooth_discovery: get LAP of undiscaverable devices"""
	
		logging.info("Get LAP")
		cmd = "/usr/bin/ubertooth-rx -t %s" % str(time_scan)
		get_data = str(self.call(cmd))[1:].strip("'")
		return_data = []

		if get_data.count('uh oh, full_usb_buf not emptied') != 0:
			logging.warning("Error :uh oh, full_usb_buf not emptied")
			get_data.replace('uh oh, full_usb_buf not emptied','')
		logging.info(get_data)

		for line in get_data.split('\\n'):
		
			if line.count("ch= ") == 1:
				line = line.replace('ch= ','ch=')

			if line == None or line == "":
				continue
			json_data = '{"' + line.replace('=','":"').replace(' ' ,'","') + '"}'

			try:
				return_data.append(json.loads(json_data))
			except Exception as e:
				logging.error("Ubertooth Discovery Error: %s" % e)

		return return_data
		
	def ubertooth_kill(self, timeout, kill_message):
		
		"""ubertooth_kill: kill ubertooth-rx process if it doesn't stop after timeout"""
		
		time.sleep(timeout)
		command = "ps -aux | grep \"%s\" | awk '{print $2}'" % (kill_message)
		uber_pids = self.call(command)[1:].strip("'").rstrip('\\n').split('\\n')
		logging.info("Ubertooth process: %s" % uber_pids)
		if len(uber_pids) > 0:
			for pid in uber_pids:
				try:
					kill(int(pid), SIGKILL)			
					logging.info("Process %s was killed" % pid)
				except Exception:
					logging.info("Process %s already killed" % pid)
			return "Killed"
		else:
			return "Nothing to kill"

	def get_mac(self, lap, time_scan):
	
		"""get_mac: get MAC address (LAP+UAP) of undiscoverable devices"""
	
		logging.info("Get MAC(LAP+UAP)")
		mac = ''
		cmd = "/usr/bin/ubertooth-rx -l %s -t %s" % (lap, str(time_scan))
		try:
			pool = ThreadPool(processes=2)
			async_result_start = pool.apply_async(self.call, (cmd,))
			async_result_kill = pool.apply_async(self.ubertooth_kill, (time_scan + 10,"ubertooth-rx -l",))
			uap_result = async_result_start.get()
			uap_kill = async_result_kill.get()
			logging.info(uap_kill)
			pool.close()
			time.sleep(1)
			data = str(self.call(uap_result))[1:].strip("'")
			uap = re.findall(r'UAP = \w\w\w\w', data)[0].split(' = ')[1]
		except Exception as e:
			logging.error("UAP_Scan_Error : %s" % e)
			return mac
				
		logging.info("UAP = %s" % uap)
		mac = "00:00:%s:%s:%s:%s" % (
									  uap[2:4].upper(),
									  lap[0:2].upper(),
									  lap[2:4].upper(),
									  lap[4:6].upper()
									  )
		return mac  

	def ubertooth_scan(self, timeout_lap=120, timeout_uap=120):
	
		"""ubertooth_scan: discover undiscoverable devices"""
	
		logging.info("Ubertooth Scan")
		self.ubertooth_init()
		time.sleep(2)
		logging.info("TimeOutLap = %s, TimeOutUap = %s" % (timeout_lap,timeout_uap))
		device = {}

		try:
			pool = ThreadPool(processes=2)
			async_result_start = pool.apply_async(self.ubertooth_discovery, (timeout_lap,))
			async_result_kill = pool.apply_async(self.ubertooth_kill, (timeout_lap + 10,"ubertooth-rx -t",))
			get_uber_info = async_result_start.get()
			lap_kill = async_result_kill.get()
			logging.info(lap_kill)
			pool.close()
			
			time.sleep(2)
			if len(get_uber_info) != 0:
				for line in get_uber_info:
					if int(line['err']) == 2:
						continue
						
					mac = self.get_mac(lap, timeout_uap)
					if mac == '':
						continue
					
					logging.info("Address was found: %s" % mac)
					
					if not mac in device.keys():
						device[mac] = BT_Classic()
						
					device[mac].set_time(time.strftime(self._SENSOR_TIME_FORMAT, 
										 time.localtime(int(line['systime']))))				
					device[mac].set_pocket_number()
				
				if len(device.keys()) == 0:
					logging.warning("Ubertooth got nothing!")

			else:
				logging.warning("Ubertooth got nothing!")

		except Exception as e:
			logging.error("Ubertooth Scan Error: %s" % e)
			
		return device
	
	def get_bt_info(self, devices):
	
		"""get_bt_info: collect information from known devices"""
	
		logging.info("Get BT Devices Info")

		for mac in devices.keys():
			logging.info(mac)
		
			if not self.checkup(mac):
				devices[mac].set_services([{"name" : None, "uuid": None, "protocol" : None}])
				devices[mac].set_version(None)
				devices[mac].set_manufacturer(None)
				devices[mac].set_ssid(None)
				devices[mac].set_rssi(None)
				devices[mac].set_classes(None)
				continue
		
			time.sleep(1)
			while True:
				try:
					service_info = find_service(address = mac)
					logging.info(service_info)
					break
					
				except Exception as e:
					logging.error("Service discovering error: %s" % e)
							
			info = []
			if len(service_info) == 0:
				devices[mac].set_services([{"name" : None, "uuid": None, "protocol" : None}])
			else:
				for serv in service_info:
					info.append({
								 "name" : serv["name"], 
								 "uuid" : serv["service-classes"], 
								 "protocol" : serv["protocol"]
								 })
				devices[mac].set_services(info)
				
			time.sleep(1)
			
			bt_name_rssi_scan = False
			try:
				device_info = InfoDiscoverer(mac)
				device_info.find_devices(lookup_names = True)
			
				can_read, can_write, has_exc = select([device_info], [], [], 10)
				
				if device_info in can_read:
					device_info.process_event()
					if device_info.cls != 0:
						devices[mac].set_classes(str(device_info.cls))
						devices[mac].set_rssi(str(device_info.rssi))
						devices[mac].set_ssid(str(device_info.dname)[1:])
				else:
					devices[mac].set_classes(None)
					bt_name_rssi_scan = True
									
			except Exception:
				devices[mac].set_classes(None)
				bt_name_rssi_scan = True
				
			time.sleep(1)

			hci_sock = _bt.hci_open_dev()
			hci_fd = hci_sock.fileno()
			
			try:

				bt_sock = BluetoothSocket(L2CAP)
				bt_sock.settimeout(10)
				result = bt_sock.connect_ex((mac, 1))
				handle = get_acl_conn_handle(hci_sock, mac)
				
			except Exception as e:
				logging.error("BT connection error: %s" % e)
				devices[mac].set_version(None)
				devices[mac].set_manufacturer(None)
				if bt_name_rssi_scan:
					devices[mac].set_ssid(None)
					devices[mac].set_rssi(None)
				bt_sock.close()
				hci_sock.close()
				continue
			
			try:
			
				cmd_pkt = struct.pack('H',handle)
				manufacturer = _bt.hci_send_req(
												hci_sock, 
												_bt.OGF_LINK_CTL, 
												_bt.OCF_READ_REMOTE_VERSION, 
												_bt.EVT_READ_REMOTE_VERSION_COMPLETE, 
												_bt.EVT_READ_REMOTE_VERSION_COMPLETE_SIZE, 
												cmd_pkt
												)
				time.sleep(2)
				if bt_name_rssi_scan:
					rssi_code = _bt.hci_send_req(hci_sock, _bt.OGF_STATUS_PARAM, _bt.OCF_READ_RSSI, 2, 4, cmd_pkt)
					time.sleep(2)
					devices[mac].set_ssid(_bt.hci_read_remote_name(hci_sock, mac, 10000))
					devices[mac].set_rssi(struct.unpack('b'*4, rssi_code)[3])
				
				result = struct.unpack('b'*8, manufacturer)
				devices[mac].set_version(self._get_bt_version[str(result[3])])
				devices[mac].set_manufacturer(self._get_manufacturers_name[str(result[4])])
				
			except _bt.error:
				devices[mac].set_version(None)
				devices[mac].set_manufacturer(None)
				if bt_name_rssi_scan:
					devices[mac].set_ssid(None)
					devices[mac].set_rssi(None)
					devices[mac].set_classes(None)

			bt_sock.close()
			hci_sock.close()
			
	def create_bt_json(self, devices):
	
		"""create_bt_json: create json with information about BT classic devices"""
	
		logging.info("Create Classic BT JSON")
	
		data_of_devices = []
		devinfo = []
		
		for mac in devices.keys():
				
			devinfo.append({
							"name": devices[mac].get_ssid(),
							"mac": mac,
							"timestamp": devices[mac].get_time(),
							"standard": devices[mac].get_version(),
							"deviceClass": devices[mac].get_classes(),
							"level": devices[mac].get_rssi(),
							"packages": devices[mac].get_pocket_number(),
							"vendorChip": devices[mac].get_manufacturer(),
							 "services": devices[mac].get_services()
							})
		return devinfo

