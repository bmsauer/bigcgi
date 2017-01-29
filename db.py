import pymongo

from settings import app_settings

class MongoDatabaseConnection(object):
    def __init__(self):
        self.client = pymongo.MongoClient(app_settings.DATABASE_URI)

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
        
        
        
            
        
        
        
    
    
