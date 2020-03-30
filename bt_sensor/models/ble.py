#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class BLE:

	def __init__(self):
		
		self.__ble_services = None
		self.__ble_rssi = None
		self.__ble_ssid = None
		self.__ble_pocket_number = 0
		self.__ble_time = None
		
	def set_ble_service(self, serv):
		self.__services = serv
	
	def get_ble_services(self):
		return self.__ble_services
		
	def set_ble_rssi(self, rssi):
		self.__ble_rssi = rssi
		
	def get_ble_rssi(self):
		return self.__ble_rssi
		
	def set_ble_ssid(self, ssid):
		self.__ble_ssid = ssid
		
	def get_ble_ssid(self):
		return self.__ble_ssid
		
	def set_ble_pocket_number(self, pocket_number):
		self.__ble_pocket_number += 1
		
	def get_ble_pocket_number(self):
		return self.__ble_pocket_number
		
	def set_ble_time(self, time):
		self.__ble_time = time
		
	def get_ble_time(self):
		return self.__ble_time
