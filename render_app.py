from flask import Flask, render_template
import requests

app = Flask(__name__)

# Replace with your Raspberry Pi's IP or domain
PI_API_URL = "http://192.168.0.191:5000/control"
SECRET_KEY = "meow"

def send_command(state):
    """Send ON/OFF command to Raspberry Pi API"""
    response = requests.post(PI_API_URL, json={"state": state, "key": SECRET_KEY})
    return response.json()

@app.route("/")
def home():
    return render_template("off.html")

@app.route("/on")
def led_on():
    send_command("on")
    return render_template("on.html")

@app.route("/off")
def led_off():
    send_command("off")
    return render_template("off.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
