from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from bcrypt import hashpw, gensalt, checkpw

app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"  # Required for session management

# ---- FUNCTION TO CHECK USER LOGIN ---- #
def check_login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and checkpw(password.encode(), user[0].encode()):
        return True
    return False

# ---- ROUTES ---- #

@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect to login page first

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_login(username, password):
            session['user'] = username  # Store user in session
            return redirect(url_for('welcome'))
        else:
            return "Invalid username or password. Try again.", 401

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

@app.route('/smoke_detector')
def smoke_detector_control():
    if 'user' in session:
        return render_template('sd.html')
    return redirect(url_for('login'))

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
