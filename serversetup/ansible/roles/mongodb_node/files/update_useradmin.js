conn = new Mongo();
db = conn.getDB("admin");
db.runCommand( {
       updateUser: "useradmin",
       pwd: password,
       roles: [
           { role: "userAdminAnyDatabase", db: "admin" },
           { role: "backup", db: "admin"},
           { role: "restore", db: "admin"}
       ]
} )

