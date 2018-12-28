import http.client
conn_1 = http.client.HTTPConnection("api.msg91.com")
# sending text message notification to smo

def text_to_user(name,password,mobile):
    print(mobile)
    fix =  "Namaskar" \
               ""
    var = "username : " + name + " password : " + password
    message = fix+var
    conn_1.request("GET",
                       "/api/sendhttp.php?country=91&sender=MSGIND&route=4&mobiles=%s&authkey=243753Ak8EPySu7Jnp5bcbeaaf&encrypt=&message=%s" % (
                       (mobile), message,))

    res = conn_1.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    return ("Text Sent")