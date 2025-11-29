from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
from gpiozero import LED, DigitalInputDevice, Device
from gpiozero.pins.lgpio import LGPIOFactory
import threading
import time
import atexit
import lgpio
import re
from collections import deque

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

# ---------------- FLASK APP SETUP ----------------
app = Flask(__name__)
CORS(app)  # Enable CORS for unified dashboard
app.secret_key = "S3cUr3!K3y@2025#RNS"
FAILED_LOGIN_LOG = "failed_logins.log"

# ---------------- SQL INJECTION MONITORING ----------------
SQL_INJECTION_PATTERNS = [
    r"(\bor\b|\band\b)\s*\d*\s*=\s*\d*",
    r"(union|select|insert|update|delete|drop|create|alter|exec|execute)\s",
    r"('|\").*?(or|and).*?('|\")\s*=\s*('|\")",
    r";\s*(drop|delete|insert|update)",
    r"--|\#|/\*|\*/",
    r"1\s*=\s*1|'1'\s*=\s*'1'",
]

sql_attack_logs = deque(maxlen=100)  # Keep last 100 attacks

def detect_sql_injection(input_str):
    """Detect SQL injection attempts"""
    if not isinstance(input_str, str):
        return False
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, str(input_str), re.IGNORECASE):
            return True
    return False

@app.before_request
def check_sql_injection():
    """Check all requests for SQL injection - LOG ONLY, DO NOT BLOCK"""
    # Skip checking our monitoring endpoints
    if request.path in ['/api/sql-logs', '/api/sql-stats']:
        return
    
    detected = False
    malicious_inputs = []
    
    # Check query parameters
    for key, value in request.args.items():
        if detect_sql_injection(str(value)):
            detected = True
            malicious_inputs.append(f"{key}: {value}")
    
    # Check form data
    if request.form:
        for key, value in request.form.items():
            if detect_sql_injection(str(value)):
                detected = True
                malicious_inputs.append(f"{key}: {value}")
    
    # Check JSON body
    if request.is_json:
        try:
            data = request.get_json()
            for key, value in data.items():
                if isinstance(value, str) and detect_sql_injection(value):
                    detected = True
                    malicious_inputs.append(f"{key}: {value}")
        except:
            pass
    
    # If SQL injection detected, LOG IT but ALLOW the request to proceed
    if detected:
        # Create query string from all malicious inputs
        query_string = "; ".join(malicious_inputs)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query_string,
            'parameter': malicious_inputs[0].split(':')[0] if malicious_inputs else 'unknown',
            'endpoint': request.path,
            'method': request.method,
            'blocked': False,  # Not blocking, just logging
            'ip': request.remote_addr
        }
        sql_attack_logs.append(log_entry)
        
        # Print detailed warning in terminal
        print("\n" + "="*80)
        print("🚨 [SQL INJECTION DETECTED - ALLOWED TO PROCEED]")
        print("="*80)
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   IP Address: {request.remote_addr}")
        print(f"   Endpoint: {request.method} {request.path}")
        print(f"   User-Agent: {request.headers.get('User-Agent', 'N/A')}")
        print("\n   Malicious Inputs Detected:")
        for idx, malicious_input in enumerate(malicious_inputs, 1):
            print(f"      {idx}. {malicious_input}")
        print("\n   ⚠️  Attack is being ALLOWED for educational purposes!")
        print("="*80 + "\n")

# ---------------- DATABASE FUNCTIONS ----------------
def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def verify_user(username, password):
    """VULNERABLE: Direct string concatenation - allows SQL injection."""
    conn = get_db_connection()
    
    # VULNERABILITY: String formatting instead of parameterized query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    # Show the query in terminal for learning
    print(f"\n[SQL INJECTION TEST] Query executed:")
    print(f">>> {query}\n")
    
    try:
        user = conn.execute(query).fetchone()
        conn.close()
        
        if user:
            return True
        return False
    except Exception as e:
        print(f"[ERROR] SQL Exception: {e}\n")
        conn.close()
        return False

# ---------------- MONITORING ENDPOINTS (NO AUTH REQUIRED) ----------------
@app.route('/api/sql-logs')
def get_sql_logs():
    """Get SQL injection attack logs - NO AUTH REQUIRED FOR SIEM DASHBOARD"""
    return jsonify({
        'success': True,
        'logs': list(sql_attack_logs)
    })

@app.route('/api/sql-stats')
def get_sql_stats():
    """Get SQL injection statistics - NO AUTH REQUIRED FOR SIEM DASHBOARD"""
    total_attacks = len(sql_attack_logs)
    
    # Count unique IPs
    unique_ips = len(set(log['ip'] for log in sql_attack_logs)) if sql_attack_logs else 0
    
    # Count endpoints targeted
    endpoints_set = set(log['endpoint'] for log in sql_attack_logs) if sql_attack_logs else set()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_attempts': total_attacks,
            'unique_ips': unique_ips,
            'blocked_attacks': 0,  # Not blocking, just logging
            'endpoints_targeted': len(endpoints_set)
        }
    })

# ---------------- MAIN FLASK ROUTES ----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login with VULNERABLE SQL query."""
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
            f.write(f"{ts} Failed login - Username: '{u}' from {ip}\n")
        
        return "<h2>❌ Invalid username or password</h2><p><a href='/login'>Try again</a></p>", 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/welcome')
def welcome():
    """Dashboard."""
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

# ---------------- VULNERABLE ENDPOINTS ----------------
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """VULNERABLE: Add user without authentication, no hashing, SQL injection possible."""
    
    if request.method == 'POST':
        new_user = request.form.get('username', '')
        new_pass = request.form.get('password', '')
        
        # VULNERABILITY: Direct string concatenation
        conn = get_db_connection()
        query = f"INSERT INTO users (username, password) VALUES ('{new_user}', '{new_pass}')"
        
        print(f"\n[SQL INJECTION TEST] Query executed:")
        print(f">>> {query}\n")
        
        try:
            conn.execute(query)
            conn.commit()
            conn.close()
            
            return f"""
            <html>
            <head><title>Success</title></head>
            <body style="font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px;">
                <h2>✅ User Added Successfully!</h2>
                <p>Username: <strong>{new_user}</strong></p>
                <p>Password: <strong>{new_pass}</strong> (stored as plain text!)</p>
                <hr>
                <p>
                    <a href="/add_user">➕ Add Another</a> | 
                    <a href="/view_users">👥 View All Users</a> | 
                    <a href="/welcome">🏠 Dashboard</a>
                </p>
            </body>
            </html>
            """
        except Exception as e:
            return f"""
            <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px;">
                <h2>❌ SQL Error</h2>
                <pre style="background: #ffe6e6; padding: 15px; border-radius: 5px; overflow-x: auto;">{str(e)}</pre>
                <h3>Query Attempted:</h3>
                <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto;">{query}</pre>
                <p><a href="/add_user">← Try Again</a></p>
            </body>
            </html>
            """, 500
    
    # GET request - show form
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
            .warning {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin-bottom: 20px;
                color: #856404;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 14px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 18px;
                cursor: pointer;
            }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>➕ Add New User</h2>
            
            <div class="warning">
                ⚠️ <strong>VULNERABLE ENDPOINT</strong><br>
                • No authentication required<br>
                • Passwords stored in plain text<br>
                • SQL injection possible in both fields
            </div>
            
            <form method="POST">
                <label><strong>Username:</strong></label>
                <input type="text" name="username" placeholder="Enter username" required>
                
                <label><strong>Password:</strong></label>
                <input type="text" name="password" placeholder="Enter password (plain text!)" required>
                
                <button type="submit">Add User</button>
            </form>
            
            <br>
            <p style="text-align: center;">
                <a href="/view_users">👥 View All Users</a> | 
                <a href="/welcome">🏠 Dashboard</a>
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/view_users')
def view_users():
    """Display all users with plain text passwords."""
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, password FROM users ORDER BY id").fetchall()
    conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Users</title>
        <style>
            body { font-family: Arial; max-width: 900px; margin: 50px auto; padding: 20px; }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            th, td { 
                border: 1px solid #ddd; 
                padding: 12px; 
                text-align: left; 
            }
            th { 
                background: #dc3545; 
                color: white; 
                font-weight: bold;
            }
            tr:nth-child(even) { background: #f9f9f9; }
            tr:hover { background: #f1f1f1; }
            .warning {
                background: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 15px;
                margin-bottom: 20px;
                color: #721c24;
            }
            code {
                background: #ffe6e6;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <h1>👥 Database Users</h1>
        
        <div class="warning">
            <strong>🚨 CRITICAL SECURITY ISSUE</strong><br>
            Passwords are stored and displayed in PLAIN TEXT! Never do this in production!
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Password (Plain Text!)</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for user in users:
        html += f'''
                <tr>
                    <td>{user['id']}</td>
                    <td><strong>{user['username']}</strong></td>
                    <td><code>{user['password']}</code></td>
                </tr>
        '''
    
    html += '''
            </tbody>
        </table>
        
        <p style="text-align: center; margin-top: 30px;">
            <a href="/add_user">➕ Add New User</a> | 
            <a href="/welcome">🏠 Dashboard</a> | 
            <a href="/logout">🚪 Logout</a>
        </p>
    </body>
    </html>
    '''
    
    return html

# ---------------- CLEANUP ----------------
def cleanup():
    """Turn off all devices on exit."""
    print("\n🧹 Cleaning up GPIO...")
    for led in [led_sound, led_pir, led_ldr] + list(devices.values()):
        led.off()

atexit.register(cleanup)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("\n" + "="*70)
    print("⚠️  VULNERABLE SMART CAMPUS - SQL INJECTION LAB")
    print("="*70)
    print("\n🔓 VULNERABILITIES:")
    print("   • /login        - SQL injection in authentication")
    print("   • /add_user     - SQL injection + no auth + plain text passwords")
    print("   • /view_users   - Exposes all passwords in plain text")
    print("\n📊 SQL INJECTION MONITORING:")
    print("   • All requests are monitored for SQL injection patterns")
    print("   • Detected attacks are LOGGED but NOT BLOCKED")
    print("   • Attacks proceed normally for educational demonstration")
    print("\n🔗 MONITORING ENDPOINTS (No Auth Required):")
    print("   • /api/sql-logs  - Get all SQL injection attack logs")
    print("   • /api/sql-stats - Get SQL injection statistics")
    print("\n💡 TIP: Check terminal output to see:")
    print("   - SQL injection detection warnings")
    print("   - Executed SQL queries")
    print("   - Attack details (IP, timestamp, malicious input)")
    print("\n✅ Server running on http://0.0.0.0:5001")
    print("   CORS enabled for unified SIEM dashboard")
    print("="*70 + "\n")
    
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
