#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class BT_Classic:
	
	def __init__(self):
		self.__services = None
		self.__class = None
		self.__rssi = None
		self.__ssid = None
		self.__manufacturer = None
		self.__version = None
		self.__pocket_number = 0
		self.__time = None
		
	def set_services(self, serv):
		self.__services = serv
	
	def get_services(self):
		return self.__services
		
	def set_class(self, cls):
		self.__class = cls
		
	def get_class(self):
		return self.__class
		
	def set_rssi(self, rssi):
		self.__rssi = rssi
		
	def get_rssi(self):
		return self.__rssi
		
	def set_ssid(self, ssid):
		self.__ssid = ssid
		
	def get_ssid(self):
		return self.__ssid
		
	def set_manufacturer(self, manufacturer):
		self.__manufacturer = manufacturer
		
	def get_manufacturer(self):
		return self.__manufacturer
		
	def set_version(self, version):
		self.__version = version
		
	def get_version(self):
		return self.__version
		
	def set_pocket_number(self):
		self.__pocket_number += 1
		
	def get_pocket_number(self):
		return self.__pocket_number
		
	def set_time(self, time):
		self.__time = time
		
	def get_time(self):
		return self.__time


