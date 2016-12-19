#!/usr/local/bin/tclsh8.6

puts "Adding /usr/local/bigcgi if not exist..."
file mkdir /usr/local/bigcgi
puts "Copying bigcgi_apache.conf to /usr/local/etc/apache24/Includes"
file copy -force bigcgi_apache.conf /usr/local/etc/apache24/Includes/bigcgi_apache.conf


