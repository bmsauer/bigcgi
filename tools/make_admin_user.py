from cork import Cork
from cork.backends import MongoDBBackend
import pymongo

from settings import app_settings

#makes a user an admin

def run():
    username = input("Username: ")
    mb = MongoDBBackend(db_name='bigcgi-cork',
                        username=app_settings.DATABASE_USERNAME,
                        password=app_settings.DATABASE_PASSWORD,
                        initialize=False)
    
    cork = Cork(backend=mb)

    mb.users._coll.find_one_and_update(
        {"login":username},
        {"$set": {"role":"admin"}}
    )

if __name__=="__main__":
    print("Please run this file with toolrunner.py.")
