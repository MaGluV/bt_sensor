#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bluetooth import *

class InfoDiscoverer(DeviceDiscoverer):

	"""Class InfoDiscoverer get rssi, name and class of discoverable devices"""

	def __init__(self,mac):
		self.mac = mac
		DeviceDiscoverer.__init__(self)
		self.adr = ''
		self.cls = 0
		self.rssi = 0
		self.dname = ''

	def pre_inquiry(self):
		self.done = False

	def device_discovered(self,address,device_class,rssi,name):
		self.adr = str(address)
		self.cls = hex(device_class)
		self.rssi = rssi
		self.dname = name
		if self.mac == str(address):
			self.done = True

