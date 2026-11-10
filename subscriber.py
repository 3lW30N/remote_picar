import json
import sys
from pathlib import Path

import paho.mqtt.client as mqtt

motor_ctrl_path = (
    Path(__file__).resolve().parents[1]
    / "Code"
    / "adeept_picarpro"
    / "Examples"
    / "03_Motor"
)
sys.path.insert(0, str(motor_ctrl_path))
import MotorCtrl as motorctrl

BROKER_ADDRESS = "10.208.164.135"
BROKER_PORT = 1883
TOPIC = "remotePicar"
COMMANDS = {"avancer", "reculer", "gauche", "droite", "stop"}


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"Connecté. Écoute du topic {TOPIC}...")
        client.subscribe(TOPIC)
    else:
        print(f"Échec de connexion MQTT : {reason_code}")


def on_message(client, userdata, message):
    try:
        command = json.loads(message.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"Message JSON invalide ignoré : {error}")
        return

    if not isinstance(command, dict):
        print("Message invalide ignoré : un objet JSON était attendu.")
        return

    action = command.get("action")
    if not isinstance(action, str) or action not in COMMANDS:
        print(f"Action inconnue ignorée : {action}")
        return

    if action == "stop":
        if set(command) != {"action"}:
            print("Commande stop invalide : elle ne doit pas contenir de vitesse.")
            return
        motorctrl.motorStop()
        print("Commande reçue : stop")
        return

    if (
        set(command) != {"action", "vitesse"}
        or isinstance(command["vitesse"], bool)
        or not isinstance(command["vitesse"], (int, float))
    ):
        print(f"Commande invalide pour {action} : une vitesse numérique est requise.")
        return

    speed = command["vitesse"]
    if not 0 <= speed <= 100 or not float(speed).is_integer():
        print(f"Vitesse hors limites ignorée : {speed}")
        return
    speed = int(speed)

    print(f"Commande reçue : {action}, vitesse {speed}")
    if action == "avancer":
        motorctrl.move(speed, "forward", "no")
    elif action == "reculer":
        motorctrl.move(speed, "backward", "no")
    elif action == "gauche":
        motorctrl.move(speed, "no", "left")
    elif action == "droite":
        motorctrl.move(speed, "no", "right")


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nArrêt du subscriber.")
    finally:
        motorctrl.destroy()
        client.disconnect()


if __name__ == "__main__":
    main()
