from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import RPi.GPIO as GPIO
import bcrypt
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Single appliance pin
APPLIANCE_PIN = 2
GPIO.setup(APPLIANCE_PIN, GPIO.OUT, initial=GPIO.LOW)

FAILED_LOGIN_LOG = "failed_logins.log"

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
            return redirect(url_for('on'))

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
        GPIO.output(APPLIANCE_PIN, GPIO.HIGH)
        return render_template('on.html')
    return redirect(url_for('login'))

@app.route('/off')
def off():
    if 'user' in session:
        GPIO.output(APPLIANCE_PIN, GPIO.LOW)
        return render_template('off.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
