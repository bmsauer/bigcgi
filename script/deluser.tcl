#!/usr/bin/env tclsh8.6

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

#You should have received a copy of the GNU General Public License
#along with bigCGI.  If not, see <http://www.gnu.org/licenses/>.


#removes a user and their home directory from the system
#this script should be run as sudo

set username [lindex $argv 0]

if {$tcl_platform(os) == "FreeBSD"} {
    set command [list pw userdel $username -r]
} elseif {$tcl_platform(os) == "Linux"} {
    set command [list userdel -f -r $username]
} else {
    puts "Could not detect os."
    exit 1
}

if { [catch { exec {*}$command } msg ] } {
    puts "Error deleting user: $msg"
    if { [string first spool $msg ] > 0 } {
	#error is about mail spool, ignore
	exit 0
    } else {
	exit 2
    }
}
exit 0
