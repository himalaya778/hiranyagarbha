from django.shortcuts import render

# Create your views here.
from rest_framework.parsers import JSONParser,MultiPartParser,FormParser
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
#import rest_framework.parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .serializers import AuthCustomTokenSerializer
from rest_framework.authtoken.models import Token
import json
import psycopg2
import http.client
conn_text = http.client.HTTPConnection("api.msg91.com")
from django.contrib.auth.models import User
from .msg91test import *
 # Python URL functions
#conn = psycopg2.connect("dbname=lewjwtyv user=lewjwtyv password=mQJ6jIVit_1IR0vhvauSh7Bi9-kTZqe5 host='baasu.db.elephantsql.com'")
#conn = psycopg2.connect("dbname=hiranya user=postgres password=1234 host=localhost")
conn = psycopg2.connect("dbname = d6033pklmp2aij user=kchzgyvpypnnkk password=b421cad27d99754ad0771149a573f61f28b03da630bba71b6c7510c67b8515d0 host='ec2-54-83-50-145.compute-1.amazonaws.com'")
cur = conn.cursor()


@authentication_classes((SessionAuthentication, TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
class UserCreate(APIView):
    """
    Creates the user.
    """
    def post(self, request, format='json'):
        relevant_data = json.loads(request.body)
        name=relevant_data['username']
        password = relevant_data['password']
        role = relevant_data['role']
        mobile = relevant_data['mobile']
        print(relevant_data)
        serializer = UserSerializer(data=relevant_data)

        user_id = request.user.id
        print(request.user)
        if serializer.is_valid():
            user = serializer.save()
            if user:

                ###############################

                cur.execute("SELECT bmo_id FROM bmo_level WHERE bmo = %s",(str(request.user),))
                records = cur.fetchall()
                if len(records) > 0:
                    bmo_id = records[0][0]
                else:
                    cur.execute("SELECT cdpo_id FROM cdpo_level WHERE cdpo = %s",(str(request.user),))
                    records = cur.fetchall()
                    if(len(records)>0):
                        cdpo_id = records[0][0]

                token = Token.objects.create(user=user)

                json_data = serializer.data
                json_data['token'] = token.key
                if(relevant_data['role'] == 'bmo' or relevant_data['role'] == 'cdpo'):
                    cur.execute("UPDATE auth_user SET role = %s, block = %s, district = %s, division = %s, state = %s, mobile = %s,first_name = %s WHERE id = %s",
                            (   relevant_data['role'],relevant_data['block'] ,relevant_data['division'] , relevant_data['district'], relevant_data['state'],relevant_data['mobile'],relevant_data['name'],json_data['id'] ))

                else:
                    if(relevant_data['role'] == 'smo' or relevant_data['role'] == 'anm'):
                        cur.execute('SELECT state, division, block, district FROM auth_user WHERE id = %s' , (user_id,))
                        h_records = cur.fetchall()
                        print(h_records)
                        state = h_records[0][0]
                        division = h_records[0][1]
                        block = h_records[0][2]
                        district = h_records[0][3]
                        cur.execute(
                            "UPDATE auth_user SET role = %s, block = %s, district = %s, division = %s, state = %s, mobile = %s,first_name = %s WHERE id = %s",
                            (relevant_data['role'], block, division,
                             district,state, relevant_data['mobile'],
                             relevant_data['name'], json_data['id']))


                    if(relevant_data['role'] == 'supervisor' or relevant_data['role'] == 'worker'):
                        cur.execute('SELECT state, division, block, district FROM auth_user WHERE id = %s' , (user_id,))
                        i_records = cur.fetchall()
                        print(i_records)
                        state = i_records[0][0]
                        division = i_records[0][1]
                        block = i_records[0][2]
                        district = i_records[0][3]
                        cur.execute(
                            "UPDATE auth_user SET role = %s, block = %s, district = %s, division = %s, state = %s, mobile = %s,first_name = %s WHERE id = %s",
                            (relevant_data['role'], block, division,
                             district,state, relevant_data['mobile'],
                             relevant_data['name'], json_data['id']))


                if(relevant_data['role'] == 'district'):
                    state = relevant_data['state']
                    division = relevant_data['division']
                    block = relevant_data['block']
                    district = relevant_data['district']
                    mobile = relevant_data['mobile']
                    cur.execute(
                        "UPDATE auth_user SET role = %s, block = %s, district = %s, division = %s, state = %s, mobile = %s,first_name = %s WHERE id = %s",
                        (relevant_data['role'], block, division,
                         district, state, mobile,
                         relevant_data['name'], json_data['id']))

                    cur.execute("INSERT INTO district_officer(officer,district) VALUES(%s,%s)", (relevant_data['username'],district))

                if(relevant_data['role'] == 'division'):
                    state = relevant_data['state']
                    division = relevant_data['division']
                    block = relevant_data['block']
                    district = relevant_data['district']
                    mobile = relevant_data['mobile']
                    cur.execute(
                        "UPDATE auth_user SET role = %s, block = %s, district = %s, division = %s, state = %s, mobile = %s,first_name = %s WHERE id = %s",
                        (relevant_data['role'], block, division,
                         district, state, mobile,
                         relevant_data['name'], json_data['id']))

                    cur.execute("INSERT INTO division_officer(officer,division) VALUES(%s,%s)", (relevant_data['username'],division,))

                #entry to bmo_level
                if (relevant_data['role'] == 'bmo'):
                    cur.execute("INSERT INTO bmo_level(bmo) VALUES(%s)",(relevant_data['username'],))
                    text_to_user(name,password,mobile)
                #entry to smo_level
                if (relevant_data['role'] == 'smo'):
                    cur.execute("INSERT INTO smo_level(smo,mobile_number,bmo_id) VALUES(%s,%s,%s)",(relevant_data['username'],relevant_data['mobile'],bmo_id))
                    text_to_user(name, password,mobile)
                #entry to anm_level
                if (relevant_data['role'] == 'anm'):
                    cur.execute("INSERT INTO anm_level(anm,mobile_number,bmo_id) VALUES(%s,%s,%s)",
                                (relevant_data['username'], relevant_data['mobile'], bmo_id))
                    print('anm in creation')
                    print(user_id)
                    text_to_user(name, password,mobile)
                    print("function executed successfully")


                #entry to cdpo
                if (relevant_data['role'] == 'cdpo'):
                    cur.execute("INSERT INTO cdpo_level(cdpo) VALUES(%s)",(relevant_data['username'],))
                #entry to supervisor level
                if (relevant_data['role'] == 'supervisor'):
                    cur.execute("INSERT INTO supervisor_level(supervisor,cdpo_id) VALUES(%s,%s)",(relevant_data['username'],cdpo_id))
                #entry to anganbadi_worker level
                if (relevant_data['role'] == 'anganbadi_worker'):
                    cur.execute("INSERT INTO worker_level(worker,cdpo_id) VALUES(%s,%s)",(relevant_data['username'],cdpo_id))

                conn.commit()

                return Response(json_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        FormParser,
        MultiPartParser,
        JSONParser,
    )

    renderer_classes = (JSONRenderer,)

    def post(self, request):
        #print("request data is" , request.data)
        #print(request.data["_parts"][0][1])
        #print("request body is" , request.body)

        if not("source" in request.data):
            serializer = AuthCustomTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            if(user.is_superuser):
                role = "admin"
            token, created = Token.objects.get_or_create(user=user)
            print(token.user_id)
            #harman_singh
            #kaushik
            #ramesh_kumar
            #seema_rani
            cur.execute("SELECT * FROM auth_user WHERE id = %s" , (str(token.user_id),))
            records = list(set(cur.fetchall()))
            print(records)

            if (records[0][11] == 'bmo'):

                cur.execute("""SELECT * FROM bmo_level WHERE bmo = %s""" , (str(records[0][4]),))
                records_candidate = cur.fetchall()
                bmo_id = records_candidate[0][0]
                cur.execute(""" SELECT  bmo_level.bmo_id,
                                        smo_level.smo
                                        FROM
                                        bmo_level
                                        INNER JOIN smo_level ON smo_level.bmo_id = bmo_level.bmo_id""")

                records_bmo = cur.fetchall()
                print(records_bmo)
                smo = []
                for i in range(0, len(records_bmo)):
                    if (records_bmo[i][0] == bmo_id):
                        smo.append(records_bmo[i][1])
                ###############################################
                cur.execute("""SELECT bmo_level.bmo,
                                      village_level.village,
                                      anganbadi_level.agbdi
                                      FROM 
                                      bmo_level
                                      INNER JOIN village_level ON village_level.bmo_id = bmo_level.bmo_id
                                      INNER JOIN anganbadi_level ON anganbadi_level.village_id = village_level.village_id""")
                #print("anganbadi list : " , cur.fetchall())
                agbdi_records = cur.fetchall()
                agbdi = []
                for  a in agbdi_records:
                    print(a[0] , " ", records[0][4])
                    if a[0] == records[0][4]:
                        agbdi.append(a[2])
                print(agbdi)
                cur.execute(""" SELECT  bmo_level.bmo_id,
                                                        anm_level.anm
                                                        FROM
                                                        bmo_level
                                                        INNER JOIN anm_level ON anm_level.bmo_id = bmo_level.bmo_id""")

                records_anm = cur.fetchall()
                print(records_anm)
                anm = []
                for i in range(0, len(records_anm)):
                    if (records_anm[i][0] == bmo_id):
                        anm.append(records_anm[i][1])

                content = {
                    'status' : 'success','token': str(token.key) , 'role' : (records[0][11]), 'state' : records[0][12], 'block' : records[0][14],
                    'district' : records[0][15] , 'division' : records[0][13] , 'name' : records[0][4] , "smo" : smo, "anm" : anm, "agbdi" : agbdi
                }

                return Response(content)
            content = {
                'status': 'success', 'token': str(token.key), 'role': (records[0][11]), 'state': 'Madhya Pradesh',
                'block': 'gazipur',
                'district': 'Bhopal', 'division': 'hoshangabad', 'name': records[0][4]
            }


            if(records[0][11] == "cdpo"):

                cur.execute("""SELECT * FROM cdpo_level WHERE cdpo = %s""" , (str(records[0][4]),))
                records_candidate = cur.fetchall()
                cdpo_id = records_candidate[0][0]
                cur.execute(""" SELECT  cdpo_level.cdpo_id,
                                        supervisor_level.supervisor
                                        FROM
                                        cdpo_level
                                        INNER JOIN supervisor_level ON supervisor_level.cdpo_id = cdpo_level.cdpo_id""")

                records_supervisor = cur.fetchall()
                print(records_supervisor)
                supervisor = []
                for i in range(0, len(records_supervisor)):
                    if (records_supervisor[i][0] == cdpo_id):
                        supervisor.append(records_supervisor[i][1])

                cur.execute(""" SELECT  cdpo_level.cdpo_id,
                                                        worker_level.worker
                                                        FROM
                                                        cdpo_level
                                                        INNER JOIN worker_level ON worker_level.cdpo_id =  cdpo_level.cdpo_id""")

                records_worker = cur.fetchall()
                print(records_worker)
                worker = []
                for i in range(0, len(records_worker)):
                    if (records_worker[i][0] == cdpo_id):
                        worker.append(records_worker[i][1])

                content = {
                    'status' : 'success','token': str(token.key) , 'role' : (records[0][11]), 'state' : records[0][12], 'block' : records[0][14],
                    'district' : records[0][15] , 'division' : records[0][13] , 'name' : records[0][4] , "supervisor" : supervisor,
                    "anganbadi_workers" : worker
                }

                return Response(content)

            if (records[0][11] == "smo"):
                vill_list = []
                cur.execute("SELECT smo_id FROM smo_level WHERE smo = %s", (records[0][4],))
                rec_smo = cur.fetchall()
                smo_id = rec_smo[0][0]
                cur.execute("SELECT anm_id FROM anm_level WHERE smo_id = %s", (smo_id,))
                rec_anm = cur.fetchall()
                anm_ids = rec_anm[0]
                for a in anm_ids:
                    cur.execute("SELECT village FROM village_level WHERE anm_id = %s", (a,))
                    rec_vill = cur.fetchall()
                    if(len(rec_vill)>0):
                        vill_list.append(rec_vill[0][0])
                content = {
                    'status' : 'success','token': str(token.key) , 'role' : (records[0][11]), 'state' : records[0][12], 'block' : records[0][14],
                    'district' : records[0][15] , 'division' : records[0][13] , 'name' : records[0][4] , 'villages' : vill_list
                }

                return Response(content)

            if (records[0][11] == "anm"):
                print(str(request.user.username))
                cur.execute("SELECT smo_id,anm_id FROM anm_level WHERE anm = %s" , (str(records[0][4]),))
                records_officers = cur.fetchall()
                smo_id = records_officers[0][0]
                cur.execute("SELECT smo FROM smo_level WHERE smo_id = %s" , (int(smo_id),))
                records_smo = cur.fetchall()
                smo_name = records_smo[0][0]

                anm_id = records_officers[0][1]
                cur.execute("SELECT village FROM village_level WHERE anm_id = %s" , (int(anm_id),))
                records_villages = cur.fetchall()
                villages = records_villages[0]
                content = {
                    'status' : 'success','token': str(token.key) , 'role' : (records[0][11]), 'state' : records[0][12], 'block' : records[0][14],
                    'district' : records[0][15] , 'division' : records[0][13] , 'name' : records[0][4] , 'officer' : smo_name , 'villages' : villages
                }

                return Response(content)

            content = {
                'status': 'success', 'token': str(token.key), 'role': (records[0][11]), 'state': 'Madhya Pradesh'
            }
        #print(content)
            return Response(content)

        else:

            mock_data = {"email_or_username" : request.data["email_or_username"] , "password" : request.data["password"] }

            serializer = AuthCustomTokenSerializer(data=mock_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            if (user.is_superuser):
                role = "admin"
            else:
                role = "manager"
            token, created = Token.objects.get_or_create(user=user)

            content = {
                "status": "success", "role": role, "token": str(token.key)
            }
            content = json.dumps(content)
            # print(content)
            return Response(content)