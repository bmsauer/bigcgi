pkg install -y git bash sudo tcl86 python35 mongodb rabbitmq py27-supervisor
pkg install -y tcllib tdbc
pkg install -y /home/bigcgi/bigcgi-repo/serversetup/apache24-2.4.26-suexec.txz
python3.5 -m ensurepip
pip3 install -r /home/bigcgi/bigcgi-repo/requirements.txt
pw useradd bigcgi -d /home/bigcgi -m -s /usr/local/bin/bash
. /home/bigcgi/bigcgi-repo/env.sh
tclsh8.6 /home/bigcgi/bigcgi-repo/serversetup/install.tcl


