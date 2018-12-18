#!/usr/bin/env tclsh8.6
package require Tcl 8.6
package require tdbc::postgres
package require json::write
package require inifile
source bcgi.tcl

##config
set config [::ini::open "files/config.ini"]
set blog_db_hostname [::ini::value config blog_db_username]
set blog_db_password [::ini::value config blog_db_password]
set blog_db_database [::ini::value config blog_db_database]

## global vars
set output [list]
tdbc::postgres::connection create db -host $blog_db_hostname -user $blog_db_username -password $blog_db_password -database $blog_db_database

## procs
proc get_post {id} {
    dict set query_values id $id
    set rows [get_all_rows_sql {select id, title, content, date from blog_posts WHERE id = :id} $query_values]
    if { [llength $rows] > 0 } {
	set record [lindex $rows 0]
	set result [build_json_from_row $record]
	return $result
    } else {
	set result [json::write object \
			error [json::write string "post with id $id not found"]
		    ]
	return $result
    }
}

proc get_all {page pagesize} {
    dict set query_values limit $pagesize
    dict set query_values offset [expr {$pagesize * ($page - 1)}]
    set rows [get_all_rows_sql {SELECT id, title, content, date from blog_posts ORDER BY date desc LIMIT :limit OFFSET :offset} $query_values]
    if { [llength $rows] > 0 } {
	set result_rows [list]
	foreach {row} $rows {
	    set post [build_json_from_row $row]
	    lappend result_rows $post
	}
	set result [json::write object posts [json::write array {*}$result_rows] ]
	return $result
    } else {
	set result [json::write object \
			error [json::write string "posts not found"]
		    ]
	return $result
    }
}

proc get_tags_for_post {post_id} {
    set tags [list]
    set stmt [db prepare {SELECT tag FROM blog_tags WHERE post_id = :post_id}]
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
    foreach {row} $rows {
	lappend tags [json::write string [lindex $row 1]]
    }
    return $tags
}

proc build_json_from_row {row} {
    set post_id [lindex $row 1]
    set tags [get_tags_for_post $post_id]
    set post [json::write object \
		  id [json::write string [lindex $row 1] ] \
		  title [json::write string [lindex $row 3] ] \
		  content [json::write string [lindex $row 5] ] \
		  date [json::write string [lindex $row 7] ] \
		  tags [json::write array {*}$tags] \
		 ]
    return $post
}

proc get_all_rows_sql {sql {query_values ""}} {
    set rows [list]
    set stmt [db prepare $sql]
    try {
	set res [$stmt execute $query_values]
	try {
	    set rows [$res allrows]
	} finally {
	    $res close
	}
    } finally {
	$stmt close
    }
    return $rows
}

proc main {} {
    if { $::env(REQUEST_METHOD) == "GET" } {
	set query [parse_query_string $::env(QUERY_STRING)]
	set id [expr {[dict exist $query id] == 0  ? "" : [dict get $query id]}]
	set page [expr {[dict exist $query page] == 0 ? 1 : [dict get $query page]}]
	set pagesize [expr {[dict exist $query pagesize] == 0 ? 10 : [dict get $query pagesize]}]
	if { $id == ""} {
	    lappend output [get_all $page $pagesize]
	} else {
	    lappend output [get_post $id]
	}
    } else {
	lappend output "method not allowed"
    }

    output_headers application/json Access-Control-Allow-Origin *
    foreach {line} $output {
	puts "$line"
    }
}

if { ![info exists _testing] } { #if _testing var not set, do main
    main
}
	
