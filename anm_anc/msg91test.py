import http.client
conn_1 = http.client.HTTPConnection("api.msg91.com")
# sending text message notification to smo


fix =  "High Risk Identified ! " \
               ""
var = "Patient Name : " +  " and Anganbadi : "
message = fix+var
conn_1.request("GET",
                       "/api/sendhttp.php?country=91&sender=MSGIND&route=4&mobiles=%s&authkey=243753Ak8EPySu7Jnp5bcbeaaf&encrypt=&message=%s" % (
                       '8766288377', message,))

res = conn_1.getresponse()
data = res.read()
print(data.decode("utf-8"))