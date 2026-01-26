import RPi.GPIO as GPIO
import time

# --- CONFIGURATION ---
BUZZER_PIN = 11  # BCM 11 (Physical Pin 23)
STEP_DELAY = 1 # How long to stay on each frequency (seconds)
START_FREQ = 3500
END_FREQ   = 4500
STEP_SIZE  = 50

# --- SETUP ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize PWM with a starting frequency
pwm = GPIO.PWM(BUZZER_PIN, START_FREQ)

print("--- Passive Piezo Frequency Sweeper ---")
print(f"Testing from {START_FREQ}Hz to {END_FREQ}Hz...")
print("Press Ctrl+C to stop at the current frequency.")

try:
    pwm.start(50)  # 50% Duty Cycle (constant square wave)
    
    for freq in range(START_FREQ, END_FREQ + 1, STEP_SIZE):
        pwm.ChangeFrequency(freq)
        print(f"Current Frequency: {freq} Hz")
        time.sleep(STEP_DELAY)

    print("\nSweep complete!")

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up. Note the frequency you liked best!")
