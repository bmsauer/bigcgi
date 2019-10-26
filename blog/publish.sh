#!/bin/bash

#!/usr/local/bin/tclsh8.6

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

#---------------------------------------------------
#--  publish.sh - publish static blog with rsync
#----------------------------------------------------

#SETUP:

# 1) update ~/.ssh/config with:
#        Host hostname
#            User username
#            IdentityFile ~/.ssh/somekey

# 2) add bigcgi_blog.conf to apache config folder:
#    ##virtual hosts
#    <VirtualHost *:80>
#        DocumentRoot /usr/local/www/apache24/data
#    </VirtualHost>
#    <VirtualHost *:80>
#        ServerName blog.bigcgi.com
#        ServerAlias www.blog.bigcgi.com
#        #Header always set Access-Control-Allow-Origin "*"
#        Header always set Access-Control-Allow-Methods "POST, GET, OPTIONS, DELETE, #PUT"
#        Header always set Access-Control-Max-Age "1000"
#        Header always set Access-Control-Allow-Headers "x-requested-with, Content-Type, origin, authorization, accept"
#        #ServerAdmin webmaster@localhost
#        Redirect permanent / https://blog.bigcgi.com/
#    </VirtualHost>
#    <VirtualHost *:443>
#        SSLEngine on
#        SSLCertificateFile      /usr/local/etc/letsencrypt/live/blog.bigcgi.com/cert.pem
#        SSLCertificateKeyFile /usr/local/etc/letsencrypt/live/blog.bigcgi.com/privkey.pem
#        SSLCertificateChainFile /usr/local/etc/letsencrypt/live/blog.bigcgi.com/chain.pem
#        ServerName blog.bigcgi.com
#        ServerAlias www.blog.bigcgi.com
#        DocumentRoot /usr/local/www/apache24/data/bigcgi-blog        
#    </VirtualHost>

# 3) edit env.sh.template, save as env.sh, source to shell
#---------------------------------------------------

rsync -Pav ./dist/ "$BLOG_USERNAME@$BLOG_HOST:$BLOG_DIR"
