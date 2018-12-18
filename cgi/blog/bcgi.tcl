#bcgi: snippets grabbed from ncgi
package require Tcl 8.6

proc url_decode {str} {
    # rewrite "+" back to space
    # protect \ from quoting another '\'
    set str [string map [list + { } "\\" "\\\\" \[ \\\[ \] \\\]] $str]

    # prepare to process all %-escapes
    regsub -all -- {%([Ee][A-Fa-f0-9])%([89ABab][A-Fa-f0-9])%([89ABab][A-Fa-f0-9])} \
	$str {[encoding convertfrom utf-8 [DecodeHex \1\2\3]]} str
    regsub -all -- {%([CDcd][A-Fa-f0-9])%([89ABab][A-Fa-f0-9])}                     \
	$str {[encoding convertfrom utf-8 [DecodeHex \1\2]]} str
    regsub -all -- {%([0-7][A-Fa-f0-9])} $str {\\u00\1} str

    # process \u unicode mapped chars
    return [subst -novar $str]
}

proc get_body {} {
    set body ""
    if {[info exists ::env(CONTENT_LENGTH)] &&
	[string length $::env(CONTENT_LENGTH)] != 0} {
	fconfigure stdin -translation binary -encoding binary
	set body [read stdin $::env(CONTENT_LENGTH)]
    }
    return $body
}
    

proc parse_query_string {query} {
    set result [dict create]
    foreach {x} [split [string trim $query] &] {
	set pos [string first = $x]
	set len [string length $x]
	
	if { $pos>=0 } {
	    if { $pos == 0 } { # if the = is at the beginning ...
		if { $len>1 } { 
		    # ... and there is something to the right ...
		    set varname anonymous
		    set val [string range $x 1 end]
		} else { 
		    # ... otherwise, all we have is an =
		    set varname anonymous
		    set val ""
		}
	    } elseif { $pos==[expr {$len-1}] } { 
		# if the = is at the end ...
		set varname [string range $x 0 [expr {$pos-1}]]
		set val ""
	    } else {
		set varname [string range $x 0 [expr {$pos-1}]]
		set val [string range $x [expr {$pos+1}] end]
	    }
	} else { # no = was found ...
	    set varname anonymous
	    set val $x
	}		
	dict set result [url_decode $varname] [url_decode $val]
    }
    return $result
}


proc output_headers {{type text/html} args} {
    puts "Content-Type: $type"
    foreach {n v} $args {
	puts "$n: $v"
    }
    puts ""
    flush stdout
}
