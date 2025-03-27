from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
import RPi.GPIO as GPIO

app = Flask(__name__)
run_with_ngrok(app)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LIGHT_PIN = 18
FAN_PIN = 23

GPIO.setup(LIGHT_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)

@app.route("/control/<device>/<state>", methods=["POST"])
def control_device(device, state):
    if device == "light":
        pin = LIGHT_PIN
    elif device == "fan":
        pin = FAN_PIN
    else:
        return jsonify({"error": "Invalid device"}), 400

    GPIO.setup(pin, GPIO.OUT)

    if state == "on":
        GPIO.output(pin, GPIO.HIGH)
    elif state == "off":
        GPIO.output(pin, GPIO.LOW)
    else:
        return jsonify({"error": "Invalid state"}), 400

    return jsonify({"status": f"{device} turned {state}"})

if __name__ == "__main__":
    try:
        app.run()
    except KeyboardInterrupt:
        GPIO.cleanup()
