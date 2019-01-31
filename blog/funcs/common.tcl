proc func_common_display_tags {tag_list} {
    set rv ""
    foreach tag $tag_list {
	append rv "<span class='tag'>$tag</span>"
    }
    return $rv
}
