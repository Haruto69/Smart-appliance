from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import config

app = Flask(__name__)

def esp32_request(device_key, endpoint, method="GET"):
    device = config.ESP32_DEVICES.get(device_key)
    if not device:
        return {"error": f"Unknown device: {device_key}"}
    try:
        url = f"http://{device['ip']}:{device['port']}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=3)
        else:
            response = requests.post(url, timeout=3)
        return response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
    except:
        return {"error": "ESP32 connection failed"}

@app.route("/")
def index():
    return render_template("index.html", devices=config.ESP32_DEVICES)

# Individual building pages
@app.route("/parking")
def parking():
    status = esp32_request("parking", "/status")
    device = config.ESP32_DEVICES["parking"]
    return render_template("parking.html", status=status, device=device)

@app.route("/park")
def park():
    status = esp32_request("park", "/status")
    device = config.ESP32_DEVICES["park"]
    return render_template("park.html", status=status, device=device)

@app.route("/building1")
def building1():
    status = esp32_request("building1", "/status")
    device = config.ESP32_DEVICES["building1"]
    return render_template("building1.html", status=status, device=device)

@app.route("/building2")
def building2():
    status = esp32_request("building2", "/status")
    device = config.ESP32_DEVICES["building2"]
    return render_template("building2.html", status=status, device=device)

# Control routes
@app.route("/<device_key>/led/<action>", methods=["POST"])
def led_control(device_key, action):
    if action in ["on", "off", "toggle"]:
        esp32_request(device_key, f"/led/{action}", "POST")
    return redirect(url_for(device_key))

@app.route("/<device_key>/mode/<mode_type>", methods=["POST"])
def mode_control(device_key, mode_type):
    if mode_type in ["auto", "manual"]:
        esp32_request(device_key, f"/mode/{mode_type}", "POST")
    return redirect(url_for(device_key))

# API endpoints
@app.route("/api/<device_key>/status")
def api_status(device_key):
    return jsonify(esp32_request(device_key, "/status"))

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏢 Multi-Building ESP32 Dashboard")
    print("="*60)
    for key, dev in config.ESP32_DEVICES.items():
        print(f"📡 {dev['name']}: {dev['ip']}:{dev['port']} ({key})")
    print("🌐 http://0.0.0.0:5000")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
