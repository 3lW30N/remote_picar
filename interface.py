import tkinter as tk
from tkinter import messagebox

import publisher

VITESSE = 50


def envoyer_commande(action):
    try:
        if action == "stop":
            publisher.publish_command(action)
        else:
            publisher.publish_command(action, VITESSE)
    except (OSError, RuntimeError, ValueError) as error:
        messagebox.showerror("Erreur MQTT", f"Envoi impossible : {error}")


def fermer():
    publisher.disconnect()
    root.destroy()

root = tk.Tk()
root.title("Contrôleur directionnel")
root.geometry("250x300")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", fermer)

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="center")

style = {
    "font": ("Arial", 20, "bold"),
    "width": 3,
    "height": 1,
    "bg": "#333333",
    "fg": "black",
    "activebackground": "#555555",
    "activeforeground": "white",
    "relief": "raised",
    "bd": 2
}

# Flèche du haut
tk.Button(
    frame, text="↑",
    command=lambda: envoyer_commande("avancer"),
    **style
).grid(row=0, column=1, padx=3, pady=3)

# Flèche de gauche
tk.Button(
    frame, text="←",
    command=lambda: envoyer_commande("gauche"),
    **style
).grid(row=1, column=0, padx=3, pady=3)

# Flèche de droite
tk.Button(
    frame, text="→",
    command=lambda: envoyer_commande("droite"),
    **style
).grid(row=1, column=2, padx=3, pady=3)

# Flèche du bas
tk.Button(
    frame, text="↓",
    command=lambda: envoyer_commande("reculer"),
    **style
).grid(row=2, column=1, padx=3, pady=3)

tk.Button(
    frame, text="STOP",
    command=lambda: envoyer_commande("stop"),
    **{**style, "font": ("Arial", 12, "bold"), "width": 7}
).grid(row=3, column=1, padx=3, pady=3)

root.mainloop()