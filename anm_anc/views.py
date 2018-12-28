from django.shortcuts import render
from .add_on_methods import *
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
# Create your views here.
# 1 update patient data multiple times
#patient_registration  one time
cur = conn.cursor()
hrisk_bgroups = ['A-','B-','AB-','O-']

@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def patient_registry(request):
    anm_id = get_anm_id(request.user)
    id = request.user.id
    relevant_data = json.loads(request.body)
    location = address_mapping(id)
    state = location['state']#14
    block = location['block']#15
    division = location['division']#16
    district = location['district']#17
    aadhar_number = relevant_data['aadhar_number'] #1
    patient_name = relevant_data['patient_name']   # 2
    husband_name = relevant_data['husband_name']   # 3
    #husband_age = relevant_data["husband_age"] #4
    mobile_number = relevant_data['mobile_number'] # 5
    date_of_birth = relevant_data['date_of_birth']  # 6
    age = relevant_data['age']
    economic_status = relevant_data['economic_status']  # 7
    cast = relevant_data['cast']  # 8
    relegion = relevant_data['relegion']  # 9
    lmp_date = relevant_data['lmp_date'] # 10
    edd_date = relevant_data['edd_date']  # 11
    #officer = relevant_data['officer']  # 12
    smo_id = get_smo_id(request.user)
    address = relevant_data["address"]
    #agbdi = relevant_data["agbdi"]
    #agbdi_name = relevant_data['agbdi_name'] #13

    cur.execute("""INSERT INTO patient_level (state,block,division,district,aadhar_number,patient_name,husband_name,mobile_number,
                   date_of_birth,age,economic_status,cast_type,relegion,lmp_date,edd_date,address,smo_id,anm_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s ) 
                   RETURNING patient_id """ , (state,block,division,district,
                     aadhar_number,patient_name,husband_name,mobile_number,date_of_birth,age,economic_status,cast,relegion,lmp_date,edd_date,address,smo_id,anm_id))
    conn.commit()
    res = cur.fetchall()
    print(res)
    patient_id = res[0][0]

    return Response({'patient_id' : patient_id})


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def anc_visit(request):
    id = request.user.id
    anm_id = get_anm_id(request.user)
    smo_id = get_smo_id(request.user)
    relevant_data = json.loads(request.body)
    print( (relevant_data))
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

    visit_number = get_visit_number_anm(p_id)



    #constant high risk factors check
    cur.execute("SELECT age,lmp_date,edd_date,created_at::DATE,patient_name FROM patient_level WHERE patient_id = %s" , (p_id,))
    print(p_id)
    age_rec = cur.fetchall()
    print(len(age_rec))
    print(age_rec)
    age = age_rec[0][0] #1
    lmp = age_rec[0][1]
    edd = age_rec[0][2]
    reg_date = age_rec[0][3]
    patient_name = age_rec[0][4]
    cur.execute("SELECT height FROM anm_anc WHERE patient_id = %s", (p_id,))
    rec_height = cur.fetchall()

    if(len(rec_height)==0):
        anm_anc_date = []
        anm_anc_date.append(relevant_data["anm_anc_date"])

        if (age<18 or age>35):
            c_ctr+=1
            const_factors+=('age ')
            print( "age is reason")

        height = relevant_data['height'] #2
        if (height<145) :
            c_ctr+=1
            const_factors+=('height ')
            print("height is reason")

        previous_lscs = relevant_data['previous_lscs']#3
        if (previous_lscs == True):
            c_ctr+=1
            const_factors+=('previous_lscs ')
            print( "p_lscs is reason")

        bgroup = relevant_data['bgroup']#4
        if(bgroup in hrisk_bgroups):
            c_ctr+=1
            const_factors+=('blood group ')
            print("blood group is reason")

        disability = relevant_data['disability']#5
        if (not (disability == 'None')):
            c_ctr+=1
            const_factors+=('disability ')
            print("disablity is reason")

        blood_disease = relevant_data['blood_disease']#6
        if( not(blood_disease == 'Normal' )):
            c_ctr+=1
            const_factors+=('blood disease ')
            print("blood disease is reason")

        hiv = relevant_data['hiv']#7
        if( hiv == True):
            c_ctr+=1
            const_factors+=('hiv ')
            print("HIV is reason")

        hbsag = relevant_data['hbsag']#8
        if( hbsag == True):
            c_ctr+=1
            const_factors+=('HbsAg ')
            print("Hbsag is reason")

        cardiac = relevant_data['cardiac']#9
        if( cardiac == True):
            c_ctr+=1
            const_factors+=('cardiac_disease ')
            print("cardiac is reason")

        p_uterus = relevant_data['p_uterus']#10
        if( p_uterus == True):
            c_ctr+=1
            const_factors+=('prolapse_uterus ')
            print("prolapse uterus is reason")

        asthama = relevant_data['asthama']#11
        if( asthama == True):
            c_ctr+=1
            const_factors+=('asthama ')
            print("asthama is reason")

        twin_delivery = relevant_data['twin_delivery']#12
        if( twin_delivery == True):
            c_ctr+=1
            const_factors+=('twin_delivery ')
            print("twin delivery is reason")

        gravita = relevant_data['gravita']
        para = relevant_data['para']
        live = relevant_data['live']
        abortion = relevant_data['abortion']

        if(abortion>0):
            c_ctr+=1
            const_factors+=('abortion ')
            print("abortion is reason")



    ########################################################

        #variable high risk factors check
        weight = []
        weight.append(relevant_data['weight'])#13
        if (weight[0]<40 or weight[0]>90):
            v_ctr+=1
            variable_factors+=('weight ')
            print("weight is reason")

        bp1 = []
        bp2 = []
        bp1.append(relevant_data['bp1'])#14
        bp2.append(relevant_data['bp2'])#15
        if (bp1[0]>140 or bp2[0]>90):
            v_ctr+=1
            variable_factors+=('bp ')
            print("BP is reason")

        malrep = []
        malrep.append(relevant_data["malrep"])
        if (not (malrep[0]=="Normal")):
            v_ctr+=1
            variable_factors+=('malrepresentation ')
            print("malrepresentation is reason")

        gdm = []
        gdm.append(relevant_data["gdm"])
        if (gdm[0]>139):
            v_ctr+=1
            variable_factors+=("gdm ")
            print("gdm is reason")

        anemia = []
        anemia.append(relevant_data['anemia'])#18
        if (not(anemia[0]=='None')):
            v_ctr+=1
            variable_factors+=('anemia ')
            print("anemia is reason")

        hb = []
        hb.append(relevant_data['hb'])#19
        if (hb[0]<8):
            v_ctr+=1
            variable_factors+=('haemoglobin ')
            print("HB is reason")

        thyroid = []
        thyroid.append(relevant_data['thyroid'])#20
        if (not (thyroid[0] == 'Normal')):
            v_ctr+=1
            variable_factors+=('thyroid ')
            print("thyroid is reason")

        tobacohol = []
        tobacohol.append(relevant_data['alcohol_tobacco'])#21
        if(tobacohol[0] == True):
            v_ctr+=1
            variable_factors+=('alcohol_tobacco ')
            print("tobacohol is reason")

        vdrl = []
        vdrl.append(relevant_data['vdrl'])#22
        if(vdrl[0] == True):
            v_ctr+=1
            variable_factors+=('vdrl ')
            print("vdrl is reason")

        preg_disease = []
        preg_disease.append(relevant_data['preg_disease'])#23
        if(not(preg_disease[0]=='Adequate')):
            v_ctr+=1
            variable_factors+=('preg_disease ')
            print("preg related disease is reason")

        bleeding_check = []
        bleeding_check.append(relevant_data['bleeding_check'])#24
        if(bleeding_check[0] == True):
            variable_factors+=('bleeding ')
            print("bleeding is reason")

        iugr = []
        iugr.append(relevant_data['iugr'])#25
        if(iugr[0] == True):
            variable_factors+=('iugr ')
            print("iugr is reason")

        alb = []
        alb.append(relevant_data['alb'])#25
        if(not(alb[0] == "None")):
            variable_factors+=('alb ')
            print("ALB is reason")



        if (c_ctr>0 or v_ctr>0):
            hrisk_check = True
            hrisk_factors+=(const_factors)
            hrisk_factors+=(variable_factors)

        if(hrisk_check == False):
            hrisk_check = relevant_data['hrisk_check']

        h_f.append(hrisk_factors)
        c_f.append(const_factors)
        v_f.append(variable_factors)
        visit_number+=1
        print("visit number is  : " + str(visit_number))
        print("high risk value " + str(hrisk_check))
        cur.execute("""INSERT INTO anm_anc (patient_id,anm_anc_date,age,height, previous_lscs, blood_group,disability,blood_disease,
        hiv_check,hbsag,cardiac_disease,prolapse_uterus,asthama,twin_delivery,gravita,para,live,abortion,weight,bp_1,bp_2,malrepresentation,gdm,anemia,
        haemoglobin,thyroid, alcohol_tobacco_check,preg_related_disease,bleeding_check,iugr,alb,hrisk_check,
        constant_factors, variable_factors,hrisk_factors,anm_id,visit_no) VALUES (%s,%s::DATE[],%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (p_id,anm_anc_date,age,height, previous_lscs, bgroup,disability,blood_disease,hiv,hbsag,cardiac,p_uterus,asthama,
        twin_delivery,gravita,para,live,abortion,weight,bp1,bp2,malrep,gdm,anemia,hb,thyroid, tobacohol,preg_disease,bleeding_check,iugr,alb,
        hrisk_check,c_f, v_f,h_f,anm_id,visit_number,))

        cur.execute("UPDATE patient_level SET anc_check=true WHERE patient_id=%s", (p_id,))
        conn.commit()
        print(("anc_check set true done"))
    else:
        ########################################################

        # variable high risk factors check
        anm_anc_date = relevant_data["anm_anc_date"]

        #weight = []
        weight=(relevant_data['weight'])  # 13
        if (weight < 40 or weight > 90):
            v_ctr += 1
            variable_factors += ('weight ')
        #bp1 = []
        #bp2 = []
        bp1=(relevant_data['bp1'])  # 14
        bp2=(relevant_data['bp2'])  # 15
        if (bp1 > 90 or bp2 > 140):
            v_ctr += 1
            variable_factors += ('bp ')

        #malrep = []
        malrep=(relevant_data["malrep"])
        if (not (malrep == 'None')):
            v_ctr += 1
            variable_factors += ('malrepresentation ')

        #gdm = []
        gdm=(relevant_data["gdm"])
        if (gdm > 139):
            v_ctr += 1
            variable_factors += ("gdm ")

        #anemia = []
        anemia=(relevant_data['anemia'])  # 18
        print("anemia is " + str(anemia))
        if (not (anemia == 'None')):
            v_ctr += 1
            variable_factors += ('anemia ')

        #hb = []
        hb=(relevant_data['hb'])  # 19
        if (hb < 8):
            v_ctr += 1
            variable_factors += ('haemoglobin ')

        #thyroid = []
        thyroid=(relevant_data['thyroid'])  # 20
        if (not (thyroid == 'Normal')):
            v_ctr += 1
            variable_factors += ('thyroid ')

        tobacohol = []
        tobacohol=(relevant_data['alcohol_tobacco'])  # 21
        if (tobacohol == True):
            v_ctr += 1
            variable_factors += ('alcohol_tobacco ')

        #vdrl = []
        vdrl=(relevant_data['vdrl'])  # 22
        if (vdrl == True):
            v_ctr += 1
            variable_factors += ('vdrl ')

        #preg_disease = []
        preg_disease=(relevant_data['preg_disease'])  # 23
        if (not (preg_disease == 'Adequate')):
            v_ctr += 1
            variable_factors += ('preg_disease ')

        #bleeding_check = []
        bleeding_check=(relevant_data['bleeding_check'])  # 24
        if (bleeding_check == True):
            variable_factors += ('bleeding ')

        #iugr = []
        iugr=(relevant_data['iugr'])  # 25
        if (iugr == True):
            variable_factors += ('iugr ')

        #alb = []
        alb=(relevant_data['alb'])  # 25
        if (not (alb == "None")):
            variable_factors += ('alb ')

        if (c_ctr > 0 or v_ctr > 0):
            hrisk_check = True
            hrisk_factors += (const_factors)
            hrisk_factors += (variable_factors)

        if (hrisk_check == False):
            hrisk_check = relevant_data['hrisk_check']

        visit_number+=1
        print( "high risk value " + str(hrisk_check))
        #h_f.append(hrisk_factors)
        #c_f.append(const_factors)
        #v_f.append(variable_factors)

        #cur.execute("""INSERT INTO anm_anc (patient_id,age,height, previous_lscs, blood_group,disability,blood_disease,
        #    hiv_check,hbsag,cardiac_disease,prolapse_uterus,asthama,twin_delivery,gravita,para,live,abortion,weight,bp_1,bp_2,malrepresentation,gdm,anemia,
        #    haemoglobin,thyroid, alcohol_tobacco_check,preg_related_disease,bleeding_check,iugr,alb,hrisk_check,
        #    constant_factors, variable_factors,hrisk_factors,anm_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        #            (p_id, age, height, previous_lscs, bgroup, disability, blood_disease, hiv, hbsag, cardiac, p_uterus,
        #             asthama,
        #             twin_delivery, gravita, para, live, abortion, weight, bp1, bp2, malrep, gdm, anemia, hb, thyroid,
        #             tobacohol, preg_disease, bleeding_check, iugr, alb,
        #             hrisk_check, c_f, v_f, h_f, anm_id))


        # bp_1=%s::INTEGER[] ,bp_2=%s::INTEGER[] ,malrepresentation=%s::TEXT[] ,gdm=%s::INTEGER[] ,anemia=%s::TEXT[] ,
        #        haemoglobin=%s::INTEGER[] ,thyroid=%s::TEXT[] , alcohol_tobacco_check=%s::BOOLEAN[] ,preg_related_disease=%s::BOOLEAN[] ,bleeding_check=%s::BOOLEAN[] ,iugr=%s::BOOLEAN[] ,

        cur.execute("""UPDATE anm_anc SET weight=array_append(weight, %s) ,bp_1=array_append(bp_1,%s),bp_2=array_append(bp_2,%s),
        malrepresentation=array_append(malrepresentation,%s),gdm=array_append(gdm,%s),anemia=array_append(anemia,%s),haemoglobin=array_append(haemoglobin,%s),
        thyroid=array_append(thyroid,%s), alcohol_tobacco_check=array_append(alcohol_tobacco_check,%s),preg_related_disease=array_append(preg_related_disease,%s),
        bleeding_check=array_append(bleeding_check,%s),iugr=array_append(iugr,%s),      
                constant_factors=array_append(constant_factors,%s) , variable_factors=array_append(variable_factors,%s) ,
                hrisk_factors=array_append(hrisk_factors,%s),
                visit_no=%s,hrisk_check=%s, anm_anc_date=array_append(anm_anc_date, %s) WHERE patient_id = %s""",
                    ( [weight],[bp1], [bp2],[malrep], [gdm], [anemia], [hb], [thyroid],
                     [tobacohol], [preg_disease], [bleeding_check], [iugr],
                      [const_factors], [variable_factors], [hrisk_factors], [visit_number],[hrisk_check],[anm_anc_date],p_id,))

        conn.commit()

    if(hrisk_check==True):
        cur.execute("UPDATE patient_level SET high_risk_check=True WHERE patient_id = %s", (p_id,))

        visit_dates = []
        visit_dates = visit_schedule(lmp, edd, reg_date)
        #add record to smo_anc table as 0th visit data
        cur.execute("""INSERT INTO smo_anc (patient_id,weight,bp_1,bp_2,malrepresentation,gdm,anemia,
            haemoglobin,thyroid, alcohol_tobacco_check,preg_related_disease,bleeding_check,iugr,alb,hrisk_check,
            constant_factors, variable_factors,hrisk_factors,smo_id,visits_done,visit_dates) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (p_id, weight, bp1, bp2, malrep, gdm, anemia, hb, thyroid,
                     tobacohol, preg_disease, bleeding_check, iugr,alb,
                     hrisk_check, c_f, v_f,h_f, smo_id,0,visit_dates))

        print("smo_id" + str(smo_id))

        officer = get_smo_name(smo_id)
        notify_smo(officer)
        text_to_smo(p_id, officer,patient_name)
        #text_to_supervisor(anm_id,p_id)

        conn.commit()

    return Response({"high_risk" : hrisk_check})


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def anm_app_data_with_anc(request):
    anm_id = get_anm_id(request.user)
    start = int(request.GET.get('start',0))
    patients = []
    cur.execute(
        """SELECT row_to_json(patient_record) FROM (
        SELECT *  FROM anm_anc 
         INNER JOIN patient_level ON anm_anc.patient_id=patient_level.patient_id 
         WHERE patient_level.anm_id=%s and patient_level.anc_check=true)patient_record """,( anm_id,))

    records = cur.fetchall()
    for r in records:
        patients.append(r[0])
    print(len(records))
    end = (start+25)
    return Response({"patients" : patients[start:end]})


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def anm_app_data_without_anc(request):

    anm_id = get_anm_id(request.user)
    start = int(request.GET.get('start', 0))
    patients = []
    cur.execute(
        """SELECT row_to_json(patient_record) FROM (

        SELECT *  FROM patient_level WHERE anm_id=%s and anc_check =false)patient_record """, (anm_id,))

    records = cur.fetchall()
    for r in records:
        patients.append(r[0])
    print(len(records))
    end = (start + 25)
    return Response({"patients": patients[start:end]})


