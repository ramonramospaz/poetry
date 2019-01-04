import webapp2
import urllib
import logging
import json
import itertools
from google.appengine.api import taskqueue
from google.appengine.ext import db

class Music(db.Model):
	usuario = db.StringProperty(indexed=True)
	album = db.StringProperty(indexed=False)
	pista = db.StringProperty(indexed=False)
	numero = db.IntegerProperty(indexed=False)
	popularidad = db.StringProperty(indexed=False)
	artista = db.StringProperty(indexed=False)
	

class SearchPage(webapp2.RequestHandler):
	def get(self):
		verso=self.request.get('verso')
		myid=self.request.get('id')
		self.borrar(myid)
		logging.info('Buscando.... '+verso)
		palabras=verso.split(' ')

		for palabra in palabras:			
			taskqueue.add(url='/AddSearch', params={'palabra': palabra,'id' : myid})
		self.response.write('Buscando la musica')
				
	
	def borrar(self,id):
		mymusica = db.GqlQuery("SELECT * FROM Music WHERE usuario=:1",id)
		db.delete(mymusica)


class AddSearch(webapp2.RequestHandler):
	def post(self):
		palabra=self.request.get('palabra')
		myid=self.request.get('id')
		response=urllib.urlopen("http://ws.spotify.com/search/1/track.json?q="+palabra)
		myjson=response.read()
		canciones=json.loads(myjson)
		for i in range(0,len(canciones['tracks'])):
			if(canciones['tracks'][i]['name'].find(palabra)!=-1):

				logging.info('Ingreso la cancion '+canciones['tracks'][i]['name']+' '+myid)
				myalbum=canciones['tracks'][i]['album']['name']
				mypista=canciones['tracks'][i]['name']
				mynumero=int(canciones['tracks'][i]['track-number'])
				mypopularidad=canciones['tracks'][i]['popularity']
				myartista=canciones['tracks'][i]['artists'][0]['name']
				MiMusica=Music(usuario=myid,album=myalbum,pista=mypista,numero=mynumero,popularidad=mypopularidad,artista=myartista)
				MiMusica.put()

class ShowSearch(webapp2.RequestHandler):
	def get(self):
		myid=self.request.get('id')
		mymusica = db.GqlQuery("SELECT * FROM Music WHERE usuario=:1",myid)

		self.response.write('[')
		for mus in mymusica:
			self.response.write('{')
			self.response.write('"codigo":"'+str(mus.usuario)+'",')
			self.response.write('"album":"'+mus.album+'",')
			self.response.write('"pista":"'+mus.pista+'",')
			self.response.write('"numero":"'+str(mus.numero)+'",')
			self.response.write('"popularidad":"'+mus.popularidad+'",')
			self.response.write('"Artista":"'+mus.artista+'"')
			self.response.write('},')
		self.response.write('{}')	
		self.response.write(']')
class DeleteSearch(webapp2.RequestHandler):
	def get(self):
		myid=self.request.get('id')
		self.response.write('Se borra el usuario:'+str(myid)+'<br>')
		mymusica = db.GqlQuery("SELECT * FROM Music WHERE usuario=:1",myid)
		db.delete(mymusica)

application = webapp2.WSGIApplication([('/SearchPage',SearchPage),('/AddSearch',AddSearch),('/ShowSearch',ShowSearch),('/DeleteSearch',DeleteSearch)],debug=True)
