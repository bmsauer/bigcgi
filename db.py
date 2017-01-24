import pymongo

from settings import app_settings

class MongoDatabaseConnection(object):
    def __init__(self):
        self.client = pymongo.MongoClient(app_settings.DATABASE_URI)

class AppDBOMongo(MongoDatabaseConnection):
    def __init__(self):
        super().__init__()
        self.db = self.client["bigcgi-main"]

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
                "$set": {"stats":{"hits":0}}
            }, upsert=True)
        else:
            inserted = self.db.apps.insert_one({"username":username, "name":appname, "stats":{"hits":0}})
            app_id = inserted.inserted_id
            self.db.users.update_one({"username":username}, {"$push":{"apps":{appname: app_id}}}, upsert=True)

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
            return_apps.append({"name":app["name"], "hits":app["stats"]["hits"]})
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
        
        
            
        
        
        
    
    
