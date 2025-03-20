import paho.mqtt.client as mqtt
import json
import time
import math

# Configuration MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "trajectory/coordinates"

# Constantes physiques
ACCELERATION = 0.2 * 9.81  # g en m/s²
MAX_SPEED = 30 * 1000 / 3600  # km/h en m/s
EMIT_INTERVAL = 0.5  # 500 ms

def calculate_trajectory(coordinates):
    trajectory = []
    distance = 0
    for i in range(1, len(coordinates)):
        lat1, lon1 = coordinates[i-1]
        lat2, lon2 = coordinates[i]
        segment_distance = haversine(lat1, lon1, lat2, lon2)
        distance += segment_distance
        trajectory.append((distance, lat1, lon1, lat2, lon2, segment_distance))
    return trajectory

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Rayon de la Terre en mètres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def interpolate(lat1, lon1, lat2, lon2, fraction):
    lat = lat1 + (lat2 - lat1) * fraction
    lon = lon1 + (lon2 - lon1) * fraction
    return lat, lon

def emit_trajectory(trajectory):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    speed = 0
    total_distance = trajectory[-1][0]
    deceleration_distance = (MAX_SPEED ** 2) / (2 * ACCELERATION)
    current_distance = 0
    index = 0

    while index < len(trajectory):
        distance, lat1, lon1, lat2, lon2, segment_distance = trajectory[index]

        # Calculer la distance parcourue dans les 500 ms suivants
        distance_traveled = speed * EMIT_INTERVAL
        current_distance += distance_traveled

        # Si la distance parcourue dépasse la distance du segment actuel, passer au segment suivant
        if current_distance >= distance:
            index += 1
            if index < len(trajectory):
                distance, lat1, lon1, lat2, lon2, segment_distance = trajectory[index]
            continue

        # Calculer la fraction de la distance parcourue dans le segment actuel
        fraction = (current_distance - (distance - segment_distance)) / segment_distance
        lat, lon = interpolate(lat1, lon1, lat2, lon2, fraction)

        # Mettre à jour la vitesse
        if speed < MAX_SPEED and (total_distance - current_distance) > deceleration_distance:
            speed += ACCELERATION * EMIT_INTERVAL
            if speed > MAX_SPEED:
                speed = MAX_SPEED
        else:
            speed -= ACCELERATION * EMIT_INTERVAL
            if speed < 0:
                speed = 0
                index += 1

        message = json.dumps({"lat": lat, "lon": lon, "speed": speed})
        print(f'({lat},{lon}) "speed": {speed:.02f}')
        client.publish(MQTT_TOPIC, message)
        time.sleep(EMIT_INTERVAL)

    client.disconnect()

def load_geojson(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return [(coord[1], coord[0]) for coord in data['features'][0]['geometry']['coordinates']]

def main():
    file_path = "trajet.json"
    coordinates = load_geojson(file_path)
    trajectory = calculate_trajectory(coordinates)
    emit_trajectory(trajectory)

if __name__ == "__main__":
    main()
