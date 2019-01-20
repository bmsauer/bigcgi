package require Tcl 8.5

proc get_slug {title} {
    set slug $title
    set slug [string map {. "" , "" \\ "" / "" ~ "" ` "" ! "" @ "" # "" $ "" % "" ^ "" & "" * "" ( "" ) ""  | "" : "" \" "" \' "" < "" > "" ? "" = "" + "" _ "" \{ "" \} "" \[ "" \] "" }  $slug]
    set slug [string trim $slug]
    set slug [string map {" " "-"} $slug]
    set slug [string tolower $slug]
    return $slug
}

proc render_template {template_filename {contents_filename {}} {other_vars {}} } {
    if { [llength $other_vars] != 0 } {
	foreach var $other_vars {
	    upvar $var $var
	}
    }
    if { [llength $contents_filename] != 0 } {
	source $contents_filename
    }
    set template [open $template_filename r]
    set template_contents [read $template]
    set output [subst $template_contents]
    close $template
    return $output
}

proc write_contents {contents filename} {
    set fileout [open $filename w]
    puts $fileout $contents
    close $fileout
}

proc compare_posts { a b } {
    set a_seconds [clock scan [lindex $a 1] -format "%Y-%m-%d"]
    set b_seconds [clock scan [lindex $b 1] -format "%Y-%m-%d"]
    if {$a_seconds == $b_seconds} {
	return 0
    } elseif { $a_seconds > $b_seconds } {
	return 1
    } else {
	return -1
    }
}

proc compile_content {} {
    set filenames [glob "content/*"]
    set posts [list]
    foreach filename $filenames {
	#get content, set vars
	source $filename
	lappend posts [list $title $date $tags]
	#render template
	set output [render_template "templates/post.html" $filename]
	#dump file
        write_contents $output "dist/[get_slug $title].html"
    }
    return $posts
}

proc compile_index {posts} {
    set posts [lsort -command compare_posts $posts]
    set list_of_posts ""
    foreach post_data $posts {
	set title [lindex $post_data 0]
	set date [lindex $post_data 1]
	set tags [lindex $post_data 2]
	append list_of_posts "<a href=\"[get_slug $title].html\"><h2>$title</h2></a><br> $date $tags<br>"
    }
    set title "bigCGI Blog Home"
    #render template
    set output [render_template "templates/index.html" "pages/index.tcl"  {list_of_posts title}]
    #dump file
    write_contents $output "dist/index.html"
}

proc compile_assets {} {
    exec cp -R assets dist/assets
}

exec rm -rf dist
exec mkdir dist
set posts [compile_content]
compile_index $posts
compile_assets

puts done