
from webtest import TestApp
from nose import with_setup

import app

def setup_func():
    pass
def teardown_func():
    pass

    
@with_setup(setup_func, teardown_func)
def test_index():
    dweedle = TestApp(app.app)
    response = dweedle.get("/")
    assert "bigCGI" in response

