#!/bin/sh

#provision.sh
#run as root in directory it sits in
#installs packages, kicks off tcl script to handle config

pkg
pkg install -y tcl86
pkg install -y python35
pkg install -y apache24
pkg install -y ssmtp

chmod +x install.tcl
./install.tcl

