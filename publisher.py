import json

import paho.mqtt.client as mqtt

BROKER_ADDRESS = "10.208.164.135"
BROKER_PORT = 1883
TOPIC = "robot/commande"
COMMANDS = {"avancer", "reculer", "gauche", "droite", "stop", "servo"}

client = mqtt.Client()
connected = False


def publish_command(action, speed=None, canal=1, angle=90):
    global connected

    if action not in COMMANDS:
        raise ValueError(f"Action inconnue : {action}")

    command = {"action": action}
    if action == "servo":
        command["canal"] = canal
        command["angle"] = angle
    elif action != "stop":
        if speed is None:
            raise ValueError(f"La vitesse est requise pour l'action {action}")
        command["vitesse"] = speed

    if not connected:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        client.loop_start()
        connected = True

    result = client.publish(TOPIC, json.dumps(command), qos=1)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(f"Impossible de publier la commande MQTT : {result.rc}")
    return result


def disconnect():
    global connected

    if connected:
        client.disconnect()
        client.loop_stop()
        connected = False
