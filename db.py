import pymongo

from settings import app_settings

class MongoDatabaseConnection(object):
    def __init__(self):
        self.client = pymongo.MongoClient(app_settings.DATABASE_URI)

class AppDBOMongo(MongoDatabaseConnection):
    def __init__(self):
        super().__init__()
        self.db = self.client["bigcgi-main"]

    def create(self, appname, appprog, username):
        existing = self.db.apps.find_one({"username":username, "name":appname})
        if existing:
            self.db.apps.update_one({"username":username, "name":appname}, {"$set":{"appprog":appprog, "stats":{"hits":0}}}, upsert=True)
        else:
            inserted = self.db.apps.insert_one({"username":username, "name":appname, "appprog":appprog, "stats":{"hits":0}})
            app_id = inserted.inserted_id
            self.db.users.update_one({"username":username}, {"$push":{appname: app_id}}, upsert=True) 
        
        
    
    
