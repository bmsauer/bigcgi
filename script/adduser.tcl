#!/usr/bin/env tclsh8.6

#This file is part of bigCGI.

#bigCGI is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#bigCGI is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with bigCGI.  If not, see <http://www.gnu.org/licenses/>.


#adds a user from command line arguments.
#this script should be run as sudo

set username [lindex $argv 0]

if {$tcl_platform(os) == "FreeBSD"} {
    set command [list pw useradd $username -d /home/$username -m -s /usr/sbin/nologin]
} elseif {$tcl_platform(os) == "Linux"} {
    set command [list useradd -d /home/$username -m -s /bin/false $username]
}  else {
    puts "Could not detect os."
    exit 1
}

if { [catch { exec {*}$command } msg] } {
    puts "Error creating user: $msg"
    exit 2
}
if { [catch { exec mkdir /home/$username/public_html } msg ] } {
    puts "Error adding home directory: $msg"
    exit 2
}
if { [catch { exec chown $username:$username /home/$username/public_html } msg ] } {
    puts "Error changing home dir owner: $msg"
    exit 2
}
if { [catch { exec chmod -R 711 /home/$username } msg ] } {
    puts "Error changing home dir permissions: $msg"
    exit 2
}
if { [catch { exec rctl -a user:$username:maxproc:deny=10/user } msg ] } {
    puts "Error setting process resource limits: $msg"
    exit 2
}
if { [catch { exec rctl -a user:$username:memoryuse:deny=1G/user } msg ] } {
    puts "Error setting memory resource limits: $msg"
    exit 2
}

exit 0
