from .views import conn
cur = conn.cursor()
def village_list(user_name):
    villages = []
    cur.execute("SELECT smo_id FROM smo_level WHERE smo = %s", (user_name,))
    rec_smo = cur.fetchall()
    smo_id = rec_smo[0][0]

    cur.execute("SELECT anm_id FROM anm_level WHERE smo_id = %s",(smo_id,))
    rec_anm = cur.fetchall()
    anm_ids = rec_anm[0]
    if(len(anm_ids)>0):
        for a in anm_ids:
            cur.execute("SELECT village FROM village_level WHERE anm_id = %s", (a,))
            rec_village = cur.fetchall()
            vill = rec_village[0][0]
            villages.append(vill)

    return villages
