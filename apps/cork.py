"""
This file is part of bigCGI.

bigCGI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

bigCGI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with bigCGI.  If not, see <http://www.gnu.org/licenses/>.
"""

import bottle
from cork import Cork, AuthException, AAAException
from cork.backends import MongoDBBackend
from util.request import *
from settings import app_settings
import os
import subprocess

from util.auth import get_cork_instance
from util.email import send_gmail

app_settings.get_logger()

cork_app = bottle.Bottle()
cork_app.install(require_csrf)

@cork_app.post('/login')
def login():
    #Authenticate users
    cork = get_cork_instance()
    username = post_get('username')
    password = post_get('password')
    cork.login(username, password, success_redirect='/?flash=Hello {}.'.format(username), fail_redirect='/?error=Login failure.')

@cork_app.route('/logout')
def logout():
    cork = get_cork_instance()
    cork.logout(success_redirect='/?flash=Logout success.')

@cork_app.post('/register')
def register():
    #Send out registration email
    cork = get_cork_instance()
    username = post_get('username')
    password = post_get('password')
    email_addr = post_get('email_address')
    cork.register(username, password, email_addr)
    app_settings.logger.info("new user registered", {"actor":username,"action":"registered", "object":"bigcgi"})
    send_gmail("New bigCGI User!", "U: " + username + " E: " + email_addr, "bigcgi.app@gmail.com", "bigcgi.app@gmail.com")
    bottle.redirect("/?flash=Confirmation email sent.")

@cork_app.route('/validate_registration/:registration_code')
def validate_registration(registration_code):
    """Validate registration, create user account"""
    cork = get_cork_instance()
    try:
        username = cork._store.pending_registrations[registration_code]["username"]
    except:
        #valideate_registration will handle
        pass
    cork.validate_registration(registration_code)
    
    process = subprocess.run(["sudo", "script/adduser.tcl", username], stdout=subprocess.PIPE)
    status = process.returncode
    stdout = process.stdout.decode("utf-8")
    if status != 0 or "error" in stdout.lower():
        cork.user(username).delete() #clean up cork user
        app_settings.logger.error("failed to add user from script.", {"actor": username, "action":"error", "object":"register"})
        bottle.abort(500, "Failed to add user: {}".format(stdout))
        
    bottle.redirect("/?flash=Thank you for registering.")
    #return 'Thanks. <a href="/">Go to login</a>'

@cork_app.post("/reset-password")
def reset_password():
    """Send out password reset email"""
    cork = get_cork_instance()
    try:
        cork.send_password_reset_email(
            username=post_get('username'),
        )
        bottle.redirect("/?flash=Password reset sent.")
    except AAAException as e:
        bottle.redirect("/reset-password?error={}".format(str(e)))
    

@cork_app.get("/reset-password")
def reset_password_view():
    cork = get_cork_instance()
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    try:
        user = cork.current_user
        current_user = user.username
    except AuthException as e:
        current_user = None
    return bottle.template("cork/reset_password",{"title":"Reset Password","current_user":current_user, "csrf":get_csrf_token(), "flash":flash, "error":error })

@cork_app.get("/change-password/<reset_code>")
def change_password_view(reset_code):
    return bottle.template("cork/change_password",{"title":"Change Password","current_user":None, "csrf":get_csrf_token(), "reset_code":reset_code})

@cork_app.post("/change-password")
def change_password():
    cork = get_cork_instance()
    cork.reset_password(post_get('reset_code'), post_get('password'))
    bottle.redirect("/?flash=Password successfully reset.")
