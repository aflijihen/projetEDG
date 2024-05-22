import paho.mqtt.client as mqtt
import json
from openai import OpenAI
import os  
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


broker_address = "mqtt.eclipseprojects.io"
topic = "Spirulina"

class Publisher:
   
    def __init__(self) :
         self.llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
     
    
    def generate_recommendation(self, generated_response):
        # Construct user input string summarizing sensor data
        user_input = (f"utiliser  : {generated_response}  et la document et extracter  le code ")
        template_prompt = """
          Assurez-vous que toutes les réponses sont sous forme JSON : -et de la forme suivante: {"recommandations": [C, D, E, ]}

        """
      # Ajout de la prompt à l'input utilisateur
        user_input_with_prompt = f"{template_prompt}\n\n{user_input}"
        # Generate response using the=
        response = self.llm.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "system", "content": template_prompt},
                {"role": "user", "content": user_input_with_prompt},
            ],
        )

        return (response.choices[0].message.content ) # Convert to uppercase for easier matching


    def publish_recommendations(self, recommendations):
        
        # Connect to MQTT broker
        client = mqtt.Client()
        client.connect(broker_address)
         # Convertir les recommandations extraites en JSON et publier au topic
        message = json.dumps(recommendations)
        client.publish(topic, message)
        print("Published recommendations:", recommendations)

