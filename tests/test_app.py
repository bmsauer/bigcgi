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
from unittest.mock import MagicMock, PropertyMock, patch

from util.test import CorkMock, ResponseMock #, AppDBOMongoMock
from util.test import get_csrf_token_mock, generate_csrf_token_mock, get_cork_instance_test
import os
import bottle

import apps.cork; apps.cork.get_cork_instance = get_cork_instance_test
#import db.mongodbo; db.mongodbo.AppDBOMongo = AppDBOMongoMock
import util.request; util.request.get_csrf_token = get_csrf_token_mock
util.request.generate_csrf_token = generate_csrf_token_mock
os.system = MagicMock()
bottle.redirect = MagicMock()

from app import index, dashboard, create_app_view, upgrade_app_view, delete_app_view, delete_app
from app import create_app, bigcgi_run
from settings import app_settings

def setup_func():
    os.system.reset_mock()
    bottle.redirect.reset_mock()
def teardown_func():
    pass

def create_test_app():
    setup_func()
    #this tells the mock to default to having an app
    """
    db.mongodbo.AppDBOMongo.APPS = [
        {"name":"app1", "username":"testuser",
         "stats":{"hits":4, "total_millisecs":12}},
        {"name":"app1", "username":"testuser2",
         "stats":{"hits":4, "total_millisecs":12}},
        {"name":"app2", "username":"testuser",
         "stats":{"hits":5, "total_millisecs":10}},
    ]
    """
    client = app_settings.get_database()
    client[app_settings.DATABASE_MAIN]["apps"].insert_one({"name":"app1", "username":"testuser",
         "stats":{"hits":4, "total_millisecs":12}})
    client[app_settings.DATABASE_MAIN]["apps"].insert_one({"name":"app1", "username":"testuser2",
         "stats":{"hits":4, "total_millisecs":12}})
    client[app_settings.DATABASE_MAIN]["apps"].insert_one({"name":"app2", "username":"testuser",
         "stats":{"hits":5, "total_millisecs":10}})

def remove_test_app():
    client = app_settings.get_database()
    client[app_settings.DATABASE_MAIN]["apps"].remove({})
    #db.mongodbo.AppDBOMongo.APPS = []

def test_index():
    with boddle(params={"error":"errormsg", "flash":"flashmsg"}):
        response = index()
        assert "bigCGI" in response
        assert "errormsg" in response
        assert "flashmsg" in response
        
@with_setup(create_test_app, remove_test_app)
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

@with_setup(create_test_app, remove_test_app)
def test_delete_app():
    with boddle(params={}):
        response = delete_app("app1")
        client = app_settings.get_database()
        result = client[app_settings.DATABASE_MAIN]["apps"].find_one({"name":"app1", "username":"testuser"})
        assert result == None
        #for app in AppDBOMongoMock.APPS:
        #    assert not (app["name"] != "app1" and app["username"] != "testuser")
        bottle.redirect.assert_called_with("/dashboard?flash=Successful delete.")

@with_setup(setup_func, teardown_func)
def test_create_app():
    with boddle(params={}):
        response = create_app()
        bottle.redirect.assert_called_with("/dashboard?error=App must have a name.")
      
    with boddle(params={"name":"app3"}):
        with patch('bottle.BaseRequest.files') as mock_files:
            mock_files.return_value = {"upload":MagicMock()}
            response = create_app()
            bottle.redirect.assert_called_with("/dashboard?flash=Successfully created app.")
            client = app_settings.get_database()
            last_inserted = client[app_settings.DATABASE_MAIN].apps.find_one({"name":"app3"})
            assert last_inserted != None
            assert last_inserted["username"] == "testuser"

@with_setup(create_test_app, remove_test_app)
def test_bigcgi_run():
    with patch('requests.get') as request_get:
        request_get.return_value = ResponseMock(404, "not found balooga")
        response = bigcgi_run("testuser", "app3")
        assert response.status_code == 404
        assert "not found balooga" in response.body

    with patch('requests.get') as request_get:
        request_get.return_value = ResponseMock(200, "ok balooga")
        response = bigcgi_run("testuser", "app1")
        assert response.status_code == 200
        assert "ok balooga" in response.body
        client = app_settings.get_database()
        app = client[app_settings.DATABASE_MAIN].apps.find_one({"name":"app1", "username":"testuser"})
        assert app["stats"]["hits"] == 5
        assert app["stats"]["total_millisecs"] == 135
