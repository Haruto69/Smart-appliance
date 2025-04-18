from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import RPi.GPIO as GPIO
import bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Device GPIO pins
DEVICE_PINS = {
    "light_1": 27,
    "light_2": 23,
    "light_3": 25,
    "light_4": 5,
    "fan_1": 12,
    "fan_2": 16
}

# Set all pins as output and turn off
for pin in DEVICE_PINS.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

# Function to verify user login from users.db
def verify_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row[0]):
        return True
    return False

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_user(username, password):
            session['user'] = username
            return redirect(url_for('welcome'))
        return "Invalid username or password.", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/welcome')
def welcome():
    if 'user' in session:
        return render_template('welcome.html')
    return redirect(url_for('login'))

@app.route('/control/<device>')
def control_device(device):
    if 'user' in session and device in DEVICE_PINS:
        return render_template('device.html', device=device)
    return redirect(url_for('login'))

@app.route('/control/<device>/<state>', methods=['POST'])
def control_device_state(device, state):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    if device not in DEVICE_PINS:
        return jsonify({"error": "Invalid device"}), 400

    pin = DEVICE_PINS[device]
    GPIO.output(pin, GPIO.HIGH if state == 'on' else GPIO.LOW)
    return jsonify({"status": f"{device} turned {state}"})

@app.route('/lights/<state>', methods=['POST'])
def all_lights_control(state):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    for device, pin in DEVICE_PINS.items():
        if "light" in device:
            GPIO.output(pin, GPIO.HIGH if state == 'on' else GPIO.LOW)

    return jsonify({"status": f"All lights turned {state}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
