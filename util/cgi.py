import subprocess
import io

def run_cgi(script_name, username, request_method, path_info, query_string, remote_addr, auth, content_type, body, content_length, headers ):
    env = {}
    env["SERVER_SOFTWARE"] = "bigCGI"
    env["SERVER_NAME"] = "internal.bigcgi.com"
    env["GATEWAY_INTERFACE"] = "CGI/1.1"
    env["SERVER_PROTOCOL"] = "HTTP/1.1"
    env["SERVER_PORT"] = "80"
    
    env["REQUEST_METHOD"] = request_method
    env["PATH_INFO"] = path_info
    #env["PATH_TRANSLATED"] = None
    env["SCRIPT_NAME"] = "/{}".format(script_name)
    #env["SCRIPT_FILENAME"] = None
    env["QUERY_STRING"] = query_string
    env["REMOTE_HOST"] = "NULL"
    env["REMOTE_ADDR"] = remote_addr
    #env["AUTH_TYPE"] = "Basic" if auth == None else None
    #env["REMOTE_USER"] = auth[0] if auth != None else None
    #env["REMOTE_IDENT"] = None
    env["CONTENT_TYPE"] = content_type
    env["CONTENT_LENGTH"] = str(content_length)

    env["HTTP_ACCEPT"] = headers["ACCEPT"]
    env["HTTP_ACCEPT_ENCODING"] = headers["ACCEPT_ENCODING"]
    env["HTTP_ACCEPT_LANGUAGE"] = headers["ACCEPT_LANGUAGE"]
    env["HTTP_CONNECTION"] = headers["CONNECTION"]
    env["HTTP_HOST"] = headers["HOST"]
    env["HTTP_USER_AGENT"] = headers["USER-AGENT"]

    

    #TODO: switch to fork based, like in CGIHTTPServer.py
    script = "/home/{}/public_html/{}".format(username, script_name)
    try:
        process = subprocess.run([script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, input=body, timeout=20) #TODO: preexec_fn - https://gist.github.com/sweenzor/1685717
        return_value = process.returncode
    except subprocess.TimeoutExpired as e:
        return_value = 1
        
    return process.stdout.decode("utf-8"), process.stderr.decode("utf-8"), return_value
    
def parse_output(output):
    iostr = io.StringIO(output)
    parsing_headers = True
    output = ""
    headers = {}
    for line in iostr:
        if line.strip() == "":
            parsing_headers = False
            continue
        if parsing_headers == True:
            line_list = line.split(":")
            headers[line_list[0].strip()] = line_list[1].strip()
        else:
            output += line
    return headers, output
            
        
