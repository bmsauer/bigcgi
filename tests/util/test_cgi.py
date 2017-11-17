import util.cgi

def test_parse_output():
    output = "Content-Type: application/json\nStatus: 201\n\nhello world"
    headers, body = util.cgi.parse_output(output)
    assert headers["Content-Type"] == "application/json"
    assert headers["Status"] == "201"
    assert body == "hello world"
