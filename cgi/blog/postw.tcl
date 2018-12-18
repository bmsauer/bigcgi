#!/usr/bin/env tclsh8.6
package require Tcl 8.6
package require tdbc::postgres
package require json
package require json::write
source bcgi.tcl

##config
set config [::ini::open "files/config.ini"]
set blog_db_hostname [::ini::value config blog_db_username]
set blog_db_password [::ini::value config blog_db_password]
set blog_db_database [::ini::value config blog_db_database]

## global vars
set output [list]
tdbc::postgres::connection create db -host $blog_db_hostname -user $blog_db_username -password $blog_db_password -database $blog_db_database

proc parse_json {} {
    set raw_json [get_body]
    set d [json::json2dict $raw_json]
    return $d
}

proc create_post {data} {
    set content [dict get $data content]
    set title [dict get $data title]
    set tags [dict get $data tags]
    set stmt [db prepare {INSERT INTO blog_posts (content, title, date) VALUES (:content, :title, CURRENT_TIMESTAMP) RETURNING id, date} ]
    try {
	set res [$stmt execute]
	try {
	    set rows [$res allrows]
	} finally {
	    $res close
	}
    } finally {
	$stmt close
    }
    set post_id [lindex [lindex $rows 0] 1]
    set date [lindex [lindex $rows 0] 3]
    set json_tags [list]
    foreach {tag} $tags {
	set stmt [db prepare {INSERT INTO blog_tags (post_id, tag) VALUES (:post_id, :tag)} ]
	try {
	    set res [$stmt execute]
	    lappend json_tags [json::write string $tag]
	} finally {
	    $stmt close
	}
    }
    set post [json::write object \
		  id [json::write string $post_id ] \
		  title [json::write string $title ] \
		  content [json::write string $content ] \
		  date [json::write string $date ] \
		  tags [json::write array {*}$json_tags] \
		 ]
    return $post
}

proc delete_post {data} {
    set id [dict get $data id]
    set stmt [db prepare {DELETE FROM blog_tags WHERE post_id = :id} ]
    try {
	set res [$stmt execute]
	try {
	    set rows [$res allrows]
	} finally {
	    $res close
	}
    } finally {
	$stmt close
    }
    set stmt [db prepare {DELETE FROM blog_posts WHERE id = :id} ]
    try {
	set res [$stmt execute]
	try {
	    set rows [$res allrows]
	} finally {
	    $res close
	}
    } finally {
	$stmt close
    }
    return [json::write object success [json::write string "true"] ]
}

proc main {} {
    if { $::env(REQUEST_METHOD) == "POST" } {
	#create
	if { [catch { set data [parse_json] } err] } {
	    set result [json::write object \
			    error [json::write string "failed to parse json: $err"]
		       ]
	} elseif { [catch { set result [create_post $data] } err] } {
	    set result [json::write object \
			    error [json::write string "failed to create post: $err"]
		       ]
	}
	lappend output $result
    } elseif {$::env(REQUEST_METHOD) == "DELETE"} {
	#delete
	if { [catch { set data [parse_json] } err] } {
	    set result [json::write object \
			    error [json::write string "failed to parse json: $err"]
		       ]
	} elseif { [catch { set result [delete_post $data] } err] } {
	    set result [json::write object \
			    error [json::write string "failed to delete post: $err"]
		       ]
	}
	lappend output $result
    } else {
	set result [json::write object \
			    error [json::write string "method not allowed"]
		   ]
	lappend output $result
    }

    output_headers application/json Access-Control-Allow-Origin *
    foreach {line} $output {
	puts "$line"
    }
}

if { ![info exists _testing] } { #if _testing var not set, do main
    main
}
	
