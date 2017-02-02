#!/bin/sh

#provision.sh
#run as root in directory it sits in
#installs packages, kicks off tcl script to handle config

pkg install sudo
pkg install tcl86
pkg install python35
pkg install apache24
pkg install mongodb

chmod +x install.tcl
./install.tcl

