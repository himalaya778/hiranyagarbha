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
    husband_age = relevant_data["husband_age"] #4
    mobile_number = relevant_data['mobile_number'] # 5
    date_of_birth = relevant_data['date_of_birth']  # 6
    economic_status = relevant_data['economic_status']  # 7
    cast = relevant_data['cast']  # 8
    relegion = relevant_data['relegion']  # 9
    lmp_date = relevant_data['lmp_date'] # 10
    edd_date = relevant_data['edd_date']  # 11
    officer = relevant_data['officer']  # 12
    address = relevant_data["address"]
    agbdi_name = relevant_data['agbdi_name'] #13

    cur.execute("""INSERT INTO patient_level (state,block,division,district,officer,agbdi_name,aadhar_number,patient_name,husband_name,husband_age,mobile_number,
                   date_of_birth, economic_status,cast_type,relegion,lmp_date,edd_date,address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s ) RETURNING patient_id """ , (state,block,division,district,officer,
                    agbdi_name, aadhar_number,patient_name,husband_name,husband_age,mobile_number,date_of_birth, economic_status,cast,relegion,lmp_date,edd_date,address,))
    conn.commit()
    res = cur.fetchall()
    print(res)
    patient_id = res[0]['patient_id']

    return Response({'patient_id' : patient_id})


@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def anc_visit(request):
    id = request.user.id
    relevant_data = json.loads(request.body)
    p_id = relevant_data['patient_id']
    ctr = 0
    hrisk_check = False
    hrisk_factors = []
    const_factors = []
    variable_factors = []

    #constant high risk factors check

    age = relevant_data['age'] #1
    if (age<18 or age>35):
        ctr+=1
        const_factors.append('age')

    height = relevant_data['height'] #2
    if (height<145) :
        ctr+=1
        const_factors.append('height')

    previous_lscs = relevant_data['previous_lscs']
    if (previous_lscs == True):
        ctr+=1
        const_factors.append('previous_lscs')

    bgroup = relevant_data['bgroup']
    if(bgroup in hrisk_bgroups):
        ctr+=1
        const_factors.append('blood group')

    disability = relevant_data['disablity']
    if (not (disability == 'None')):
        ctr+=1
        const_factors.append('disability')

    blood_disease = relevant_data['blood_disease']
    if( not(blood_disease == 'Normal' )):
        ctr+=1
        const_factors.append('blood disease')

    hiv = relevant_data['hiv']
    if( hiv == True):
        ctr+=1
        const_factors.append('hiv')

    hbsag = relevant_data['hbsag']
    if( hbsag == True):
        ctr+=1
        const_factors.append('HbsAg')

    cardiac = relevant_data['cardiac']
    if( cardiac == True):
        ctr+=1
        const_factors.append('cardiac disease')

    p_uterus = relevant_data['p_uterus']
    if( p_uterus == True):
        ctr+=1
        const_factors.append('prolapse uterus')

    asthama = relevant_data['asthama']
    if( asthama == True):
        ctr+=1
        const_factors.append('asthama')

    twin_delivery = relevant_data['twin_delivery']
    if( twin_delivery == True):
        ctr+=1
        const_factors.append('twin delivery')

    ########################################################

    #variable high risk factors check






    return Response ('data saved')













