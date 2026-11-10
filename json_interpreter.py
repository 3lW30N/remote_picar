import json

def interpret_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    dictionnaire = {}

    for key, value in data.items():
        dictionnaire[key] = value

    return dictionnaire


data = interpret_json("data.json")

print(data)