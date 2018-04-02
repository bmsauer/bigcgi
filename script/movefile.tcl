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
#
#You should have received a copy of the GNU General Public License
#along with bigCGI.  If not, see <http://www.gnu.org/licenses/>.


#this script takes a file stored in temporary space,
#moves it to the users home directory via sudo, and
#changes its permissions

set username [lindex $argv 0]
set progpath [lindex $argv 1]
set newpath  [lindex $argv 2]
set permissions [lindex $argv 3]

file copy -force $progpath $newpath
exec chmod $permissions $newpath
exec chown $username:$username $newpath
