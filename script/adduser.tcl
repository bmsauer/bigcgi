#adds a user from command line arguments.
#this script should be run as sudo

set username [lindex $argv 0]

if {$tcl_platform(os) == "FreeBSD"} {
    set command [list pw useradd $username -d /nonexistent -s /usr/sbin/nologin]
} elseif {$tcl_platform(os) == "Linux"} {
    set command [list useradd -M -s /bin/false $username]
}  else {
    puts "Could not detect os."
    exit 1
}

if { [catch { exec {*}$command } msg] } {
    puts "Error creating user: $msg"
    exit 2
}

exit 0
