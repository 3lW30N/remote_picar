# Lancement
Installer tkinter pour Python
`sudo apt install python3-tk`

Installer les requirements
`python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`

Lancer le subscriber sur le Raspberry Pi du robot
`python3 subscriber.py`

Le Raspberry Pi doit avoir accès au broker sur le port TCP 1883 et disposer
des dépendances du contrôleur moteur.

Lancer l'interface sur l'ordinateur de commande
`python3 interface.py`

Les flèches publient un objet JSON sur le topic MQTT `remotePicar` du broker
`10.125.111.135`. Par exemple, avancer publie `{"action": "avancer",
"vitesse": 50}` et le bouton STOP publie `{"action": "stop"}`. Le subscriber
écoute ce même topic et transmet les commandes au contrôleur moteur local.

Le broker doit être accessible depuis l'ordinateur de commande et le Raspberry Pi.