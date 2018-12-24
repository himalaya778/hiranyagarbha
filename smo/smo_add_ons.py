from accounts.views import conn


cur = conn.cursor()
def get_visit_number(id):
    cur.execute("SELECT visits_done FROM smo_anc WHERE patient_id = %s" , (id,))
    records_v = cur.fetchall()
    v_no = records_v[0][0]
    return v_no
def find_smo_id(user):
    print(user)
    cur.execute("SELECT smo_id FROM smo_level WHERE smo = %s", (str(user),))
    records_smo = cur.fetchall()
    #print(records_smo)
    smo_id = records_smo[0][0]
    return smo_id