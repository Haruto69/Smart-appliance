from flask import Flask, request, jsonify
import RPi.GPIO as GPIO

app = Flask(__name__)

# GPIO Setup
LED_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Secret key for authentication
SECRET_KEY = "meow"

@app.route("/control", methods=["POST"])
def control_led():
    data = request.json
    if not data or data.get("key") != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401  # Reject unauthorized requests
    
    if data["state"] == "on":
        GPIO.output(LED_PIN, GPIO.HIGH)
        return jsonify({"status": "LED turned ON"})
    elif data["state"] == "off":
        GPIO.output(LED_PIN, GPIO.LOW)
        return jsonify({"status": "LED turned OFF"})
    else:
        return jsonify({"error": "Invalid state"}), 400

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    finally:
        GPIO.cleanup()  # Clean up on exit
