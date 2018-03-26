import os
import tempfile

from settings import app_settings

def check_user_directories(username):
    """
    check_user_directories() : checks if user's CGI and file directories exist
      Creates them if they don't exist
    Params:
    - username (string) : the user we are checking
    Returns:
    - (bool) : true for success, False for exception raised, caught, and logged
    """
    try:
        os.mkdir(app_settings.FILE_BASE_PATH_TEMPLATE.format(username), mode=711)
    except FileNotFoundError:
        app_settings.logger.critical("Creating files path failed: home directory doesn't exist", extra={"actor":"INSTANCE " + app_settings.BIGCGI_INSTANCE_ID, "action":"create file directory", "object":username})
        return False
    except FileExistsError:
        pass
    try:
        os.mkdir(app_settings.CGI_BASE_PATH_TEMPLATE.format(username), mode=711)
    except FileNotFoundError:
        app_settings.logger.critical("Creating cgi path failed: home directory doesn't exist", extra={"actor":"INSTANCE " + app_settings.BIGCGI_INSTANCE_ID, "action":"create cgi directory", "object":username})
        return False
    except FileExistsError:
        pass
    return True

def move_file_contents(filename, username, kind, file_contents):
    """
    move_file_contents() : generate arguments for move_file sudo script
    Params:
    - filename (string) : the name of the file
    - username (string) : the name of the user
    - kind (string) : "app" for an app,  "file" for a file
    - file_contents (bytes) : the contents of the file
    Returns:
    - (bool) : true on success, false on failure
    """
    with tempfile.NamedTemporaryFile(dir=app_settings.TMP_FILE_STORE) as temp_storage:
        temp_storage.write(file_contents)
        if kind == "file":
            final_path = os.path.join(app_settings.FILE_BASE_PATH_TEMPLATE.format(username), filename)
            permissions = "400"
        elif kind == "app":
            final_path = os.path.join(app_settings.CGI_BASE_PATH_TEMPLATE.format(username), filename)
            permissions = "500"
        return move_file(username, temp_storage.name, final_path, permissions)
        

def move_file(username, tmpfilename, final_path, permissions):
    """
    move_file_contents() : run the move_file sudo script
    Params:
    - username (string) : the name of the user
    - tmpfilename (string) : the name of the temporary file to move
    - final_path (string) : the end location in the users home directory
    - permissions (string) : numeric permissions, like 500
    Returns:
    - (bool) : true on success, false on failure
    """
    status = os.system("sudo script/movefile.tcl {} {} {} {}".format(username, tmpfilename, final_path, permissions))
    if status != 0:
        app_settings.logger.error("failed to move file", extra={"actor":"INSTANCE " + app_settings.BIGCGI_INSTANCE_ID, "action": "sync file", "object": final_path})
        return False
    else:
        app_settings.logger.info("file synced", extra={"actor":"INSTANCE " + app_settings.BIGCGI_INSTANCE_ID, "action": "sync file", "object": final_path})
        return True

    
