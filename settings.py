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

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from log4mongo.handlers import BufferedMongoHandler
import pymongo
import mongomock
from unittest.mock import MagicMock


class AppSettings(object):
    BIGCGI_ENV = os.environ["BIGCGI_ENV"]
    SECRET_KEY = os.environ["BIGCGI_SECRET_KEY"]
    ADMIN_PASSWORD = os.environ["BIGCGI_ADMIN_PASSWORD"]
    SMTP_USERNAME = os.environ["BIGCGI_SMTP_USERNAME"]
    SMTP_PASSWORD = os.environ["BIGCGI_SMTP_PASSWORD"]

    DATABASE_USERADMIN_PASSWORD = os.environ["BIGCGI_DATABASE_USERADMIN_PASSWORD"]
    DATABASE_USERNAME = os.environ["BIGCGI_DATABASE_USERNAME"]
    DATABASE_PASSWORD = os.environ["BIGCGI_DATABASE_PASSWORD"]
    DATABASE_URI = "mongodb://localhost:27017"
    DATABASE_MAIN = "bigcgi-main"
    DATABASE_CORK = "bigcgi-cork"
    DATABASE_REPORTING = "bigcgi-reporting"
    DATABASE_LOGS = "bigcgi-logs"
    
    CGI_BASE_PATH_TEMPLATE = "/home/{}/public_html"
    FILE_BASE_PATH_TEMPLATE = "/home/{}/files"
    TMP_FILE_STORE = "/var/bigcgi"
    
    BIGCGI_INSTANCE_ID = os.environ["BIGCGI_INSTANCE_ID"]
    BIGCGI_TOTAL_INSTANCES = os.environ["BIGCGI_TOTAL_INSTANCES"]

    def __init__(self):
        self.logger = None
        self.database = None

    def get_logger(self):
        if self.logger == None:
            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            logging.basicConfig(format=format)
            formatter = logging.Formatter(format)
            self.logger = logging.getLogger()
            filehandler = RotatingFileHandler("./logs/bigcgi.log", maxBytes=50000, backupCount=2)
            filehandler.setFormatter(formatter)
            self.logger.addHandler(filehandler)
            try:
                handler = BufferedMongoHandler(host='localhost',
                                               capped=True,
                                               database_name="bigcgi-logs",
                                               username=AppSettings.DATABASE_USERNAME,
                                               password=AppSettings.DATABASE_PASSWORD,
                                               authentication_db="bigcgi-logs",
                                               buffer_size=100,      
                                               buffer_periodical_flush_timing=10.0,
                                               buffer_early_flush_level=logging.CRITICAL,
                                               connectTimeoutMS=5000,
                                               serverSelectionTimeoutMS=5000,
                )
                self.logger.addHandler(handler)
            except pymongo.errors.ServerSelectionTimeoutError:
                print("Failed to connecto to MongoDB logger.")
                sys.exit(1)

            self.logger.setLevel("INFO")
        return self.logger

    def get_database(self):
        if self.database == None:
            self.database = pymongo.MongoClient(self.DATABASE_URI)
        return self.database

class TestSettings(AppSettings):
    DATABASE_MAIN = "bigcgi-main-test"
    DATABASE_CORK = "bigcgi-cork-test"
    DATABASE_REPORTING = "bigcgi-reporting-test"
    DATABASE_LOGS = "bigcgi-logs-test"

    def __init__(self):
        self.logger = None
        self.database = mongomock.MongoClient()
        self.database[TestSettings.DATABASE_MAIN].authenticate = MagicMock()
        self.database[TestSettings.DATABASE_CORK].authenticate = MagicMock()
        self.database[TestSettings.DATABASE_REPORTING].authenticate = MagicMock()
        self.database[TestSettings.DATABASE_LOGS].authenticate = MagicMock()
        
    def get_logger(self):
        if self.logger == None:
            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            logging.basicConfig(format=format)
            self.logger = logging.getLogger()
        self.logger.setLevel("DEBUG")
        return self.logger

    def get_database(self):
        return self.database


if os.environ.get("BIGCGI_ENV", None) == "TEST":
    app_settings = TestSettings()
else:
    app_settings = AppSettings()
