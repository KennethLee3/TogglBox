import RPi.GPIO as GPIO
import requests
import base64
import time
import os
from datetime import datetime, timezone
from config import BUTTON_PINS, LED_PINS, TIMER_CONFIG, SYNC_INTERVAL#, BUZZER_PIN

# -----------------------------
# SETUP & STATE
# -----------------------------
NUM_TIMERS = len(TIMER_CONFIG)
running_entries = [None] * NUM_TIMERS
start_timestamps = [None] * NUM_TIMERS 

API_TOKEN = os.getenv("TOGGL_API_TOKEN")
WORKSPACE_ID = os.getenv("TOGGL_WORKSPACE_ID")
auth_header = "Basic " + base64.b64encode(f"{API_TOKEN}:api_token".encode()).decode()
headers = {"Authorization": auth_header, "Content-Type": "application/json"}

GPIO.setmode(GPIO.BCM)
#GPIO.setup(BUZZER_PIN, GPIO.OUT)
#buzzer_pwm = GPIO.PWM(BUZZER_PIN, 2500)

for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# -----------------------------
# CORE FUNCTIONS
# -----------------------------

#def handle_buzzer_pattern():
#    """Creates a beeping pattern if a timer is overdue."""
#    is_overdue = False
#    for i in range(NUM_TIMERS):
#        if start_timestamps[i]:
#            limit = TIMER_CONFIG[i].get("max_minutes")
#            if limit and (time.time() - start_timestamps[i] > limit * 60):
#                is_overdue = True
#                break
#    
#    if is_overdue:
#        # Simple beep pattern: 0.5s on, 0.5s off
#        if int(time.time() * 2) % 2 == 0:
#            buzzer_pwm.start(50) # 50% duty cycle = Sound ON
#        else:
#            buzzer_pwm.stop()    # Sound OFF
#    else:
#        buzzer_pwm.stop()

def parse_toggl_time(time_str):
    """Converts Toggl's UTC string to a local Unix timestamp."""
    # Toggl returns "2025-12-19T15:30:00Z"
    dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.replace(tzinfo=timezone.utc).timestamp()

def sync_from_toggl():
    global running_entries, start_timestamps
    try:
        resp = requests.get("https://api.track.toggl.com/api/v9/me/time_entries/current", headers=headers)
        if resp.status_code != 200: return
        
        data = resp.json()
        # Reset local state
        new_running = [None] * NUM_TIMERS
        new_starts = [None] * NUM_TIMERS
        
        if data:
            desc = data.get("description", "")
            for i, config in enumerate(TIMER_CONFIG):
                if desc == config["description"]:
                    new_running[i] = data["id"]
                    new_starts[i] = parse_toggl_time(data["start"])
                    GPIO.output(LED_PINS[i], GPIO.HIGH)
                else:
                    GPIO.output(LED_PINS[i], GPIO.LOW)
        else:
            for pin in LED_PINS: GPIO.output(pin, GPIO.LOW)

        running_entries, start_timestamps = new_running, new_starts
    except Exception as e:
        print(f"Sync error: {e}")

# ... (start_timer and stop_timer remain similar, ensuring they update start_timestamps[i] = time.time()) ...

def main():
    last_sync = 0
    try:
        while True:
            # Check buttons
            for i, pin in enumerate(BUTTON_PINS):
                if not GPIO.input(pin):
                    time.sleep(0.05)
                    if not GPIO.input(pin):
                        # Logic for start/stop (omitted for brevity, same as previous)
                        pass 

            # Handle the beep
            #handle_buzzer_pattern()

            # Sync logic
            if time.time() - last_sync > SYNC_INTERVAL:
                sync_from_toggl()
                last_sync = time.time()
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        #buzzer_pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
