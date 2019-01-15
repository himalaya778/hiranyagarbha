import psycopg2
from pandas import DataFrame

conn = psycopg2.connect("dbname = dfkj1lkglat6mk user=iawnbgcbnwgwjw password=e01a16637ff3acf9f09168ebf7f5ced0969e16f2fa3bcd21dac2daf759498248 host='ec2-54-225-150-216.compute-1.amazonaws.com'")
cur = conn.cursor()

#cur.execute("SELECT agbdi,cdpo_id FROM anganbadi_level WHERE village_id is Null")
cur.execute("SELECT cdpo FROM cdpo_level WHERE cdpo_id in (18,19,20,21,22,23,24,25,26,27,28,30,32,33,34,35,36,37,38,39,40,41,42)")
df = DataFrame(cur.fetchall())
#df.columns = cur.keys()

#print(df)

df.to_csv("agbdi_village_block.csv")
