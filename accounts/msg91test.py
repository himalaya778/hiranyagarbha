import http.client
conn_1 = http.client.HTTPConnection("api.msg91.com")
# sending text message notification to smo

def text_to_user(name,password,role,mobile):

    if(role=="anm"):


        fix =  "Welcome to Hiranyagarbha Smart portal" \
                   ""
        var = "User : "  + " Pass : "
        message = fix+var
        conn_1.request("GET",
                           "/api/sendhttp.php?country=91&sender=MSGIND&route=4&mobiles=%s&authkey=243753Ak8EPySu7Jnp5bcbeaaf&encrypt=&message=%s" % (
                           '9521466943', message,))

        res = conn_1.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

    if (role=="smo"):
        fix = """ Welcome to Hiranyagarbha Smart portal """ \
              ""
        var = "Username : " + str(name) + " Password : " + str(password)
        message = fix + var
        conn_1.request("GET",
                       "/api/sendhttp.php?country=91&sender=MSGIND&route=4&mobiles=%s&authkey=243753Ak8EPySu7Jnp5bcbeaaf&encrypt=&message=%s" % (
                           mobile, message,))

        res = conn_1.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

    if (role=="bmo"):
        fix = """ Welcome to Hiranyagarbha Smart portal \n You've successfully been registered. \n Download app from here- XXXX (ANM App)
        For guide follow this link- XXXX \n Helpline- 9789XXXX8970\n""" \
              ""
        var = "Username : " + str(name) + " Password : " + str(password)
        message = fix + var
        conn_1.request("GET",
                       "/api/sendhttp.php?country=91&sender=MSGIND&route=4&mobiles=%s&authkey=243753Ak8EPySu7Jnp5bcbeaaf&encrypt=&message=%s" % (
                           mobile, message,))

        res = conn_1.getresponse()
        data = res.read()
        print(data.decode("utf-8"))


    return ("Text Sent")