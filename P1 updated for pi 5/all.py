import RPi.GPIO as GPIO
import time

# Define GPIO pins for Sensors
SOUND_SENSOR_PIN = 18  # DO pin of the Sound Sensor
PIR_SENSOR_PIN = 22    # PIR Motion Sensor
LDR_SENSOR_PIN = 17  # LDR Sensor
SMOKE_SENSOR_PIN = 8  # Smoke Sensor

# Define GPIO pins for LEDs
LED_SOUND = 24  # LED for Sound Sensor
LED_PIR = 26    # LED for PIR Sensor
LED_LDR = 25    # LED for LDR Sensor
LED_SMOKE = 5   # LED for Smoke Sensor

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOUND_SENSOR_PIN, GPIO.IN)
GPIO.setup(PIR_SENSOR_PIN, GPIO.IN)
GPIO.setup(LDR_SENSOR_PIN, GPIO.IN)
GPIO.setup(SMOKE_SENSOR_PIN, GPIO.IN)

GPIO.setup(LED_SOUND, GPIO.OUT)
GPIO.setup(LED_PIR, GPIO.OUT)
GPIO.setup(LED_LDR, GPIO.OUT)
GPIO.setup(LED_SMOKE, GPIO.OUT)

# Initial LED states (OFF)
GPIO.output(LED_SOUND, GPIO.LOW)
GPIO.output(LED_PIR, GPIO.LOW)
GPIO.output(LED_LDR, GPIO.LOW)
GPIO.output(LED_SMOKE, GPIO.LOW)

try:
    while True:
        # 🔊 Clap Detection (Sound Sensor)
        if GPIO.input(SOUND_SENSOR_PIN):
            GPIO.output(LED_SOUND, not GPIO.input(LED_SOUND))  # Toggle LED
            print("🔊 Clap detected! LED_SOUND", "ON" if GPIO.input(LED_SOUND) else "OFF")
            time.sleep(0.5)  # Debounce

        # 🚶 Motion Detection (PIR Sensor)
        if GPIO.input(PIR_SENSOR_PIN):
            GPIO.output(LED_PIR, GPIO.HIGH)
            print("🚶 Motion detected! LED_PIR ON")
            time.sleep(2)
            GPIO.output(LED_PIR, GPIO.LOW)

        # 💡 Light Detection (LDR Sensor)
        if GPIO.input(LDR_SENSOR_PIN):  # Assuming LOW means dark
            GPIO.output(LED_LDR, GPIO.HIGH)
            #print("🌑 Darkness detected! LED_LDR ON")
        else:
            GPIO.output(LED_LDR, GPIO.LOW)

        # 🔥 Smoke Detection (Smoke Sensor)
        if GPIO.input(SMOKE_SENSOR_PIN)==GPIO.LOW:
            GPIO.output(LED_SMOKE, GPIO.HIGH)
            #print("🔥 Smoke detected! LED_SMOKE ON")
        else:
            GPIO.output(LED_SMOKE, GPIO.LOW)

        time.sleep(0.05)  # Small delay for continuous checking

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    # Ensure all LEDs are OFF before exit
    GPIO.output(LED_SOUND, GPIO.LOW)
    GPIO.output(LED_PIR, GPIO.LOW)
    GPIO.output(LED_LDR, GPIO.LOW)
    GPIO.output(LED_SMOKE, GPIO.LOW)
    GPIO.cleanup()
    print("GPIO cleanup done. All LEDs OFF.")


