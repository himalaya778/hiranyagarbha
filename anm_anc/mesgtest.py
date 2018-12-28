import http.client
conn_1 = http.client.HTTPConnection("api.msg91.com")

fix =  "Hiranyagarbha %0a" \
               ""
var = "USER: " + "chc_manakany_babai" + " PASS: " + "8766288377"
message = fix+var
conn_1.request("GET","/api/sendhttp.php?country=91&sender=MSGIND&route=4&mobiles=%s&authkey=243753Ak8EPySu7Jnp5bcbeaaf&encrypt=&message=%s" % (
                       '8766288377', message,))

print(len(message))
res = conn_1.getresponse()
data = res.read()
print(data.decode("utf-8"))