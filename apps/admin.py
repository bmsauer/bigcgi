import bottle
from util.request import *
from settings import app_settings
from apps.cork import cork

admin_app = bottle.Bottle()
admin_app.install(require_csrf)

@admin_app.route('/')
def admin():
    """Only admin users can see this"""
    cork.require(role='admin', fail_redirect='/?error=Not authorized.')
    flash = bottle.request.query.flash or None
    error = bottle.request.query.error or None
    #pregenerate selectbox html (bottle templates don't support nesting fors)
    select_html = ""
    for r in cork.list_roles():
        select_html += "<option value='{}'>{}</option>".format(r[0],r[0])
    return bottle.template("admin/admin_page",{
        "current_user":cork.current_user,
        "users":cork.list_users(),
        "roles":cork.list_roles(),
        "select_html":select_html,
        "csrf":get_csrf_token(),
        "flash":flash,
        "error":error
    })

@admin_app.post("/delete-user")
def admin_delete_user():
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
