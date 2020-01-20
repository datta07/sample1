from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import telegram
import logging
import requests
from pyDes import *
import base64
import websocket
import json
import time
import threading
import os

os.environ['TZ']='Asia/Kolkata'
time.tzset()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

class DowMusic:
	def __init__(self):
		self.updater = Updater(token='1061220265:AAGeTlhy13Iz65YstQbwM8Jdw2-AOBH4Veo', use_context=True)
		self.dispatcher = self.updater.dispatcher
		start_handler = CommandHandler('start', self.start)
		self.dispatcher.add_handler(start_handler)
		start_handler = CommandHandler('exit', self.exit)
		self.dispatcher.add_handler(start_handler)
		echo_handler = MessageHandler(Filters.text, self.echo)
		self.dispatcher.add_handler(echo_handler)
		self.current={}
		self.updater.start_polling()

	def set_firebase(self,path,data):
		url1='https://guvi-41d93.firebaseio.com/telebot/'+path+'/.json'
		if path=='':
			url1='https://guvi-41d93.firebaseio.com/'
		r = json.dumps(data)
		to_database = json.loads(r)
		requests.patch(url = url1 , json = to_database)

	def note(self,matter):
		print(matter)
		with open('logs.txt','a') as f:
			f.write(matter+'\n')

	def start(self,update, context):
		context.chat_data['stage']=0
		details=update.effective_chat
		name=self.getUserName(update)
		self.note(time.strftime('%D-%T')+' - '+name+' - '+' Started')
		context.bot.send_message(chat_id=update.effective_chat.id, text='-'*26+"\n🧞‍♂️@garudadevbot🧞‍♂️ \n"+'-'*26+"\n  🎉Welcomes You  \n"+'-'*26+'\n    Dear '+name+', Enjoy UNLIMTED HIGH QUALITY SONGS DOWNLOAD on this BOT.  User Guide is posted below 👇')
		context.bot.send_video(chat_id=update.effective_chat.id,video='https://drive.google.com/uc?export=download&id=1-rUQAZ_WjrL9dXYM3b5fd4valmXM0Oys',supports_streaming=True,caption='📌User Guide')
		context.bot.send_message(chat_id=update.effective_chat.id, text='👋\n Enter the Song or Movie you Want:- 🧜‍♂️')
		self.set_firebase(name,{time.strftime("%d-%m-%Y-%T"):"started"})

	def exit(self,update, context):
		name=self.getUserName(update)
		self.note(time.strftime('%D-%T')+' - '+name+' - '+' Exited')
		context.bot.send_message(chat_id=update.effective_chat.id,text="🙅‍♂️ Canceled present query")
		context.bot.send_message(chat_id=update.effective_chat.id,text='👋\n Enter another Movie name or Song name:- 🧜‍♂️')
		try:
			context.chat_data['stage']=0
		except Exception:
			pass

	def send_song(self,url,update,context):
		name=self.getUserName(update)
		self.note(time.strftime('%D-%T')+' - '+name+' - '+'song downloaded')
		context.bot.send_message(chat_id=update.effective_chat.id,text='Please wait the song is loading... 🧨')
		context.chat_data['stage']=0
		threading.Thread(target=self.set_firebase,args=(context.chat_data['name'],{time.strftime('%d-%m-%Y-%T'):context.chat_data['update']})).start()
		context.bot.send_audio(chat_id=update.effective_chat.id,title='garuda',caption='🙏Thanks for downloading song using GARUDA🙏\nFor any details contact :-\nakula.gurudatta@gmail.com',audio=url)
		context.bot.send_message(chat_id=update.effective_chat.id,text='👋\n Enter another Movie name or Song name:- 🧜‍♂️')

	def getUserName(self,update):
		name=''
		try:
			details=update.effective_chat
			name=details['first_name']+" "
			name+=details['last_name']
		except Exception:
			pass
		return name

	def echo(self,update, context):
		name=self.getUserName(update)
		self.note(time.strftime('%D-%T')+' - '+name+' - '+update.message.text)
		if (context.chat_data=={}):
			context.chat_data['stage']=0

		if (context.chat_data['stage']!=0):
			context.chat_data['update']+=str(update.message.text)
			try:
				if (int(update.message.text) in context.chat_data['options']):
					no=int(update.message.text)-1
				else:
					context.bot.send_message(chat_id=update.effective_chat.id, text="🙅‍♂️ Options must be b/w 1 and "+str(len(context.chat_data['options'])))
					context.bot.send_message(chat_id=update.effective_chat.id,text='👋\n TRY again Enter Movie name or Song name:- 🧜‍♂️')
					context.chat_data['stage']=0
			except Exception:
				context.bot.send_message(chat_id=update.effective_chat.id, text="🙅‍♂️ Entered Wrong... Must be a NUMBER,Check tutorial once again...")
				context.bot.send_message(chat_id=update.effective_chat.id,text='👋\n TRY again Enter Movie name or Song name:- 🧜‍♂️')
				context.chat_data['stage']=0

			#no=int(update.message.text)-1
			if (context.chat_data['stage']==1):
				if (no==0):
					if (context.chat_data['stage1'][2]==1):
						matter,l=self.url_album_design(context.chat_data['stage1'][1],no)
						matter+='\n 👉 Select an Option b/w 1 and '+str(len(l))
						matter+='  (or)   /exit'
						context.bot.send_message(chat_id=update.effective_chat.id, text=matter)
						context.chat_data['stage']=2
						context.chat_data['stage2']=[l]
						context.chat_data['options']=list(range(1,len(l)+1))
					else:
						url=self.url_song_design(context.chat_data['stage1'][1][no])
						self.send_song(url,update,context)

				elif (no<context.chat_data['stage1'][0]):
					matter,l=self.url_album_design(context.chat_data['stage1'][1],no)
					matter+='\n 👉 Select an Option b/w 1 and '+str(len(l))
					matter+='  (or)   /exit'
					context.bot.send_message(chat_id=update.effective_chat.id, text=matter)
					context.chat_data['stage']=2
					context.chat_data['stage2']=[l]
					context.chat_data['options']=list(range(1,len(l)+1))
				else:
					url=self.url_song_design(context.chat_data['stage1'][1][no])
					self.send_song(url,update,context)

			elif (context.chat_data['stage']==2):
				url=context.chat_data['stage2'][0][no]
				self.send_song(url,update,context)

				

		else:
			context.chat_data['name']=name
			l,matter,t,qr=self.sendList(update.message.text)
			context.chat_data['stage']=1
			context.chat_data['stage1']=[t,l,qr]
			context.chat_data['options']=list(range(1,len(l)+1))
			if (len(context.chat_data['options'])==0):
				context.bot.send_message(chat_id=update.effective_chat.id, text="😒\n  NO RESULTS FOUND..,ENTER CORRECT SPEELING..")
				context.bot.send_message(chat_id=update.effective_chat.id,text='👋\n TRY again Enter Movie name or Song name:- 🧜‍♂️')
				context.chat_data['stage']=0
			else:
				context.chat_data['update']=update.message.text
				matter+='\n 👉 Select an Option b/w 1 and '+str(len(l))
				matter+='  (or)   /exit'
				context.bot.send_message(chat_id=update.effective_chat.id, text=matter)



	def searcher(self,query):
		url='wss://ws.saavn.com/'
		ws = websocket.create_connection(url)
		msg='{"url":"\\\/api.php?__call=autocomplete.get&_marker=0&query='+query+'&ctx=android&_format=json&_marker=0"}'
		ws.send(msg)
		result = ws.recv()
		result=json.loads(result)
		result=result['resp']
		result=json.loads(result)
		top_query=[]
		song=[]
		album=[]
		for j in list(result.keys()):
			try:
				if (j=='topquery'):
					i=result[j]
					i=i['data'][0]
					if (i['type']=='album'):
						top_query.append({'id':i['id'],'title':i['title'],'music':i['music'],'year':i['more_info']['year'],'language':i['more_info']['language'],'movie':i['more_info']['is_movie'],'state':1})
					else:
						top_query.append({'id':i['id'],'title':i['title'],'album':i['album'],'primary_artists':i['more_info']['primary_artists'],'state':0})
			except Exception:
				pass

			if (j=='albums'):
				k=result[j]
				k=k['data']
				for i in k:
					album.append({'id':i['id'],'title':i['title'],'music':i['music'],'year':i['more_info']['year'],'language':i['more_info']['language'],'movie':i['more_info']['is_movie']})

			if (j=='songs'):
				k=result[j]
				k=k['data']
				for i in k:
					song.append({'id':i['id'],'title':i['title'],'album':i['album'],'primary_artists':i['more_info']['primary_artists']})
		ws.close()
		return (top_query,album,song)


	def sendList(self,query):
		top_query,album,song=self.searcher(query)
		l=[]
		ab=[]
		no=0
		TotalMatter=''
		TotalMatter+='--'*26+'\n'
		TotalMatter+='\ttopquery:-'+'\n'
		qr=1

		for i in top_query:
			no+=1
			if (i['state']==1):
				l.append(i['id'])
				ab.append(i['title'])
				TotalMatter+='--'*26+'\n'
				TotalMatter+=str(no)+') '+'\n'
				TotalMatter+=i['title']+' '+i['year']+'\n'
				TotalMatter+='   lan: '+i['language']+'  music: '+i['music']+'\n'
				if (i['movie']=='1'):
					TotalMatter+='   album of a movie'+'\n'
				else:
					TotalMatter+='   album of some_playlist'+'\n'
			else:
				qr=0
				l.append(i['id'])
				TotalMatter+='--'*26+'\n'
				TotalMatter+=str(no)+') '
				TotalMatter+=i['title']+'  music: '+i['primary_artists']+'\n'
				TotalMatter+='a song from '+i['album']+'\n'


		TotalMatter+='--'*26+'\n'
		TotalMatter+='\talbums:-'+'\n'

		for i in album:
			no+=1
			l.append(i['id'])
			ab.append(i['title'])
			TotalMatter+='--'*26+'\n'
			TotalMatter+=str(no)+') '
			TotalMatter+=i['title']+' '+i['year']+'\n'
			TotalMatter+='   lan: '+i['language']+'  music: '+i['music']+'\n'
			if (i['movie']=='1'):
				TotalMatter+='   album of a movie'+'\n'
			else:
				TotalMatter+='   album of some_playlist'+'\n'
		t=no

		TotalMatter+='--'*26+'\n'
		TotalMatter+='\tsongs:-'+'\n'
		for i in song:
			no+=1
			l.append(i['id'])
			TotalMatter+='--'*26+'\n'
			TotalMatter+=str(no)+') '
			TotalMatter+=i['title']+'  music:'+i['primary_artists']+'\n'
			TotalMatter+='a song from '+i['album']+'\n'

		TotalMatter+='--'*26+'\n'
		return (l,TotalMatter,t,qr)

	def url_album_design(self,l,no):
		id=l[int(no)]	
		k=requests.get('https://www.saavn.com/api.php?cc=in&_marker=0&albumid='+str(id)+'&_format=json&__call=content.getAlbumDetails')
		k=k.json()
		matter=''
		matter+=k['title']+' '+k['release_date']+'\n'
		l={}
		name=des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
		for i in k['songs']:
			j=i['encrypted_media_url']
			j=base64.b64decode(j.strip())
			name1=name.decrypt(j, padmode=PAD_PKCS5).decode('utf-8')
			l[i['song']]=name1
		matter+='select an song to Music'+'\n'
		no=0
		k=l
		l=[]
		for i in k.keys():
			no+=1
			matter+=str(no)+') '+i+'\n'
			l.append(k[i])
		return (matter,l)

	def url_song_design(self,id):	
		k=requests.post('https://www.saavn.com/api.php?cc=in&_marker=0?_marker=0&_format=json&model=Redmi_5A&__call=song.getDetails&pids='+id)
		k=k.json()
		k=k[id]
		name=des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
		j=k['encrypted_media_url']
		j=base64.b64decode(j.strip())
		name1=name.decrypt(j, padmode=PAD_PKCS5).decode('utf-8')
		return name1

k=DowMusic()
