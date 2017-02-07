#!/usr/local/bin/tclsh8.6

proc safe_append {filename line} {
    set file_contents [read [open $filename r]]
    #set idx [string first $line $file_contents]
    if { [string first $line $file_contents] < 0 } {
	set fileout [open $filename a]
	puts $fileout $line
	close $fileout 
    }
}

#---------------------------
# setup rc.conf
#---------------------------
safe_append "/etc/rc.conf" {apache24_enable="yes"}
safe_append "/etc/rc.conf" {mongod_enable="yes"}

#---------------------------
# edit sudoers / setup scripts
#---------------------------
safe_append "/usr/local/etc/sudoers" {bigcgi ALL=(ALL:ALL) NOPASSWD: /usr/home/bigcgi/bigcgi-repo/script/adduser.tcl}
safe_append "/usr/local/etc/sudoers" {bigcgi ALL=(ALL:ALL) NOPASSWD: /usr/home/bigcgi/bigcgi-repo/script/moveprog.tcl}
safe_append "/usr/local/etc/sudoers" {bigcgi ALL=(ALL:ALL) NOPASSWD: /usr/home/bigcgi/bigcgi-repo/script/delprog.tcl}

exec {chmod 700 /usr/home/bigcgi/bigcgi-repo/script/adduser.tcl}
exec {chmod 700 /usr/home/bigcgi/bigcgi-repo/script/moveprog.tcl}
exec {chmod 700 /usr/home/bigcgi/bigcgi-repo/script/delprog.tcl}

exec {chown root:root /usr/home/bigcgi/bigcgi-repo/script/adduser.tcl}
exec {chown root:root /usr/home/bigcgi/bigcgi-repo/script/moveprog.tcl}
exec {chown root:root /usr/home/bigcgi/bigcgi-repo/script/delprog.tcl}

#---------------------------
#  apache config
#---------------------------
#puts "Adding /usr/local/bigcgi if not exist..."
#file mkdir /usr/local/bigcgi
puts "Copying bigcgi_apache.conf to /usr/local/etc/apache24/Includes"
file copy -force bigcgi_apache.conf /usr/local/etc/apache24/Includes/bigcgi_apache.conf
puts "Restarting server..."
exec service apache24 restart

#---------------------------
# mongodb config
#---------------------------
exec python3.5 toolrunner.py setup_auth_db run
file copy -force bigcgi_mongodb.conf /usr/local/etc/mongodb.conf
exec service mongod restart

#---------------------------
# app config
#---------------------------
cd ..
exec python3.5 -m ensurepip
exec pip3 install virtualenv
exec virtualenv -p /usr/local/bin/python3.5 env

