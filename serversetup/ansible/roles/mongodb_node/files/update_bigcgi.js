conn = new Mongo();
db = conn.getDB("bigcgi-main");
db.runCommand( {
       updateUser: username,
       pwd: password,
       roles: [
           { role: "readWrite", db: "bigcgi-main" },
           { role: "readWrite", db: "bigcgi-cork" },
           { role: "readWrite", db: "bigcgi-logs" },
           { role: "readWrite", db: "bigcgi-reporting" }
       ]
} )

