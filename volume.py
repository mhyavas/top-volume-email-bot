from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json , pprint
from datetime import datetime
import sqlite3
import config


vol_time= int(datetime.now().timestamp())
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
  'start':'1',
  'limit':'5000',
  'convert':'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': config.coincapapi,
}

session = Session()
session.headers.update(headers)
volumes={}
ascending_vol={}
def table_del():
    del_con=sqlite3.connect('volume.db')
    del_cur=del_con.cursor()
    del_cur.execute('''SELECT name FROM sqlite_master WHERE  type='table'; ''')
    tables=del_cur.fetchall()
    for i in tables:
        table_name=i[0]
        if int(table_name) + 43200000 < vol_time:
            del_cur.execute("DROP TABLE [{}]".format(table_name))

def sorting(dictionary):
    sayac=1
    list_values=[]
    #Database Connection
    con=sqlite3.connect('volume.db')
    cursor=con.cursor()
    cursor.execute(''' CREATE TABLE [{}](coin TEXT, volume REAL, sira INTEGER)'''.format(str(vol_time)))
    con.commit()
    for i in dictionary.keys():
        list_values.append(dictionary[i][-1])
    list_values.sort(reverse=True)
    for i in range(len(list_values)):
        for x in dictionary.keys():
            if list_values[i] == dictionary[x][-1]:
                con_volume=sqlite3.connect('volume.db')
                cur_vol=con_volume.cursor()
                cur_vol.execute(" INSERT INTO "+str([vol_time])+"(coin, volume,sira) VALUES (?,?,?)",(x,list_values[i],sayac))
                con_volume.commit()


                sayac=sayac+1

            if sayac==101:
                break
def handle_message(msg):
    for i in range(len(msg['data'])):
        sembol=msg['data'][i]['symbol']
        vol_24h=float(msg['data'][i]['quote']['USD']['volume_24h'])
        volumes[sembol]=[]
        volumes[sembol].append(vol_24h)
    #pprint.pprint(volumes)
    sorting(volumes)
try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)
  
  handle_message(data)
  table_del()
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)
