class CorkUserMock(object):
    def __init__(self):
        self.username = "testuser"

class CorkMock(object):
    def __init__(self):
        self.current_user = CorkUserMock()

    def require(*args, **kwargs):
        return True

class AppDBOMongoMock(object):
    APPS = []
    
    def __init__(self):
        pass
    
    def get_all(self, username):
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

    def close(self):
        pass

def generate_csrf_token_mock():
    return "123"

def get_csrf_token_mock():
    return "123"

def get_cork_instance_test():
    return CorkMock()
