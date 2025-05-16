from re import match
PATTERN_ALPR_PLAQUE_FRANCAISE = r'^[A-Z018]{2}[0-9IOB]{3}[A-Z018]{2}$'

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
                else :
                    plaque_normalisee += caractere
            # sinon le caractere doit être un chiffre
            else :
                if caractere == "O" :
                    plaque_normalisee += "0"
                elif caractere == "I" :
                    plaque_normalisee += "1"
                else :
                    plaque_normalisee += caractere
                    
            # ajouter un tiret après les deuxième et cinquième caractères 
            if index in [1,4] :
                plaque_normalisee += "-"
        
    return plaque_normalisee

plaque_test = normaliser_plaque("AB1O3CD")
print (plaque_test)



