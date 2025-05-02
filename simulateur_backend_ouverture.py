#simulateur de backend
import paho.mqtt.client as mqtt

def verifier_camion(plaque):
    return 0

TOPIC_SUB = "vehicule/camion"  # Le topic où tu recevras les infos du camion
TOPIC_PUB = "vahicule/reponse"  # Le topic où tu publieras les réponses
BROKER = "localhost"
PORT = 1883
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connexion réussie au broker MQTT")
        client.subscribe(TOPIC_SUB)

def on_message(client, userdata, msg) :
    # Message reçu au format texte
    message = msg.payload.decode("utf-8")
    print(f"Message reçu : {message}")
    verifier_camion(message)
        
# Création du client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
print("Client connecté, en attente de messages...")
client.loop_forever()