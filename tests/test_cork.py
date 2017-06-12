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

from webtest import TestApp
from nose import with_setup

import app

def setup_func():
    pass
def teardown_func():
    pass

"""    
@with_setup(setup_func, teardown_func)
def test_index():
    testapp = TestApp(app.app)
    response = testapp.get("/?error=errormsg&flash=flashmsg")
    assert "bigCGI" in response
    assert "errormsg" in response
    assert "flashmsg" in response
"""

