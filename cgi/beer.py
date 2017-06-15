#!/usr/local/bin/python3.5
import cgi
import cgitb; cgitb.enable()  # for troubleshooting

filled = False

form = cgi.FieldStorage()
if "cents" in form and "containers" in form and "ounces" in form:
    cents = form.getvalue("cents")
    containers = form.getvalue("containers")
    ounces = form.getvalue("ounces")

    price_per_ounce = float(cents) / (float(containers) * float(ounces))
    price_per_ounce = round(price_per_ounce,3)
    
    filled = True
else:
    filled = False



print("Content-type: text/html")
print("") 

print("<html>")
print("<head>")
print("<title>Beer Price Calculator</title>")
print("</head>")
print("<body>")
if filled == True:
    print("Price per ounce: {}".format(price_per_ounce))
print("""
<form method='POST'>
<label for='cents'>Cents</label>
<input type='text' name='cents' />
<label for='containers'>Containers</label>
<input type='text' name='containers' />
<label for='ounces'>Ounces</label>
<input type='text' name='ounces' />
<input type='submit' />
</form>
""")
print("</body>")
print("</html>")

