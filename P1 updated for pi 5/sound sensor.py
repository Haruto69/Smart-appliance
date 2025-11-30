import RPi.GPIO as GPIO
import time

# Define GPIO Pins (All on the left side)
SOUND_SENSOR_PIN = 18  # D0 pin of sound sensor (Pin 12)
BUZZER_PIN = 23        # Buzzer pin (Pin 16)
LED_PIN = 24           # LED pin (Pin 18)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOUND_SENSOR_PIN, GPIO.IN)  # Digital sound sensor
GPIO.setup(BUZZER_PIN, GPIO.OUT)       # Buzzer
GPIO.setup(LED_PIN, GPIO.OUT)          # LED

print("Listening for sound...")
time.sleep(2)  # Small delay before starting

try:
    while True:
        sound_detected = GPIO.input(SOUND_SENSOR_PIN)  # LOW = Sound detected

        if sound_detected:
            print("🔊 Sound detected! Activating buzzer and LED.")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(1)  # Keep buzzer and LED on for a short time
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            GPIO.output(LED_PIN, GPIO.LOW)

        time.sleep(0.1)  # Short delay before checking again

except KeyboardInterrupt:
    print("Stopping...")
    GPIO.cleanup()  # Cleanup GPIO on exit
