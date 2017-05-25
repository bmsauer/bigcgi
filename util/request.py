import bottle
import uuid

class AccessDeniedException(Exception):
    pass

def authorize(creds):
    return True

def parse_basic_auth(headers):
    if not "Authorization" in headers:
        raise AccessDeniedException("No Authorization header.")
    else:
        try:
            plain = headers["Authorization"][6:] #strip off Basic_
            bytes_creds= base64.b64decode(plain)
            creds = tuple(bytes_creds.decode().split(":"))
            return creds
        except IndexError as e:
            raise AccessDeniedException("Basic auth was malformed.")
        except Exception as e:
            raise AccessDeniedException("Unknown error occured parsing basic auth.")

def generate_csrf_token():
    return str(uuid.uuid4())

def get_csrf_token():
    session = bottle.request.environ.get('beaker.session')
    return session['csrf']
        
def require_csrf(callback):
    def wrapper(*args, **kwargs):
        session = bottle.request.environ.get('beaker.session')
        if bottle.request.method == 'POST':
            csrf = bottle.request.forms.get('csrf')
            if not csrf or csrf != session.get('csrf'):
                bottle.abort(400, "Failed csrf validation.")
        session['csrf'] = generate_csrf_token()
        session.save()
        body = callback(*args, **kwargs)
        return body
    return wrapper

def postd():
    return bottle.request.forms

def post_get(name, default=''):
    return bottle.request.POST.get(name, default).strip()
