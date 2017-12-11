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
import io
import pwd
import os
import pickle
import codecs

def run_cgi(script_name, username, request_method, path_info, query_string, remote_addr, auth, content_type, body, content_length, headers):
    payload = {
        "env" : {
            "SERVER_SOFTWARE" : "bigCGI",
            "SERVER_NAME": "internal.bigcgi.com",
            "GATEWAY_INTERFACE": "CGI/1.1",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "SERVER_PORT": "80",
            "REQUEST_METHOD": request_method,
            "PATH_INFO": path_info,
            "PATH_TRANSLATED": "NULL",
            "SCRIPT_NAME": "/{}".format(script_name),
            "SCRIPT_FILENAME": "NULL",
            "QUERY_STRING": query_string,
            "REMOTE_HOST": "NULL",
            "REMOTE_ADDR": remote_addr,
            "AUTH_TYPE": "Basic" if auth == None else "NULL",
            "REMOTE_USER": auth[0] if auth != None else "NULL",
            "REMOTE_IDENT": "NULL",
            "CONTENT_TYPE": content_type,
            "CONTENT_LENGTH": str(content_length),
            "HTTP_ACCEPT": headers["ACCEPT"],
            "HTTP_ACCEPT_ENCODING": headers["ACCEPT_ENCODING"],
            "HTTP_ACCEPT_LANGUAGE": headers["ACCEPT_LANGUAGE"],
            "HTTP_CONNECTION": headers["CONNECTION"],
            "HTTP_HOST": headers["HOST"],
            "HTTP_USER_AGENT": headers["USER-AGENT"],
        },
        "script": script_name,
        "username": username,
        "body": body,
    }
    #TODO: look into a shared memory solution 
    pickle_payload = codecs.encode(pickle.dumps(payload), "base64").decode()
    try:
        process = subprocess.run(["sudo", "script/runcgi.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=pickle_payload.encode("utf-8"), timeout=30)
        return_value = process.returncode
        return process.stdout.decode("utf-8"), process.stderr.decode("utf-8"), return_value
    except subprocess.TimeoutExpired as e:
        return "", "Process timed out.", 1
    
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
            
        
