from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import bcrypt
import sqlite3
import os
from datetime import datetime
from gpiozero import LED, Device
from gpiozero.pins.lgpio import LGPIOFactory
import lgpio
import atexit
import socket
import sys
import time

app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"

# --- GPIO Setup ---
Device.pin_factory = LGPIOFactory()

DEVICE_PINS = {
    "light_1": 2,
    "light_2": 3,
    "light_3": 24,
    "light_4": 25,
    "fan_1": 12,
    "fan_2": 16
}

def reset_gpio(pin):
    """Force free a GPIO pin."""
    h = lgpio.gpiochip_open(0)
    try:
        lgpio.gpio_free(h, pin)
    except Exception:
        pass
    try:
        lgpio.gpiochip_close(h)
    except Exception:
        pass

def cleanup_all_gpio():
    """Clean up all GPIO before starting."""
    print("🧹 Cleaning up all GPIO pins...")
    for pin in DEVICE_PINS.values():
        reset_gpio(pin)
    time.sleep(0.1)  # Small delay
    print("✅ GPIO cleanup complete")

# Clean GPIO first
cleanup_all_gpio()

# Initialize devices
devices = {}
print("\n📌 Initializing GPIO devices:")
for device_name, pin in DEVICE_PINS.items():
    try:
        devices[device_name] = LED(pin)
        devices[device_name].off()
        print(f"   ✓ {device_name:12} → GPIO {pin}")
    except Exception as e:
        print(f"   ✗ {device_name:12} → Error: {e}")

FAILED_LOGIN_LOG = "failed_logins.log"

# --- Database Functions ---
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password BLOB NOT NULL
                    );''')
    conn.commit()
    
    user = conn.execute("SELECT * FROM users WHERE username = ?", ('admin',)).fetchone()
    if not user:
        hashed_password = bcrypt.hashpw(b"Letshavepizzatoday!626$$", bcrypt.gensalt())
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed_password))
        conn.commit()
    conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user['password']):
        return True
    return False

# --- Routes ---
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
    if device not in devices:
        return jsonify({"error": "Invalid device"}), 400
    
    try:
        if state == 'on':
            devices[device].on()
        else:
            devices[device].off()
        return jsonify({"status": f"{device} turned {state}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/lights/<state>', methods=['POST'])
def all_lights_control(state):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        for device_name in devices.keys():
            if "light" in device_name:
                if state == 'on':
                    devices[device_name].on()
                else:
                    devices[device_name].off()
        return jsonify({"status": f"All lights turned {state}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Cleanup ---
def cleanup():
    """Turn off all devices and free GPIO."""
    print("\n🧹 Shutting down - cleaning GPIO...")
    for device in devices.values():
        try:
            device.off()
            device.close()
        except:
            pass
    for pin in DEVICE_PINS.values():
        reset_gpio(pin)
    print("✅ GPIO cleanup complete")

atexit.register(cleanup)

# --- Run Server ---
if __name__ == '__main__':
    init_db()
    
    print("\n" + "="*70)
    print("🚀 Flask Smart Appliance Server")
    print("="*70)
    
    hostname = socket.gethostname()
    print(f"\n📍 Access URLs:")
    print(f"   • Local:   http://localhost:5001")
    
    try:
        ip_list = socket.gethostbyname_ex(hostname)[2]
        for ip in ip_list:
            if not ip.startswith("127."):
                print(f"   • Network: http://{ip}:5001")
    except:
        pass
    
    print(f"\n🔐 Login: admin / Letshavepizzatoday!626$$")
    print("="*70 + "\n")
    
    sys.stdout.flush()
    
    try:
        app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
        cleanup()
