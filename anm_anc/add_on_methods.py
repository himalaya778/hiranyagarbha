from accounts.views import conn
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
    print(records_anm)
    anm_id = records_anm[0][0]
    return anm_id