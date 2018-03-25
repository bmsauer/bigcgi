pkg install -y git bash sudo tcl86 python35 mongodb redis py27-supervisor apache24
pkg install -y tcllib tdbc
pw useradd bigcgi -d /home/bigcgi -m -s /usr/local/bin/bash
python3.5 -m ensurepip
pip3 install -r /home/bigcgi/bigcgi-repo/requirements.txt
. /home/bigcgi/bigcgi-repo/env.sh
tclsh8.6 /home/bigcgi/bigcgi-repo/serversetup/install.tcl


