from cork import Cork
from cork.backends import MongoDBBackend

from settings import app_settings

#sets up an admin user in the database.

def run():
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

if __name__=="__main__":
    print("Please run this file with toolrunner.py.")
