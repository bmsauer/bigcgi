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
        toolrunner.go("setup_auth_db", "clear_test_databases", [])
    except Exception as e:
        print(str(e))
        sys.exit(1)
