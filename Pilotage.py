import json
import time
import threading
import paho.mqtt.client as mqtt
from gpiozero import Motor, DistanceSensor

# --- IMPORTS POUR LES SERVOS (PCA9685) ---
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

# --- 1. CONFIGURATION MATÉRIELLE DES MOTEURS (Adeept) ---
Motor_A_EN    = 4
Motor_B_EN    = 17
Motor_A_Pin1  = 26
Motor_A_Pin2  = 21
Motor_B_Pin1  = 27
Motor_B_Pin2  = 18

motor_left = Motor(forward=Motor_A_Pin1, backward=Motor_A_Pin2, enable=Motor_A_EN)
motor_right = Motor(forward=Motor_B_Pin1, backward=Motor_B_Pin2, enable=Motor_B_EN)

VITESSE_TEST = 40  # Limitation de vitesse de sécurité (Partie B - Q4)

# --- 2. CONFIGURATION MATÉRIELLE DES SERVOS ---
try:
    i2c = busio.I2C(SCL, SDA)
    pca = PCA9685(i2c, address=0x40)
    pca.frequency = 50
except Exception as e:
    print(f"[AVERTISSEMENT] I2C non initialisé ou carte PCA9685 absente : {e}")
    pca = None

def set_angle(ID, angle):
    """Permet de positionner un servo sur un angle précis (0 à 180°)"""
    if pca is None:
        print("[ERREUR] Impossible de bouger le servo : PCA9685 non disponible.")
        return
    angle = max(0, min(180, angle))
    servo_angle = servo.Servo(pca.channels[ID], min_pulse=500, max_pulse=2400, actuation_range=180)
    servo_angle.angle = angle
    print(f"-> Action Servo : Canal {ID} positionné à {angle}°")


# --- 3. CONFIGURATION DU CAPTEUR ULTRASON (Partie D - Q8 & Q9) ---
Tr = 11
Ec = 8
sensor = DistanceSensor(echo=Ec, trigger=Tr, max_distance=2)

def publier_telemetrie(client):
    """Lit le capteur à 2 Hz (0.5s) et publie la distance sur le topic de télémétrie."""
    while True:
        try:
            distance_cm = sensor.distance * 100
            if distance_cm < 2 or distance_cm > 200:
                payload = {"distance": None, "statut": "incoherente"}
            else:
                payload = {"distance": round(distance_cm, 1), "statut": "ok"}
        except Exception:
            payload = {"distance": None, "statut": "absente"}

        client.publish("robot/telemetrie", json.dumps(payload))
        time.sleep(0.5)


# --- PARTIE B : Fonctions de pilotage des moteurs ---

def initialiser_robot():
    """Q4 : Arrêt obligatoire au démarrage."""
    print("[SECURITE] Initialisation : Arrêt des moteurs et centrage servo.")
    motor_stop()
    if pca is not None:
        set_angle(1, 90)  # Met le servo du canal 1 au milieu (90°)

def motor_stop():
    motor_left.stop()
    motor_right.stop()

def move_adeept(speed, direction, turn, radius=0.6):
    speed = speed / 100
    if direction == 'forward':
        if turn == 'right':
            motor_left.backward(speed * radius)
            motor_right.forward(speed)
        elif turn == 'left':
            motor_left.forward(speed)
            motor_right.backward(speed * radius)
        else:
            motor_left.forward(speed)
            motor_right.forward(speed)
    elif direction == 'backward':
        if turn == 'right':
            motor_left.forward(speed * radius)
            motor_right.backward(speed)
        elif turn == 'left':
            motor_left.backward(speed)
            motor_right.forward(speed * radius)
        else:
            motor_left.backward(speed)
            motor_right.backward(speed)
    elif direction == 'no':
        if turn == 'right':
            motor_left.backward(speed)
            motor_right.forward(speed)
        elif turn == 'left':
            motor_left.forward(speed)
            motor_right.backward(speed)
        else:
            motor_stop()


def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        data = json.loads(payload_str)

        # Q11 : Calcul de la latence de transmission
        timestamp_cmd = data.get("timestamp")
        if timestamp_cmd:
            delai_ms = (time.time() * 1000) - timestamp_cmd
            print(f"[LATENCE] Délai de prise en compte : {delai_ms:.2f} ms")

        action = data.get("action")

        print(f"\n[MQTT] Reçu -> {data}")

        if action == "avancer":
            vitesse = data.get("vitesse", VITESSE_TEST)
            move_adeept(vitesse, 'forward', 'no')

        elif action == "reculer":
            vitesse = data.get("vitesse", VITESSE_TEST)
            move_adeept(vitesse, 'backward', 'no')

        elif action == "gauche":
            vitesse = data.get("vitesse", VITESSE_TEST)
            move_adeept(vitesse, 'no', 'left')

        elif action == "droite":
            vitesse = data.get("vitesse", VITESSE_TEST)
            move_adeept(vitesse, 'no', 'right')

        elif action == "stop":
            motor_stop()

        elif action == "servo":
            canal = data.get("canal", 1)
            angle = data.get("angle", 90)
            set_angle(canal, angle)

        else:
            print(f"[AVERTISSEMENT] Action inconnue : {action}")

    except json.JSONDecodeError:
        print("[ERREUR] JSON invalide.")
    except Exception as e:
        print(f"[ERREUR] {e}")


# --- PROGRAMME PRINCIPAL ---

def main():
    initialiser_robot()

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        client = mqtt.Client()

    client.on_message = on_message

    broker_ip = "localhost"
    topic_commande = "robot/commande"

    print(f"Connexion au broker MQTT sur '{broker_ip}'...")
    client.connect(broker_ip, 1883, 60)
    client.subscribe(topic_commande)

    # Lancement du thread de télémétrie ultrason (2 Hz)
    threading.Thread(target=publier_telemetrie, args=(client,), daemon=True).start()

    print(f"Prêt ! En attente de commandes MQTT sur '{topic_commande}'...")

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nArrêt manuel demandé (Ctrl+C).")
    finally:
        motor_stop()
        if pca is not None:
            set_angle(1, 90)
            pca.deinit()
        client.disconnect()
        print("[SECURITE] Arrêt propre du robot effectué.")

if __name__ == '__main__':
    main()