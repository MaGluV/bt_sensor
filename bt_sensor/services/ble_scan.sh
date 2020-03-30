#!/usr/bin/env sh
echo "Start scan"
rm -f uber_info
sudo ubertooth-btle -f -c crack.pcap > uber_info &
sleep 60
sudo kill -STOP $!
sleep 5
sudo kill -INT $!
sleep 5
sudo kill -CONT $!
echo 'Done'
sleep 5
sudo kill -kill `ps -aux | grep ubertooth-btle | awk '{print $2}'`
sleep 2
