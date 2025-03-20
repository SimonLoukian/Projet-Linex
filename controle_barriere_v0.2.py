import time
from bottle import Bottle, run, template, request
from pymodbus.client import ModbusTcpClient

# Configuration EDW-100
EDW_IP = "192.168.191.100"
EDW_PORT = 502
client = ModbusTcpClient(host=EDW_IP, port=EDW_PORT)

# Initialisation de l'application Bottle
app = Bottle()

# Page principale avec boutons
@app.route('/')
def home():
    return template("gui_controle_acces.html")

# Route pour envoyer les commandes à l'EDW-100
@app.post('/command')
def send_command():
    coil_address = int(request.forms.get('state'))
    response = client.write_coil(address=coil_address, value=True, slave=65)
    if response.isError():
        return "Erreur lors de l'envoi de la commande."
    return f"Commande envoyée avec succès : {coil_address}"

def lecture_input_register (valeur) :
    input_register_addr = valeur
    response = client.read_input_registers(address = valeur, count=1, slave = 65)
    return response.registers[0]

historique_valeur = []
historique_valeur_preci = []

a = 0
try:
    while True:
        valeur_registre = lecture_input_register(0)
        print("Valeur du registre:", valeur_registre)
        valeur_registre_preci = lecture_input_register(1) 
        historique_valeur.append(valeur_registre)
        print (historique_valeur)
        historique_valeur_preci.append(valeur_registre_preci)
        print(historique_valeur_preci)
        
        
        if len(historique_valeur) > 1:
                derniere_valeur = historique_valeur[-1]   # Valeur actuelle
                valeur_precedente = historique_valeur[-2]  # Valeur précédente
                valeur_en_compte = derniere_valeur - valeur_precedente
                
                if valeur_en_compte > 100:
                    
                     v = derniere_valeur * 1.1207 - 3929,4
                     print(v)
                     
                     
                     
                     
                     print("Poids du camion détecté:", v)
             
        time.sleep(5)  # Attente de 5 secondes
        

except KeyboardInterrupt:
    print("\nArrêt du programme par l'utilisateur.")


# Lancer le serveur Bottle
if __name__ == "__main__":
    run(app, host='192.168.190.26', port=5000, debug=True)