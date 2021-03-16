conn = new Mongo();
db = conn.getDB("bigcgi-main");
db.runCommand( {
       createUser: username,
       pwd: password,
       roles: []
} )

