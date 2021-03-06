#!/usr/local/bin/tclsh8.6


#This file is part of bigCGI.
#
#bigCGI is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#bigCGI is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with bigCGI.  If not, see <http://www.gnu.org/licenses/>.


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
# modify DNS
#---------------------------
safe_append "/etc/hosts" {127.0.0.1		internal.bigcgi.com}
safe_append "/etc/hosts" {::1			internal.bigcgi.com}

#---------------------------
# setup rc.conf
#---------------------------
safe_append "/etc/rc.conf" {apache24_enable="yes"}
safe_append "/etc/rc.conf" {mongod_enable="yes"}
safe_append "/etc/rc.conf" {redis_enable="yes"}

#---------------------------
# edit sudoers / setup scripts
#---------------------------
safe_append "/usr/local/etc/sudoers" {bigcgi ALL=(ALL:ALL) NOPASSWD: /home/bigcgi/bigcgi-repo/script/adduser.tcl}
safe_append "/usr/local/etc/sudoers" {bigcgi ALL=(ALL:ALL) NOPASSWD: /home/bigcgi/bigcgi-repo/script/deluser.tcl}
safe_append "/usr/local/etc/sudoers" {bigcgi ALL=(ALL:ALL) NOPASSWD: /home/bigcgi/bigcgi-repo/script/movefile.tcl}
safe_append "/usr/local/etc/sudoers" {bigcgi ALL=(ALL:ALL) NOPASSWD: /home/bigcgi/bigcgi-repo/script/delprog.tcl}
safe_append "/usr/local/etc/sudoers" {bigcgi ALL=(ALL:ALL) NOPASSWD: /home/bigcgi/bigcgi-repo/script/runcgi.py}


exec chmod 700 /home/bigcgi/bigcgi-repo/script/adduser.tcl
exec chmod 700 /home/bigcgi/bigcgi-repo/script/deluser.tcl
exec chmod 700 /home/bigcgi/bigcgi-repo/script/movefile.tcl
exec chmod 700 /home/bigcgi/bigcgi-repo/script/delprog.tcl
exec chmod 700 /home/bigcgi/bigcgi-repo/script/runcgi.py

exec chown root:wheel /home/bigcgi/bigcgi-repo/script/adduser.tcl
exec chown root:wheel /home/bigcgi/bigcgi-repo/script/deluser.tcl
exec chown root:wheel /home/bigcgi/bigcgi-repo/script/movefile.tcl
exec chown root:wheel /home/bigcgi/bigcgi-repo/script/delprog.tcl
exec chown root:wheel /home/bigcgi/bigcgi-repo/script/runcgi.py

#---------------------------
#  make log dir
#---------------------------
if { ![file exists /home/bigcgi/bigcgi-repo/logs] } {
    exec mkdir /home/bigcgi/bigcgi-repo/logs
} else {
    puts "Logs directory already exists."
}

#---------------------------
#  make tmp dir
#---------------------------
if {! [file exists /tmp/bigcgi] } {
    exec mkdir /tmp/bigcgi
} else {
    puts "Tmp dirctory already exists."
}

#---------------------------
#  lock down directories
#---------------------------
exec chown -R bigcgi:bigcgi /home/bigcgi/bigcgi-repo
exec chmod -R 700 /home/bigcgi/bigcgi-repo
exec chown -R bigcgi:bigcgi /tmp/bigcgi
exec chmod -R 700 /tmp/bigcgi

#---------------------------
#  apache config
#---------------------------
puts "Copying bigcgi_apache.conf to /usr/local/etc/apache24/Includes"
file copy -force /home/bigcgi/bigcgi-repo/serversetup/bigcgi_apache.conf /usr/local/etc/apache24/Includes/bigcgi_apache.conf
puts "Restarting server..."
if { [catch  { exec service apache24 restart } msg ] } {
  puts "Output from apache restart: $::errorInfo"
}

#---------------------------
# mongodb config
#---------------------------
puts "Initializing auth db..."
exec service mongod start
exec python3.5 /home/bigcgi/bigcgi-repo/toolrunner.py setup_auth_db run ;# do this first, while auth is off
puts "Moving mongodb config..."
file copy -force /home/bigcgi/bigcgi-repo/serversetup/bigcgi_mongodb.conf /usr/local/etc/mongodb.conf
puts "Restarting mongod..."
exec service mongod restart

