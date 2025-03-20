import paho.mqtt.client as mqtt
import struct

def traiter_latitude(latitude):
    """Convertit une latitude codée en entier 32 bits signé en degrés."""
    return latitude / 10000000  

def traiter_longitude(longitude):
    """Convertit une longitude codée en entier 32 bits signé en degrés."""
    return longitude / 10000000


#########################################################

# Configuration
BROKER = "mqtt.bts-sn-lrq.info"
PORT = 1883 
TOPIC = "terminal/0/position"  

# Callback appelé lorsqu'un message est reçu
def on_message(client, userdata, message):
    """Callback appelé lorsqu'un message MQTT est reçu."""
    try:
        # Décodage des 8 octets reçus (2x 32 bits signés)
        latitude, longitude = struct.unpack('ii', message.payload)

        # Traitement des valeurs
        latitude = traiter_latitude(latitude)
        longitude = traiter_longitude(longitude)

        # Affichage des coordonnées
        print(f"Message reçu sur {message.topic}")
        print(f"Latitude : {latitude}, Longitude : {longitude}")
    
    except struct.error as e:
        print(f"Erreur de décodage du message : {e}")

# Création du client MQTT
client = mqtt.Client()

# Configuration du callback
client.on_message = on_message

# Connexion au broker
client.username_pw_set("user1TG", "btsciel1")
client.connect(BROKER, PORT, 120)

# S'abonner au topic
client.subscribe(TOPIC)
print(f"Abonné au topic {TOPIC}, en attente de messages...")

# Lancer la boucle d'écoute
client.loop_forever()


