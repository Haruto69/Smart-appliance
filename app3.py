from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import RPi.GPIO as GPIO
import bcrypt
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Device GPIO pins
DEVICE_PINS = {
    "light_1": 2,
    "light_2": 3,
    "light_3": 24,
    "light_4": 25,
    "fan_1": 12,
    "fan_2": 16
}

# Set all pins as output and turn off
for pin in DEVICE_PINS.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

# File to log failed login attempts
FAILED_LOGIN_LOG = "failed_logins.log"

# Database connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password BLOB NOT NULL
                    );''')
    conn.commit()

    # Create default admin user if not present
    user = conn.execute("SELECT * FROM users WHERE username = ?", ('admin',)).fetchone()
    if not user:
        hashed_password = bcrypt.hashpw(b"Letshavepizzatoday!626$$", bcrypt.gensalt())
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed_password))
        conn.commit()

    conn.close()

# Verify user login
def verify_user(username, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode(), user['password']):
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

        ip = request.remote_addr
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} Failed login attempt for user '{username}' from IP {ip}\n"
        with open(FAILED_LOGIN_LOG, "a") as log_file:
            log_file.write(log_entry)

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
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
