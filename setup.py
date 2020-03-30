#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup
from shutil import copy
from subprocess import Popen,PIPE

setup(
    name='bt_sensor',
    version="0.0.1",
    description="Program for scanning BT Classis and BLE devices",
    author="some_people",
    author_email="sh345sqrt@gmail.com",
    maintainer='Some_People',
    maintainer_email='some.people@somemail.com',
    url="https://MaximGlushkov93@bitbucket.org/polovincev/sensor-bluetooth-j2.git",
    packages=['bt_sensor', 'bt_sensor/models', 'bt_sensor/services'],
    package_data={'': ['*.sh'],},
)

copy('bt_sensor/bt_sensor_init.py', '/usr/bin')
ps = Popen('chmod -u=rwx /usr/bin/bt_sensor_init.py', stdout=PIPE, stderr=PIPE, shell=True)
ps.communicate()
ps = Popen('rm /etc/bt_sensor/BT.conf || mkdir /etc/bt_sensor || cp bt_sensor/BT.conf /etc/bt_sensor', stdout=PIPE, stderr=PIPE, shell=True)
ps.communicate()
