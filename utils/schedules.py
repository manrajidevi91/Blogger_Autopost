import json
import os

SCHEDULES_FILE = 'schedules.json'

def load_schedules_data():
    if not os.path.exists(SCHEDULES_FILE):
        with open(SCHEDULES_FILE, 'w') as f:
            json.dump({}, f)
    with open(SCHEDULES_FILE, 'r') as f:
        return json.load(f)

def save_schedules_data(data):
    with open(SCHEDULES_FILE, 'w') as f:
        json.dump(data, f, indent=4)
