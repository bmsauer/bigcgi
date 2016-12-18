from bottle import route, template, run, request, abort
import requests
import base64

class AccessDeniedException(Exception):
    pass

def authorize(creds):
    return True

def parse_basic_auth(headers):
    if not "Authorization" in headers:
        raise AccessDeniedException("No Authorization header.")
    else:
        try:
            plain = request.headers["Authorization"][6:] #strip off Basic_
            bytes_creds= base64.b64decode(plain)
            creds = tuple(bytes_creds.decode().split(":"))
            return creds
        except IndexError as e:
            raise AccessDeniedException("Basic auth was malformed.")
        except Exception as e:
            raise AccessDeniedException("Unknown error occured parsing basic auth.")
            
        
@route("/")
def index():
    return template("index",{})

@route("/app/<appname>",method=["GET","POST"])
def app(appname):
    try:
        creds = parse_basic_auth(request.headers)
    except AccessDeniedException as e:
        #abort(401, str(e))
        creds = ("brian","brian")
        
    if not authorize(creds):
        abort(401, "Authorization failed.")
    else:
        url = "http://localhost/~{}/cgi-bin/{}".format(creds[0], appname)
        if request.method == "GET":
            response = requests.get(url, params=dict(request.query))
        elif request.method == "POST":
            response = requests.post(url,data=dict(request.forms))
        return response.text
        
if __name__ == "__main__":
    run(host='localhost', port=8888, debug=True)
