import json


def load_json(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            return json_data
    except Exception:
        return None


def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        try:
            json.dump(data, f, indent=4)
        except Exception:
            return None
