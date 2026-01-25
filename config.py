# config.py

# --- GPIO Pin Configuration ---
LED_PINS    = [4, 14, 15, 17, 18]
BUTTON_PINS = [22, 23, 24, 25, 27]
#BUZZER_PIN  = 11

# --- Timer Properties ---
TIMER_CONFIG = [
    {"description": "Deep Work", "max_minutes": 60, "project_id": None, "tags": ["code"]},
    {"description": "Admin/Email", "max_minutes": 20, "project_id": None, "tags": ["admin"]},
    {"description": "Learning", "max_minutes": 45, "project_id": None, "tags": ["edu"]},
    {"description": "Meetings", "max_minutes": 30, "project_id": None, "tags": ["social"]},
    {"description": "Break", "max_minutes": 10, "project_id": None, "tags": ["rest"]}
]

SYNC_INTERVAL = 60
