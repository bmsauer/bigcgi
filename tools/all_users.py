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
import subprocess
import pymongo
from db.mongodbo import UserDBOMongo, FileDBOMongo, AppDBOMongo
from settings import app_settings
from tasks.tasks import sync_file 

def create_users(user):
    try:
        username = user["username"]
    except KeyError:
        print("invalid user: " + str(user))
        return
    process = subprocess.run(["sudo", "script/adduser.tcl", username], stdout=subprocess.PIPE)
    status = process.returncode
    stdout = process.stdout.decode("utf-8")
    if status != 0 or "error" in stdout.lower():
        print("error: " + stdout)
    else:
        print("created user " + username)

def sync_files(user):
    try:
        username = user["username"]
    except KeyError:
        print("invalid user: " + str(user))
        return
    #sync apps
    app_db = AppDBOMongo(app_settings.get_database())
    user_apps = app_db.get_summary(username)
    for app in user_apps:
        sync_file.run(app["name"], username, "app")
        print("synced app: " + username + " -> " + app["name"])
    #sync files
    files_db = FileDBOMongo(app_settings.get_database())
    user_files = files_db.get_user_files(username)
    for fil in user_files:
        sync_file.run(fil, username, "file")
        print("synced file: " + username + " -> " + fil)
    
        
def all_users(callback, *args):
    db = UserDBOMongo(app_settings.get_database())
    users = db.get_all_users()
    for user in users:
        callback(user)

def run(*args):
    callback = None
    if args[0] == "create":
        callback = create_users
    if args[0] == "sync_files":
        callback = sync_files
    else:
        print("error: invalid command for all_users")
        return

    all_users(callback, args[1:])
            
            
    
