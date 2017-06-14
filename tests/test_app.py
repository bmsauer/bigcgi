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

from nose import with_setup
from boddle import boddle
from unittest.mock import MagicMock

from util.test import CorkMock
from util.test import AppDBOMongoMock
from util.test import get_csrf_token_mock, generate_csrf_token_mock

import apps.cork; apps.cork.cork = CorkMock()
import db.mongodbo; db.mongodbo.AppDBOMongo = AppDBOMongoMock
import util.request; util.request.get_csrf_token = get_csrf_token_mock
util.request.generate_csrf_token = generate_csrf_token_mock

from app import index, dashboard, create_app_view, upgrade_app_view, delete_app_view

def setup_func():
    pass
def teardown_func():
    pass

def test_index():
    with boddle(params={"error":"errormsg", "flash":"flashmsg"}):
        response = index()
        assert "bigCGI" in response
        assert "errormsg" in response
        assert "flashmsg" in response

def test_dashboard():
    with boddle(params={}):
        response = dashboard()
        assert "app1" in response
        assert "app2" in response
        assert "3.0" in response
        assert "2.0" in response

def test_create_app_view():
    with boddle(params={}):
        response = create_app_view()
        assert "Create App" in response

def test_upgrade_app_view():
    with boddle(params={}):
        response = upgrade_app_view("testapp")
        assert "Upgrade App" in response
        assert "testapp" in response

def test_delete_app_view():
    with boddle(params={}):
        response = delete_app_view("testapp")
        assert "Delete App" in response
        assert "testapp" in response
        
