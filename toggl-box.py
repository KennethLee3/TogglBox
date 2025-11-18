import RPi.GPIO as GPIO
import requests
import base64
import time
import os
from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------

API_TOKEN = os.getenv("TOGGL_API_TOKEN")
WORKSPACE_ID = os.getenv("TOGGL_WORKSPACE_ID")

if not API_TOKEN or not WORKSPACE_ID:
    raise RuntimeError("Environment variables not set: TOGGL_API_TOKEN or TOGGL_WORKSPACE_ID")

# Button–LED pairs (5 buttons, 5 LEDs), BCM numbering
BUTTON_PINS = [4, 14, 15, 17, 18]
LED_PINS    = [21, 22, 23, 24, 25]

# Track the running entry for each button
running_entries = [None] * 5

# How often to sync from Toggl (seconds)
SYNC_INTERVAL = 10

# -----------------------------
# AUTH HEADER
# -----------------------------
auth_header = "Basic " + base64.b64encode(f"{API_TOKEN}:api_token".encode()).decode()
headers = {
    "Authorization": auth_header,
    "Content-Type": "application/json"
}

# -----------------------------
# GPIO SETUP
# -----------------------------
GPIO.setmode(GPIO.BCM)

for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# -----------------------------
# TOGGL API FUNCTIONS
# -----------------------------

def start_timer(index):
    """Start a running timer for a given button index."""
    global running_entries

    if running_entries[index] is not None:
        return  # already running

    start_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "description": f"Button {index+1} timer",
        "created_with": "RaspberryPiButtonBox",
        "duration": -1,
        "start": start_time,
        "workspace_id": WORKSPACE_ID
    }

    url = f"https://api.track.toggl.com/api/v9/workspaces/{WORKSPACE_ID}/time_entries"

    resp = requests.post(url, json=payload, headers=headers)
    print("START:", resp.status_code, resp.text)

    if resp.status_code == 200:
        entry = resp.json()
        running_entries[index] = entry["id"]
        GPIO.output(LED_PINS[index], GPIO.HIGH)


def stop_timer(index):
    """Stop the running timer for a specific button index."""
    global running_entries

    entry_id = running_entries[index]
    if entry_id is None:
        return

    url = f"https://api.track.toggl.com/api/v9/workspaces/{WORKSPACE_ID}/time_entries/{entry_id}/stop"

    resp = requests.patch(url, headers=headers)
    print("STOP:", resp.status_code, resp.text)

    if resp.status_code == 200:
        running_entries[index] = None
        GPIO.output(LED_PINS[index], GPIO.LOW)


def fetch_running_entry():
    """Fetch the currently running Toggl timer (if any)."""
    url = "https://api.track.toggl.com/api/v9/me/time_entries/current"
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print("Error fetching running entry:", resp.status_code)
        return None

    data = resp.json()
    return data if data else None


def sync_from_toggl():
    """Sync LEDs with whatever timer is running on Toggl."""
    global running_entries

    running = fetch_running_entry()

    if running is None:
        # Nothing running → turn everything off
        running_entries = [None] * 5
        for pin in LED_PINS:
            GPIO.output(pin, GPIO.LOW)
        return

    entry_id = running["id"]
    description = running.get("description", "")

    matched = False
    for i in range(5):
        if description == f"Button {i+1} timer":
            running_entries = [None] * 5
            running_entries[i] = entry_id

            # Light only that LED
            for j in range(5):
                GPIO.output(LED_PINS[j], GPIO.HIGH if j == i else GPIO.LOW)

            matched = True
            break

    if not matched:
        # Unknown timer (e.g., started manually on web) → turn all LEDs off
        running_entries = [None] * 5
        for pin in LED_PINS:
            GPIO.output(pin, GPIO.LOW)


# -----------------------------
# MAIN LOOP
# -----------------------------

def main():
    last_sync = 0

    try:
        while True:
            # Check buttons
            for i, pin in enumerate(BUTTON_PINS):
                if not GPIO.input(pin):  # button pressed
                    time.sleep(0.05)     # debounce
                    if not GPIO.input(pin):
                        if running_entries[i] is None:
                            start_timer(i)
                        else:
                            stop_timer(i)

                        # Wait until the button is released
                        while not GPIO.input(pin):
                            time.sleep(0.05)

            # Periodic sync with Toggl
            if time.time() - last_sync > SYNC_INTERVAL:
                sync_from_toggl()
                last_sync = time.time()

            time.sleep(0.02)

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
