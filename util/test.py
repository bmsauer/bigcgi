from unittest.mock import MagicMock
from datetime import timedelta

class CorkUserMock(object):
    def __init__(self):
        self.username = "testuser"

class CorkMock(object):
    def __init__(self):
        self.current_user = CorkUserMock()

    def require(*args, **kwargs):
        return True

class ResponseMock(object):
    def __init__(self, status_code, text, elapsed=timedelta(milliseconds=123)):
        self.status_code = status_code
        self.text = text
        self.elapsed = elapsed
        
class AppDBOMongoMock(object):
    APPS = []
    
    def __init__(self):
        pass
    
    def get_summary(self, username):
        rv = []
        for item in AppDBOMongoMock.APPS:
            rv.append({"name":item["name"],
                       "username":item["username"],
                       "total_millisecs":item["stats"]["total_millisecs"],
                       "hits":item["stats"]["hits"]
            })
        return rv 

    def delete(self, appname, username):
        new_apps = []
        for item in AppDBOMongoMock.APPS:
            if item["name"] == appname and item["username"] == username:
                pass
            else:
                new_apps.append(item)
        AppDBOMongoMock.APPS = new_apps

    def create(self, appname, username):
        AppDBOMongoMock.APPS.append(
            {"name":appname, "username":username, "stats":{"hits":0, "total_millisecs":0}},
        )

    def inc_hits(self, username, appname):
        for item in AppDBOMongoMock.APPS:
            if item["name"] == appname and item["username"] == username:
                item["stats"]["hits"] += 1

    def inc_millisecs(self, username, appname, mills):
        for item in AppDBOMongoMock.APPS:
            if item["name"] == appname and item["username"] == username:
                item["stats"]["total_millisecs"] += mills

    def close(self):
        pass

def generate_csrf_token_mock():
    return "123"

def get_csrf_token_mock():
    return "123"

def get_cork_instance_test():
    return CorkMock()
