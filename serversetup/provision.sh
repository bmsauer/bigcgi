#!/bin/sh
pkg install -y git bash sudo tcl86 python35 mongodb redis py27-supervisor apache24 wget unzip
pkg install -y tcllib tdbc
pw useradd bigcgi -d /home/bigcgi -m -s /usr/local/bin/bash
python3.5 -m ensurepip
#install cork from github repo
wget https://github.com/FedericoCeratto/bottle-cork/archive/master.zip
unzip master.zip
cd bottle-cork-master
python3.5 setup.py install
cd ..
rm -rf bottle-cork-master master.zip
pip3 install -r /home/bigcgi/bigcgi-repo/requirements.txt
. /home/bigcgi/bigcgi-repo/env.sh
tclsh8.6 /home/bigcgi/bigcgi-repo/serversetup/install.tcl


