from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import bcrypt
import sqlite3
import os
from datetime import datetime
from gpiozero import LED, DigitalInputDevice, Device
from gpiozero.pins.lgpio import LGPIOFactory
import threading
import time
import atexit
import lgpio

# ---------------- GPIO SETUP ----------------
# Force gpiozero to use lgpio backend (for Raspberry Pi 5)
Device.pin_factory = LGPIOFactory()

def reset_gpio(pin):
    """Free GPIO pin if it's busy (e.g. left from previous run)."""
    h = lgpio.gpiochip_open(0)
    try:
        lgpio.gpio_free(h, pin)
    except Exception:
        pass
    lgpio.gpiochip_close(h)

# --- SENSOR & LED PIN DEFINITIONS ---
SOUND_SENSOR_PIN = 18
PIR_SENSOR_PIN = 22
LDR_SENSOR_PIN = 17

LED_SOUND_PIN = 24
LED_PIR_PIN = 26
LED_LDR_PIN = 25

# --- DEVICE CONTROL PINS (for Flask control) ---
DEVICE_PINS = {
    "light_1": 2,
    "light_2": 3,
    "light_3": 27,
    "light_4": 23,
    "fan_1": 12,
    "fan_2": 16
}

# --- Reset all pins before use ---
for pin in [SOUND_SENSOR_PIN, PIR_SENSOR_PIN, LDR_SENSOR_PIN,
            LED_SOUND_PIN, LED_PIR_PIN, LED_LDR_PIN] + list(DEVICE_PINS.values()):
    reset_gpio(pin)

# --- Initialize sensors ---
sound_sensor = DigitalInputDevice(SOUND_SENSOR_PIN)
pir_sensor = DigitalInputDevice(PIR_SENSOR_PIN)
ldr_sensor = DigitalInputDevice(LDR_SENSOR_PIN)

# --- Initialize LEDs ---
led_sound = LED(LED_SOUND_PIN)
led_pir = LED(LED_PIR_PIN)
led_ldr = LED(LED_LDR_PIN)

# --- Initialize controlled devices (lights/fans) ---
devices = {name: LED(pin) for name, pin in DEVICE_PINS.items()}
for d in devices.values():
    d.off()

# ---------------- SENSOR MONITORING ----------------
def sensor_monitor():
    """Background thread to monitor sensors continuously."""
    while True:
        # 🔊 Sound Detection (Clap)
        if sound_sensor.value == 1:
            led_sound.toggle()
            print(f"🔊 Clap detected! LED_SOUND {'ON' if led_sound.is_lit else 'OFF'}")
            time.sleep(0.5)

        # 🚶 Motion Detection (PIR)
        if pir_sensor.value == 1:
            led_pir.on()
            print("🚶 Motion detected! LED_PIR ON")
            time.sleep(2)
            led_pir.off()

        # 💡 Light Detection (LDR)
        if ldr_sensor.value == 1:  # Assuming HIGH means dark
            led_ldr.on()
        else:
            led_ldr.off()

        time.sleep(0.05)

# Run sensor monitoring in a background thread
sensor_thread = threading.Thread(target=sensor_monitor, daemon=True)
sensor_thread.start()

# ---------------- DATABASE & AUTH ----------------
app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"
FAILED_LOGIN_LOG = "failed_logins.log"

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create SQLite DB with default admin user."""
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password BLOB NOT NULL
                    );''')
    conn.commit()

    # Default admin
    user = conn.execute("SELECT * FROM users WHERE username = ?", ('admin',)).fetchone()
    if not user:
        hashed = bcrypt.hashpw(b"Letshavepizzatoday!626$$", bcrypt.gensalt())
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed))
        conn.commit()
    conn.close()

def verify_user(username, password):
    """Check username/password against DB."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user['password']):
        return True
    return False

# ---------------- FLASK ROUTES ----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        if verify_user(u, p):
            session['user'] = u
            return redirect(url_for('welcome'))

        # Log failed login
        ip = request.remote_addr
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(FAILED_LOGIN_LOG, "a") as f:
            f.write(f"{ts} Failed login for '{u}' from IP {ip}\n")
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
    if device not in devices:
        return jsonify({"error": "Invalid device"}), 400

    if state == 'on':
        devices[device].on()
    else:
        devices[device].off()
    return jsonify({"status": f"{device} turned {state}"})

@app.route('/lights/<state>', methods=['POST'])
def all_lights_control(state):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    for name in devices.keys():
        if "light" in name:
            if state == 'on':
                devices[name].on()
            else:
                devices[name].off()
    return jsonify({"status": f"All lights turned {state}"})

# ---------------- CLEANUP ----------------
def cleanup():
    """Turn off all devices on exit."""
    print("\nCleaning up GPIO...")
    for led in [led_sound, led_pir, led_ldr] + list(devices.values()):
        led.off()

atexit.register(cleanup)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    init_db()
    print("✅ Smart Home + Sensor Monitor running on http://0.0.0.0:5001")
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)