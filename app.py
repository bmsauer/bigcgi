import bottle
from beaker.middleware import SessionMiddleware
from cork import Cork, AuthException
from cork.backends import MongoDBBackend
import requests
import base64
import os
import tempfile
import uuid

from settings import app_settings
from db import AppDBOMongo
#----------------------------------------------------
# MISC
#----------------------------------------------------

class AccessDeniedException(Exception):
    pass

def authorize(creds):
    return True

def parse_basic_auth(headers):
    if not "Authorization" in headers:
        raise AccessDeniedException("No Authorization header.")
    else:
        try:
            plain = request.headers["Authorization"][6:] #strip off Basic_
            bytes_creds= base64.b64decode(plain)
            creds = tuple(bytes_creds.decode().split(":"))
            return creds
        except IndexError as e:
            raise AccessDeniedException("Basic auth was malformed.")
        except Exception as e:
            raise AccessDeniedException("Unknown error occured parsing basic auth.")

def generate_csrf_token():
    return str(uuid.uuid4())

def get_csrf_token():
    session = bottle.request.environ.get('beaker.session')
    return session['csrf']
        
def require_csrf(callback):
    def wrapper(*args, **kwargs):
        session = bottle.request.environ.get('beaker.session')
        if bottle.request.method == 'POST':
            csrf = bottle.request.forms.get('csrf')
            if not csrf or csrf != session.get('csrf'):
                bottle.abort(400, "Failed csrf validation.")
        session['csrf'] = generate_csrf_token()
        session.save()
        body = callback(*args, **kwargs)
        return body
    return wrapper

app = bottle.Bottle()
app.install(require_csrf)
    
#----------------------------------------------------
# CORK
#----------------------------------------------------
smtp_url = 'ssl://{}:{}@smtp.gmail.com:465'.format(app_settings.SMTP_USERNAME, app_settings.SMTP_PASSWORD)
cork = Cork(
    backend=MongoDBBackend(db_name='bigcgi-cork',
                           username=app_settings.DATABASE_USERNAME,
                           password=app_settings.DATABASE_PASSWORD,
                           initialize=False),
    email_sender="brianmsauer@gmail.com",
    smtp_url=smtp_url,
)

session_opts = {
    'session.cookie_expires': True,
    'session.encrypt_key': app_settings.SECRET_KEY,
    'session.httponly': True,
    'session.timeout': 3600 * 24,  # 1 day
    'session.type': 'cookie',
    'session.validate_key': True,
}


def postd():
    return bottle.request.forms

def post_get(name, default=''):
    return bottle.request.POST.get(name, default).strip()

@app.post('/login')
def login():
    #Authenticate users
    username = post_get('username')
    password = post_get('password')
    cork.login(username, password, success_redirect='/?flash=Hello {}.'.format(username), fail_redirect='/?error=Login failure.')

@app.route('/logout')
def logout():
    cork.logout(success_redirect='/?flash=Logout success.')

@app.post('/register')
def register():
    #Send out registration email
    username = post_get('username')
    password = post_get('password')
    email_addr = post_get('email_address')

    status = os.system("sudo script/adduser.tcl " + username)
    if status != 0:
        bottle.abort(500, "Failed to add user")
    cork.register(username, password, email_addr)
    bottle.redirect("/?flash=Confirmation email sent.")

@app.route('/validate_registration/:registration_code')
def validate_registration(registration_code):
    """Validate registration, create user account"""
    cork.validate_registration(registration_code)
    bottle.redirect("/?flash=Thank you for registering.")
    #return 'Thanks. <a href="/">Go to login</a>'

#----------------------------------------------------
# STATIC FILES
#----------------------------------------------------
@app.route('/static/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root='static/')
        
#----------------------------------------------------
# UI
#---------------------------------------------------- 
@app.route("/")
def index():
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    try:
        user = cork.current_user
        current_user = user.username
    except AuthException as e:
        current_user = None
    return bottle.template("index",{"current_user":current_user, "flash":flash, "error":error})

@app.route("/dashboard")
def dashboard():
    cork.require(fail_redirect='/?error=You are not authorized to access this page.')
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    user = cork.current_user
    current_user = user.username
    db = AppDBOMongo()
    apps = db.get_all(current_user)
    db.close()
    return bottle.template("dashboard",{"title":"Dashboard","current_user":current_user, "apps":apps, "flash":flash, "error":error})

@app.get("/create-app")
def create_app_view():
    cork.require(fail_redirect="/?error=You are not authorized to access this page.")
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    user = cork.current_user
    current_user = user.username

    return bottle.template("create-app",{"title":"Create App","current_user":current_user, "flash":flash, "error":error, "csrf":get_csrf_token()})

@app.get("/upgrade-app/<appname>")
def upgrade_app_view(appname):
    cork.require(fail_redirect="/?error=You are not authorized to access this page.")
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    user = cork.current_user
    current_user = user.username

    return bottle.template("upgrade-app",{"title":"Upgrade App","current_user":current_user, "flash":flash, "error":error, "appname":appname, "csrf":get_csrf_token()})

@app.get("/delete-app/<appname>")
def delete_app_view(appname):
    cork.require(fail_redirect="/?error=You are not authorized to access this page.")
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    user = cork.current_user
    current_user = user.username

    return bottle.template("delete-app",{"title":"Delete App", "current_user":current_user, "flash":flash, "error":error, "appname":appname, "csrf":get_csrf_token()})

@app.post("/delete-app/<appname>")
def delete_app(appname):
    cork.require(fail_redirect="/?error=You are not authorized to access this page.")
    user = cork.current_user
    current_user = user.username

    app_location = os.path.join(app_settings.CGI_BASE_PATH_TEMPLATE.format(current_user), appname)
    db = AppDBOMongo()
    db.delete(appname, current_user)
    db.close()
    os.system("sudo script/delprog.tcl {}".format(app_location))

    bottle.redirect("/dashboard?flash={}".format("Successful delete."))

@app.post("/create-app")
def create_app():
    cork.require(fail_redirect="/?error=You are not authorized to access this page.")
    user = cork.current_user
    current_user = user.username

    name = bottle.request.forms.get('name')
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
        bottle.redirect("/dashboard?flash={}".format(flash))
    
    
@app.get("/login")
def login_view():
    return bottle.template("login", {"title":"Login", "csrf":get_csrf_token()})

@app.get("/register")
def register_view():
    return bottle.template("register", {"title":"Register", "csrf":get_csrf_token()})

#----------------------------------------------------
# API
#----------------------------------------------------

@app.route("/<username>/run/<appname>",method=["GET","POST"])
def bigcgi_run(username,appname):
    #try:
    #    creds = parse_basic_auth(bottle.request.headers)
    #except AccessDeniedException as e:
    #    bottle.abort(401, str(e))
        
    #if not authorize(creds):
    #    bottle.abort(401, "Authorization failed.")
    #else:
    url = "http://internal.bigcgi.com/~{}/{}".format(username, appname)
    if bottle.request.method == "GET":
        response = requests.get(url, params=dict(bottle.request.query))
    elif bottle.request.method == "POST":
        response = requests.post(url,data=dict(bottle.request.forms))
    db = AppDBOMongo()
    db.inc_hits(username, appname)
    db.inc_millisecs(username, appname, response.elapsed.total_seconds()/1000)
    db.close()
    return response.text
    
app = SessionMiddleware(app, session_opts)    
if __name__ == "__main__":
    bottle.run(app=app,host='0.0.0.0', port=8888, debug=True, reloader=True)
