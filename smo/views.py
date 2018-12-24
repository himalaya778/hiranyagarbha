from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from django.contrib.auth.decorators import permission_required,login_required
import google.cloud.storage
import uuid
import psycopg2
import json
import re
import datetime
import http.client
import time
from datetime import timedelta
from accounts.views import conn
from pyfcm import FCMNotification
from notify.signals import notify
from django.contrib import messages
from anm_anc.add_on_methods import *
from .smo_add_ons import *
# Create your views here.
# mobile application all APIa
# dashboard
# refer patient
# set visit
# device registeration
# update patient_data on visits

cur = conn.cursor()
###############################################################HIRANYAGARBHA#######################################
@api_view(['GET'])
def check_update(request):
    cur.execute("SELECT * FROM patient_level WHERE high_risk_check = 'true' and notified = False")
    records = cur.fetchall()
    if len(records)>0:
        print(records[0][0])
        cur.execute("UPDATE patient_level SET notified = %s WHERE patient_id = %s", ( True, records[0][0],))
        #conn.commit()
        return Response({'patient_details' : records[0]})
    conn.commit()
    return Response("No Update")

#refer to hospital
@api_view(['POST'])
def refer_patient(request):
    relevant_data = json.loads((request.body))
    patient_id = relevant_data['patient_id']
    reason = relevant_data['reason']
    hospital = relevant_data['hospital']

    cur.execute("UPDATE patient_level SET refer_check = 'true', r_reason = %s, r_hospital = %s WHERE patient_id = %s",(reason,hospital,patient_id))
    print("updated")
    return Response("Patient Referred")

##################smo visit data entry
@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def smo_anc_visit(request):
    id = request.user.id
    anm_id = get_anm_id(request.user)
    smo_id = get_smo_id(request.user)
    relevant_data = json.loads(request.body)
    p_id = relevant_data['patient_id']
    c_ctr = 0
    v_ctr = 0
    hrisk_check = False
    hrisk_factors = ""
    const_factors = ""
    variable_factors = ""
    h_f = []
    c_f = []
    v_f = []

    visit_number = get_visit_number(p_id)

    weight = []
    weight.append(relevant_data['weight'])  # 1
    if (weight[0] < 40 or weight[0] > 90):
        v_ctr += 1
        variable_factors += ('weight ')
    bp1 = []
    bp2 = []
    bp1.append(relevant_data['bp1'])  # 2
    bp2.append(relevant_data['bp2'])  # 3
    if (bp1[0] > 90 or bp2[0] > 140):
        v_ctr += 1
        variable_factors += ('bp ')

    malrep = []                       #4
    malrep.append(relevant_data["malrep"])
    if (not (malrep[0] == None)):
        v_ctr += 1
        variable_factors += ('malrepresentation ')

    gdm = []                            #5
    gdm.append(relevant_data["gdm"])
    if (gdm[0] > 139):
        v_ctr += 1
        variable_factors += ("gdm ")

    anemia = []
    anemia.append(relevant_data['anemia'])  #6
    if (not (anemia[0] == None)):
        v_ctr += 1
        variable_factors += ('anemia ')

    hb = []
    hb.append(relevant_data['hb'])  # 7
    if (hb[0] < 8):
        v_ctr += 1
        variable_factors += ('haemoglobin ')

    thyroid = []
    thyroid.append(relevant_data['thyroid'])  # 8
    if (not (thyroid[0] == 'Normal')):
        v_ctr += 1
        variable_factors += ('thyroid ')

    tobacohol = []
    tobacohol.append(relevant_data['alcohol_tobacco'])  # 9
    if (tobacohol[0] == True):
        v_ctr += 1
        variable_factors += ('alcohol_tobacco ')

    vdrl = []
    vdrl.append(relevant_data['vdrl'])  # 10
    if (vdrl[0] == True):
        v_ctr += 1
        variable_factors += ('vdrl ')

    preg_disease = []
    preg_disease.append(relevant_data['preg_disease'])  # 11
    if (not (preg_disease[0] == 'Adequate')):
        v_ctr += 1
        variable_factors += ('preg_disease ')

    bleeding_check = []
    bleeding_check.append(relevant_data['bleeding_check'])  # 12
    if (bleeding_check[0] == True):
        variable_factors += ('bleeding ')

    iugr = []
    iugr.append(relevant_data['iugr'])  # 13
    if (iugr[0] == True):
        variable_factors += ('iugr ')

    if (c_ctr > 0 or v_ctr > 0):
        hrisk_check = True
        hrisk_factors += (const_factors)
        hrisk_factors += (variable_factors)

    #if (hrisk_check == False):
    #    hrisk_check = relevant_data['hrisk_check']

    h_f.append(hrisk_factors) #14
    c_f.append(const_factors) #15
    v_f.append(variable_factors) #16
    visit_number+=1
    v_date = []
    v_date.append(datetime.date.today())
    cur.execute("""UPDATE smo_anc SET weight=%s::INTEGER[] ,bp_1=%s::INTEGER[] ,bp_2=%s::INTEGER[] ,malrepresentation=%s::TEXT[] ,gdm=%s::INTEGER[] ,anemia=%s::TEXT[] ,
        haemoglobin=%s::INTEGER[] ,thyroid=%s::TEXT[] , alcohol_tobacco_check=%s::BOOLEAN[] ,preg_related_disease=%s::BOOLEAN[] ,bleeding_check=%s::BOOLEAN[] ,iugr=%s::BOOLEAN[] ,
        
        constant_factors=%s::TEXT[] , variable_factors=%s::TEXT[] ,hrisk_factors=%s::TEXT[],smo_id=%s,visits_done=%s,actual_vdate=%s::DATE[] WHERE patient_id = %s""",
                (weight, bp1, bp2, malrep, gdm, anemia, hb, thyroid,
                 tobacohol, preg_disease, bleeding_check, iugr,
                  c_f, v_f, h_f, smo_id,visit_number,v_date,p_id, ))
    conn.commit()
    return Response("Visit " + str(visit_number) +" Data Updated")



##################delivery data entry
@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def delivery_details(request):
    id = request.user.id
    smo_id = find_smo_id(request.user)
    relevant_data = json.loads(request.body)
    p_id = relevant_data['patient_id']
    delivery_status = True
    date_of_del = relevant_data["dod"]
    time_of_del = relevant_data["tod"]
    place_of_del = relevant_data["place"]
    conducted_by = relevant_data["conducted_by"]
    delivery_type = relevant_data["del_type"]
    complications = relevant_data["complications"]
    discharge_date = relevant_data["disch_date"]
    delivery_outcome = relevant_data["d_outcome"]
    live_count = relevant_data["live"]
    still_count = relevant_data["still"]
    baby_weight = relevant_data["b_weight"]
    infant_danger = relevant_data["infant_danger"]

    cur.execute("""INSERT INTO delivery_details (patient_id,dod,tod,place,conducted_by,delivery_type,
    complications, discharge_date, d_outcome, live,still, b_weight, infant_danger) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""" ,
                (p_id,date_of_del, time_of_del, place_of_del, conducted_by, delivery_type, complications, discharge_date, delivery_outcome,live_count,
                 still_count,baby_weight,infant_danger))

    cur.execute("UPDATE patient_level SET delivery_status = TRUE WHERE patient_id = s", (p_id,))

    conn.commit()

    return Response("Delivery Details Saved")

##################pnc visit data
@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def pnc_visit(request):
    id = request.user.id
    smo_id = get_smo_id(request.user)
    relevant_data = json.loads(request.body)
    p_id = relevant_data['patient_id']

    visit_date = relevant_data["v_date"]
    mother_status = relevant_data["m_status"]
    stutch = (relevant_data["stutch"],None)
    color_lochia = relevant_data["color_lochia"]
    oedema = relevant_data["oedema"]
    breast_feeding = relevant_data["breast_feed"]
    breast_infection = relevant_data["breast_infec"]
    infant_danger = relevant_data["danger"]

    cur.execute("""INSERT INTO smo_pnc (patient_id, v_date, mother_status, stutch, color_lochia, oedema,
    breast_feed, breast_infec, infant_danger) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (p_id,visit_date,mother_status,stutch,color_lochia,oedema,
                 breast_feeding,breast_infection, infant_danger))

    conn.commit()

    return Response("PNC Details Saved")

##################pnc visit data
@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def final_visit(request):
    id = request.user.id
    smo_id = get_smo_id(request.user)
    relevant_data = json.loads(request.body)
    p_id = relevant_data['patient_id']

    maternal_status = relevant_data["m_status"]

    cur.execute("UPDATE smo_pnc SET maternal_status = %s WHERE patient_id = %s",(maternal_status,p_id))
    conn.commit()

    return Response("Maternal Status Saved")

@api_view(['POST'])
def set_visit(request):
    relevant_data = json.loads(request.body)
    patient_id = relevant_data['patient_id']
    s_date = relevant_data['date']
    array_date = []
    array_date.append(s_date)
    print(array_date)
    #s_time = relevant_data['time']

    cur.execute("UPDATE patient_level  SET visit_schedule = visit_schedule || %s::DATE[] , v_scheduled = 'true' WHERE patient_id = %s ", (array_date, patient_id,))

    cur.execute(" SELECT visit_schedule FROM patient_level WHERE patient_id = %s", (patient_id,))
    records = cur.fetchall()
    print("records length : " , len(records))
    print("records[0] length : " , len(records[0]))
    print("records [0][0] length " , len(records[0][0]))
    print("dates array ", records[0][0])

    conn.commit()
    return Response("3 visits already sceduled")


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def device_registeration(request):
    relevant_data = json.loads(request.body)
    device_id = relevant_data["reg_token"]
    cur.execute("UPDATE auth_user SET device_id = %s WHERE username = %s" , (device_id ,str(request.user), ))
    conn.commit()
    return Response("Registeration Token Saved")

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def update_patient_data(request):
    sample = []
    var_sample = []
    relevant_data = json.loads(request.body)
    #visit_number = relevant_data["visit_no"]
    patient_id = relevant_data["patient_id"]
    cur.execute(" SELECT doctor_visits FROM patient_level WHERE patient_id = %s", (patient_id,))
    records = cur.fetchall()
    print("visit number " , records[0][0])

    visit_number = int(records[0][0])

    cur.execute("SELECT visit_data FROM patient_level WHERE patient_id = %s" , (patient_id,))
    records = cur.fetchall()
    if(records[0][0] == None):
        visit_data = []
    else:
        visit_data = records[0][0]

    cur.execute("SELECT var_reasons FROM patient_level WHERE patient_id = %s" , (patient_id,))
    records = cur.fetchall()
    if(records[0][0] == None):
        var_reasons = []
    else:
        var_reasons = records[0][0]
    #var_reasons = []

    sample.append(str(datetime.date.today()))
    new_weight = relevant_data["weight"]
    sample.append(new_weight)

    new_bp1 = int(relevant_data["bp1"])
    sample.append(new_bp1)
    new_bp2 = int(relevant_data["bp2"])
    sample.append(new_bp2)
    if (new_bp1 > 130 or new_bp2 > 90):
        print("bp is the reason")
        var_check = "yes"

        var_sample.append("bp")
    else:
        var_sample.append('')

    new_sugar = int(relevant_data["sugar"])
    sample.append(new_sugar)

    if (new_sugar > 139):
        print("sugar is the reason")
        var_check = "yes"
        var_sample.append("sugar")
    else:
        var_sample.append('')

    new_haemoglobin = int(relevant_data["haemoglobin"])
    sample.append(new_haemoglobin)
    if (new_haemoglobin < 10):
        print("haemoglobin is the reason")
        var_check = "yes"
        #high_risk_check = True
        var_sample.append("haemoglobin")
    else:
        var_sample.append('')

    new_dietary_advice = relevant_data["dietary_advice"]
    sample.append(new_dietary_advice)

    new_image_link = relevant_data["image_url"]
    sample.append(new_image_link)

    visit_number+=1
    visit_data.append(sample)

    #var_sample.append('')
    var_reasons.append(var_sample)
    print("var reasons is " , var_reasons)
    improv2 = []
    if(visit_number==2):
        print("visit 2 improvement being checked")
        for v in var_reasons[1]:
            print(v)
            if(not v in var_sample):
                improv2.append(v)

        cur.execute("UPDATE patient_level SET visit_data = %s::TEXT[][], var_reasons = %s::TEXT[][],doctor_visits=%s,improv2=%s::TEXT[] WHERE patient_id = %s"
                    , (visit_data,var_reasons,visit_number,improv2,patient_id,))

    if (visit_number == 3):
        improv3 = []
        for v in var_reasons[2]:
            if(not v in var_sample):
                improv3.append(v)

        cur.execute(
            "UPDATE patient_level SET visit_data = %s::TEXT[][], var_reasons = %s::TEXT[][],doctor_visits=%s,improv3=%s::TEXT[] WHERE patient_id = %s"
            , (visit_data, var_reasons, visit_number, improv3, patient_id,))

    if (visit_number == 4):
        improv4 = []
        for v in var_reasons[3]:
            if(not v in var_sample):
                improv4.append(v)

        cur.execute(
            "UPDATE patient_level SET visit_data = %s::TEXT[][], var_reasons = %s::TEXT[][],doctor_visits=%s,improv4=%s::TEXT[] WHERE patient_id = %s"
            , (visit_data, var_reasons, visit_number, improv4, patient_id,))

    print("visit data is " , visit_data)
    cur.execute(
        "UPDATE patient_level SET visit_data = %s::TEXT[][], var_reasons = %s::TEXT[][],doctor_visits=%s WHERE patient_id = %s"
        , (visit_data, var_reasons, visit_number, patient_id,))

    conn.commit()
    #testing output
    cur.execute("SELECT visit_data FROM patient_level WHERE patient_id = %s" , (patient_id,))
    records = cur.fetchall()
    print("visit data length: " , len(records))
    print("visit_data[0] length " , len(records[0]))
    print("visit data[0][0] length " ,len(records[0][0]))
    print("visit data is " , records[0][0])
    ##

    cur.execute("SELECT var_reasons FROM patient_level WHERE patient_id = %s" , (patient_id,))
    records = cur.fetchall()
    print("var_reasons length: " , len(records))
    print("var_reasons[0] length " , len(records[0]))
    print("var_reasons[0][0] length " ,len(records[0][0]))
    print(records[0][0])
    conn.commit()
    return Response("Data already saved for 3 visits!!")

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def app_data(request):
    cur.execute("SELECT smo_id FROM smo_level WHERE smo = %s" , (str(request.user),))
    records_bmo = cur.fetchall()
    smo_id = records_bmo[0]
    print("get " ,request.GET)
    start = int(request.GET.get('start',1))
    patients = []
    cur.execute(
        "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE smo_id = %s and high_risk_check = 'true' ) patient_record",( smo_id,))
    records = cur.fetchall()
    for r in records:
        patients.append(r[0])
    print(len(records))
    end = (start+25)
    return Response({"patients" : patients[start:end]})

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def full_patient_details_app(request):
    relevant_data = json.loads(request.body)
    p_id = relevant_data["id"]
    cur.execute(
        "SELECT row_to_json(user_record) FROM (SELECT *  FROM patient_level WHERE patient_id = %s) user_record ", (int(p_id),))
    records = cur.fetchall()
    print(records[0][0])
    return Response({"patients" :  records[0]})