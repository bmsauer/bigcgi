import os

class AppSettings(object):
    SECRET_KEY = os.environ["BIGCGI_SECRET_KEY"]
    ADMIN_PASSWORD = os.environ["BIGCGI_ADMIN_PASSWORD"]
    SMTP_USERNAME = os.environ["BIGCGI_SMTP_USERNAME"]
    SMTP_PASSWORD = os.environ["BIGCGI_SMTP_PASSWORD"]
    
app_settings = AppSettings()
