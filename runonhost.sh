#!/bin/sh

# This is a bash script to be run on iptables system.
# Change the variables here accordingly

######### CONFIG #################
# Host-Usb connected interface to BBB
uci= #enx0035ff8db759
# Host-Internet connected interface
ici= #wlp2s0 
######### END CONFIG #################


iptables -I FORWARD -o ${uci} -i ${ici} -m state --state=RELATED,ESTABLISHED -j ACCEPT
iptables -I FORWARD -i ${uci} -o ${ici} -j ACCEPT
iptables -I POSTROUTING -o ${ici} -j MASQUERADE -tnat
sysctl -w net.ipv4.ip_forward=1
