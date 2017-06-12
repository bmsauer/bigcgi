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
appname: "appname",
stats: {
  hits: 0,
  total_millisecs: 0,
}
}

"""

class MongoDatabaseConnection(object):
    def __init__(self):
        self.client = pymongo.MongoClient(app_settings.DATABASE_URI, w=0)

class ReportingDBOMongo(MongoDatabaseConnection):
    def __init__(self):
        super().__init__()
        self.maindb = self.client["bigcgi-main"]
        self.maindb.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD)
        self.reportingdb = self.client["bigcgi-reporting"]
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
    def __init__(self):
        super().__init__()
        self.db = self.client["bigcgi-main"]
        self.db.authenticate(app_settings.DATABASE_USERNAME, app_settings.DATABASE_PASSWORD)

    def close(self):
        self.client.close()

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

    def get_all(self, username):
        """
        AppDBOMongo.get_all() - gets all apps and stats for a user
        Params:
        - username (string) : the name of the user
        Returns:
        - (list) : a list of dicts containing name, hits
        """
        apps = self.db.apps.find({"username":username})
        return_apps = []
        for app in apps:
            return_apps.append({"name":app["name"], "hits":app["stats"]["hits"], "total_millisecs":app["stats"]["total_millisecs"]})
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
        }, upsert=True)
        self.db.users.update_one({
            "username":username,
        },
        {
            "$inc": {"stats.monthly_hits":1}
        }, upsert=True)

    def inc_millisecs(self, username, appname, mills):
        """
        AppDBOMongo.add_avg() - adds to the total millisecs per request
        Params:
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
            }, upsert=True)
        
        
        
            
        
        
        
    
    
