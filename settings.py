import os

class AppSettings(object):
    SECRET_KEY = os.environ["BIGCGI_SECRET_KEY"]
    ADMIN_PASSWORD = os.environ["BIGCGI_ADMIN_PASSWORD"]
    
app_settings = AppSettings()
