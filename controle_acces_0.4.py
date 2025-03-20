import json
import sqlite3
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta

# Fonction de vérification avec les données du camion
def verifier_camion(plaque_camion, poids_camion):
    # Connexion à la base de données SQLite
    connexion = sqlite3.connect("BD_camions_livraisons.db")
    cursor = connexion.cursor()

    # Récupération des données des camions
    donnees_camions = cursor.execute("SELECT plaque_immatriculation, poids_vide FROM Camions").fetchall()
    bd_camions = {plaque: poids for plaque, poids in donnees_camions}

    # Récupération des poids de chargement et heures d'arrivée prévues
    donnees_chargements = cursor.execute("SELECT plaque_immatriculation, poids_chargement, heure_arrivee_prevue FROM Chargements").fetchall()
    bd_chargement = {plaque: (poids_chargement, horaire) for plaque, poids_chargement, horaire in donnees_chargements}

    # Vérification de la plaque dans la base de données
    if plaque_camion in bd_camions:
        poids_total = bd_camions[plaque_camion] + bd_chargement[plaque_camion][0]
        print(f"Plaque validée")

        # Vérification du poids
        if comparaison_poids(poids_camion, poids_total):
            print('Poids validé.')

            # Vérification de l'horaire
            if comparaison_horaire(bd_chargement[plaque_camion][1]):
                print("Horaire valide.")
            else:
                print("Horaire invalide.")
        else:
            print("Poids invalide.")
    else:
        print("Plaque de camion inconnue.")

    # Fermeture de la connexion à la base de données
    connexion.close()

# Vérifie si le poids du camion correspond à celui enregistré
def comparaison_poids(poids_mesure, poids_bd):
    return poids_mesure == poids_bd

# Vérifie si le camion arrive dans le créneau horaire autorisé
def comparaison_horaire(horaire_bd):
    date_actuelle = datetime.now()
    max_retard = date_actuelle + timedelta(hours=1)
    max_avance = date_actuelle - timedelta(hours=1)
    
    horaire_bd = datetime.strptime(horaire_bd, "%H:%M:%S").time()
    
    return max_avance.time() <= horaire_bd <= max_retard.time()



# Connexion MQTT
######################

TOPIC_SUB = "vehicule/camion"  # Le topic où tu recevras les infos du camion
TOPIC_PUB = "vahicule/reponse"  # Le topic où tu publieras les réponses
BROKER = "localhost"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connexion réussie au broker MQTT")
        client.subscribe(TOPIC_SUB)  # S'abonner au topic pour recevoir les messages
    else:
        print(f"Échec de la connexion, code : {rc}")

def on_message(client, userdata, msg):
    try:
        # Message reçu au format texte
        message = msg.payload.decode("utf-8")
        print(f"Message reçu : {message}")
        
        # Analyser la chaîne de caractères pour extraire la plaque et le poids
        plaque_camion, poids_camion = message.split(',')
        plaque_camion = plaque_camion.strip()  # Enlever les espaces inutiles
        poids_camion = float(poids_camion.strip().split()[0])  # Extraire et convertir le poids
        
        print(f"Plaque du camion : {plaque_camion}, Poids du camion : {poids_camion} tonnes")
        
        # Appel des fonctions de vérification avec les données du message
        verifier_camion(plaque_camion, poids_camion)
        
    except Exception as e:
        print(f"Erreur lors du traitement du message : {e}")

# Création du client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    print("Client connecté, en attente de messages...")
    client.loop_forever()  # Écouter en boucle les messages du topic
except Exception as e:
    print(f"Erreur de connexion au broker : {e}")
######################
