from django.shortcuts import render
# Create your views here.
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
import time
from datetime import timedelta
from accounts.views import conn
from pyfcm import FCMNotification
############################################################################################################################################################################3
#Establishing conection with Database
#conn = psycopg2.connect("dbname=lewjwtyv user=lewjwtyv password=mQJ6jIVit_1IR0vhvauSh7Bi9-kTZqe5 host='baasu.db.elephantsql.com'")
#conn = psycopg2.connect("dbname=hiranya user=postgres password=1234 host=localhost")
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

@api_view(['POST'])
def set_visit(request):
    relevant_data = json.loads(request.body)
    patient_id = relevant_data['patient_id']
    s_date = relevant_data['date']
    array_date = []
    array_date.append(s_date)
    #s_time = relevant_data['time']

    cur.execute("UPDATE patient_level  SET visit_schedule = visit_schedule || %s::DATE[] WHERE patient_id = %s ", (array_date, patient_id,))

    cur.execute(" SELECT visit_schedule FROM patient_level WHERE patient_id = %s", (patient_id,))
    records = cur.fetchall()
    print("records length : " , len(records))
    print("records[0] length : " , len(records[0]))
    print("records [0][0] length " , len(records[0][0]))
    print("dates array ", records[0][0])

    #if (records[0][0] == None):

     #   cur.execute("UPDATE patient_level  SET v_1_date = %s WHERE patient_id = %s " , (s_date,patient_id,))
     #   #cur.execute("UPDATE patient_level SET visit_time[0] =  %s WHERE patient_id = %s ", (s_time, patient_id,))
     #   cur.execute("UPDATE patient_level SET v_scheduled =  'true' WHERE patient_id = %s ", ( patient_id,))
     #   conn.commit()
     #   return Response("Visit  1 Scheduled")
    #if (records[0][0]["v_2_date"] == None):
     #   cur.execute("UPDATE patient_level  SET v_2_date = %s WHERE patient_id = %s ", (s_date, patient_id,))
     #   #cur.execute("UPDATE patient_level SET visit_time[1] =  %s WHERE patient_id = %s ", (s_time, patient_id,))
     #   cur.execute("UPDATE patient_level SET v_scheduled =  'true' WHERE patient_id = %s ", (patient_id,))
     #   conn.commit()
     #   return Response("Visit 2 Scheduled")

    #if (records[0][0]["v_2_date"] == None):
     #   cur.execute("UPDATE patient_level  SET v_3_date = %s WHERE patient_id = %s ", (s_date, patient_id,))
     #   #cur.execute("UPDATE patient_level SET visit_time[2] =  %s WHERE patient_id = %s ", (s_time, patient_id,))
     #   cur.execute("UPDATE patient_level SET v_scheduled =  'true' WHERE patient_id = %s ", (patient_id,))
     #   conn.commit()
     #   return Response("Visit 3 Scheduled")
    conn.commit()
    return Response("3 visits already sceduled")

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

    sample.append(visit_number)
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
    if (new_sugar < 100):
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
    end = (start+5)
    return Response({"patients" : patients[start:end]})

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def village_create(request):
    print( " body is : " , request.body)
    relevant_data = json.loads(request.body)

    v_name = relevant_data['name']
    v_pop = relevant_data['population']
    v_pop = int(v_pop)
    print(v_name)
    print( " data is  : " ,request.data)
    user_id = request.user.id
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    bmo_id = records_1[0][0]
    cur.execute('SELECT state, division, block, district FROM auth_user WHERE id = %s', (user_id,))
    h_records = cur.fetchall()
    print(h_records)
    state = h_records[0][0]
    division = h_records[0][1]
    block = h_records[0][2]
    district = h_records[0][3]

    cur.execute("INSERT INTO village_level(village,bmo_id,state,division,block,district,population) VALUES(%s,%s,%s,%s,%s,%s,%s)",(v_name ,bmo_id,state,division,block,district,v_pop) )
    conn.commit()
    return Response('village added')

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def agbdi_create(request):

    print( " body is : " , request.body)
    relevant_data = json.loads(request.body)
    v_name = relevant_data['anganbadi']
    worker_name = relevant_data['username']
    print(request.user)
    print( " data is  : " ,request.data)
    user_id = request.user.id
    cur.execute("SELECT cdpo_id FROM cdpo_level WHERE cdpo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    cdpo_id = records_1[0][0]

    cur.execute('SELECT state, division, block, district FROM auth_user WHERE id = %s', (user_id,))
    h_records = cur.fetchall()
    print(h_records)
    state = h_records[0][0]
    division = h_records[0][1]
    block = h_records[0][2]
    district = h_records[0][3]
    cur.execute("INSERT INTO anganbadi_level(agbdi,cdpo_id,worker,state,division,block,district) VALUES(%s,%s,%s,%s,%s,%s,%s)",(v_name , cdpo_id,worker_name,state,division,block,district,) )
    conn.commit()
    return Response('anganbadi added')

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def smo_dropdown(request):
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    bmo_id = records_1[0][0]
    cur.execute(""" SELECT  bmo_level.bmo_id,
                            smo_level.smo
                            FROM
                            bmo_level
                            INNER JOIN smo_level ON smo_level.bmo_id = bmo_level.bmo_id """)

    records = cur.fetchall()
    dropdown_data = []
    for i in range(len(records)):
        if records[i][0] == bmo_id:
            print(records[i])
            dropdown_data.append(records[i][1])

    result = {"smo_list" : dropdown_data}
    return Response(result)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def anm_dropdown(request):
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    bmo_id = records_1[0][0]
    cur.execute(""" SELECT  bmo_level.bmo_id,
                            anm_level.anm
                            FROM
                            bmo_level
                            INNER JOIN anm_level ON anm_level.bmo_id = bmo_level.bmo_id """)

    records = cur.fetchall()
    print(records)
    dropdown_data = []

    for i in range(0,len(records)):
        if records[i][0] == bmo_id:
            dropdown_data.append(records[i][1])

    result = {"anm_list": dropdown_data}
    return Response(result)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def village_dropdown(request):
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    bmo_id = records_1[0][0]
    cur.execute(""" SELECT  bmo_level.bmo_id,
                            village_level.village
                            FROM
                            bmo_level
                            INNER JOIN village_level ON village_level.bmo_id = bmo_level.bmo_id """)

    records = cur.fetchall()
    dropdown_data = []

    for i in range(len(records)):
        if records[i][0] == bmo_id:
            dropdown_data.append(records[i][1])

    result = {"village_list": dropdown_data}
    return Response(result)
    return Response(result)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def all_drop_down(request):
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    bmo_id = records_1[0][0]
    cur.execute(""" SELECT  bmo_level.bmo_id,
                            smo_level.smo
                            FROM
                            bmo_level
                            INNER JOIN smo_level ON smo_level.bmo_id = bmo_level.bmo_id """)

    records_smo = cur.fetchall()
    dropdown_data_smo = []
    for i in range(len(records_smo)):
        if records_smo[i][0] == bmo_id:
            print(records_smo[i])
            dropdown_data_smo.append(records_smo[i][1])

    cur.execute(""" SELECT  bmo_level.bmo_id,
                            anm_level.smo_id,
                            anm_level.anm
                            FROM
                            bmo_level
                            INNER JOIN anm_level ON anm_level.bmo_id = bmo_level.bmo_id """)


    records_anm = cur.fetchall()
    print(records_anm)
    dropdown_data_anm = []

    for i in range(0,len(records_anm)):
        if records_anm[i][0] == bmo_id:
            dropdown_data_anm.append(records_anm[i][2])

    cur.execute(""" SELECT  bmo_level.bmo_id,
                            village_level.anm_id,
                            village_level.village
                            FROM
                            bmo_level
                            INNER JOIN village_level ON village_level.bmo_id = bmo_level.bmo_id """)

    records_village = cur.fetchall()
    dropdown_data_village = []

    for i in range(len(records_village)):
        if records_village[i][0] == bmo_id :
            dropdown_data_village.append(records_village[i][2])
    result= {"smo_list" : dropdown_data_smo , "anm_list" : dropdown_data_anm , "village_list" : dropdown_data_village}

    return Response(result)

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def link_smo_anm(request):
    print( " body is : " , request.body)
    relevant_data = json.loads(request.body)
    smo = relevant_data['smo']
    anm = relevant_data['anm']
    #smo = 'Dr. Maha Shankar'
    #anm = ['sunita', 'Bharti Devi']
    cur.execute("SELECT smo_id FROM smo_level WHERE smo=%s", (smo,))
    records = cur.fetchall()
    smo_id = records[0][0]
    print(smo_id)
    # cur.execute("SELECT anm FROM anm_level WHERE anm = %s" , ('Sunita'))
    for i in range(0,len(anm)):
        cur.execute("UPDATE anm_level SET smo_id = %s WHERE anm = %s", (smo_id, anm[i],))
    conn.commit()
    return Response('Anm Linked With Smo')

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def link_anm_village(request):
    print( " body is : " , request.body)
    relevant_data = json.loads(request.body)
    villages = relevant_data['village']
    anm = relevant_data['anm']
    #smo = 'Dr. Maha Shankar'
    #anm = ['sunita', 'Bharti Devi']
    cur.execute("SELECT anm_id FROM anm_level WHERE anm=%s", (anm,))
    records = cur.fetchall()
    anm_id = records[0][0]
    print(anm_id)
    # cur.execute("SELECT anm FROM anm_level WHERE anm = %s" , ('Sunita'))
    for i in range(0,len(villages)):
        cur.execute("UPDATE village_level SET anm_id = %s WHERE village = %s", (anm_id, villages[i],))
    conn.commit()
    return Response('Villages Linked With Anm')

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def check_link(request):
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    bmo_id = records_1[0][0]
    cur.execute(""" SELECT  bmo_level.bmo_id,
                            bmo_level.bmo,
                            smo_level.smo,
                            anm_level.anm,
                            village_level.village
                            FROM
                            bmo_level
                            INNER JOIN smo_level ON smo_level.bmo_id = bmo_level.bmo_id
                            INNER JOIN anm_level ON anm_level.smo_id = smo_level.smo_id
                            INNER JOIN village_level ON village_level.anm_id = anm_level.anm_id""")

    records = cur.fetchall()
    links = []
    for i in range(0,len(records)):
        if (records[i][0] == bmo_id):
            links.append(records[i])

    print(records)
    result = {"links" : links}

    return Response(result)

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def link_sup_village(request):
    print( " body is : " , request.body)
    relevant_data = json.loads(request.body)
    villages = relevant_data['villages']
    sup = relevant_data['sup']
    #smo = 'Dr. Maha Shankar'
    #anm = ['sunita', 'Bharti Devi']
    cur.execute("SELECT sup_id FROM supervisor_level WHERE supervisor=%s", (sup,))
    records = cur.fetchall()
    sup_id = records[0][0]
    print(sup_id)
    # cur.execute("SELECT anm FROM anm_level WHERE anm = %s" , ('Sunita'))
    for i in range(0,len(villages)):
        cur.execute("UPDATE village_level SET sup_id = %s WHERE village = %s", (sup_id, villages[i],))
    conn.commit()
    return Response('Villages Linked With supervisor')

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def link_village_agbdi(request):
    print( " body is : " , request.body)
    relevant_data = json.loads(request.body)
    agbdis = relevant_data['agbdis']
    village = relevant_data['village']
    #smo = 'Dr. Maha Shankar'
    #anm = ['sunita', 'Bharti Devi']
    cur.execute("SELECT village_id FROM village_level WHERE village=%s", (village,))
    records = cur.fetchall()
    village_id = records[0][0]
    print(village_id)
    # cur.execute("SELECT anm FROM anm_level WHERE anm = %s" , ('Sunita'))
    for i in range(0,len(agbdis)):
        cur.execute("UPDATE anganbadi_level SET village_id = %s WHERE agbdi = %s", (village_id, agbdis[i],))
    conn.commit()
    return Response('Anganbadi Linked With Village')

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def link_agbdi_worker(request):
    print( " body is : " , request.body)
    relevant_data = json.loads(request.body)
    agbdi = relevant_data['agbdi']
    workers = relevant_data['workers']
    #smo = 'Dr. Maha Shankar'
    #anm = ['sunita', 'Bharti Devi']
    cur.execute("SELECT agbdi_id FROM anganbadi_level WHERE agbdi=%s", (agbdi,))
    records = cur.fetchall()
    agbdi_id = records[0][0]
    print(agbdi_id)
    # cur.execute("SELECT anm FROM anm_level WHERE anm = %s" , ('Sunita'))
    for i in range(0,len(workers)):
        cur.execute("UPDATE worker_level SET agbdi_id = %s WHERE worker = %s", (agbdi_id, workers[i],))
    conn.commit()
    return Response('Workers Linked With Anganbadi')


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def drop_down_icds(request):
    user_id = request.user.id
    cur.execute("SELECT cdpo_id FROM cdpo_level WHERE cdpo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    cdpo_id = records_1[0][0]
    cur.execute(""" SELECT  cdpo_level.cdpo_id,
                            supervisor_level.supervisor
                            FROM
                            cdpo_level
                            INNER JOIN supervisor_level ON supervisor_level.cdpo_id = cdpo_level.cdpo_id """)
    records_sup = cur.fetchall()
    cur.execute('SELECT state, division, block, district FROM auth_user WHERE id = %s', (user_id,))
    h_records = cur.fetchall()
    print(h_records)
    block = h_records[0][2]

    dropdown_data_sup = []
    for i in range(len(records_sup)):
        if records_sup[i][0] == cdpo_id:
            print(records_sup[i])
            dropdown_data_sup.append(records_sup[i][1])

    cur.execute("""SELECT village from village_level WHERE block = %s""" , (block,))
    records_village = cur.fetchall()
    dropdown_data_village = []
    for i in range(len(records_village)):
        dropdown_data_village.append(records_village[i][0])
    print(records_village)

    cur.execute("""SELECT agbdi FROM anganbadi_level WHERE block = %s""" , (block,))
    records_agbdi = cur.fetchall()
    dropdown_data_agbdi = []
    for i in range(len(records_agbdi)):
        dropdown_data_agbdi.append(records_agbdi[i][0])

    #cur.execute("""SELECT cdpo_level.cdpo_id,
    #                worker_level.worker
    #                FROM
    #                cdpo_level
    #                INNER JOIN worker_level ON worker_level.cdpo_id = cdpo_level.cdpo_id""")
    #records_worker = cur.fetchall()
    #dropdown_data_worker = []
    #for i in range(len(records_worker)):
    #    dropdown_data_worker.append(records_worker[i][1])

    result = {"supervisors" : dropdown_data_sup , "villages" : dropdown_data_village , "anganbadis" : dropdown_data_agbdi}

    return Response(result)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def check_link_icds(request):
    cur.execute("SELECT cdpo_id FROM cdpo_level WHERE cdpo = %s", (str(request.user),))
    records_1 = cur.fetchall()
    cdpo_id = records_1[0][0]
    cur.execute(""" SELECT  cdpo_level.cdpo_id,
                            cdpo_level.cdpo,
                            supervisor_level.supervisor,
                            village_level.village,
                            anganbadi_level.agbdi,
                            worker_level.worker
                            FROM
                            cdpo_level
                            INNER JOIN supervisor_level ON supervisor_level.cdpo_id = cdpo_level.cdpo_id
                            INNER JOIN village_level ON village_level.sup_id = supervisor_level.sup_id
                            INNER JOIN anganbadi_level ON anganbadi_level.village_id = village_level.village_id
                            INNER JOIN worker_level ON worker_level.agbdi_id = anganbadi_level.agbdi_id""")

    records = cur.fetchall()
    links = []
    for i in range(0,len(records)):
        if (records[i][0] == cdpo_id):
            links.append(records[i])

    print(records)
    result = {"links" : links}

    return Response(result)

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def patient_data(request):
    const_check="no"
    var_check="no"
    high_risk_check = False
    print("const check : " , const_check)
    print("var check : " , var_check)
    print(" high risk check : " , high_risk_check)
    #print( " body is : " , request.body)
    relevant_data = json.loads(request.body)
    print("id is " , request.user)
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s" , (str(request.user),))
    records_bmo = cur.fetchall()
    bmo_id = records_bmo[0]

    cur.execute("SELECT block FROM auth_user WHERE username = %s" ,(str(request.user),) )
    records_block = cur.fetchall()
    block = records_block[0]

    cur.execute("SELECT state FROM auth_user WHERE username = %s" ,(str(request.user),) )
    records_state = cur.fetchall()
    state = records_state[0]

    cur.execute("SELECT district FROM auth_user WHERE username = %s" ,(str(request.user),) )
    records_district = cur.fetchall()
    district = records_district[0]

    cur.execute("SELECT division FROM auth_user WHERE username = %s" ,(str(request.user),) )
    records_division = cur.fetchall()
    division = records_division[0]

    high_risk_check = relevant_data['high_risk_check']
    print(high_risk_check)
    reg_date = datetime.date.today()
    aadhar_number = relevant_data['aadhar_number'] # 1
    patient_name = relevant_data['patient_name']   # 2
    husband_name = relevant_data['husband_name']   # 3
    mobile_number = relevant_data['mobile_number'] # 4
    date_of_birth = relevant_data['date_of_birth'] # 5
    age = relevant_data['age']   # 6
    male_child = int(relevant_data['male_child'])
    female_child = int(relevant_data['female_child'])
    economic_status = relevant_data['economic_status'] # 8
    cast = relevant_data['cast']                       # 9
    relegion = relevant_data['relegion']               # 10
    lmp_date = relevant_data['lmp_date']               # 11
    weight = relevant_data['weight']                   # 12
    edd_date = relevant_data['edd_date']               # 13
    officer = relevant_data['officer']                 # 14
    agbdi_name = relevant_data['agbdi_name']           # 15
    abortion_miscarriage = relevant_data['abortion_miscarriage'] # 16
    #blood_pressure = relevant_data['blood_pressure']             # 17
    bp1 = int(relevant_data['bp1'])
    bp2 = int(relevant_data['bp2'])
    sugar = relevant_data['sugar']                               # 18
    haemoglobin = relevant_data['haemoglobin']                   # 19
    pregnancy_number = relevant_data['pregnancy_number']         # 20
    height = relevant_data["height"]
    gravita = relevant_data["gravita"]
    para = relevant_data["para"]
    live = relevant_data["live"]
    abortion = relevant_data["abortion"]
    high_risk = []
    bp_check = "no"
    sugar_check = "no"
    #constant checks
    const_reasons = []
    if (age<18 or age>35):
        print("age is the reason")
        const_check = "yes"
        high_risk_check  = True
        const_reasons.append("age")
    print("abortion value", abortion_miscarriage)
    if(abortion_miscarriage == True):
        print("abortion is the reason")
        const_check = "yes"
        high_risk_check  = True
        const_reasons.append("abortion")

    if(height<154):
        print("height is the reason")
        const_check = "yes"
        high_risk_check = True
        const_reasons.append("height")

    var_reasons = [[]]

    if(haemoglobin<10):
        print("haemoglobin is the reason")
        var_check = "yes"
        high_risk_check = True
        var_reasons[0].append("haemoglobin")
    else:
        var_reasons[0].append('')

    if(bp1>130 or bp2>90):
        print("bp is the reason")
        var_check = "yes"
        high_risk_check = True
        bp_check = "yes"
        var_reasons[0].append("bp")
    else:
        var_reasons[0].append('')

    if(sugar<100):
        print("sugar is the reason")
        var_check = "yes"
        high_risk_check = True
        sugar_check = "yes"
        var_reasons[0].append("sugar")
    else:
        var_reasons[0].append('')

    print("const check : " , const_check)
    print("var check : " , var_check)
    print(" high risk check : " , high_risk_check)

    if(high_risk_check == True and (var_check=="no" and const_check=="no")):
        print("yes high risk")
        for i in range(0,len (relevant_data['high_risk'])):
            high_risk.append(str(relevant_data['high_risk'][i]))# 21, array of strings

    if (high_risk_check == True):
        if (sugar_check=="yes" and not("Diabetes" in high_risk)) :
            high_risk.append("Diabetes")

        if (bp_check == "yes" and not("High BP" in high_risk)):
            high_risk.append("High BP")


    dietary_advice = relevant_data['dietary_advice']             # 22
    samagra_id = relevant_data['samagra_id']                     #23
    officers_at_visit = relevant_data["officers_at_visit"]

    notified = False
    pregnancy_state = "active"
    cur.execute("SELECT agbdi_id FROM anganbadi_level WHERE agbdi = %s" , (agbdi_name,))
    agbdi_id = cur.fetchall()[0]

    cur.execute("SELECT smo_id FROM smo_level WHERE smo = %s" , (officer,))
    smo_id = cur.fetchall()[0]
    print(var_check , const_check , high_risk_check)
    cur.execute("""INSERT into patient_level(state,district,division,bmo_id,reg_date,aadhar_number, patient_name, husband_name, mobile_number, date_of_birth, age,
                    male_child,female_child, economic_status, relegion, lmp_date, weight, edd_date, officer, agbdi_name, abortion_miscarriage,bp1,bp2,sugar,haemoglobin,
                      pregnancy_number, high_risk, dietary_advice,notified,high_risk_check,agbdi_id,smo_id,block,samagra_id,const_check,const_reasons,
                      var_check,patient_status,officers_at_visit,height,gravita,para,live,abortion,var_reasons) 
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                      %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (state,district,division,bmo_id,reg_date,aadhar_number, patient_name, husband_name, mobile_number, date_of_birth, age,
                    male_child,female_child, economic_status, relegion, lmp_date, weight, edd_date, officer,
                 agbdi_name, abortion_miscarriage, bp1,bp2,sugar,haemoglobin,
                      pregnancy_number, high_risk, dietary_advice,notified, high_risk_check,agbdi_id,smo_id,
                 block,samagra_id,const_check,const_reasons,var_check,pregnancy_state,officers_at_visit,height,gravita,para,live,abortion,var_reasons))

    conn.commit()

    if(high_risk_check == True):
        # sending push notification to mobile device******
        push_service = FCMNotification(
            api_key="AAAAzxkjakU:APA91bExsgDBynVUmONLnKrm31hTOuN_aKSIwiHwOhCMfNPzANWb2sRdtp7SHHVuoop4BQ34ihUqmv95NH4XMFsQNvzMHqX7V1wEhYXhyncphoaFg94hNrrUa22XTLgHzu4QJU2zQGiX")

        registration_id = "cBRosMLnkgk:APA91bFjDgRkW4wpieK_6kXGg-cx7ueMt514qnhL6Oksi40FcaU4McGXKYBLLQKNLWfv41y4MXwEmwcMFDJgc45HgJi93IL2X-ZONDDx99AKGi7CfLxZgmZvcC8jhKAtluO0DVmtibBi"
        message_title = "New Patient Added!"
        message_body = "Tap to see details."
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body)
        print(result)
    # push notification snippet end *****************

    return Response('entry made')

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def last_entry(request):
    cur.execute("SELECT * FROM patient_data ORDER BY id DESC LIMIT 1")
    records = cur.fetchall()
    if(len(records)>0):
        return Response({"last entry" : records[0]})
    return Response("last entry not found")

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def users_record(request):
    cur.execute("SELECT row_to_json(user_record) FROM (SELECT id,state,block,division,district, username, role, mobile FROM auth_user) user_record ")
    records = cur.fetchall()
    print(records[0][0])
    users = []
    for r in records:
        users.append(r[0])
    return Response({"users" : users})

##########################api for dashboard###########################3

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def dashboard_data(request) :
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s" , (str(request.user),))
    records_bmo = cur.fetchall()
    if(len(records_bmo)>0):
        bmo_id = records_bmo[0]


    date_1 = datetime.date.today()
    date_2 = datetime.date.today() - timedelta(30)
    print(request.GET)
    #date_1 = datetime.date.today()
    #date_2 = datetime.date.today()
    x_axis = ["High BP" , "Convulsions" , "Vaginal Bleeding" , "Foul Smell Discharge" , "Severe Anemia" , "Diabetes" , "Twins" , "Any Others"]
    y_axis = [0,0,0,0,0,0,0,0]
    time_period = request.GET.get('time_period', None)
    officer_names = request.GET.get('officers', "")
    officer_names = re.sub("\[" , "", officer_names)
    officer_names = re.sub("\]", "", officer_names)
    sample = officer_names.split(',')
    print(sample)
    officer = sample

    if (time_period == 'today' or time_period == None):
        date_1 = datetime.date.today()
        date_2 = datetime.date.today()

    elif(time_period == 'this_week'):
        date_1 = datetime.date.today()
        date_2 = datetime.date.today() - timedelta(7)
        print("date 1 is : " , date_1 )
        print("date 2 is : ", date_2)
    elif(time_period == 'this_month'):
        date_1 = datetime.date.today()
        date_2 = datetime.date.today() - timedelta(30)
        print("date 1 is : ", date_1)
        print("date 2 is : ", date_2)
    #officer = ["badshah"]
    #officer = []
    if (len(records_bmo) > 0):
        officer_ids = []
        #village population

        if(len(officer)>0):
            for o in officer:
                cur.execute("SELECT smo_id FROM smo_level WHERE smo = %s" , (o,))
                off_records = cur.fetchall()
                if(len(off_records)>0):
                    officer_ids.append(off_records[0])


    #date 1, date 2, officers
        if(not(time_period == 'all')):
            cur.execute("SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE reg_date>=%s and reg_date<=%s and bmo_id = %s) patient_record" , (date_2, date_1,bmo_id))
            records = cur.fetchall()

        else:
            cur.execute(
                "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE bmo_id = %s) patient_record",
                ( bmo_id,))
            records = cur.fetchall()


        patients = []

        for r in records:
            patients.append(r[0])

        if (len(officer_ids) == 0):
            cur.execute("SELECT population FROM village_level WHERE bmo_id = %s", (bmo_id))
            v_records = cur.fetchall()
            print("v_records are : ", v_records)
            v_pop = 0
            for v in v_records:
                if not (v[0] == None):
                    v_pop += int(v[0])

            approx_registrations = int((0.015 * v_pop))
            approx_high_risk = int((0.15 * approx_registrations))
            total_number = 0
            high_risk = 0
            not_high_risk = 0
            const_cause = 0
            var_cause = 0
            total_number = len(patients)
            for p in patients:
                print("data in check is", " ", p["high_risk_check"])
                if (str(p["high_risk_check"]) == "true"):
                    high_risk+=1
                    for i in range(0,len(x_axis)):
                        if x_axis[i] in p["high_risk"] :
                            y_axis[i]+=1

                else:
                    not_high_risk+=1

                if(p["const_check"] == "yes"):
                    const_cause+=1
                if(p["var_check"] == "yes"):
                    var_cause +=1

        #result = {"total_number" : total_number , "high_risk" : high_risk , "not_high_risk" : not_high_risk , "x_axis" : x_axis, "y-axis": y_axis}
            stacked_data = [{"name": "High BP", "female": y_axis[0]}, {"name": "Convulsions", "female": y_axis[1]},
                        {"name": "Vaginal Bleeding", "female": y_axis[2]},
                        {"name": "Foul Smell Discharge", "female": y_axis[3]},
                        {"name": "Severe Anemia", "female": y_axis[4]}, {"name": "Diabetes", "female": y_axis[5]},
                        {"name": "Twins", "female": y_axis[6]}, {"name": "Any Others", "female": y_axis[7]}]

            result = {"total_number": total_number, "high_risk": high_risk, "not_high_risk": not_high_risk,
                  "stacked_data": stacked_data, "total_pop" : v_pop , "approx_reg" : approx_registrations , "approx_high_risk" : approx_high_risk,
                      "const_cause" : const_cause,"var_cause" : var_cause}
            return Response(result)
        else:
            #villages after filter
            anm_ids = []
            const_cause = 0
            var_cause = 0
            for o in officer_ids :

                cur.execute("SELECT anm_id FROM anm_level WHERE smo_id =%s" , (o,))
                records = cur.fetchall()
                if(len(records)>0):
                    anm_ids.append(records[0][0])

            pop_list = []
            for a in anm_ids :
                cur.execute("SELECT population FROM village_level WHERE anm_id = %s",(a,))
                records = cur.fetchall()
                if (len(records)>0):
                    if not (records[0][0] == None):
                        pop_list.append(records[0][0])

            v_pop = 0
            for v in pop_list:
                if not(v == None):
                    v_pop +=int(v)

            approx_registrations = int((0.015 * v_pop))
            approx_high_risk = int((0.15 * approx_registrations))

            filter_patients = []
            total_number = 0
            high_risk = 0
            not_high_risk = 0
            for p in patients :
                print(p["officer"])
                if(p["officer"] in officer):
                    filter_patients.append(p)

            total_number = len(filter_patients)
            for p in filter_patients:
                print("data in check is", " ", p["high_risk_check"])
                if (p["high_risk_check"] == "true"):
                    high_risk+=1
                    for i in range(0,len(x_axis)):
                        if x_axis[i] in p["high_risk"] :
                            y_axis[i]+=1
                else:
                    not_high_risk+=1

                if(p["const_check"] == "yes"):
                    const_cause+=1
                if(p["var_check"] == "yes"):
                    var_cause +=1

            stacked_data = [ {"name" : "High BP"  ,"female": y_axis[0]} ,{ "name":"Convulsions" ,"female": y_axis[1]} ,{ "name" : "Vaginal Bleeding" ,"female": y_axis[2]} , {"name" : "Foul Smell Discharge" ,"female": y_axis[3]} ,
                             {"name" : "Severe Anemia" ,"female": y_axis[4] }, {"name" : "Diabetes" ,"female": y_axis[5]} , {"name":"Twins" , "female":y_axis[6]} ,
                             {"name" : "Any Others" , "female" :y_axis[7]} ]

            result = {"total_number" : total_number , "high_risk" : high_risk , "not_high_risk" : not_high_risk,"stacked_data" : stacked_data,
                      "total_pop" : v_pop , "approx_reg" : approx_registrations , "approx_high_risk" : approx_high_risk,"const_cause" : const_cause,
                      "var_cause" : var_cause}

            return Response(result)

    else:
        officer_ids = []
        cur.execute("SELECT cdpo_id FROM cdpo_level WHERE cdpo = %s", (str(request.user),))
        records_cdpo = cur.fetchall()
        cdpo_id = records_cdpo[0]

        cur.execute("SELECT block FROM auth_user WHERE username = %s", (str(request.user),))
        records_block = cur.fetchall()
        block = records_block[0][0]
        print("block is : " , block)

        cur.execute("SELECT username FROM auth_user WHERE block = %s", (str(block),))
        records_user = cur.fetchall()
        #print("records user : " , records_user)
        bmo_name = records_user[0][0]
        print("bmo is " , bmo_name)
        cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(bmo_name),))
        records_bmo = cur.fetchall()
        if (len(records_bmo) > 0):
            bmo_id = records_bmo[0]
        else:
            return Response("error in dashboard_data")

        if (not (time_period == 'all')):
            cur.execute(
                "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE reg_date>=%s and reg_date<=%s and bmo_id = %s) patient_record",
                (date_2, date_1, bmo_id))
            records = cur.fetchall()

        else:
            cur.execute(
                "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE bmo_id = %s) patient_record",
                (bmo_id,))
            records = cur.fetchall()
        #print(records)
        patients = []
        for r in records:
            patients.append(r[0])

        supervisor_ids = []
        if (len(officer) > 0):
            for o in officer:
                cur.execute("SELECT sup_id FROM supervisor_level WHERE supervisor = %s", (o,))
                off_records = cur.fetchall()
                if (len(off_records) > 0):
                    supervisor_ids.append(off_records[0][0])
        print("supervisor ids : " , supervisor_ids)
        anms = []

        for sup in supervisor_ids:
            cur.execute("SELECT anm_id FROM village_level WHERE sup_id = %s" , (sup,));
            v_Records = cur.fetchall()
            if (len(v_Records)>0):
                anms.append(v_Records[0][0])
        print("villages are " , anms)

        for a in anms:
            cur.execute("SELECT smo_id FROM anm_level WHERE anm_id = %s" , (a,));
            anm_records = cur.fetchall()
            if (len(anm_records) > 0):
                officer_ids.append(anm_records[0][0])
        print("officer ids" , officer_ids)

        smo = []
        for o in officer_ids:
            cur.execute("SELECT smo FROM smo_level WHERE smo_id = %s" , (o,));
            smo_records = cur.fetchall()
            if (len(smo_records) > 0):
                    smo.append(smo_records[0][0])

        #print("finalo officers are : ", smo)

        print("number of officers is : " , smo)


        if (len(officer_ids) == 0):
            print("filter not working")
            total_number = 0
            high_risk = 0
            not_high_risk = 0
            total_number = len(patients)
            for p in patients:
                print("data in check is", " ", p["high_risk_check"])
                if (str(p["high_risk_check"]) == "true"):
                    high_risk+=1
                    for i in range(0,len(x_axis)):
                        if x_axis[i] in p["high_risk"] :
                            y_axis[i]+=1

                else:
                    not_high_risk+=1

        #result = {"total_number" : total_number , "high_risk" : high_risk , "not_high_risk" : not_high_risk , "x_axis" : x_axis, "y-axis": y_axis}
            stacked_data = [{"name": "High BP", "female": y_axis[0]}, {"name": "Convulsions", "female": y_axis[1]},
                        {"name": "Vaginal Bleeding", "female": y_axis[2]},
                        {"name": "Foul Smell Discharge", "female": y_axis[3]},
                        {"name": "Severe Anemia", "female": y_axis[4]}, {"name": "Diabetes", "female": y_axis[5]},
                        {"name": "Twins", "female": y_axis[6]}, {"name": "Any Others", "female": y_axis[7]}]

            result = {"total_number": total_number, "high_risk": high_risk, "not_high_risk": not_high_risk,
                  "stacked_data": stacked_data}
            return Response(result)
        else:
            print("filter working")
            filter_patients = []
            total_number = 0
            high_risk = 0
            not_high_risk = 0
            for p in patients :
                #print(p["officer"])
                print(p["officer"])
                if(p["officer"] in smo):
                    print("officer found")
                    filter_patients.append(p)

            total_number = len(filter_patients)
            for p in filter_patients:
                #print("data in check is", " ", p["high_risk_check"])
                if (p["high_risk_check"] == "true"):
                    high_risk+=1
                    for i in range(0,len(x_axis)):
                        if x_axis[i] in p["high_risk"] :
                            y_axis[i]+=1
                else:
                    not_high_risk+=1

            stacked_data = [ {"name" : "High BP"  ,"female": y_axis[0]} ,{ "name":"Convulsions" ,"female": y_axis[1]} ,{ "name" : "Vaginal Bleeding" ,"female": y_axis[2]} , {"name" : "Foul Smell Discharge" ,"female": y_axis[3]} , {"name" : "Severe Anemia" ,"female": y_axis[4] }, {"name" : "Diabetes" ,"female": y_axis[5]} , {"name":"Twins" , "female":y_axis[6]} , {"name" : "Any Others" , "female" :y_axis[7]} ]

            result = {"total_number" : total_number , "high_risk" : high_risk , "not_high_risk" : not_high_risk,"stacked_data" : stacked_data}

            return Response(result)



@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def delete_user(request):
    relevant_data = json.loads(request.body)
    id_del = relevant_data["id"]
    from django.contrib.auth.models import User
    user = User.objects.filter(id = id_del)
    user.delete()
    print(request)
    print(request.body)
    return Response("User Deleted")

@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_high_risk_patient_data(request):
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s" , (str(request.user),))
    records_bmo = cur.fetchall()
    if(len(records_bmo)>0):
        bmo_id = records_bmo[0]
        patients = []
        cur.execute(
            "SELECT row_to_json(user_record) FROM (SELECT patient_id,patient_name,officer,agbdi_id,high_risk,edd_date  FROM patient_level WHERE high_risk_check = 'true' and bmo_id = %s) user_record ", (bmo_id,))
        records = cur.fetchall()
        users = []
        for r in records:
            users.append(r[0])
        print(len(records))
        for rec in records :
            r = rec[0]
            print("1")
            p_id = (r["agbdi_id"])
            if(p_id == None):
                p_id = 8
            cur.execute("SELECT village_id FROM anganbadi_level WHERE agbdi_id = %s" ,(int(p_id),))
            v_records = cur.fetchall()
            if (len(v_records)>0):
                v_id = v_records[0][0]
            else:
                v_id = 8

            cur.execute("SELECT sup_id FROM village_level WHERE village_id = %s" , (v_id,))
            s_records = cur.fetchall()
            print(s_records)
            if len(s_records)>0:
                s_id = s_records[0][0]
            else:
                s_id = 2
            print(s_id)
            cur.execute("SELECT supervisor FROM supervisor_level WHERE sup_id = %s" , (s_id,))

            sup_records = cur.fetchall()
            supervisor = sup_records[0][0]

            cur.execute("SELECT anm_id FROM village_level WHERE village_id = %s" , (v_id,))
            a_records = cur.fetchall()
            if(len(a_records)>0):
                a_id = a_records[0][0]
            else:
                a_id = 35

            cur.execute("SELECT anm FROM anm_level WHERE anm_id = %s" , (a_id,))
            anm_records = cur.fetchall()
            if(len(anm_records)>0):

                anm = anm_records[0][0]
            else:
                anm="test_anm"


            r["supervisor"] = supervisor
            r["status"] = 0
            r["visits"] = 0
            r["anm"] = anm

            patients.append(r)

        return Response({"patients" : patients})
    else:
        cur.execute("SELECT cdpo_id FROM cdpo_level WHERE cdpo = %s", (str(request.user),))
        records_cdpo = cur.fetchall()
        cdpo_id = records_cdpo[0]
        cur.execute("SELECT block FROM auth_user WHERE username = %s", (str(request.user),))
        records_block = cur.fetchall()
        block = records_block[0]
        patients = []
        cur.execute(
            "SELECT row_to_json(user_record) FROM (SELECT patient_id,patient_name,officer,agbdi_id,high_risk,edd_date  FROM patient_level WHERE high_risk_check = 'true' and block = %s) user_record ",
            (block,))
        records = cur.fetchall()
        users = []
        for r in records:
            users.append(r[0])
        print(len(records))
        for rec in records:
            r = rec[0]
            print("1")
            p_id = (r["agbdi_id"])
            if (p_id == None):
                p_id = 8
            cur.execute("SELECT village_id FROM anganbadi_level WHERE agbdi_id = %s", (int(p_id),))
            v_records = cur.fetchall()
            if (len(v_records) > 0):
                v_id = v_records[0][0]
            else:
                v_id = 8

            cur.execute("SELECT sup_id FROM village_level WHERE village_id = %s", (v_id,))
            s_records = cur.fetchall()
            if len(s_records) > 0:
                s_id = s_records[0][0]
            else:
                s_id = 2
            cur.execute("SELECT supervisor FROM supervisor_level WHERE sup_id = %s", (s_id,))

            sup_records = cur.fetchall()
            supervisor = sup_records[0][0]

            cur.execute("SELECT anm_id FROM village_level WHERE village_id = %s", (v_id,))
            a_records = cur.fetchall()
            if (len(a_records) > 0):
                a_id = a_records[0][0]
            else:
                a_id = 35

            cur.execute("SELECT anm FROM anm_level WHERE anm_id = %s", (a_id,))
            anm_records = cur.fetchall()
            if(len(anm_records)>0):
                anm = anm_records[0][0]
            else:
                anm = "shyama"

            r["supervisor"] = supervisor
            r["status"] = 0
            r["visits"] = 0
            r["anm"] = anm

            patients.append(r)

        return Response({"patients": patients})


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def full_patient_details(request):
    relevant_data = json.loads(request.body)
    p_id = relevant_data["id"]
    cur.execute(
        "SELECT row_to_json(user_record) FROM (SELECT *  FROM patient_level WHERE patient_id = %s) user_record ", (int(p_id),))
    records = cur.fetchall()
    print(records[0][0])
    return Response( records[0][0])

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def search_record(request):
    relevant_data = json.loads(request.body)
    print(relevant_data)
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(request.user),))
    records_bmo = cur.fetchall()
    s_value = relevant_data["selectvalue"]
    if (len(records_bmo) > 0):

        bmo_id = records_bmo[0]
        patients = []
        if (s_value == "aadhar" ):
            aadhar_number = relevant_data["search"]
            cur.execute(
                "SELECT row_to_json(user_record) FROM (SELECT patient_id,patient_name,officer,agbdi_id,high_risk,edd_date  FROM patient_level WHERE bmo_id = %s and aadhar_number = %s) user_record ",
                (bmo_id,aadhar_number))
            records = cur.fetchall()
            if(len(records)==0):
                return Response("Invalid Aadhar Number")
            users = []
            for r in records:
                users.append(r[0])
            print(len(records))
            for rec in records :
                r = rec[0]
                print("1")
                p_id = (r["agbdi_id"])
                if(p_id == None):
                    p_id = 8
                cur.execute("SELECT village_id FROM anganbadi_level WHERE agbdi_id = %s" ,(int(p_id),))
                v_records = cur.fetchall()
                if (len(v_records)>0):
                    v_id = v_records[0][0]
                else:
                    v_id = 8

                cur.execute("SELECT sup_id FROM village_level WHERE village_id = %s" , (v_id,))
                s_records = cur.fetchall()
                print(s_records)
                if len(s_records)>0:
                    s_id = s_records[0][0]
                else:
                    s_id = 2
                print(s_id)
                cur.execute("SELECT supervisor FROM supervisor_level WHERE sup_id = %s" , (s_id,))

                sup_records = cur.fetchall()
                supervisor = sup_records[0][0]

                cur.execute("SELECT anm_id FROM village_level WHERE village_id = %s" , (v_id,))
                a_records = cur.fetchall()
                if(len(a_records)>0):
                    a_id = a_records[0][0]
                else:
                    a_id = 35

                cur.execute("SELECT anm FROM anm_level WHERE anm_id = %s" , (a_id,))
                anm_records = cur.fetchall()
                anm = anm_records[0][0]


                r["supervisor"] = supervisor
                r["status"] = 0
                r["visits"] = 0
                r["anm"] = anm

                patients.append(r)

            return Response({"patients" : patients})

        if (s_value == "patient_id" ):
            patient_id = relevant_data["search"]
            cur.execute(
                "SELECT row_to_json(user_record) FROM (SELECT patient_id,patient_name,officer,agbdi_id,high_risk,edd_date  FROM patient_level WHERE bmo_id = %s and patient_id = %s) user_record ",
                (bmo_id, patient_id))
            records = cur.fetchall()
            if (len(records) == 0):
                return Response("Invalid Patient ID")
            users = []
            for r in records:
                users.append(r[0])
            print(len(records))
            for rec in records:
                r = rec[0]
                print("1")
                p_id = (r["agbdi_id"])
                if (p_id == None):
                    p_id = 8
                cur.execute("SELECT village_id FROM anganbadi_level WHERE agbdi_id = %s", (int(p_id),))
                v_records = cur.fetchall()
                if (len(v_records) > 0):
                    v_id = v_records[0][0]
                else:
                    v_id = 8

                cur.execute("SELECT sup_id FROM village_level WHERE village_id = %s", (v_id,))
                s_records = cur.fetchall()
                print(s_records)
                if len(s_records) > 0:
                    s_id = s_records[0][0]
                else:
                    s_id = 2
                print(s_id)
                cur.execute("SELECT supervisor FROM supervisor_level WHERE sup_id = %s", (s_id,))

                sup_records = cur.fetchall()
                supervisor = sup_records[0][0]

                cur.execute("SELECT anm_id FROM village_level WHERE village_id = %s", (v_id,))
                a_records = cur.fetchall()
                if (len(a_records) > 0):
                    a_id = a_records[0][0]
                else:
                    a_id = 35

                cur.execute("SELECT anm FROM anm_level WHERE anm_id = %s", (a_id,))
                anm_records = cur.fetchall()
                anm = anm_records[0][0]

                r["supervisor"] = supervisor
                r["status"] = 0
                r["visits"] = 0
                r["anm"] = anm

                patients.append(r)

            return Response({"patients": patients})

        if (s_value == "samagra_id"):
            samagra_id = relevant_data["search"]
            cur.execute(
                "SELECT row_to_json(user_record) FROM (SELECT patient_id,patient_name,officer,agbdi_id,high_risk,edd_date  FROM patient_level WHERE bmo_id = %s and samagra_id= %s) user_record ",
                (bmo_id, samagra_id))
            records = cur.fetchall()
            if (len(records) == 0):
                return Response("Invalid Samagra ID")
            users = []
            for r in records:
                users.append(r[0])
            print(len(records))
            for rec in records:
                r = rec[0]
                print("1")
                p_id = (r["agbdi_id"])
                if (p_id == None):
                    p_id = 8
                cur.execute("SELECT village_id FROM anganbadi_level WHERE agbdi_id = %s", (int(p_id),))
                v_records = cur.fetchall()
                if (len(v_records) > 0):
                    v_id = v_records[0][0]
                else:
                    v_id = 8

                cur.execute("SELECT sup_id FROM village_level WHERE village_id = %s", (v_id,))
                s_records = cur.fetchall()
                print(s_records)
                if len(s_records) > 0:
                    s_id = s_records[0][0]
                else:
                    s_id = 2
                print(s_id)
                cur.execute("SELECT supervisor FROM supervisor_level WHERE sup_id = %s", (s_id,))

                sup_records = cur.fetchall()
                supervisor = sup_records[0][0]

                cur.execute("SELECT anm_id FROM village_level WHERE village_id = %s", (v_id,))
                a_records = cur.fetchall()
                if (len(a_records) > 0):
                    a_id = a_records[0][0]
                else:
                    a_id = 35

                cur.execute("SELECT anm FROM anm_level WHERE anm_id = %s", (a_id,))
                anm_records = cur.fetchall()
                anm = anm_records[0][0]

                r["supervisor"] = supervisor
                r["status"] = 0
                r["visits"] = 0
                r["anm"] = anm

                patients.append(r)

            return Response({"patients": patients})

        else:
            return Response("Invalid Request")


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def final_entry(request):
    relevant_data = json.loads(request.body)
    print(relevant_data)
    value = relevant_data["value"]
    patient_id = relevant_data["patient_id"]
    if value == "delivered":
        b_weight = relevant_data["baby_weight"]
        d_type = relevant_data["delivery_type"]
        f_outcome = relevant_data["foetal_outcome"]
        d_date = relevant_data["date"]
        d_status = "delivered"
        cur.execute("UPDATE patient_level SET b_weight = %s,d_type=%s,f_outcome=%s,d_date=%s,d_status=%s,patient_status=%s WHERE patient_id = %s" ,
                    (int(b_weight), d_type, f_outcome, d_date, d_status,"inactive" ,patient_id,))
        return Response("Final data entered")

    if value == "not_delivered":
        cause = relevant_data["cause"]
        reason = relevant_data["reason"]
        d_status = "not_delivered"
        cur.execute("UPDATE patient_level SET cause = %s, reason=%s, d_status=%s WHERE patient_id=%s, patient_status = %s" , (cause, reason, d_status, patient_id,"inactive"))
        return Response("Final data entered")
    conn.commit()
    return  Response("Entry could not be made")



###############################################################report###########################

##############hiGH RISK ANALYSIS###############################################################
@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def report_data_high_risk(request):
    print(request)
    start = request.GET.get('start', None)

    officer_names = request.GET.get('officers', "")
    officer_names = re.sub("\[", "", officer_names)
    officer_names = re.sub("\]", "", officer_names)
    sample = officer_names.split(',')
    print(sample)
    if(sample[0] == ''):
        sample = []

    officer = sample

    total_reg = 0
    t_high_risk = 0
    con_risk = 0
    n_con_risk = 0
    const_cause = 0
    var_cause = 0
    causes_1 = ["bp","sugar","haemoglobin"]
    causes_2 = ["High BP" , "Diabetes" , "Haemoglobin"]
    cases = [0, 0, 0]
    improv2 = [0, 0, 0]
    improv3 = [0, 0, 0]
    improv4 = [0, 0, 0]
    cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s" , (str(request.user),))
    records_bmo = cur.fetchall()
    if(len(records_bmo)>0):
        bmo_id = records_bmo[0]

        if(len(officer) == 0):
            print("no smo filter applied yet")
            cur.execute("SELECT population FROM village_level WHERE bmo_id = %s", (bmo_id))
            v_records = cur.fetchall()
            print("v_records are : ", v_records)
            v_pop = 0
            for v in v_records:
                if not (v[0] == None):
                    v_pop += int(v[0])

            approx_registrations = int((0.015 * v_pop))
            approx_high_risk = int((0.15 * approx_registrations))


            if not(start == 'All'):
                date_2 = request.GET.get('start', None)
                date_1 = request.GET.get('end', None)
                print("active patients records")
                cur.execute(
                    "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE reg_date>=%s and reg_date<=%s and bmo_id = %s and patient_status=%s) patient_record",
                    (date_2,date_1,bmo_id,"active",))
                records = cur.fetchall()

            else:
                cur.execute("SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE bmo_id = %s ) patient_record",
                    (bmo_id,))
                records = cur.fetchall()

            patients = []

            for r in records:
                patients.append(r[0])

            total_reg = len(patients)

            for p in patients :

                if(str(p["high_risk_check"]) == "true" ):
                    t_high_risk+=1
                    for i in range (0,len(causes_1)) :
                        #print(p["high_risk"])
                        if causes_2[i] in p["high_risk"]:
                            cases[i]+=1
                        #print("improv2", p["improv2"])
                        if not(p["improv2"] == None):
                            print(improv2)
                            if causes_1[i] in p["improv2"]:
                                improv2[i]+=1
                        if not (p["improv3"] == None):
                            if causes_1[i] in p["improv3"]:
                                improv3[i]+=1
                        if not (p["improv4"] == None):
                            if causes_1[i] in p["improv4"]:
                                improv4[i]+=1

                if(p["d_status"] == "delivered" and "patient_status" == "inactive"):
                    con_risk+=1

                if(p["d_status"] == "not_delivered" and "patient_status" == "inactive"):
                    n_con_risk+=1

                if(p["const_check"] == "yes"):
                    const_cause+=1

                if(p["var_check"] == "yes"):
                    var_cause+=1

            total = 1
            for c in cases:
                total+=int(c)

            percentage = []
            for c in cases:
                percentage.append(int((c*100)/total))


            ###########improvement##################
            for i in range(0,len(improv2)):
                improv2[i] = int((improv2[i]*100)/total)

            for i in range(0,len(improv3)):
                improv3[i] = int((improv3[i]*100)/total)

            for i in range(0,len(improv4)):
                improv4[i] = int((improv4[i]*100)/total)



            result = {"total_reg" : total_reg , "total_high_risk" : t_high_risk , "convertible" : con_risk , "not_convertible" : n_con_risk,
                      "const_cause" : const_cause , "var_cause" : var_cause , "causes" : causes_2 , "cases" : cases , "percentage" : percentage,
                      "improv2" : improv2 , "improv3" : improv3 , "improv4" : improv4,"total_pop" : v_pop , "approx_reg" : approx_registrations ,
                      "approx_high_risk" : approx_high_risk}

            return Response(result)

        else:
            print("smo filter applied")
            officer_ids = []
            anm_ids = []
            #smo ids and population of villages
            for o in officer:
                cur.execute("SELECT smo_id FROM smo_level WHERE smo = %s", (o,))
                off_records = cur.fetchall()
                if (len(off_records) > 0):
                    officer_ids.append(off_records[0])
            print(officer_ids)
            for o in officer_ids:

                cur.execute("SELECT anm_id FROM anm_level WHERE smo_id =%s", (o,))
                records = cur.fetchall()
                if (len(records) > 0):
                    anm_ids.append(records[0][0])

            pop_list = []
            for a in anm_ids:
                cur.execute("SELECT population FROM village_level WHERE anm_id = %s", (a,))
                records = cur.fetchall()
                if (len(records) > 0):
                    if not (records[0][0] == None):
                        pop_list.append(records[0][0])

            v_pop = 0
            for v in pop_list:
                if not (v == None):
                    v_pop += int(v)

            approx_registrations = int((0.015 * v_pop))
            approx_high_risk = int((0.15 * approx_registrations))

            if not (start == 'All'):
                date_2 = request.GET.get('start', None)
                date_1 = request.GET.get('start', None)
                cur.execute(
                    "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE reg_date>=%s and reg_date<=%s and bmo_id = %s and smo_id in %s) patient_record",
                    (date_2, date_1, bmo_id,tuple(officer_ids)))
                records = cur.fetchall()
            else:
                cur.execute(
                    "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE bmo_id = %s and smo_id in %s) patient_record",
                    (bmo_id,tuple(officer_ids)))
                records = cur.fetchall()

            print(records)
            patients = []

            for r in records:
                patients.append(r[0])

            total_reg = len(patients)

            for p in patients:

                if (str(p["high_risk_check"]) == "true"):
                    t_high_risk += 1
                    for i in range(0, len(causes_1)):
                        print(p["high_risk"])
                        if causes_2[i] in p["high_risk"]:
                            cases[i] += 1
                        if not(p["improv2"] == None):
                            print(improv2)
                            if causes_1[i] in p["improv2"]:
                                improv2[i]+=1
                        if not (p["improv3"] == None):
                            if causes_1[i] in p["improv3"]:
                                improv3[i]+=1
                        if not (p["improv4"] == None):
                            if causes_1[i] in p["improv4"]:
                                improv4[i]+=1

                if (p["d_status"] == "delivered" and "patient_status" == "inactive"):
                    con_risk += 1

                if (p["d_status"] == "not_delivered" and "patient_status" == "inactive"):
                    n_con_risk += 1

                if (p["const_check"] == "yes"):
                    const_cause += 1

                if (p["var_check"] == "yes"):
                    var_cause += 1

            total = 1
            for c in cases:
                total += int(c)

            percentage = []
            for c in cases:
                percentage.append(int((c * 100) / total))

            ###########improvement##################
            for i in range(0, len(improv2)):
                improv2[i] = int((improv2[i] * 100) / total)

            for i in range(0, len(improv3)):
                improv3[i] = int((improv3[i] * 100) / total)

            for i in range(0, len(improv4)):
                improv4[i] = int((improv4[i] * 100) / total)

            result = {"total_reg": total_reg, "total_high_risk": t_high_risk, "convertible": con_risk,
                      "not_convertible": n_con_risk,
                      "const_cause": const_cause, "var_cause": var_cause, "causes": causes_2, "cases": cases,
                      "percentage": percentage,"improv2": improv2, "improv3": improv3, "improv4": improv4,
                      "total_pop": v_pop, "approx_reg": approx_registrations, "approx_high_risk": approx_high_risk}

            return Response(result)

    #cdpo
    else:

        officer_ids = []
        cur.execute("SELECT cdpo_id FROM cdpo_level WHERE cdpo = %s", (str(request.user),))
        records_cdpo = cur.fetchall()
        cdpo_id = records_cdpo[0]

        cur.execute("SELECT block FROM auth_user WHERE username = %s", (str(request.user),))
        records_block = cur.fetchall()
        block = records_block[0][0]
        print("block is : " , block)

        cur.execute("SELECT username FROM auth_user WHERE block = %s", (str(block),))
        records_user = cur.fetchall()
        #print("records user : " , records_user)
        bmo_name = records_user[0][0]
        print("bmo is " , bmo_name)
        cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s", (str(bmo_name),))
        records_bmo = cur.fetchall()
        if (len(records_bmo) > 0):
            bmo_id = records_bmo[0]
        else:
            return Response("error in dashboard_data")

        if(len(officer)==0):
            cur.execute("SELECT population FROM village_level WHERE bmo_id = %s", (bmo_id))
            v_records = cur.fetchall()
            print("v_records are : ", v_records)
            v_pop = 0
            for v in v_records:
                if not (v[0] == None):
                    v_pop += int(v[0])

            approx_registrations = int((0.015 * v_pop))
            approx_high_risk = int((0.15 * approx_registrations))
            if not(start == 'All'):
                date_2 = request.GET.get('start', None)
                date_1 = request.GET.get('start', None)
                cur.execute(
                    "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE reg_date>=%s and reg_date<=%s and bmo_id = %s) patient_record",
                    (date_2,date_1,bmo_id,))
                records = cur.fetchall()

            cur.execute("SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE bmo_id = %s and) patient_record",
                (bmo_id,))
            records = cur.fetchall()

            patients = []

            for r in records:
                patients.append(r[0])

            total_reg = len(patients)

            for p in patients :

                if(str(p["high_risk_check"]) == "true" ):
                    t_high_risk+=1
                    for i in range (0,len(causes_1)) :
                        print(p["high_risk"])
                        if causes_2[i] in p["high_risk"]:
                            cases[i]+=1
                        if not(p["improv2"] == None):
                            print(improv2)
                            if causes_1[i] in p["improv2"]:
                                improv2[i]+=1
                        if not (p["improv3"] == None):
                            if causes_1[i] in p["improv3"]:
                                improv3[i]+=1
                        if not (p["improv4"] == None):
                            if causes_1[i] in p["improv4"]:
                                improv4[i]+=1

                if(p["d_status"] == "delivered" and "patient_status" == "inactive"):
                    con_risk+=1

                if(p["d_status"] == "not_delivered" and "patient_status" == "inactive"):
                    n_con_risk+=1

                if(p["const_check"] == "yes"):
                    const_cause+=1

                if(p["var_check"] == "yes"):
                    var_cause+=1

            total = 1
            for c in cases:
                total+=int(c)

            percentage = []
            for c in cases:
                percentage.append(int((c*100)/total))


            ###########improvement##################
            for i in range(0,len(improv2)):
                improv2[i] = int((improv2[i]*100)/total)

            for i in range(0,len(improv3)):
                improv3[i] = int((improv3[i]*100)/total)

            for i in range(0,len(improv4)):
                improv4[i] = int((improv4[i]*100)/total)



            result = {"total_reg" : total_reg , "total_high_risk" : t_high_risk , "convertible" : con_risk , "not_convertible" : n_con_risk,
                      "const_cause" : const_cause , "var_cause" : var_cause , "causes" : causes_2 , "cases" : cases , "percentage" : percentage,
                      "improv2" : improv2 , "improv3" : improv3 , "improv4" : improv4,
                      "total_pop": v_pop, "approx_reg": approx_registrations, "approx_high_risk": approx_high_risk}

            return Response(result)

        else:
            supervisor_ids = []
            if (len(officer) > 0):
                for o in officer:
                    cur.execute("SELECT sup_id FROM supervisor_level WHERE supervisor = %s", (o,))
                    off_records = cur.fetchall()
                    if (len(off_records) > 0):
                        supervisor_ids.append(off_records[0][0])
            print("supervisor ids : ", supervisor_ids)

            pop_list = []
            for s in supervisor_ids:
                cur.execute("SELECT population FROM village_level WHERE sup_id = %s", (s,))
                records = cur.fetchall()
                if (len(records) > 0):
                    if not (records[0][0] == None):
                        pop_list.append(records[0][0])

            v_pop = 0
            for v in pop_list:
                if not (v == None):
                    v_pop += int(v)

            approx_registrations = int((0.015 * v_pop))
            approx_high_risk = int((0.15 * approx_registrations))


            anms = []
            for sup in supervisor_ids:
                cur.execute("SELECT anm_id FROM village_level WHERE sup_id = %s", (sup,));
                v_Records = cur.fetchall()
                if (len(v_Records) > 0):
                    anms.append(v_Records[0][0])
            print("villages are ", anms)

            for a in anms:
                cur.execute("SELECT smo_id FROM anm_level WHERE anm_id = %s", (a,));
                anm_records = cur.fetchall()
                if (len(anm_records) > 0):
                    officer_ids.append(anm_records[0][0])
            print("officer ids", officer_ids)

            if not (start == 'All'):
                date_2 = request.GET.get('start', None)
                date_1 = request.GET.get('start', None)
                cur.execute(
                    "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE reg_date>=%s and reg_date<=%s and bmo_id = %s  and smo_id in %s) patient_record",
                    (date_2, date_1, bmo_id,tuple(officer_ids)))
                records = cur.fetchall()
            else:
                cur.execute(
                    "SELECT row_to_json(patient_record) FROM (SELECT * FROM patient_level WHERE bmo_id = %s  and smo_id in %s) patient_record",
                    (bmo_id,tuple(officer_ids)))
                records = cur.fetchall()

            patients = []

            for r in records:
                patients.append(r[0])

            total_reg = len(patients)

            for p in patients:

                if (str(p["high_risk_check"]) == "true"):
                    t_high_risk += 1
                    for i in range(0, len(causes_1)):
                        print(p["high_risk"])
                        if causes_2[i] in p["high_risk"]:
                            cases[i] += 1
                        if not(p["improv2"] == None):
                            print(improv2)
                            if causes_1[i] in p["improv2"]:
                                improv2[i]+=1
                        if not (p["improv3"] == None):
                            if causes_1[i] in p["improv3"]:
                                improv3[i]+=1
                        if not (p["improv4"] == None):
                            if causes_1[i] in p["improv4"]:
                                improv4[i]+=1

                if (p["d_status"] == "delivered" and "patient_status" == "inactive"):
                    con_risk += 1

                if (p["d_status"] == "not_delivered" and "patient_status" == "inactive"):
                    n_con_risk += 1

                if (p["const_check"] == "yes"):
                    const_cause += 1

                if (p["var_check"] == "yes"):
                    var_cause += 1

            total = 1
            for c in cases:
                total += int(c)

            percentage = []
            for c in cases:
                percentage.append(int((c * 100) / total))

            ###########improvement##################
            for i in range(0, len(improv2)):
                improv2[i] = int((improv2[i] * 100) / total)

            for i in range(0, len(improv3)):
                improv3[i] = int((improv3[i] * 100) / total)

            for i in range(0, len(improv4)):
                improv4[i] = int((improv4[i] * 100) / total)

            result = {"total_reg": total_reg, "total_high_risk": t_high_risk, "convertible": con_risk,
                      "not_convertible": n_con_risk,
                      "const_cause": const_cause, "var_cause": var_cause, "causes": causes_2, "cases": cases,
                      "percentage": percentage,"improv2": improv2, "improv3": improv3, "improv4": improv4,
                      "total_pop": v_pop, "approx_reg": approx_registrations, "approx_high_risk": approx_high_risk}

            return Response(result)