#!/usr/bin/env tclsh8.6

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

exit 0
