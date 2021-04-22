#!/usr/bin/python

import os
import sqlite3
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
import json
import discord
from discord.ext import commands
import config

client=commands.Bot(command_prefix= '.')

discord_token=config.discord_token
con=sqlite3.connect('volume.db')
cursor=con.cursor()

cursor.execute('''SELECT name FROM sqlite_master WHERE  type='table'; ''')
tables= cursor.fetchall()
list_table=[]
loc_sembol={}
pos_sembol={}
out_of_list=[]
into_list={}
for i in tables:
	table_name=i[0]
	list_table.append(table_name)

table1=pd.read_sql('''SELECT * FROM [{}]; '''.format(list_table[-1]),con)

table2=pd.read_sql('''SELECT * FROM [{}]; '''.format(list_table[-2]),con)

table1_list=table1['coin'].values.tolist()
table1_sira=table1['sira'].values.tolist()
for i in range(len(table1_list)):
	loc_sembol[table1_list[i]]=[]
	pos_sembol[table1_list[i]]=0
	loc_sembol[table1_list[i]].append(table1_sira[i])

table2_list=table2['coin'].values.tolist()
table2_sira=table2['sira'].values.tolist()
for i in range(len(table2_list)):
	if not table2_list[i] in loc_sembol.keys():
		#print('coin yok {}'.format(table2_list[i]))
		loc_sembol[table2_list[i]]=[]
		loc_sembol[table2_list[i]].append(1000)
	else:
		loc_sembol[table2_list[i]].append(table2_sira[i])


for i in loc_sembol.keys():
	if len(loc_sembol[i])<2:
			position=loc_sembol[i][-1]
			pos_sembol[i]=position
	else:
		position=loc_sembol[i][-1] - loc_sembol[i][-2]
		pos_sembol[i]=position

#print(combine)
list_pos_sembol_value=list(pos_sembol.values())
list_pos_sembol_value.sort(reverse=True)
order_pos_sembol={}
for i in range(len(list_pos_sembol_value)):
	for j in pos_sembol.keys():
		if pos_sembol[j]==list_pos_sembol_value[i]:
			order_pos_sembol[j]=pos_sembol[j]

changed_coin={}
for x in order_pos_sembol:
	if order_pos_sembol[x]==1000:
		out_of_list.append(x)
	elif len(loc_sembol[x])<2:
		into_list[x]=loc_sembol[x][-1]
	elif order_pos_sembol[x]>0 and order_pos_sembol[x]<1000:
		changed_coin[x]=order_pos_sembol[x]
	elif order_pos_sembol[x]<=0:
		changed_coin[x]=order_pos_sembol[x]



results=json.dumps(order_pos_sembol)
into=json.dumps(into_list)
chan=json.dumps(changed_coin)
combine=pd.concat([table1,table2],axis=1)

text_list=open("list.txt","a")
text_list.write(str([list_table[-1],list_table[-2]])+'\n')
text_list.write(str(combine.to_string()))

#text_list.write(combine.to_string())
text_list.close()




#Discord
@client.event
async def on_ready():
   #print('bot ready')
   channel=client.get_channel(config.channel)
   content=str("Into_list:\n" + into + "\n" + "Out_of_list:\n" + str(out_of_list) + "\n" + "changed:\n" + chan)
   await channel.send(content)
   await channel.send(file=discord.File('list.txt'))
   await client.close()

client.run(discord_token)
#Mail

s=smtplib.SMTP_SSL(host='smtp.example.com')
s.login("example@example.com", "[YOUR MAIL PASSWORD]")

msg=EmailMessage()

msg['Subject']="Last 6h volumes"

msg.set_content("Into_list:\n"+into+"\n"+"Out of list:\n"+str(out_of_list)+"\n"+'changed:\n'+chan)
filename='list.txt'
msg.add_attachment(open(filename, "r").read(),filename='list.txt')
s.sendmail("example@example.com","[Reciever Mail]",msg.as_string())
s.quit()


if os.path.exists('list.txt'):
	os.remove('list.txt')
else:
	pass
