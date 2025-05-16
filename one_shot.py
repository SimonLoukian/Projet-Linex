from traitement_plaque import lecture_plaque
from datetime import datetime


while True:
    print(f"{str(datetime.now())}:{lecture_plaque()}")
    

