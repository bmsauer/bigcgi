#!/usr/bin/env python3.5
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
import sys
import pickle
import codecs
import getpass
import grp
import stat

class SecurityException(Exception):
    pass

def check_security(payload):
    username = payload["username"]
    script_name = payload["script"]
    #suexec security model: https://httpd.apache.org/docs/2.4/suexec.html
    #1)Is the user executing this wrapper a valid user of this system?
    try:
        pwd.getpwuid(os.getuid())[0]
    except KeyError:
        raise SecurityException('User {} does not exist'.format(username))
    #2)Was the wrapper called with the proper number of arguments?
    if len(sys.argv) != 1:
        raise SecurityException('runcgi.py called with wrong number of arguments')
    #3)Is this valid user allowed to run the wrapper?
    env_user = pwd.getpwuid(os.getuid())[0]
    if env_user != "root":
        raise SecurityException('env_user ({}) is  invalid'.format(env_user,eff_user))
    #4)Does the target CGI or SSI program have an unsafe hierarchical reference?
    if ".." in script_name or script_name[0] == "/":
        raise SecurityException("Script name {} contains .. or /".format(script_name))
    #5)Is the target user name valid?
    try:
        pwd.getpwnam(username)
    except KeyError:
        raise SecurityException('Target user {} does not exist'.format(username))
    #6)Is the target group name valid?
    try:
        grp.getgrnam(username)
    except KeyError:
        raise SecurityException('Target group {} does not exist'.format(username))
    #7)Is the target user NOT superuser?
    if username == "root" or username == "bigcgi":
        raise SecurityException('Target user cannot be root.')
    #8)Is the target userid ABOVE the minimum ID number?
    user_id = pwd.getpwnam(username).pw_uid
    if user_id < 1000:
        raise SecurityException('User id {} is less than 1000'.format(user_id))
    #9)Is the target group NOT the superuser group?
    #this will be username, already checked
    #10)Is the target groupid ABOVE the minimum ID number?
    #this will be username, already checked
    #11)Can the wrapper successfully become the target user and group?
    #checked below
    #12)Can we change directory to the one in which the target CGI/SSI program resides?
    directory = "/home/{}/public_html".format(username)
    if not os.path.isdir(directory):
        raise SecurityException('Target script directory {} does not exist'.format(directory))
    #13)Is the directory within the httpd webspace?
    #not needed
    #14)Is the directory NOT writable by anyone else?
    mode = os.stat(directory).st_mode
    mode_stripped = stat.S_IMODE(mode)
    permissions = oct(mode_stripped)
    if permissions[-3:] != "500":
        raise SecurityException('Target directory has invalid permissions')
    #15)Does the target CGI/SSI program exist?
    script = "/home/{}/public_html/{}".format(username, script_name)
    if not os.path.isfile(script):
        raise SecurityException('Target script does not exist')
    #16)Is the target CGI/SSI program NOT writable by anyone else?
    mode = os.stat(script).st_mode
    permissions = oct(stat.S_IMODE(mode))
    if permissions[-3:] != "500":
        raise SecurityException('Target script has invalid permissions')
    #17)Is the target CGI/SSI program NOT setuid or setgid?
    if script == "setgid" or script == "setuid":
        raise SecurityException('Cannot use setuid or setgid as target')
    #18)Is the target user/group the same as the program's user/group?
    mode = os.stat(script)
    group_id = pwd.getpwnam(username).pw_gid
    if mode.st_uid != user_id or mode.st_gid != group_id:
        raise SecurityException('Script owner is not the target user')
    #19)Can we successfully clean the process environment to ensure safe operations?
    payload["env"]["PATH"] = "/usr/local/bin:/usr/bin:/bin"
    #20)Can we successfully become the target CGI/SSI program and execute?
    #checked below

    
def demote(user_uid, user_gid):
    """Pass the function 'set_ids' to preexec_fn, rather than just calling
    setuid and setgid. This will change the ids for that subprocess only"""
    #https://gist.github.com/sweenzor/1685717
    def set_ids():
        os.setgroups([])
        os.setgid(user_gid)
        os.setuid(user_uid)
    return set_ids

if __name__ == "__main__":
    pickle_payload = sys.stdin.read()
    payload = pickle.loads(codecs.decode(pickle_payload.encode(), "base64"))
    try:
        check_security(payload)
    except SecurityException as e:
        print("Security exception raised: " + str(e), file=sys.stderr)
        sys.exit(1)
    username = payload["username"]
    script_name = payload["script"]
    env = payload["env"]
    body = payload["body"]
    
    oldpath = os.getcwd()
    os.chdir("/home/{}/public_html".format(username))
    script = "/home/{}/public_html/{}".format(username, script_name)
    try:
        uid = pwd.getpwnam(username).pw_uid
        gid = pwd.getpwnam(username).pw_gid
        #TODO: switch to fork based, like in CGIHTTPServer.py
        process = subprocess.run([script], env=env, input=bytes(body,"utf-8"), timeout=20, preexec_fn=demote(uid,gid))
        os.chdir(oldpath)
        sys.exit(0)
        
    except subprocess.TimeoutExpired as e:
        print("CGI process timeout.", file=sys.stderr)
        os.chdir(oldpath)
        sys.exit(1)
    except KeyError as e: #user does not exist
        print("Invalid user.", file=sys.stderr)
        os.chdir(oldpath)
        sys.exit(1)
    except Exception as e:
        print("An unknown error occurred: " + str(e), file=sys.stderr)
        os.chdir(oldpath)
        sys.exit(1)
    

            
        
