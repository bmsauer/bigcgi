#!/usr/local/bin/tclsh8.6

#---------------------------
#  apache config
#---------------------------
#puts "Adding /usr/local/bigcgi if not exist..."
#file mkdir /usr/local/bigcgi
puts "Copying bigcgi_apache.conf to /usr/local/etc/apache24/Includes"
file copy -force bigcgi_apache.conf /usr/local/etc/apache24/Includes/bigcgi_apache.conf
puts "Restarting server..."
exec service apache24 restart

#---------------------------
# mongodb config
#---------------------------


#---------------------------
# app config
#---------------------------
cd ..
exec python3.5 -m ensurepip
exec pip3 install virtualenv
exec virtualenv -p /usr/local/bin/python3.5 env



