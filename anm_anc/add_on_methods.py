from accounts.views import conn
import http.client
from pyfcm import FCMNotification
from datetime import date
from datetime import timedelta

cur = conn.cursor()

def address_mapping(id):
    cur.execute(
        "SELECT row_to_json(user_record) FROM (SELECT state,block,division,district  FROM auth_user WHERE id = %s) user_record ",
        (int(id),))
    records = cur.fetchall()
    return (records[0][0])

def get_anm_id(user):
    print(user)
    cur.execute("SELECT anm_id FROM anm_level WHERE anm = %s", (str(user),))
    records_anm = cur.fetchall()
    #print(records_anm)
    anm_id = records_anm[0][0]
    return anm_id


def get_smo_id(user):
    print(user)
    cur.execute("SELECT smo_id FROM anm_level WHERE anm = %s", (str(user),))
    records_smo = cur.fetchall()
    #print(records_smo)
    smo_id = records_smo[0][0]
    return smo_id

def get_smo_name(id):

    cur.execute("SELECT smo FROM smo_level WHERE smo_id = %s", (int(id),))
    records_smo = cur.fetchall()
    #print(records_smo)
    smo_name = records_smo[0][0]
    return smo_name

def notify_smo(officer):
    # sending push notification to mobile device******

    registration_id = "cBRosMLnkgk:APA91bFjDgRkW4wpieK_6kXGg-cx7ueMt514qnhL6Oksi40FcaU4McGXKYBLLQKNLWfv41y4MXwEmwcMFDJgc45HgJi93IL2X-ZONDDx99AKGi7CfLxZgmZvcC8jhKAtluO0DVmtibBi"
    cur.execute("SELECT device_id FROM auth_user WHERE username = %s", (officer,))
    records = cur.fetchall()
    if (len(records) > 0):
        registration_id = records[0][0]

        push_service = FCMNotification(
            api_key="AAAAzxkjakU:APA91bExsgDBynVUmONLnKrm31hTOuN_aKSIwiHwOhCMfNPzANWb2sRdtp7SHHVuoop4BQ34ihUqmv95NH4XMFsQNvzMHqX7V1wEhYXhyncphoaFg94hNrrUa22XTLgHzu4QJU2zQGiX")

        # registration_id = "cBRosMLnkgk:APA91bFjDgRkW4wpieK_6kXGg-cx7ueMt514qnhL6Oksi40FcaU4McGXKYBLLQKNLWfv41y4MXwEmwcMFDJgc45HgJi93IL2X-ZONDDx99AKGi7CfLxZgmZvcC8jhKAtluO0DVmtibBi"
        message_title = "New Patient Added!"
        message_body = "Tap to see details."
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body)
        print(result)
        return True
    return False

# push notification snippet end *****************

def text_to_smo(id,officer,patient):

    cur.execute("SELECT patient_name, address FROM patient_level WHERE patient_id = %s" , (id,))
    records_av = cur.fetchall()
    patient = records_av[0][0]
    #agbdi = records_av[0][1]
    village = records_av[0][1]

    conn_1 = http.client.HTTPConnection("api.msg91.com")
    # sending text message notification to smo
    cur.execute("SELECT mobile FROM auth_user WHERE username = %s", (officer,))
    records = cur.fetchall()
    smo_mobile = records[0][0]

    fix = "High Risk Identified ! " \
          ""
    var = "Patient Name : " + patient + " from Village : " + village + " and Anganbadi : " #+ agbdi
    message = fix + var
    conn_1.request("GET",
                   "/api/sendhttp.php?country=91&sender=MSGIND&route=4&mobiles=%s&authkey=243753Ak8EPySu7Jnp5bcbeaaf&encrypt=&message=%s" % (
                       smo_mobile, message,))

    res = conn_1.getresponse()
    data = res.read()

    print(data.decode("utf-8"))

    return True

def text_to_supervisor(anm_id,p_id):
    cur.execute("SELECT patient_name, address FROM patient_level WHERE patient_id = %s", (id,))
    records_av = cur.fetchall()
    patient = records_av[0][0]
    #agbdi = records_av[0][1]
    village = records_av[0][1]

    cur.execute("SELECT sup_id FROM village_level WHERE anm_id = %s", (anm_id,))
    records = cur.fetchall()
    sup_id = records[0][0]

    cur.execute("SELECT supervisor FROM supervisor_level WHERE sup_id = %s", (sup_id,))
    records = cur.fetchall()
    supervisor = records[0][0]

    cur.execute("SELECT mobile FROM auth_user WHERE username = %s", (supervisor,))
    records = cur.fetchall()
    print(records)
    sup_mobile = records[0][0]
    fix = "High Risk Identified ! " \
          ""
    var = "Patient Name : " + patient + " from Village : " + village + " and Anganbadi : " #+ agbdi
    message = fix + var

    print("supervisor mobile is ", sup_mobile)
    conn_2 = http.client.HTTPConnection("api.msg91.com")
    conn_2.request("GET",
                   "/api/sendhttp.php?country=91&sender=MSGIND&route=4&mobiles=%s&authkey=243753Ak8EPySu7Jnp5bcbeaaf&encrypt=&message=%s" %
                   (sup_mobile, message,))

    res = conn_2.getresponse()
    data = res.read()
    print("message sent to supervisor")
    print(data.decode("utf-8"))

    return True

def visit_schedule(lmp, edd, reg):
    visit_dates = []
    #d_1 = edd.split('-')
    #year_1 = d_1[0]
    #month_1 = int(d_1[1])
    #day_1 = int(d_1[2])
    #d_date = date(year_1,month_1,d_1)

    #d_2 = lmp.split('-')
    #year_2 = d_2[0]
    #month_2 = int(d_2[1])
    #day_2 = int(d_2[2])
    #l_date = date(year_2,month_2,d_2)

    #interval = (l_date-f_date)/4

    v_1_date = lmp + timedelta(days=70)
    v_2_date = lmp + timedelta(days=168)
    v_3_date = lmp + timedelta(days=224)
    v_4_date = lmp + timedelta(days=242)

    #d_r = reg.split('-')
    #year_r = d_r[0]
    #month_r = int(d_r[1])
    #day_r = int(d_r[2])
    #r_date = date(year_r, month_r, day_r)

    if(reg<v_1_date):
        visit_dates.append(v_1_date)

    if(reg<v_2_date):
        visit_dates.append(v_2_date)

    if(reg<v_3_date):
        visit_dates.append(v_3_date)

    if(reg<v_4_date):
        visit_dates.append(v_4_date)

    return visit_dates


def get_visit_number_anm(id):
    cur.execute("SELECT visit_no FROM anm_anc WHERE patient_id = %s" , (id,))
    records_v = cur.fetchall()
    if(len(records_v)==0):
        v_no = 0
    else:
        v_no = records_v[0][0]
    return v_no