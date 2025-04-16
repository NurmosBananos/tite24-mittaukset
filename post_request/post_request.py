
import requests
import time
import random
from datetime import datetime

from datetime import datetime

with open("/home/palju/IOT/log.txt", "a") as log:
    log.write(f"[{datetime.now()}] Script started\n")

def luo_lampotila_ja_kosteus():
    """
    Luo satunnaiset lämpötila- ja kosteusmittaukset.
    Palauttaa (lampotila, kosteus).
    """
    lampotila = round(random.uniform(15, 30), 1)  # 15.0–30.0 °C
    kosteus = random.randint(30, 90)              # 30–90 %
    return lampotila, kosteus

# Valitse käyttötarkoituksen mukaan URL:
# Paikallisessa kehityksessä käytä:
# url = 'http://127.0.0.1:5000/lisaa_tieto'
# Tuotannossa/Azuressa käytä:
url = 'https://tite24-mittaukset-jk.azurewebsites.net/lisaa_tieto'

if __name__ == '__main__':
    while True:
        # Hae nykyinen aikaleima
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Luo sisä- ja ulkomittausten satunnaiset arvot
        lampo_sisa, kosteus_sisa = luo_lampotila_ja_kosteus()
        lampo_ulko, kosteus_ulko = luo_lampotila_ja_kosteus()

        # Rakennetaan mittausdata, jonka Flask-sovellus odottaa
        mittaus = {
            'aika': timestamp,
            'lampo_sisa': lampo_sisa,
            'lampo_ulko': lampo_ulko,
            'kosteus_sisa': kosteus_sisa,
            'kosteus_ulko': kosteus_ulko
        }

        print(f"Lähetetään dataa: {mittaus}")

        try:
            response = requests.post(
                url,
                json=mittaus,
                headers={'Content-Type': 'application/json'}
            )
            print(f"Palvelimen vastaus: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Virhe pyynnön lähetyksessä: {e}")  # Huom: varmista, että lainausmerkit ja sulut ovat oikein

        # Odota 10 sekuntia ennen seuraavaa mittausta
        time.sleep(10)
