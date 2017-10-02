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

"""

class MongoDatabaseConnection(object):
    def __init__(self, client):
        self.client = client
        
class ReportingDBOMongo(MongoDatabaseConnection):
    def __init__(self, client):
        super().__init__(client)
        self.maindb = self.client[app_settings.DATABASE_MAIN]
        self.maindb.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD)
        self.reportingdb = self.client[app_settings.DATABASE_REPORTING]
        self.reportingdb.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD)

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
        
class AppDBOMongo(MongoDatabaseConnection):
    def __init__(self, client):
        super().__init__(client)
        self.db = self.client[app_settings.DATABASE_MAIN]
        self.db.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD)

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
        - Nothing
        """
        self.db.apps.delete_one({"username":username, "name":appname})
        self.db.users.update_one({"username":username}, {"$pull":{"apps": appname}})

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
        
        
        
    
    
