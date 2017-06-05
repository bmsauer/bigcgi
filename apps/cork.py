import bottle
from cork import Cork, AuthException, AAAException
from cork.backends import MongoDBBackend
from util.request import *
from settings import app_settings
import os

app_settings.get_logger()

cork_app = bottle.Bottle()
cork_app.install(require_csrf)

smtp_url = 'ssl://{}:{}@smtp.gmail.com:465'.format(app_settings.SMTP_USERNAME, app_settings.SMTP_PASSWORD)
cork = Cork(
    backend=MongoDBBackend(db_name='bigcgi-cork',
                           username=app_settings.DATABASE_USERNAME,
                           password=app_settings.DATABASE_PASSWORD,
                           initialize=False),
    email_sender=app_settings.SMTP_USERNAME+"@gmail.com",
    smtp_url=smtp_url,
)

@cork_app.post('/login')
def login():
    #Authenticate users
    username = post_get('username')
    password = post_get('password')
    cork.login(username, password, success_redirect='/?flash=Hello {}.'.format(username), fail_redirect='/?error=Login failure.')

@cork_app.route('/logout')
def logout():
    cork.logout(success_redirect='/?flash=Logout success.')

@cork_app.post('/register')
def register():
    #Send out registration email
    username = post_get('username')
    password = post_get('password')
    email_addr = post_get('email_address')

    status = os.system("sudo script/adduser.tcl " + username)
    if status != 0:
        bottle.abort(500, "Failed to add user")
    cork.register(username, password, email_addr)
    app_settings.logger.info("new user registered", {"actor":username,"action":"registered", "object":"bigcgi"})
    bottle.redirect("/?flash=Confirmation email sent.")

@cork_app.route('/validate_registration/:registration_code')
def validate_registration(registration_code):
    """Validate registration, create user account"""
    cork.validate_registration(registration_code)
    bottle.redirect("/?flash=Thank you for registering.")
    #return 'Thanks. <a href="/">Go to login</a>'

@cork_app.post("/reset-password")
def reset_password():
    """Send out password reset email"""
    try:
        cork.send_password_reset_email(
            username=post_get('username'),
        )
        bottle.redirect("/?flash=Password reset sent.")
    except AAAException as e:
        bottle.redirect("/reset-password?error={}".format(str(e)))
    

@cork_app.get("/reset-password")
def reset_password_view():
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
    cork.reset_password(post_get('reset_code'), post_get('password'))
    bottle.redirect("/?flash=Password successfully reset.")
