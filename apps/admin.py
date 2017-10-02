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

import bottle
from util.request import *
from settings import app_settings
from util.auth import get_cork_instance
import os

admin_app = bottle.Bottle()
admin_app.install(require_csrf)

@admin_app.route('/')
def admin():
    """Only admin users can see this"""
    cork = get_cork_instance()
    cork.require(role='admin', fail_redirect='/?error=Not authorized.')
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    #pregenerate selectbox html (bottle templates don't support nesting fors)
    select_html = ""
    for r in cork.list_roles():
        select_html += "<option value='{}'>{}</option>".format(r[0],r[0])
    return bottle.template("admin/admin_page",{
        "current_user":cork.current_user,
        "users":sorted(cork.list_users()),
        "roles":reversed(sorted(cork.list_roles(), key=lambda x:int(x[1]))),
        "select_html":select_html,
        "csrf":get_csrf_token(),
        "flash":flash,
        "error":error
    })

@admin_app.post("/delete-user")
def admin_delete_user():
    cork = get_cork_instance()
    cork.require(role='admin', fail_redirect="/?error=Not authorized.")
    username = post_get('username')
    try:
        cork.delete_user(username)
        status = os.system("sudo script/deluser.tcl " + username)
        if status != 0:
            raise Exception("OS script raised nonzero status. Check logs.")
    except Exception as e:
        bottle.redirect("/admin?error=Failed to delete user: " + str(e))
    bottle.redirect("/admin/?flash=Deleted user.")

@admin_app.post("/modify-user-role")
def admin_modify_user_role():
    cork = get_cork_instance()
    cork.require(role="admin", fail_redirect="/?error=Not authorized.")
    username = post_get("username")
    role = post_get("role")
    try:
        cork._store.users._coll.find_one_and_update(
            {"login":username},
            {"$set": {"role":role}}
        )
    except Exception as e:
        bottle.redirect("/admin/?error=Failed to modify user role: " + str(e))
    bottle.redirect("/admin/?flash=Modified user role.")
