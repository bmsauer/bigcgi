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
from beaker.middleware import SessionMiddleware
from cork import AuthException
import requests
import os
import tempfile
import uuid
import time

from settings import app_settings
from db.mongodbo import AppDBOMongo
from util.request import *
from apps.admin import admin_app
from apps.cork import cork_app
from util.auth import get_cork_instance
import util.cgi

app_settings.get_logger()

main_app = bottle.Bottle()
main_app.install(require_csrf)

#----------------------------------------------------
# ERROR PAGES
#----------------------------------------------------

@main_app.error(500)
@main_app.error(404)
@main_app.error(403)
@main_app.error(400)
def error(error):
    cork = get_cork_instance()
    try:
        user = cork.current_user
        actor = user.username
    except AuthException:
        actor = "anonymous"
    obj = str(bottle.request.path) + "?" + str(bottle.request.query_string) 
    app_settings.logger.error("{} - {}".format(error.status, error.body),
                              extra={
                                  "actor":actor,
                                  "action":"errored",
                                  "object":obj
                              })
    return bottle.template("error", {"title":error.status, "message":error.body})
    
#----------------------------------------------------
# STATIC FILES
#----------------------------------------------------
static_app = bottle.Bottle()
@static_app.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root='static/')
        
#----------------------------------------------------
# UI
#---------------------------------------------------- 
@main_app.route("/")
def index():
    cork = get_cork_instance()
    flash = bottle.request.params.flash or None
    error = bottle.request.params.error or None
    try:
        user = cork.current_user
        current_user = user.username
    except AuthException as e:
        current_user = None
    return bottle.template("index",{"current_user":current_user, "flash":flash, "error":error})

@main_app.route("/dashboard")
def dashboard():
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect='/?error=You are not authorized to access this page.')
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    user = cork.current_user
    current_user = user.username
    db = AppDBOMongo(app_settings.get_database())
    apps = db.get_summary(current_user)
    return bottle.template("dashboard",{"title":"Dashboard","current_user":current_user, "apps":apps, "flash":flash, "error":error, "csrf":get_csrf_token()})

@main_app.get("/create-app")
def create_app_view():
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    user = cork.current_user
    current_user = user.username
    return bottle.template("create-app",{"title":"Create App","current_user":current_user, "flash":flash, "error":error, "csrf":get_csrf_token()})

@main_app.get("/upgrade-app/<appname>")
def upgrade_app_view(appname):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    user = cork.current_user
    current_user = user.username
    
    return bottle.template("upgrade-app",{"title":"Upgrade App","current_user":current_user, "flash":flash, "error":error, "appname":appname, "csrf":get_csrf_token()})

@main_app.get("/delete-app/<appname>")
def delete_app_view(appname):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    user = cork.current_user
    current_user = user.username

    return bottle.template("delete-app",{"title":"Delete App", "current_user":current_user, "flash":flash, "error":error, "appname":appname, "csrf":get_csrf_token()})

@main_app.post("/delete-app/<appname>")
def delete_app(appname):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    user = cork.current_user
    current_user = user.username

    app_location = os.path.join(app_settings.CGI_BASE_PATH_TEMPLATE.format(current_user), appname)
    db = AppDBOMongo(app_settings.get_database())
    db.delete(appname, current_user)
    os.system("sudo script/delprog.tcl {}".format(app_location))
    app_settings.logger.info("app deleted", extra={"actor":current_user,"action":"deleted app", "object":appname})
    bottle.redirect("/dashboard?flash={}".format("Successful delete."))

@main_app.post("/secure-app/<appname>/<security_setting:int>")
def secure_app(appname, security_setting):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    user = cork.current_user
    current_user = user.username

    db = AppDBOMongo(app_settings.get_database())
    db.secure_app(current_user, appname, security_setting)
    if security_setting == 1:
        bottle.redirect("/dashboard?flash=Secured app {}.".format(appname))
    else:
        bottle.redirect("/dashboard?flash=Unsecured app {}.".format(appname))
        
@main_app.post("/create-app")
def create_app():
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    user = cork.current_user
    current_user = user.username

    name = bottle.request.forms.get('name')
    if not name:
        bottle.redirect("/dashboard?error={}".format("App must have a name."))
        return
    name = "".join(c for c in name if c.isalnum())
    upload = bottle.request.files.get('upload')
    
    with tempfile.NamedTemporaryFile() as temp_storage:
        final_path = os.path.join(app_settings.CGI_BASE_PATH_TEMPLATE.format(current_user),name)
        save_path = temp_storage.name
        upload.save(save_path, overwrite=True) # appends upload.filename automatically
        status = os.system("sudo script/moveprog.tcl {} {} {}".format(current_user, save_path, final_path))
        
    error=None
    flash="Successfully created app."
    db = AppDBOMongo(app_settings.get_database())
    db.create(name, current_user)
    if error:
        bottle.redirect("/dashboard?error={}".format(error))
    if flash:
        app_settings.logger.info("app created", extra={"actor":current_user,"action":"created app", "object":name})
        bottle.redirect("/dashboard?flash={}".format(flash))
    
    
@main_app.get("/login")
def login_view():
    return bottle.template("login", {"title":"Login", "csrf":get_csrf_token()})

@main_app.get("/docs")
def docs_view():
    return bottle.template("docs", {"title":"Documentation"})

@main_app.get("/development")
def development_view():
    return bottle.template("development", {"title":"Development"})

@main_app.get("/register")
def register_view():
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    return bottle.template("register", {"title":"Register", "csrf":get_csrf_token(), "flash":flash, "error":error})

@main_app.get("/pricing")
def pricing_view():
    return bottle.template("pricing", {"title":"Pricing"})

@main_app.get("/pricing")
def pricing_view():
    return bottle.template("pricing", {"title":"Pricing"})

#----------------------------------------------------
# API
#----------------------------------------------------
@main_app.route("/<username>/run/<appname>", method="OPTIONS")
def bigcgi_run_options(username, appname):
    return bottle.HTTPResponse(status=200, body="", headers=None,
                               Access_Control_Allow_Headers="Origin, Accept, Content-Type, X-Requested-with, X-CSRF-Token, Authorization",
                               Access_Control_Allow_Methods="PUT, GET, POST, DELETE, OPTIONS",
                               Access_Control_Allow_Origin="*",
    )

@main_app.route("/<username>/run/<appname>",method=["GET","POST"], skip=[require_csrf])
def bigcgi_run(username,appname):
    db = AppDBOMongo(app_settings.get_database())
    if db.app_secure(username, appname):
        try:
            creds = parse_basic_auth(bottle.request.headers)
        except AccessDeniedException as e:
            bottle.abort(401, str(e))
        
        if not authorize(username, creds):
            bottle.abort(401, "Authorization failed.")
    else:
        creds = None
    #url = "http://internal.bigcgi.com/~{}/{}".format(username, appname)
    #if bottle.request.method == "GET":
    #    response = requests.get(url, params=dict(bottle.request.query))
    #elif bottle.request.method == "POST":
    #    response = requests.post(url,data=dict(bottle.request.forms)) #TODO: this should be changed to body
    #if response.status_code < 300:
    start_time = time.time()
    output, error, return_value = util.cgi.run_cgi(
        appname,
        username,
        bottle.request.method,
        bottle.request.path,
        bottle.request.query_string,
        bottle.request.remote_addr,
        creds,
        bottle.request.content_type,
        bottle.request.body.read().decode("utf-8"),
        bottle.request.content_length,
        bottle.request.headers
    )
    elapsed = time.time() - start_time    
    
    db.inc_hits(username, appname)
    db.inc_millisecs(username, appname, elapsed*1000)
    headers, output = util.cgi.parse_output(output)
    content_type = headers.get("Content-Type", "text/html")
    access_control_allow_origin = headers.get("Access-Control-Allow-Origin", "*")
    status_code = headers.get("Status", 200)
    return bottle.HTTPResponse(status=status_code, body=output, headers=None,
                               Content_Type=content_type,
                               Access_Control_Allow_Origin=access_control_allow_origin,
    )

main_app.mount("/admin/", admin_app)
main_app.merge(cork_app)
main_app.merge(static_app)
session_opts = {
    'session.cookie_expires': True,
    'session.encrypt_key': app_settings.SECRET_KEY,
    'session.httponly': True,
    'session.timeout': 3600 * 24,  # 1 day
    'session.type': 'cookie',
    'session.validate_key': True,
}
app = SessionMiddleware(main_app, session_opts)


if __name__ == "__main__":
    bottle.run(app=app,host='0.0.0.0', port=8888, debug=True, reloader=True)
