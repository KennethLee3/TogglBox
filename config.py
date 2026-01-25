# config.py

# --- GPIO Pin Configuration ---
LED_PINS    = [4, 14, 15, 17, 18]
BUTTON_PINS = [21, 22, 23, 24, 25]
BUZZER_PIN  = 11

# --- Timer Properties ---
TIMER_CONFIG = [
    {"description": "Devotions & Prayer", "max_minutes": 90, "project_id": 207953510, "tags": None},
    {"description": "Schoolhouse Electronics", "max_minutes": 600, "project_id": 192753565, "tags": None},
    {"description": "EMPTY", "max_minutes": 3, "project_id": None, "tags": ["3"]},
    {"description": "EMPTY", "max_minutes": 4, "project_id": None, "tags": ["4"]},
    {"description": "YouTube", "max_minutes": 45, "project_id": 207953438, "tags": None}
]

SYNC_INTERVAL = 120
