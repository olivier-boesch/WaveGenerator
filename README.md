# WaveGenerator

Générer une commande par logiciel pour la cuve à vagues NOVA Physics.

l'arduino se comporte comme un générateur de signal carré de fréquence variable. Trois commandes sont possibles :
* S\n : arrête le générateur
* C3600\n : génère en continu à 3600Hz
* B3,5000\n : Génère une salve de 3 impulsions de fréquence 5000Hz

Le logiciel propose une interface propre de commande de ce générateur.

## Schéma de branchement

Ordinateur --USB--> arduino --banane vers BNC--> cuve à vagues

## Comment faire

* Charger le code arduino dans l'arduino UNO.
* Faire le branchement électrique
* Relier l'arduino en USB à l'ordinateur (relier la borne noire à GND et la borne rouge au pin 10)
* Relier l'arduino à la commande du moteur avec un câble Banane-BNC
* Démarrer wavegen.exe (sous windows) ou wavegen (sous linux)

## arduino

<img src="https://github.com/olivier-boesch/WaveGenerator/raw/main/media/arduino.jpg" width=250>
<img src="https://github.com/olivier-boesch/WaveGenerator/raw/main/media/arduino_opened.jpg" width=350>

## Logiciel

Dépendances : kivy et pyserial (modules python)

### Binaires (sans installation)

<img src="https://github.com/olivier-boesch/WaveGenerator/raw/main/media/wavegen.png" width=500>

binaire windows 64 bits (zip) : https://github.com/olivier-boesch/WaveGenerator/raw/main/binairies/wavegen_win64.zip

binaire linux 64 bits (zip) : https://github.com/olivier-boesch/WaveGenerator/raw/main/binairies/wavegen_linux.zip
