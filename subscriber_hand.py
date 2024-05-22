# import paho.mqtt.client as mqtt
# import json
# from dotenv import load_dotenv
# import time
# from langchain.chat_models.openai import ChatOpenAI
# from langchain_community.document_loaders import DirectoryLoader, Docx2txtLoader
# import docx2txt
# import requests
# from datahandler import DataHandler 
# import http.client, urllib
# from pushbullet import Pushbullet
# import logging
# import os

# load_dotenv()
# # Variables globales
# broker_address = "mqtt.eclipseprojects.io"
# topic = "Spirulina_Edge"

# temperature = 0.7
# API_KEY = os.getenv('PUSHBULLET_API_KEY')
# pb = Pushbullet(API_KEY)

# class Subscriber:
#     def __init__(self, data_handler, llm_model):
#         self.client = mqtt.Client()
#         self.client.on_connect = self.on_connect
#         self.client.on_message = self.on_message
#         self.data_handler = data_handler
#         self.llm_model = llm_model
#         self.processing_message = False 
        

#     def start(self):
#         self.client.connect(broker_address)
#         self.client.loop_start()
   

#     def on_connect(self, client, userdata, flags, rc):
#         print("Connected to MQTT broker with result code " + str(rc))
#         self.client.subscribe(topic)
 

#     def on_message(self, client, userdata, msg):
#          if not self.processing_message:
#                 self.processing_message = True 
             
#             # Decode the message payload and convert to JSON object in one line
#                 data = json.loads(msg.payload.decode("utf-8"))
#                 json_data = json.loads(data)
                    
#                     # Print the received data
#                 print("Received data:", json_data)
              
#                 latitude = 37.108796
#                 longitude = 10.25208
            
#                 weather_data = self.get_weather_data(latitude, longitude)
#                 if weather_data:
#                     title = "Météo Actuelle"
#                     message = f"Température: {weather_data['hourly']['temperature_2m'][0]}°C, État du ciel: {self.get_weather_state(weather_data['sky_state'])}"
#                      # Envoyer la notification à Pushbullet
#                     pb.push_note(title, message)
                    
#                     print("Les données météorologiques pour Bio ALgues Mahdia,Tunis:")
#                     print(f"Temperature at 2m: {weather_data['hourly']['temperature_2m'][0]}°C")
#                     print(f"Precipitation: {weather_data['hourly']['precipitation'][0]} mm")
#                     print(f"État du ciel: {self.get_weather_state(weather_data['sky_state'])}")
                    
#                 else:
#                     print("Unable to fetch weather data.")
                
#                 self.data_handler.execute(json_data)
               
#                 self.processing_message = False
#     def get_weather_state(self, weather_code):
#             # Logique pour interpréter le code météo et obtenir l'état du ciel correspondant

#             if weather_code < 20:
#                 return "Ensoleillé"
                
#             elif weather_code < 40:
#                 return "Partiellement nuageux"
#             elif weather_code < 60:
#                 return "Nuageux"
#             else:
#                 return "Pluvieux"
                
#     def get_weather_data(self, latitude, longitude):
     
     
#         url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation,weathercode"

#         try:
#             response = requests.get(url)
#             response.raise_for_status()  # Raise an exception if the response status code is not 200
#             weather_data = response.json()  # Parse the JSON response

#             # Ajoutez l'état du ciel à vos données météorologiques
#             weather_data['sky_state'] = weather_data['hourly']['weathercode'][0]

#             return weather_data
#         except requests.RequestException as e:
#             print(f"Error fetching weather data: {e}")
#             return None
  
        


  
# class MyLLM(ChatOpenAI):
#     def __init__(self):
#         super().__init__(api_key=api_key, temperature=temperature)

   
#     def execute(self, recommendations):
#         response_data = {
#             "recommendations": recommendations,
#             }
#         return response_data
       
# # Exemple d'utilisation
# if __name__ == "__main__":
   
#     data_handler_instance = DataHandler()
#     llm_model_instance = MyLLM()
#     subscriber = Subscriber(data_handler=data_handler_instance, llm_model=llm_model_instance)
  
#     subscriber.start()


#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Stopping subscriber...")
#         subscriber.stop()
#         print("Subscriber stopped.")
 
     
import paho.mqtt.client as mqtt
import json
import time
import os
from openai import OpenAI
from datahandler import DataHandler
from datahandler import DataHandler 
from pushbullet import Pushbullet
import requests
from dotenv import load_dotenv
from langchain.chat_models.openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, Docx2txtLoader
import docx2txt





# Charger les variables d'environnement
load_dotenv()

# Variables globales
broker_address = "mqtt.eclipseprojects.io"
topic = "Spirulina_Edge"
API_KEY = os.getenv('PUSHBULLET_API_KEY')
pb = Pushbullet(API_KEY)

class Subscriber:
    def __init__(self, data_handler, llm_model):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.data_handler = data_handler
        self.llm_model = llm_model
        self.processing_message = False 
        
    def start(self):
        self.client.connect(broker_address)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code " + str(rc))
        self.client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        if not self.processing_message:
            self.processing_message = True 
            data = json.loads(msg.payload.decode("utf-8"))
            json_data = json.loads(data)
            print("Received data:", json_data)
            latitude = 37.108796
            longitude = 10.25208

            weather_data = self.get_weather_data(latitude, longitude)
            if weather_data:
                title = "Météo Actuelle"
                message = f"Température: {weather_data['hourly']['temperature_2m'][0]}°C, État du ciel: {self.get_weather_state(weather_data['sky_state'])}"
                pb.push_note(title, message)
                print("Les données météorologiques pour Bio ALgues Mahdia,Tunis:")
                print(f"Temperature at 2m: {weather_data['hourly']['temperature_2m'][0]}°C")
                print(f"Precipitation: {weather_data['hourly']['precipitation'][0]} mm")
                print(f"État du ciel: {self.get_weather_state(weather_data['sky_state'])}")
            else:
                print("Unable to fetch weather data.")
            self.data_handler.execute(json_data)
            self.processing_message = False

    def get_weather_state(self, weather_code):
        if weather_code < 20:
            return "Ensoleillé"
        elif weather_code < 40:
            return "Partiellement nuageux"
        elif weather_code < 60:
            return "Nuageux"
        else:
            return "Pluvieux"

    def get_weather_data(self, latitude, longitude):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation,weathercode"
        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()
            weather_data['sky_state'] = weather_data['hourly']['weathercode'][0]
            return weather_data
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

# Exemple d'utilisation
if __name__ == "__main__":
    data_handler_instance = DataHandler()
    llm_model_instance = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    subscriber = Subscriber(data_handler=data_handler_instance, llm_model=llm_model_instance)
    subscriber.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping subscriber...")
        subscriber.stop()
        print("Subscriber stopped.")