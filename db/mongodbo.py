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

import pymongo
import datetime

from settings import app_settings

"""
bigcgi-main.users
{
username: "username",
apps: ["appname",]
stats: {
  monthly_hits: 0,
}
}
bigcgi-main.apps
{
username: "username",
name: "appname",
stats: {
  hits: 0,
  total_millisecs: 0,
},
security: 0, #optional
}
bigcgi-main.files
{
username: "username",
filename: "filename",
kind: "file|app",
bytes_contents: bytes(file_contents)
}
bigcgi-logs.app-logs
{
username: "username",
name: "appname",
message: "message",
}

"""

class MongoDatabaseConnection(object):
    def __init__(self, client):
        self.client = client

class UserDBOMongo(MongoDatabaseConnection):
    def __init__(self, client):
        super().__init__(client)
        self.maindb = self.client[app_settings.DATABASE_MAIN]
        self.maindb.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD, app_settings.DATABASE_MAIN)

    def get_all_users(self):
        users = self.maindb.users.find({})
        return users
        
class ReportingDBOMongo(MongoDatabaseConnection):
    def __init__(self, client):
        super().__init__(client)
        self.maindb = self.client[app_settings.DATABASE_MAIN]
        self.maindb.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD, app_settings.DATABASE_MAIN)
        self.reportingdb = self.client[app_settings.DATABASE_REPORTING]
        self.reportingdb.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD, app_settings.DATABASE_MAIN)

    def create_monthly_hits_report(self):
        #get all users and their monthly hits
        users = self.maindb.users.find({})
        hits = {}
        for u in users:
            hits[u["username"]] = u["stats"]["monthly_hits"]
        #reset user's monthly hits
        self.maindb.users.update_many({},
            {
                "$set": {"stats.monthly_hits":0}
            }, upsert=True)
        #insert into reporting database
        self.reportingdb.monthly_hit_reports.insert_one({
            "date":datetime.datetime.utcnow(),
            "hits":hits})

class FileDBOMongo(MongoDatabaseConnection):
    def __init__(self, client):
        super().__init__(client)
        self.db = self.client[app_settings.DATABASE_MAIN]
        self.db.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD, app_settings.DATABASE_MAIN)

    def add_file(self, bytes_contents, filename, username, kind):
        """
        FileDBOMongo.add_file() : adds the contents of a file (app or file) to mongodb
        Params:
        - bytes_contents (bytes) : the contents of the file
        - filename (string) : the file string
        - username (string) : the owner of the file
        - kind (string) : the kind of file it is (file|app)
        Returns:
        - (boolean) : true on success, false on failure
        """
        try:
            self.db.files.update_one({
                "username":username,
                "filename":filename,
            },
            {
                "$set": {"kind":kind, "bytes_contents": bytes_contents}
            }, upsert=True)
            return True
        except:
            return False

    def delete_file(self, filename, username, kind):
        """
        FileDBOMongo.delete_file() : remove a file from mongodb
        Params:
        - filename (string) : the name of the file
        - username (string) : the owner of the file
        - kind (string) : kind of file it is (app|file)
        Returns:
        - (boolean) : true on success, false on failure
        """
        try:
            self.db.files.delete_one({"username": username, "filename": filename, "kind": kind})
            return True
        except:
            return False
    
    def get_file(self, filename, username, kind):
        """
        FileDBOMongo.get_file() : gets the contents of a file (app or file) from mongodb
        Params:
        - filename (string) : the file string
        - username (string) : the owner of the file
        - kind (string) : the kind of file it is (file|app)
        Returns:
        - (bytes) : the contents of the file
        """
        try:
            fileout = self.db.files.find_one({"filename":filename, "username":username, "kind":kind})
            if fileout:
                return fileout["bytes_contents"]
            else:
                return None
        except:
            return None

    def get_user_files(self, username):
        """
        FileDBOMongo.get_summary() - gets all files for a user
        Params:
        - username (string) : the name of the user
        Returns:
        - (list) : a list of filenames
        """
        files = self.db.files.find({"username":username, "kind": "file"}).sort("filename", 1)
        return_files = []
        for userfile in files:
            return_files.append(userfile["filename"])
        return return_files
        
class AppDBOMongo(MongoDatabaseConnection):
    def __init__(self, client):
        super().__init__(client)
        self.db = self.client[app_settings.DATABASE_MAIN]
        self.db.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD, app_settings.DATABASE_MAIN)
        self.logsdb = self.client[app_settings.DATABASE_LOGS]
        self.logsdb.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD, app_settings.DATABASE_MAIN)

    def create(self, appname, username):
        """
        AppDBOMongo.create() - adds a record for an app in the db
        Params:
        - appname (string) : the name of the app, which will be the name of the file
        - username (string) : the name of the user this app is for
        Returns:
        - (bool) : False for creation, True for upsert
        """
        existing = self.db.apps.find_one({"username":username, "name":appname})
        if existing:
            self.db.apps.update_one({
                "username":username,
                "name":appname
            },
            {
                "$set": {"stats":{"hits":0, "total_millisecs":0}}
            }, upsert=True)
        else:
            inserted = self.db.apps.insert_one({"username":username, "name":appname, "stats":{"hits":0, "total_millisecs":0}})
            app_id = inserted.inserted_id
            self.db.users.update_one({"username":username}, {"$push":{"apps":appname}}, upsert=True)

    def delete(self, appname, username):
        """
        AppDBOMongo.delete() - deletes a record for an app
        Params:
        - appname (string) : the name of the app, which will be the name of the file
        - username (string) : the name of the user this app is for
        Returns:
        - (boolean) : True on success, False on failure
        """
        try:
            self.db.apps.delete_one({"username":username, "name":appname})
            self.db.users.update_one({"username":username}, {"$pull":{"apps": appname}})
            return True
        except:
            return False

    def get_summary(self, username):
        """
        AppDBOMongo.get_summary() - gets all apps and stats for a user
        Params:
        - username (string) : the name of the user
        Returns:
        - (list) : a list of dicts containing name, hits, status, security
        """
        apps = self.db.apps.find({"username":username}).sort("name", 1)
        return_apps = []
        for app in apps:
            if "security" in app:
                security = app["security"]
            else:
                security = 0
            return_apps.append({"name":app["name"], "hits":app["stats"]["hits"], "total_millisecs":app["stats"]["total_millisecs"], "security": security})
        return return_apps

    def inc_hits(self, username, appname):
        """
        AppDBOMongo.inc_hits() - increments hits stat for an app
        Params:
        - username (string) : the name of the user
        - appname (string) : the app to increment
        Returns:
        - Nothing
        """
        self.db.apps.update_one({
            "username":username,
            "name":appname
        },
        {
            "$inc": {"stats.hits":1}
        })
        self.db.users.update_one({
            "username":username,
        },
        {
            "$inc": {"stats.monthly_hits":1}
        })

    def inc_millisecs(self, username, appname, mills):
        """
        AppDBOMongo.add_avg() - adds to the total millisecs per request
        Params:
        - username (string) : the name of the user
        - appname (string) : the app to increment
        - mills (int) : the number of millisecs to add
        Returns:
        - Nothing
        """
        self.db.apps.update_one({
                "username":username,
                "name":appname
            },
            {
                "$inc": {"stats.total_millisecs":mills}
            })
        
    def secure_app(self, username, appname, security_setting):
        """
        AppDBOMongo.secure_app() - sets the security setting on an app
        Params:
        - username (string) : the name of the user
        - appname (string) : the name of the app
        - security_setting (int) : 1 for secure, 0 for open
        Returns:
        - Nothing
        """
        self.db.apps.update_one({
            "username": username,
            "name": appname
        },
        {
            "$set": {"security": security_setting}
        })

    def app_secure(self, username, appname):
        """
        AppDBOMongo.app_secure() - gets the security of an app
        Params:
        - username (string) : the name of the user
        - appname (string) : the name of the app
        Returns:
        - (bool) - true if secure, false if not
        """
        app = self.db.apps.find_one({"username":username, "name": appname})
        if not app:
            return False
        if "security" in app:
            try:
                security = int(app["security"])
                if security == 1:
                    return True
                else:
                    return False
            except ValueError:
                return False
        else:
            return False
        
    def app_log(self, username, appname,  message_list):
        """
        AppDBOMongo.app_log() - log a list of messages
        Params:
        - username (string) : the name of the user
        - appname (string) : the name of the app
        - message_list (list) : a list of strings, each a line to log
        Returns:
        - Nothing
        """
        app = self.db.apps.find_one({"username":username, "name": appname})
        if not app:
            return False
        records = [{"username": username, "name": appname, "message": m} for m in message_list]
        self.logsdb.applogs.insert_many(records)

    def get_app_logs(self, username, appname):
        """
        AppDBOMongo.get_app_logs() - get a list of logs for a users app
        Params:
        - username (string) : the user of the app
        - appname (string) : the app
        Returns:
        - (list) : list of mongodb records
        """
        logs = self.logsdb.applogs.find({
            "username": username,
            "name": appname
        })
        return logs
        
    
    
