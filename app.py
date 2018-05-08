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
import requests
import os
import tempfile
import uuid
import time

from settings import app_settings
from db.mongodbo import AppDBOMongo, FileDBOMongo
from util.request import *
from apps.admin import admin_app
from apps.cork import cork_app
from util.auth import get_cork_instance
import util.cgi
from tasks.tasks import sync_file, delete_file

app_settings.get_logger()

main_app = bottle.Bottle()
main_app.install(require_csrf)

#----------------------------------------------------
# ERROR PAGES
#----------------------------------------------------

@main_app.error(500)
@main_app.error(405)
@main_app.error(404)
@main_app.error(403)
@main_app.error(400)
def error(error):
    cork = get_cork_instance()
    current_user = get_current_user(cork)
    obj = str(bottle.request.path) + "?" + str(bottle.request.query_string) 
    app_settings.logger.error("{} - {}".format(error.status, error.body),
                              extra={
                                  "actor":current_user if current_user else "anonymous",
                                  "action":"errored",
                                  "object":obj
                              })
    return bottle.template("error", {"title":error.status, "message":error.body, "current_user": current_user})
    
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
    flash, error = set_flash_and_error()
    current_user = get_current_user(cork)
    return bottle.template("index",{"current_user":current_user, "flash":flash, "error":error})

@main_app.route("/dashboard")
def dashboard():
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect='/?error=You are not authorized to access this page.')
    flash, error = set_flash_and_error()
    current_user = get_current_user(cork)
    db = AppDBOMongo(app_settings.get_database())
    apps = db.get_summary(current_user)
    file_db = FileDBOMongo(app_settings.get_database())
    files = file_db.get_user_files(current_user)
    return bottle.template("dashboard",{"title":"Dashboard","current_user":current_user, "apps":apps, "files": files, "flash":flash, "error":error, "csrf":get_csrf_token()})

@main_app.get("/create-app")
def create_app_view():
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    flash, error = set_flash_and_error()
    current_user = get_current_user(cork)
    return bottle.template("create-app",{"title":"Create App","current_user":current_user, "flash":flash, "error":error, "csrf":get_csrf_token()})

@main_app.get("/upgrade-app/<appname>")
def upgrade_app_view(appname):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    flash, error = set_flash_and_error()
    current_user = get_current_user(cork)
    return bottle.template("upgrade-app",{"title":"Upgrade App","current_user":current_user, "flash":flash, "error":error, "appname":appname, "csrf":get_csrf_token()})

@main_app.get("/delete-app/<appname>")
def delete_app_view(appname):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    flash, error = set_flash_and_error()
    current_user = get_current_user(cork)
    return bottle.template("delete-app",{"title":"Delete App", "current_user":current_user, "flash":flash, "error":error, "appname":appname, "csrf":get_csrf_token()})

@main_app.get("/create-file")
def create_file_view():
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    flash, error = set_flash_and_error()
    current_user = get_current_user(cork)
    return bottle.template("create-file",{"title": "Create File", "current_user":current_user, "flash": flash, "error":error, "csrf": get_csrf_token()})

@main_app.post("/delete-app/<appname>")
def delete_app(appname):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    current_user = get_current_user(cork)

    db = AppDBOMongo(app_settings.get_database())
    success = db.delete(appname, current_user)
    if not success:
        error = "Failed to delete app."
        app_settings.logger.error("error deleteing app", extra={
            "actor": current_user, "action": "delete app", "object": appname})
        bottle.redirect("/dashboard?error={}".format(error))
    else:
        for xx in range(0, int(app_settings.BIGCGI_TOTAL_INSTANCES)):
            delete_file.apply_async(args=[current_user, appname, "app"], kwargs={}, queue='bigcgi_instance_' + str(xx))
        app_settings.logger.info("app deleted", extra={
            "actor": current_user, "action": "delete app", "object": appname})
        bottle.redirect("/dashboard?flash={}".format("Successful delete."))

@main_app.post("/delete-file/<filename>")
def del_file(filename):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    current_user = get_current_user(cork)

    db = FileDBOMongo(app_settings.get_database())
    success = db.delete_file(filename, current_user, "file")
    if not success:
        error = "Failed to delete file."
        app_settings.logger.error("error deleteing file", extra={
            "actor": current_user, "action": "delete file", "object": filename})
        bottle.redirect("/dashboard?error={}".format(error))
    else:
        for xx in range(0, int(app_settings.BIGCGI_TOTAL_INSTANCES)):
            delete_file.apply_async(args=[current_user, filename, "file"], kwargs={}, queue='bigcgi_instance_' + str(xx))
        app_settings.logger.info("file deleted", extra={
            "actor": current_user, "action": "delete file", "object": filename})
        bottle.redirect("/dashboard?flash={}".format("Successful delete."))
        
@main_app.post("/secure-app/<appname>/<security_setting:int>")
def secure_app(appname, security_setting):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    current_user = get_current_user(cork)

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
    current_user = get_current_user(cork)

    name = bottle.request.forms.get('name')
    if not name:
        bottle.redirect("/dashboard?error={}".format("App must have a name."))
        return
    if "/" in name or ".." in name:
        error="Invalid app name: cannot contain .. or /"
        bottle.redirect("/dashboard?error={}".format(error))
        
    upload = bottle.request.files.get('upload')
    if upload.content_length > 1000000: #cap uploads to 1Mb
        error = "Failed to upload app: exceeded maximum of 1Mb"
        app_settings.logger.info("user attempted large upload", extra={
            "actor":current_user,"action":"created file", "object":name})
        bottle.redirect("/dashboard?error={}".format(error))
    db = FileDBOMongo(app_settings.get_database())
    success = db.add_file(upload.file.read(), name, current_user, "app")
    if not success:
        error = "Failed to upload app."
        app_settings.logger.error("error uploading app", extra={
            "actor":current_user,"action":"created app", "object":name})
        bottle.redirect("/dashboard?error={}".format(error))
    else:
        for xx in range(0, int(app_settings.BIGCGI_TOTAL_INSTANCES)):
            sync_file.apply_async(args=[name, current_user, "app"], kwargs={}, queue='bigcgi_instance_' + str(xx))
        flash = "Successfully uploaded app."
        db = AppDBOMongo(app_settings.get_database())
        db.create(name, current_user)
        app_settings.logger.info("file created", extra={
            "actor":current_user,"action":"created app", "object":name})
        bottle.redirect("/dashboard?flash={}".format(flash))

@main_app.post("/create-file")
def create_file():
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    current_user = get_current_user(cork)

    name = bottle.request.forms.get('name')
    if not name:
        bottle.redirect("/dashboard?error={}".format("File must have a name."))
        return
    if "/" in name or ".." in name:
        error="Invalid file name: cannot contain .. or /"
        bottle.redirect("/dashboard?error={}".format(error))

    upload = bottle.request.files.get('upload')
    if upload.content_length > 1000000: #cap uploads to 1Mb
        error = "Failed to upload file: exceeded maximum of 1Mb"
        app_settings.logger.info("user attempted large upload", extra={
            "actor":current_user,"action":"created file", "object":name})
        bottle.redirect("/dashboard?error={}".format(error))
        
    db = FileDBOMongo(app_settings.get_database())
    success = db.add_file(upload.file.read(), name, current_user, "file")
    if not success:
        error = "Failed to upload file."
        app_settings.logger.error("error uploading file", extra={
            "actor":current_user,"action":"created file", "object":name})
        bottle.redirect("/dashboard?error={}".format(error))
    else:
        for xx in range(0, int(app_settings.BIGCGI_TOTAL_INSTANCES)):
            sync_file.apply_async(args=[name, current_user, "file"], kwargs={}, queue='bigcgi_instance_' + str(xx))
        flash = "Successfully uploaded file."
        app_settings.logger.info("file created", extra={
            "actor":current_user,"action":"created file", "object":name})
        bottle.redirect("/dashboard?flash={}".format(flash))
    

@main_app.get("/logs/<appname>")
def get_app_logs(appname):
    cork = get_cork_instance()
    cork.require(role="user", fail_redirect="/?error=You are not authorized to access this page.")
    current_user = get_current_user(cork)

    db = AppDBOMongo(app_settings.get_database())
    logs = db.get_app_logs(current_user, appname)
    return bottle.template("app-logs", {"title":"Logs for " + appname,"current_user":current_user, "logs":logs})
    
@main_app.get("/login")
def login_view():
    cork = get_cork_instance()
    current_user = get_current_user(cork)
    return bottle.template("login", {"title":"Login", "csrf":get_csrf_token(), "current_user": current_user})

@main_app.get("/docs")
def docs_view():
    cork = get_cork_instance()
    current_user = get_current_user(cork)
    return bottle.template("docs", {"title":"Documentation", "current_user": current_user})

@main_app.get("/development")
def development_view():
    cork = get_cork_instance()
    current_user = get_current_user(cork)
    return bottle.template("development", {"title":"Development", "current_user": current_user})

@main_app.get("/register")
def register_view():
    cork = get_cork_instance()
    flash, error = set_flash_and_error()
    current_user = get_current_user(cork)
    return bottle.template("register", {"title":"Register", "csrf":get_csrf_token(), "flash":flash, "error":error, "current_user": current_user})

@main_app.get("/pricing")
def pricing_view():
    cork = get_cork_instance()
    current_user = get_current_user(cork)
    return bottle.template("pricing", {"title":"Pricing", "current_user": current_user})

@main_app.get("/pricing")
def pricing_view():
    cork = get_cork_instance()
    current_user = get_current_user(cork)
    return bottle.template("pricing", {"title":"Pricing", "current_user": current_user})

@main_app.get("/terms")
def terms_view():
    cork = get_cork_instance()
    current_user = get_current_user(cork)
    with open("TERMS", "r") as terms_file:
        terms = terms_file.read()
    return bottle.template("terms", {"title": "Terms of Service", "terms":terms, "current_user": current_user})

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

@main_app.route("/<username>/run/<appname>",method=["GET","POST","PUT","DELETE"], skip=[require_csrf])
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
    if return_value == 1:
        output = bottle.template("app-error", {"output":output, "error": error})
        headers = {"Status": 500}
    else:
        headers, output = util.cgi.parse_output(output)
        
    error_logs = error.split("\n")
    error_logs = [e for e in error_logs if e]
    if error_logs:
        db.app_log(username, appname, error_logs)
        
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
