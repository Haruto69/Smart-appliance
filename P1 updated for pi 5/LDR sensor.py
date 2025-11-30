import RPi.GPIO as GPIO
import time

MQ2_PIN = 21  # Smoke Detector Digital Output (D0)
LED_PIN = 20  # LED Output

GPIO.setmode(GPIO.BCM)
GPIO.setup(MQ2_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        if GPIO.input(MQ2_PIN) == 1:  # Smoke Detected (LOW signal)
            print("Smoke Detected! Turning LED ON")
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            print('Give smoke mmhm')
            GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nExiting...")
