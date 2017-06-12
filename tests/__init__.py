import os
import sys

import toolrunner
from settings import app_settings

def setup():
    print("setting up package")
    if os.environ.get("BIGCGI_ENV", None) != "TEST":
        print("Aborting tests: BIGCGI_ENV is not set to TEST.")
        sys.exit(1)

    print("setting up test database")
    try:
        toolrunner.go("setup_auth_db", "create_test_databases", [])
    except Exception as e:
        print(str(e))
        sys.exit(1)
    

def teardown():
    print("tearing down package")
    print("tearing down test database")
    try:
        toolrunner.go("setup_auth_db", "delete_test_databases", [])
    except Exception as e:
        print(str(e))
        sys.exit(1)
