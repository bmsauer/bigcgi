import bottle
from beaker.middleware import SessionMiddleware
from cork import Cork, AuthException
from cork.backends import MongoDBBackend
import requests
import base64
import os

from settings import app_settings

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

app = bottle.Bottle()
    
#----------------------------------------------------
# CORK
#----------------------------------------------------
smtp_url = 'ssl://{}:{}@smtp.gmail.com:465'.format(app_settings.SMTP_USERNAME, app_settings.SMTP_PASSWORD)
cork = Cork(
    backend=MongoDBBackend(db_name='bigcgi-cork', initialize=False),
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
    cork.register(username, password, email_addr)

    status = os.system("sudo script/adduser.tcl " + username)
    if status != 0:
        bottle.abort(500, "Failed to add user")
    bottle.redirect("/?flash=Confirmation email sent.")
    #return 'Please check your mailbox.'

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

@app.get("/login")
def login_view():
    return bottle.template("login", {"title":"Login"})

@app.get("/register")
def register_view():
    return bottle.template("register", {"title":"Register"})

#----------------------------------------------------
# API
#----------------------------------------------------

@app.route("/<username>/run/<appname>",method=["GET","POST"])
def bigcgi_run(username,appname):
    try:
        creds = parse_basic_auth(bottle.request.headers)
    except AccessDeniedException as e:
        #bottle.abort(401, str(e))
        creds = ("brian","brian")
        
    if not authorize(creds):
        bottle.abort(401, "Authorization failed.")
    else:
        url = "http://localhost/~{}/{}".format(creds[0], appname)
        if bottle.request.method == "GET":
            response = requests.get(url, params=dict(bottle.request.query))
        elif bottle.request.method == "POST":
            response = requests.post(url,data=dict(bottle.request.forms))
        return response.text
        
if __name__ == "__main__":
    app = SessionMiddleware(app, session_opts)
    bottle.run(app=app,host='localhost', port=8888, debug=True, reloader=True)
