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
        if sound_sensor.value == 1:
            led_sound.toggle()
            print(f"🔊 Clap detected! LED_SOUND {'ON' if led_sound.is_lit else 'OFF'}")
            time.sleep(0.5)

        if pir_sensor.value == 1:
            led_pir.on()
            print("🚶 Motion detected! LED_PIR ON")
            time.sleep(2)
            led_pir.off()

        if ldr_sensor.value == 1:
            led_ldr.on()
        else:
            led_ldr.off()

        time.sleep(0.05)

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
    """Create SQLite DB with PLAIN TEXT passwords for easy demo."""
    conn = get_db_connection()
    
    # Users table - password as TEXT (no hashing!)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    );''')
    
    conn.commit()

    # Default admin with PLAIN TEXT password
    user = conn.execute("SELECT * FROM users WHERE username = ?", ('admin',)).fetchone()
    if not user:
        # NO HASHING - plain text password!
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                    ('admin', 'admin123'))
        conn.commit()
    conn.close()

def verify_user(username, password):
    """VULNERABLE: Direct string concatenation in SQL query."""
    conn = get_db_connection()
    
    # VULNERABILITY: String formatting instead of parameterized query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    print(f"\n🔍 DEBUG - Executing SQL: {query}\n")  # Show the actual query
    
    try:
        user = conn.execute(query).fetchone()
        conn.close()
        
        if user:
            return True
        return False
    except Exception as e:
        print(f"❌ SQL Error: {e}")
        return False

# ---------------- FLASK ROUTES ----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '')
        p = request.form.get('password', '')
        
        if verify_user(u, p):
            session['user'] = u
            return redirect(url_for('welcome'))

        # Log failed login
        ip = request.remote_addr
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(FAILED_LOGIN_LOG, "a") as f:
            f.write(f"{ts} Failed login attempt - Username: '{u}' from IP {ip}\n")
        
        return "Invalid username or password.", 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/welcome')
def welcome():
    if 'user' in session:
        return render_template('welcome.html', username=session['user'])
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

# ---------------- VULNERABLE USER REGISTRATION ----------------
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """VULNERABLE: No authentication check, no password hashing, SQL injection possible."""
    
    if request.method == 'POST':
        new_user = request.form.get('username', '')
        new_pass = request.form.get('password', '')
        
        # NO VALIDATION, NO HASHING!
        # VULNERABILITY: Direct string concatenation
        conn = get_db_connection()
        query = f"INSERT INTO users (username, password) VALUES ('{new_user}', '{new_pass}')"
        
        print(f"\n🔍 DEBUG - Executing SQL: {query}\n")  # Show the query
        
        try:
            conn.execute(query)
            conn.commit()
            conn.close()
            return f"""
            <html>
            <head><title>User Added</title></head>
            <body style="font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px;">
                <h2>✅ Success!</h2>
                <p>User '<strong>{new_user}</strong>' has been added to the database.</p>
                <p><a href="/add_user">Add Another User</a> | <a href="/view_users">View All Users</a> | <a href="/welcome">Dashboard</a></p>
            </body>
            </html>
            """
        except Exception as e:
            return f"""
            <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px;">
                <h2>❌ Error!</h2>
                <p style="color: red;">SQL Error: {str(e)}</p>
                <pre style="background: #f4f4f4; padding: 10px; overflow-x: auto;">{query}</pre>
                <p><a href="/add_user">Try Again</a></p>
            </body>
            </html>
            """, 500
    
    # HTML form for adding users
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add User</title>
        <style>
            body { 
                font-family: Arial; 
                max-width: 600px; 
                margin: 50px auto; 
                padding: 20px; 
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                font-size: 16px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 14px;
                background: #007bff;
                color: white;
                border: none;
                font-size: 18px;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover { background: #0056b3; }
            .warning {
                background: #fff3cd;
                border: 1px solid #ffc107;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 20px;
                color: #856404;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔓 Add New User</h2>
            <div class="warning">
                <strong>⚠️ WARNING:</strong> This endpoint is VULNERABLE to SQL injection!<br>
                No authentication required. No password hashing. Direct SQL concatenation.
            </div>
            
            <form method="POST">
                <label>Username:</label>
                <input type="text" name="username" placeholder="Enter username" required>
                
                <label>Password:</label>
                <input type="text" name="password" placeholder="Enter password (stored as plain text!)" required>
                
                <button type="submit">➕ Add User</button>
            </form>
            
            <br>
            <p><a href="/view_users">👥 View All Users</a> | <a href="/welcome">🏠 Dashboard</a></p>
        </div>
    </body>
    </html>
    '''

# ---------------- VIEW USERS (for testing) ----------------
@app.route('/view_users')
def view_users():
    """Display all users (including plain text passwords!)"""
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, password FROM users").fetchall()
    conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Users</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background: #007bff; color: white; }
            tr:nth-child(even) { background: #f9f9f9; }
            .warning { background: #fff3cd; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h2>👥 All Users in Database</h2>
        <div class="warning">
            <strong>⚠️ SECURITY ISSUE:</strong> Passwords are stored in PLAIN TEXT and visible here!
        </div>
        <table>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Password (Plain Text!)</th>
            </tr>
    '''
    
    for user in users:
        html += f'''
            <tr>
                <td>{user['id']}</td>
                <td>{user['username']}</td>
                <td><code>{user['password']}</code></td>
            </tr>
        '''
    
    html += '''
        </table>
        <p><a href="/add_user">Add User</a> | <a href="/welcome">Dashboard</a></p>
    </body>
    </html>
    '''
    
    return html

# ---------------- CLEANUP ----------------
def cleanup():
    """Turn off all devices on exit."""
    print("\nCleaning up GPIO...")
    for led in [led_sound, led_pir, led_ldr] + list(devices.values()):
        led.off()

atexit.register(cleanup)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Delete old database to start fresh
    if os.path.exists('users.db'):
        os.remove('users.db')
        print("🗑️  Deleted old database")
    
    init_db()
    print("\n" + "="*60)
    print("⚠️  VULNERABLE VERSION - FOR EDUCATIONAL TESTING ONLY!")
    print("="*60)
    print("\n📌 Default credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🔓 Vulnerable endpoints:")
    print("   /login         - SQL injection possible")
    print("   /add_user      - SQL injection + no auth required")
    print("   /view_users    - Shows all passwords in plain text")
    print("\n✅ Server running on http://0.0.0.0:5001")
    print("="*60 + "\n")
    
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
