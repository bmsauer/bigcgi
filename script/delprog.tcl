#!/usr/bin/env tclsh8.6

#this script removes an app file

set filepath [lindex $argv 0]
exec rm $filepath
