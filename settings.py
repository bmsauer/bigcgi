import os
import logging
from logging.handlers import RotatingFileHandler
from log4mongo.handlers import BufferedMongoHandler

class AppSettings(object):
    SECRET_KEY = os.environ["BIGCGI_SECRET_KEY"]
    ADMIN_PASSWORD = os.environ["BIGCGI_ADMIN_PASSWORD"]
    SMTP_USERNAME = os.environ["BIGCGI_SMTP_USERNAME"]
    SMTP_PASSWORD = os.environ["BIGCGI_SMTP_PASSWORD"]

    DATABASE_USERADMIN_PASSWORD = os.environ["BIGCGI_DATABASE_USERADMIN_PASSWORD"]
    DATABASE_USERNAME = os.environ["BIGCGI_DATABASE_USERNAME"]
    DATABASE_PASSWORD = os.environ["BIGCGI_DATABASE_PASSWORD"]
    DATABASE_URI = "mongodb://localhost:27017"
    
    CGI_BASE_PATH_TEMPLATE = "/home/{}/public_html"

    def __init__(self):
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=format)
        formatter = logging.Formatter(format)
        self.logger = logging.getLogger()
        filehandler = RotatingFileHandler("bigcgi.log", maxBytes=50000, backupCount=2)
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)
        handler = BufferedMongoHandler(host='localhost',
                                       capped=True,
                                       database_name="bigcgi-logs",
                                       username=AppSettings.DATABASE_USERNAME,
                                       password=AppSettings.DATABASE_PASSWORD,
                                       authentication_db="bigcgi-logs",
                                       buffer_size=100,      
                                       buffer_periodical_flush_timing=10.0,
                                       buffer_early_flush_level=logging.CRITICAL)

        self.logger.addHandler(handler)
        self.logger.setLevel("INFO")
    
app_settings = AppSettings()
