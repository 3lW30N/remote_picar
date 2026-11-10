# Lancement

Installer Tkinter pour Python :
`sudo apt install python3-tk`

Installer l'environnement virtuel et les dépendances :
`python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`

## Utilisation

1. **Sur le Raspberry Pi du robot** :
   Lance le script principal de pilotage, de gestion des servos, du capteur ultrason et de la télémétrie :
   `python3 Pilotage_2.py`

2. **Sur l'ordinateur de commande** :
   Lance l'interface graphique de contrôle :
   `python3 interface_3.py`

## Fonctionnement MQTT

* **Broker** : Accessible sur le port TCP `1883` (IP : `10.208.164.135`).
* **Topic de commande** : `robot/commande`. Les flèches de l'interface publient un objet JSON (par exemple, `{"action": "avancer", "vitesse": 40}` ou `{"action": "stop"}`). Le script sur le Raspberry Pi écoute ce topic et transmet les ordres aux moteurs.
* **Topic de télémétrie** : `robot/telemetrie`. Le robot y publie automatiquement les mesures du capteur ultrason à une fréquence de 2 Hz.

Le broker doit être accessible depuis l'ordinateur de commande et le Raspberry Pi.