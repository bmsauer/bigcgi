#!/usr/local/bin/python3.5
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import json

form = cgi.FieldStorage()
if "cents" in form and "containers" in form and "ounces" in form:
    cents = form.getvalue("cents")
    containers = form.getvalue("containers")
    ounces = form.getvalue("ounces")

    price_per_ounce = float(cents) / (float(containers) * float(ounces))
    price_per_ounce = round(price_per_ounce,3)
    
    response = {
        "cents": cents,
        "containers": containers,
        "ounces": ounces,
        "price_per_ounce": price_per_ounce
    }
else:
    response = {"error": "Invalid arguments"}

print("Content-type: application/json")
print("")
print(json.dumps(response))

