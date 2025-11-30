import RPi.GPIO as GPIO
import time

# Define GPIO Pins (All on the left side)
PIR_SENSOR_PIN = 18  # OUT pin of PIR sensor (Pin 12)
BUZZER_PIN = 23      # Buzzer pin (Pin 16)
LED_PIN = 20         # LED pin (Pin 18)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_SENSOR_PIN, GPIO.IN)  # PIR motion sensor
GPIO.setup(BUZZER_PIN, GPIO.OUT)     # Buzzer
GPIO.setup(LED_PIN, GPIO.OUT)        # LED

print("PIR Sensor warming up...")
time.sleep(2)  # Allow PIR sensor to stabilize

try:
    while True:
        motion_detected = GPIO.input(PIR_SENSOR_PIN) # HIGH = Motion detected

        if motion_detected:
            print("🚶‍♂️ Motion detected! Activating buzzer and LED.")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(5)  # Keep alert active for a while
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            GPIO.output(LED_PIN, GPIO.LOW)

        time.sleep(0.1)  # Small delay before checking again

except KeyboardInterrupt:
    print("Stopping...")
    GPIO.cleanup()  # Cleanup GPIO on exit
