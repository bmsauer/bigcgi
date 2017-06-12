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
