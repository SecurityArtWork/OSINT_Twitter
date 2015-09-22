#!/usr/bin/env python
# -*- coding: utf-8 -*-
##################################################################
__author__ = 'José F. González Krause'
__license__ = 'MIT'


from time import sleep
from sys import exit
import tweepy
import json
import conf


########## CONFIG ##########
consumer_token = conf.consumer_token
consumer_secret = conf.consumer_secret
access_token = conf.access_token
access_secret = conf.access_secret
############################

def OAuth():
   ''' Devuelve nustra instancia de la API '''
   cToken = consumer_token
   cSecret = consumer_secret
   aToken = access_token
   aSecret = access_secret

   # Instanciamos el gestor de autorización
   auth = tweepy.OAuthHandler(cToken, cSecret)

   '''En el caso de que no tengamos los tokens de autorización de nuestra cuenta
   solicitaremos la url que nos generará el pin.'''
   if aToken == '' or aSecret == '':
      try:
         redirect_url = auth.get_authorization_url()
         print('Ve a Twitter y autoriza la aplicación: {0}'.format(redirect_url))
      except tweepy.TweepError:
         print('Error al solicitar el token.')
         
      # Le pasamos el PIN a auth para que solicite los tokens 
      verifier = raw_input('Verifier: ').strip()
      auth.get_access_token(verifier)

      '''Guardamos nuestros tokens y los imprimimos en pantalla para añadirlos
      a las variables de configuración. Así la próxima vez no tendremos que
      realizar este paso.'''
      aToken = auth.access_token.key
      aSecret = auth.access_token.secret
      
      log('Your access_token: {0}'.format(aToken))
      log('Your access_secret: {0}'.format(aSecret))

   # Seteamos auth token y secret
   auth.set_access_token(aToken, aSecret)

   return (tweepy.API(auth), auth)


def getTrends(woeid=1):
   ''' 
   Devuelve una lista de trends por localización,
   la localización es un WOEID de Yahoo, el ID para
   todo todo el mundo es 1.
   '''
   
   '''Hacemos una llamada a la API y recuperamos directamente los elementos que
   nos interesan del diccionario.'''
   trends = api.trends_place(1)[0]['trends']
   
   # Extraemos el nombre de los trends y los devolvemos.
   trendList = [trend['name'] for trend in trends]

   return trendList


class StreamListener(tweepy.StreamListener):
   '''Cuando un Tweet haga match con nuestros targetTerms será pasado a
   esta función'''
   def on_data(self, data):
      # Asignamos el JSON de los datos a la variable data
      data = json.loads(data)
      # Intentamos ejecutar el codigo
      try:
         # Si los datos no contienen cooedenadas no nos interesan
         if data['geo'] is not None:
            '''recuperamos los elementos que nos interesan de data
            y los imprimimos por pantalla'''
            print('[>] {0}(@{1}) -- LAT/LON: {2}'.format(
               data['user']['name'].encode('ascii', 'ignore'),
               data['user']['screen_name'].encode('ascii', 'ignore'), 
               data['geo']['coordinates']
               )
            )

         return True

      # En caso de un error lo imprimimos
      except Exception, e:
         print('[!] Error: {0}'.format(e))
   
   
   # Si alcanzamos el limite de llamadas alerta y espera 10"
   def on_limit(self, track):
      print('[!] Limit: {0}').format(track)
      sleep(10)
   
   
   # En caso de producirse un error interrumpe el listener
   # https://dev.twitter.com/overview/api/response-codes
   def on_error(self, status):
      print('[!] Error: {0}').format(status)
      return False


def streamAPI(auth):
   # Instanciamos nuestro listener
   l = StreamListener()
   # Iniciamos el streamer con el objeto OAuth y el listener
   streamer = tweepy.Stream(auth=auth, listener=l)
   # Definimos los terminos de los que queremos hacer un tracking
   targetTerms = ['hola', 'buenos dias', 'buenas tardes', 'buenas noches']
   # Iniciamos el streamer, pasandole nuestros trackTerms
   streamer.filter(track=targetTerms)


try:
   api, auth = OAuth()


   print('[*] Trending topics:')
   # Recuperamos los tt y los imprimimos uno por uno
   trendingTopics = getTrends(woeid=776688)
   for topic in trendingTopics:
      print(topic)


   print('\n[*] Iniciando streamer:')
   streamAPI(auth)

except KeyboardInterrupt, e:
   exit(1)

