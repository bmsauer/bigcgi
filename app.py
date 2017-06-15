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

from settings import app_settings
from db.mongodbo import AppDBOMongo
from util.request import *
from apps.admin import admin_app
from apps.cork import cork_app, get_cork_instance

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
@main_app.route('/static/<filepath:path>')
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
    db = AppDBOMongo()
    apps = db.get_summary(current_user)
    db.close()
    return bottle.template("dashboard",{"title":"Dashboard","current_user":current_user, "apps":apps, "flash":flash, "error":error})

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
    db = AppDBOMongo()
    db.delete(appname, current_user)
    db.close()
    os.system("sudo script/delprog.tcl {}".format(app_location))
    app_settings.logger.info("app deleted", extra={"actor":current_user,"action":"deleted app", "object":appname})
    bottle.redirect("/dashboard?flash={}".format("Successful delete."))

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
    db = AppDBOMongo()
    db.create(name, current_user)
    db.close()
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
    return bottle.template("register", {"title":"Register", "csrf":get_csrf_token()})

@main_app.get("/pricing")
def pricing_view():
    return bottle.template("pricing", {"title":"Pricing"})

@main_app.get("/pricing")
def pricing_view():
    return bottle.template("pricing", {"title":"Pricing"})

#----------------------------------------------------
# API
#----------------------------------------------------

@main_app.route("/<username>/run/<appname>",method=["GET","POST"], skip=[require_csrf])
def bigcgi_run(username,appname):
    #try:
    #    creds = parse_basic_auth(bottle.request.headers)
    #except AccessDeniedException as e:
    #    bottle.abort(401, strn(e))
        
    #if not authorize(creds):
    #    bottle.abort(401, "Authorization failed.")
    #else:
    url = "http://internal.bigcgi.com/~{}/{}".format(username, appname)
    if bottle.request.method == "GET":
        response = requests.get(url, params=dict(bottle.request.query))
    elif bottle.request.method == "POST":
        response = requests.post(url,data=dict(bottle.request.forms))
    if response.status_code < 300:
        db = AppDBOMongo()
        db.inc_hits(username, appname)
        db.inc_millisecs(username, appname, response.elapsed.total_seconds()*1000)
        db.close()
    return bottle.HTTPResponse(status=response.status_code, body=response.text)

main_app.mount("/admin/", admin_app)
main_app.merge(cork_app)
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
