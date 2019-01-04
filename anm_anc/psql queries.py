import psycopg2
from pandas import DataFrame

conn = psycopg2.connect("dbname = dfkj1lkglat6mk user=iawnbgcbnwgwjw password=e01a16637ff3acf9f09168ebf7f5ced0969e16f2fa3bcd21dac2daf759498248 host='ec2-54-225-150-216.compute-1.amazonaws.com'")
cur = conn.cursor()

#cur.execute("SELECT count(*),village,bmo_id,population FROM village_level GROUP BY village,bmo_id,population HAVING count(*)>1 ORDER BY bmo_id")

cur.execute("SELECT count(8),* FROM village_level GROUP BY village_id,village,anm_id,bmo_id,sup_id,state,division,block,population")
df = DataFrame(cur.fetchall())
#df.columns = cur.keys()

#print(df)

df.to_csv("village_repeat.csv")
