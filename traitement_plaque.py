from cv2 import VideoCapture, imwrite, rectangle
from cv2 import error as cv2_error
from subprocess import run, PIPE
from json import loads
from re import match
import logging

COULEUR_NOIR = (0,0,0)
logging.basicConfig(filename="analyse_lecteur_plaque.log", encoding="utf8", level=logging.INFO)
FLUX_RTSP = "rtsp://ProjetLinex:Grum3s2P!n@linex-cam.bts-sn.lrq:1554/live/ch1" #IP Camera
CHEMIN_IMAGE = "image_vehicule.jpg"
PATTERN_PLAQUE_FRANCAISE = r'^[A-Z]{2}-[0-9]{3}-[A-Z]{2}$'
#PATTERN_ALPR_PLAQUE_FRANCAISE = r'^[A-Z0-9]{7}$'
PATTERN_ALPR_PLAQUE_FRANCAISE = r'^[A-Z018]{2}[0-9IBO]{3}[A-Z018]{2}$'
NB_TENTATIVES_ENREG_IMAGE = 10

def normaliser_plaque(plaque):
    plaque_normalisee = ""
    # normaliser une plaque au format renvoyé par le logiciel ALPR (AAAAAAA)
    if match(PATTERN_ALPR_PLAQUE_FRANCAISE, plaque) :
        # remplacer toutes les lettres "O" par des "Q" ou des "0" selon leurs emplacement
        for index, caractere in enumerate(plaque) :
            # si le caractere doit être une lettre 
            if index in [0,1,5,6] :
                if caractere == "O" :
                    plaque_normalisee += "Q"
                elif caractere == "0" :
                    plaque_normalisee += "Q"
                elif caractere == "8" :
                    plaque_normalisee += "B"
                else :
                    plaque_normalisee += caractere
            # sinon le caractere doit être un chiffre
            else :
                if caractere == "O" :
                    plaque_normalisee += "0"
                elif caractere == "I" :
                    plaque_normalisee += "1"
                elif caractere == "B" :
                    plaque_normalisee += "8"
                else :
                    plaque_normalisee += caractere
                    
            # ajouter un tiret après les deuxième et cinquième caractères 
            if index in [1,4] :
                plaque_normalisee += "-"
    
    logging.info (f"la valeur de la plaque est '{plaque}'")
    return plaque_normalisee

# lis une plaque d'immatriculation à partir du flux FLUX_RTSP la plaque d'immatriculation est renvoyée au format "AB-123-CD"
# revoie None si aucune plaque ne peut être lue 
def lecture_plaque():
    # Création ou écrasement d'un fichier image à partir du flux vidéo
    flux = VideoCapture(FLUX_RTSP)
    _, image = flux.read()
    # Un carré noir va être placer en haut a droite de l'image pour masquer l'heure et la date qui est
    # parfois prise en compte par le programme
    modification = rectangle(image,(430,0), (640,20), COULEUR_NOIR, thickness = -1)
    enregistrement_ok = False
    tentatives_enregistrement = 0
    while (not enregistrement_ok) and (tentatives_enregistrement < NB_TENTATIVES_ENREG_IMAGE):
        try:
            tentatives_enregistrement += 1
            imwrite(CHEMIN_IMAGE, modification)
            enregistrement_ok = True
        except cv2_error as e:
            logging.warning(f"Tentative d'enregistrement n°{tentatives_enregistrement} : {e}")
        
    # Reconnaissance de la plaque sur le fichier image
    resultat_reconnaissance = reconnaissance_plaque(CHEMIN_IMAGE, country="eu", top_n = 3)
    plaque_brute = plaque_la_plus_probable(resultat_reconnaissance)
    if not plaque_brute :
        return None
    plaque_immatriculation = normaliser_plaque(plaque_brute)
    return  plaque_immatriculation

def reconnaissance_plaque(image_path: str, alpr_path: str = "alpr.exe", country: str = "us", top_n: int = 10, 
                    json_output: bool = True, detect_region: bool = False, debug: bool = False, clock: bool = False,
                    pattern: str = None, motion: bool = False, config_file: str = None) : 
    
    cmd = [alpr_path, "-c", country, "-n", str(top_n), image_path]
    
    if config_file:
        cmd.extend(["--config", config_file])
    if json_output:
        cmd.append("-j")
    if detect_region:
        cmd.append("-d")
    if debug:
        cmd.append("--debug")
    if clock:
        cmd.append("--clock")
    if motion:
        cmd.append("--motion")
    if pattern:
        cmd.extend(["-p", pattern])
    
    alpr_execution_result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)
    return alpr_execution_result.stdout

# interprète et extrait la plaque la plus probable des résultats au format json fournis par alpr. 
# renvoie None si aucune plaque n'est détectée.
def plaque_la_plus_probable(stdout_alpr) :
    json_plaque = loads(stdout_alpr)
    if not json_plaque["results"] :
        logging.info (f"la valeur de la plaque est '{None}'")
        return None
    plaque = json_plaque["results"][0]["plate"]
    return plaque 
