from flask import Flask, render_template
import RPi.GPIO as GPIO

# GPIO Setup
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("off.html");


@app.route("/on")
def led_on():
    GPIO.output(LED_PIN, GPIO.HIGH);
    return render_template("on.html");

@app.route("/off")
def led_off():
    GPIO.output(LED_PIN, GPIO.LOW);
    return render_template("off.html");

if __name__ == "__main__":
    try:

        app.run(host="0.0.0.0", port=5000, debug=True);
    
    finally:
        GPIO.cleanup();
