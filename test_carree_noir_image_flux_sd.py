import cv2

COULEUR_NOIR = (0,0,0)
FLUX_RTSP = "rtsp://ProjetLinex:Grum3s2P!n@linex-cam.bts-sn.lrq:1554/live/ch1" #IP Camera
CHEMIN_IMAGE = "image_vehicule.jpg"
PATTERN_ALPR_PLAQUE_FRANCAISE = r'^[A-Z018]{2}[0-9IB]{3}[A-Z018]{2}$'

def lecture_plaque():
    # Création ou écrasement d'un fichier image à partir du flux vidéo
    flux = cv2.VideoCapture(FLUX_RTSP)
    _, image = flux.read()
    # Un carré noir va être placer en haut a droite de l'image pour masquer l'heure et la date qui est
    # parfois prise en compte par le programme
    modification = cv2.rectangle(image,(430,0), (640,20), COULEUR_NOIR, thickness = -1)
    cv2.imwrite(CHEMIN_IMAGE, modification)

test_carree = lecture_plaque()

