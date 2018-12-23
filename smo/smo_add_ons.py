def get_visit_number(id):
    cur.execute("SELECT visits_done FROM smo_anc WHERE patient_id = s" , (id,))
    records_v = cur.fetchall()
    v_no = records_v[0][0]
    return v_no
