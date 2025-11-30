import RPi.GPIO as GPIO
import time

# Define GPIO Pins (All on the left side)
SMOKE_SENSOR_PIN = 18  # D0 pin of smoke sensor (Pin 12)
BUZZER_PIN = 23        # Buzzer pin (Pin 16)
LED_PIN = 24           # LED pin (Pin 18)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SMOKE_SENSOR_PIN, GPIO.IN)  # Digital smoke sensor
GPIO.setup(BUZZER_PIN, GPIO.OUT)       # Buzzer
GPIO.setup(LED_PIN, GPIO.OUT)          # LED

print("Gas sensor warming up...")
time.sleep(20)  # Allow MQ-6 to warm up

try:
    while True:
        smoke_detected = GPIO.input(SMOKE_SENSOR_PIN) == 0  # LOW = Smoke detected

        if smoke_detected:
            print("🔥 Smoke detected! Turning on buzzer and LED.")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            print("✅ No smoke detected.")
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            GPIO.output(LED_PIN, GPIO.LOW)

        time.sleep(0.5)  # Wait before next reading

except KeyboardInterrupt:
    print("Stopping...")
    GPIO.cleanup()  # Cleanup GPIO on exit
