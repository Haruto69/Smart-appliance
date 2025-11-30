from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
import sqlite3
from datetime import datetime

from gpiozero import LED, Device
from gpiozero.pins.lgpio import LGPIOFactory
import lgpio

app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"

# --- GPIO Setup ---
# Force gpiozero to use lgpio backend (needed for Raspberry Pi 5)
Device.pin_factory = LGPIOFactory()

# Reset GPIO pin before use (in case it's left "busy")
def reset_gpio(pin):
    h = lgpio.gpiochip_open(0)
    try:
        lgpio.gpio_free(h, pin)
    except Exception:
        pass
    lgpio.gpiochip_close(h)

APPLIANCE_PIN = 23
reset_gpio(APPLIANCE_PIN)
appliance = LED(APPLIANCE_PIN)

FAILED_LOGIN_LOG = "failed_logins.log"


# --- User Verification ---
def verify_user(username, password):
    """Verify username and password from SQLite database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row[0]):
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
            return redirect(url_for('status'))

        # Log failed attempt
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


@app.route('/on')
def on():
    if 'user' in session:
        appliance.on()
        return render_template('on.html')
    return redirect(url_for('login'))


@app.route('/off')
def off():
    if 'user' in session:
        appliance.off()
        return render_template('off.html')
    return redirect(url_for('login'))


@app.route('/status')
def status():
    """Show current pin state."""
    if 'user' in session:
        state = appliance.is_lit
        return render_template('status.html', state=state)
    return redirect(url_for('login'))


# --- Run Server ---
if __name__ == '__main__':
    # Disable Flask's autoreload to avoid GPIO busy errors
    app.run(host="0.0.0.0", port=5000, debug=False)
