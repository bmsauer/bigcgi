from cork import Cork
from cork.backends import MongoDBBackend
import pymongo

from settings import app_settings

#sets up an admin user in the database.

def run():
    #cork (app auth)
    mb = MongoDBBackend(db_name='bigcgi-cork', initialize=True)
    cork = Cork(backend=mb)
    admin_hash = cork._hash("admin", app_settings.ADMIN_PASSWORD)
    mb.users._coll.insert({
        "login": "admin",
        "email_addr": "admin@localhost.local",
        "desc": "admin test user",
        "role": "admin",
        "hash": admin_hash,
        "creation_date": "2012-10-28 20:50:26.286723"
    })
    mb.roles._coll.insert({'role': 'admin', 'val': 100})
    #mb.roles._coll.insert({'role': 'editor', 'val': 60})
    mb.roles._coll.insert({'role': 'user', 'val': 50})

    #database users and roles
    client = pymongo.MongoClient(app_settings.DATABASE_URI)
    db = client["admin"]
    db.add_user('useradmin', app_settings.DATABASE_USERADMIN_PASSWORD, roles:[{"role":"userAdminAnyDatabase","db": "admin"}])
    db = client["bigcgi-main"]
    db.add_user(app_settings.DATABASE_USERNAME,
                app_settings.DATABASE_PASSWORD,
                roles:[{"role":"readWrite", "db": "bigcgi-main"}])
    db = client["bigcgi-cork"]
    db.add_user(app_settings.DATABASE_USERNAME,
                app_settings.DATABASE_PASSWORD,
                roles:[{"role":"readWrite", "db": "bigcgi-cork"}])
    
if __name__=="__main__":
    print("Please run this file with toolrunner.py.")
