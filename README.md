# WaveGenerator

Générer une commande par logiciel pour la cuve à vagues NOVA Physics.

Article présentant le montage : https://www.pedagogie.ac-aix-marseille.fr/jcms/c_10865222/fr/generateur-de-vagues-commande-par-une-tablette-d-une-cuve-a-vagues-nova-physics

l'arduino se comporte comme un générateur de signal carré de fréquence variable. Trois commandes sont possibles :
* S\n : arrête le générateur
* C3600\n : génère en continu à 3600Hz
* B3,5000\n : Génère une salve de 3 impulsions de fréquence 5000Hz

Le logiciel propose une interface propre de commande de ce générateur.

## Schéma de branchement

Ordinateur --USB--> arduino --banane vers BNC--> cuve à vagues

## Comment faire

* Charger le code arduino dans l'arduino UNO.
* Faire le branchement électrique (relier la borne noire à GND et la borne rouge au pin 10)
* Relier l'arduino en USB à l'ordinateur
* Relier l'arduino à la commande du moteur avec un câble Banane-BNC
* Démarrer wavegen.exe (sous windows) ou wavegen (sous linux)

## arduino

<img src="https://github.com/olivier-boesch/WaveGenerator/raw/main/media/arduino.jpg" width=250>
<img src="https://github.com/olivier-boesch/WaveGenerator/raw/main/media/arduino_opened.jpg" width=350>

## Logiciel

Dépendances : kivy et pyserial (modules python)

### Binaires v1.3.0 (sans installation)

<img src="https://github.com/olivier-boesch/WaveGenerator/raw/main/media/wavegen_dev.png" width=500>

binaire windows 64 bits (zip) : https://github.com/olivier-boesch/WaveGenerator/releases/download/v1.3.0/wavegen_win64.zip

binaire linux 64 bits (zip) : https://github.com/olivier-boesch/WaveGenerator/releases/download/v1.3.0/Wavegen_linux64.zip

binaire Android Arm64 (apk) : https://github.com/olivier-boesch/WaveGenerator/releases/download/v1.3.0/wavegen-1.3.0-arm64-v8a-debug.apk
