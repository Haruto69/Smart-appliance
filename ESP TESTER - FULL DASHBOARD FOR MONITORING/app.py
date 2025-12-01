from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests
import config
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Simple authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Simple authentication - change to proper DB authentication in production
        if username == "admin" and password == "admin123":
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    return render_template("index.html", devices=config.ESP32_DEVICES, username=session.get('username'))

@app.route("/about")
@login_required
def about():
    return render_template("about.html", username=session.get('username'))

# Individual building pages
@app.route("/parking")
@login_required
def parking():
    status = esp32_request("parking", "/status")
    device = config.ESP32_DEVICES["parking"]
    return render_template("parking.html", status=status, device=device, username=session.get('username'))

@app.route("/park")
@login_required
def park():
    status = esp32_request("park", "/status")
    device = config.ESP32_DEVICES["park"]
    return render_template("park.html", status=status, device=device, username=session.get('username'))

@app.route("/building1")
@login_required
def building1():
    status = esp32_request("building1", "/status")
    device = config.ESP32_DEVICES["building1"]
    return render_template("building1.html", status=status, device=device, username=session.get('username'))

@app.route("/building2")
@login_required
def building2():
    status = esp32_request("building2", "/status")
    device = config.ESP32_DEVICES["building2"]
    return render_template("building2.html", status=status, device=device, username=session.get('username'))

# Control routes
@app.route("/<device_key>/led/<action>", methods=["POST"])
@login_required
def led_control(device_key, action):
    if action in ["on", "off", "toggle"]:
        esp32_request(device_key, f"/led/{action}", "POST")
    return redirect(url_for(device_key))

@app.route("/<device_key>/mode/<mode_type>", methods=["POST"])
@login_required
def mode_control(device_key, mode_type):
    if mode_type in ["auto", "manual"]:
        esp32_request(device_key, f"/mode/{mode_type}", "POST")
    return redirect(url_for(device_key))

# API endpoints
@app.route("/api/<device_key>/status")
@login_required
def api_status(device_key):
    return jsonify(esp32_request(device_key, "/status"))

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔐 Smart Campus Security Dashboard")
    print("="*60)
    print("🌐 Login at: http://0.0.0.0:5000/login")
    print("👤 Default credentials: admin / admin123")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
