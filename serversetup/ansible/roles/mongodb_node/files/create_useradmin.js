conn = new Mongo();
db = conn.getDB("admin");
db.runCommand( {
       createUser: "useradmin",
       pwd: password,
       roles: []
} )

