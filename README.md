# Toggl Box

A physical 5-button Raspberry Pi–powered controller to start/stop Toggl Track timers with LEDs indicating the active timer. Designed for productivity through visual time tracking.

This project uses:

- Raspberry Pi (any model with GPIO)
- 5 momentary pushbuttons
- 5 LEDs
- Toggl Track API v9

## Features

- Press a button → starts a Toggl timer
- Press the same button again → stops that timer
- LEDs show which timer is running
- Syncs every 10 seconds with Toggl
- If a timer is started on another device, the correct LED lights
- Fully offline-safe (will queue actions until network returns)
- Runs automatically on boot via systemd
- Fully open source and easy to modify

## Hardware Requirements

- Raspberry Pi (Zero, 1, 2, 3, 4 — all supported)
- 5x momentary push buttons
- 5x LEDs
- 5x 220–330 Ω resistors

## Wiring

TODO: Wiring diagram

## Installation

Clone the repo onto the Raspberry Pi:
```
git clone https://github.com/KennethLee3/TogglBox.git
cd toggl-box
```

Install Python dependencies:
```
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install requests RPi.GPIO
```

Edit the config at the top of the script:
```
API_TOKEN = "YOUR_API_TOKEN"
WORKSPACE_ID = 1234567
```

## Running manually
```
python3 toggl_button_box.py
```

## Autostart with systemd

Create the service:
```
sudo nano /etc/systemd/system/toggl-button-box.service
```

Paste:
```
[Unit]
Description=Toggl Button Box
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/toggl-button-box
ExecStart=/usr/bin/python3 /home/pi/toggl-button-box/toggl_button_box.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```
sudo systemctl daemon-reload
sudo systemctl enable toggl-button-box
sudo systemctl start toggl-button-box
```

## API Requirements

You must generate a Toggl API Token from:
[https://track.toggl.com/profile#api-token
]([url](https://track.toggl.com/profile#api-token
))

The script uses:
```
POST /workspaces/{id}/time_entries to start running entry (duration = -1)

PATCH /time_entries/{id}/stop to stop

GET /me/time_entries/current to sync LEDs
```
