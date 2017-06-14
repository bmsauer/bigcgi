class CorkUserMock(object):
    def __init__(self):
        self.username = "testuser"

class CorkMock(object):
    def __init__(self):
        self.current_user = CorkUserMock()

    def require(*args, **kwargs):
        return True

class AppDBOMongoMock(object):
    def __init__(self):
        pass
    
    def get_all(self, username):
        return [{"name":"app1", "hits":4, "total_millisecs":12},
                {"name":"app2", "hits":5, "total_millisecs":10},
        ]

    def close(self):
        pass

def generate_csrf_token_mock():
    return "123"

def get_csrf_token_mock():
    return "123"
