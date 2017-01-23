#!/usr/bin/env tclsh8.6

#this script takes a file stored in temporary space,
#moves it to the users home directory via sudo, and
#changes its permissions

set username [lindex $argv 0]
set progpath [lindex $argv 1]
set newpath  [lindex $argv 2]

file copy -force $progpath $newpath
exec chmod 711 $newpath
exec chown $username:$username $newpath
