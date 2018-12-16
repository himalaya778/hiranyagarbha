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
    officer = relevant_data['officer']  # 12
    address = relevant_data["address"]
    #agbdi_name = relevant_data['agbdi_name'] #13

    cur.execute("""INSERT INTO patient_level (state,block,division,district,officer,aadhar_number,patient_name,husband_name,mobile_number,
                   date_of_birth,age,economic_status,cast_type,relegion,lmp_date,edd_date,address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s ) 
                   RETURNING patient_id """ , (state,block,division,district,officer,
                     aadhar_number,patient_name,husband_name,mobile_number,date_of_birth,age,economic_status,cast,relegion,lmp_date,edd_date,address,))
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
    relevant_data = json.loads(request.body)
    p_id = relevant_data['patient_id']
    c_ctr = 0
    v_ctr = 0
    hrisk_check = False
    hrisk_factors = []
    const_factors = []
    variable_factors = []

    #constant high risk factors check
    cur.execute("SELECT age FROM patient_level WHERE patient_id = %s" , (p_id,))
    age_rec = cur.fetchall()
    age = age_rec[0][0] #1
    #age = relevant_data['age']
    if (age<18 or age>35):
        c_ctr+=1
        const_factors.append('age')

    height = relevant_data['height'] #2
    if (height<145) :
        c_ctr+=1
        const_factors.append('height')

    previous_lscs = relevant_data['previous_lscs']#3
    if (previous_lscs == True):
        c_ctr+=1
        const_factors.append('previous_lscs')

    bgroup = relevant_data['bgroup']#4
    if(bgroup in hrisk_bgroups):
        c_ctr+=1
        const_factors.append('blood group')

    disability = relevant_data['disability']#5
    if (not (disability == 'None')):
        c_ctr+=1
        const_factors.append('disability')

    blood_disease = relevant_data['blood_disease']#6
    if( not(blood_disease == 'Normal' )):
        c_ctr+=1
        const_factors.append('blood disease')

    hiv = relevant_data['hiv']#7
    if( hiv == True):
        c_ctr+=1
        const_factors.append('hiv')

    hbsag = relevant_data['hbsag']#8
    if( hbsag == True):
        c_ctr+=1
        const_factors.append('HbsAg')

    cardiac = relevant_data['cardiac']#9
    if( cardiac == True):
        c_ctr+=1
        const_factors.append('cardiac disease')

    p_uterus = relevant_data['p_uterus']#10
    if( p_uterus == True):
        c_ctr+=1
        const_factors.append('prolapse uterus')

    asthama = relevant_data['asthama']#11
    if( asthama == True):
        c_ctr+=1
        const_factors.append('asthama')

    twin_delivery = relevant_data['twin_delivery']#12
    if( twin_delivery == True):
        c_ctr+=1
        const_factors.append('twin delivery')

    ########################################################

    #variable high risk factors check
    weight = []
    weight.append(relevant_data['weight'])#13
    if (weight[0]<40 or weight[0]>90):
        v_ctr+=1
        variable_factors.append('weight')
    bp1 = []
    bp2 = []
    bp1.append(relevant_data['bp1'])#14
    bp2.append(relevant_data['bp2'])#15
    if (bp1[0]>90 or bp2[0]>140):
        v_ctr+=1
        variable_factors.append('bp')

    malrep = []
    malrep.append(relevant_data["malrep"])
    if (not (malrep[0]==None)):
        v_ctr+=1
        variable_factors.append('malrepresentation')

    gdm = []
    gdm.append(relevant_data["gdm"])
    if (gdm[0]>139):
        v_ctr+=1
        variable_factors.append("gdm")

    anemia = []
    anemia.append(relevant_data['anemia'])#18
    if (not(anemia[0]==None)):
        v_ctr+=1
        variable_factors.append('anemia')

    hb = []
    hb.append(relevant_data['hb'])#19
    if (hb[0]<8):
        v_ctr+=1
        variable_factors.append('haemoglobin')

    thyroid = []
    thyroid.append(relevant_data['thyroid'])#20
    if (not (thyroid[0] == 'Normal')):
        v_ctr+=1
        variable_factors.append('thyroid')

    tobacohol = []
    tobacohol.append(relevant_data['alcohol_tobacco'])#21
    if(tobacohol[0] == True):
        v_ctr+=1
        variable_factors.append('alcohol/tobacco')

    vdrl = []
    vdrl.append(relevant_data['vdrl'])#22
    if(vdrl[0] == True):
        v_ctr+=1
        variable_factors.append('vdrl')

    preg_disease = []
    preg_disease.append(relevant_data['preg_disease'])#23
    if(not(preg_disease[0]=='Adequate')):
        v_ctr+=1
        variable_factors.append('preg_disease')

    bleeding_check = []
    bleeding_check.append(relevant_data['bleeding_check'])#24
    if(bleeding_check[0] == True):
        variable_factors.append('bleeding')

    iugr = []
    iugr.append(relevant_data['iugr'])#25
    if(iugr[0] == True):
        variable_factors.append('iugr')


    if (c_ctr>0 or v_ctr>0):
        hrisk_check = True
        hrisk_factors.append(const_factors)
        hrisk_factors.append(variable_factors)
        factors = []
        factors = relevant_data['hrisk_factors']
        hrisk_factors.append(factors)

    if(hrisk_check == False):
        hrisk_check = relevant_data['hrisk_check']
        if (hrisk_check == True):
            hrisk_factors = relevant_data['hrisk_factors']


    cur.execute("""INSERT INTO anm_anc (patient_id,age,height, previous_lscs, blood_group,disability,blood_disease,
    hiv_check,hbsag,cardiac_disease,prolapse_uterus,asthama,twin_delivery,weight,bp_1,bp_2,malrepresentation,gdm,anemia,
    haemoglobin,thyroid, alcohol_tobacco_check,preg_related_disease,bleeding_check,iugr,hrisk_check,
    constant_factors, variable_factors) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (p_id,age,height, previous_lscs, bgroup,disability,blood_disease,hiv,hbsag,cardiac,p_uterus,asthama,
    twin_delivery,weight,bp1,bp2,malrep,gdm,anemia,hb,thyroid, tobacohol,preg_disease,bleeding_check,iugr,
    hrisk_check,const_factors, variable_factors,))

    conn.commit()

    return Response("visit data saved")














    return Response ('data saved')















