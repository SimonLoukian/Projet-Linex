from geopy.distance import geodesic
import paho.mqtt.client as mqtt
import json

# Vérification si le camion est dans un rayon de 2 mètres
def traiter_point(loc_camion):
    dict_points = {
        'tout droit': (49.611096, 0.770308),
        'droite': (49.611256, 0.770039),
        'gauche': (49.611507, 0.770326),
        'arrivée': (49.611650, 0.770021)
    }

    # Calcul de la distance entre la position du camion et la référence
    lat_camion, lon_camion = loc_camion  # on décompose les coordonnées du camion
    for nom_point, (lat, lon) in dict_points.items():
        distance = geodesic((lat, lon), (lat_camion, lon_camion)).meters
        if distance <= 5:
            print(f"allez '{nom_point}' dans (distance: {distance:.2f}m)")
        else :
            print('rien dire')
# Paramètres MQTT
BROKER = "localhost"
PORT = 1883
TOPIC = "trajectory/coordinates"

# Callback appelé lorsqu'un message est reçu
def on_message(client, userdata, message):
    try:
        latlonvit = message.payload.decode('utf-8')
        dict_latlonvit = json.loads(latlonvit)
        lat = dict_latlonvit['lat']
        lon = dict_latlonvit['lon']
        traiter_point((lat, lon))
    except Exception as e:
        print(f"Erreur dans le traitement du message: {e}")

# Création du client MQTT
client = mqtt.Client()

# Configuration du callback
client.on_message = on_message

# Connexion au broker MQTT
client.connect(BROKER, PORT, 120)

# S'abonner au topic
client.subscribe(TOPIC)
print(f"Abonné au topic {TOPIC}, en attente de messages...")

# Lancer la boucle d'écoute
client.loop_forever()
