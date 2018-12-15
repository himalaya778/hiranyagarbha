from accounts.views import conn
cur = conn.cursor()
def address_mapping(id):
    cur.execute(
        "SELECT row_to_json(user_record) FROM (SELECT state,block,division,district  FROM auth_user WHERE id = %s) user_record ",
        (int(id),))
    records = cur.fetchall()
    return (records[0][0])