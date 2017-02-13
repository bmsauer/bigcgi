#!/usr/bin/env tclsh8.6

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
