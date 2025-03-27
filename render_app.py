from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests  # To send requests to the Raspberry Pi API

app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"

# Raspberry Pi API URL (Change this to your Pi's actual IP address)
PI_API_URL = "http://192.168.0.191:5000/control"

USERNAME = "admin"
PASSWORD = "password"

def check_login(username, password):
    return username == USERNAME and password == PASSWORD

def send_command(device, state):
    """Send ON/OFF command to Raspberry Pi API"""
    response = requests.post(f"{PI_API_URL}/{device}/{state}")
    return response.json()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_login(username, password):
            session['user'] = username
            return redirect(url_for('welcome'))
        return "Invalid username or password", 401
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'user' in session:
        return render_template('welcome.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/light')
def light_control():
    if 'user' in session:
        return render_template('light.html')
    return redirect(url_for('login'))

@app.route('/fan')
def fan_control():
    if 'user' in session:
        return render_template('fan.html')
    return redirect(url_for('login'))

@app.route("/control/<device>/<state>", methods=["POST"])
def control_api(device, state):
    if "user" in session:
        return send_command(device, state)
    return jsonify({"error": "Unauthorized"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
