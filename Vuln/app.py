from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import RPi.GPIO as GPIO

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "S3cUr3!K3y@2025#RNS"  # Required for session management

# ---- GPIO SETUP ---- #
GPIO.setwarnings(False)  # Suppress warnings
GPIO.setmode(GPIO.BCM)   # Use Broadcom pin numbering

# Define GPIO Pins Individually
LIGHT_PIN = 18  # GPIO pin for Light
FAN_PIN = 23    # GPIO pin for Fan

# Setup GPIO pins as output and turn them off initially
GPIO.setup(LIGHT_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)

# ---- USER AUTHENTICATION ---- #
USERNAME = "admin"
PASSWORD = "password"  # Change this to a secure password!

def check_login(username, password):
    """Check if the entered username and password are correct."""
    return username == USERNAME and password == PASSWORD

# ---- FUNCTION TO CONTROL GPIO ---- #
def control_device(device, state):
    GPIO.setmode(GPIO.BCM)
    """Turn ON/OFF a device based on the state"""
    print(f"Received request: {device} -> {state}")  # Debugging output

    if device == "light":
        pin = LIGHT_PIN
    elif device == "fan":
        pin = FAN_PIN
    else:
        print("Invalid device!")  # Debugging output
        return False  # Invalid device

    print(f"Using GPIO Pin: {pin}")  # Debugging output to check if pin is set

    # Ensure GPIO pin is set up
    GPIO.setup(pin, GPIO.OUT)

    if state == "on":
        print(f"Turning ON {device} (GPIO {pin})")  # Debugging output
        GPIO.output(pin, GPIO.HIGH)
    elif state == "off":
        print(f"Turning OFF {device} (GPIO {pin})")  # Debugging output
        GPIO.output(pin, GPIO.LOW)
    else:
        print("Invalid state!")  # Debugging output
        return False  # Invalid state

    return True


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

# ---- API ROUTES FOR LIGHT & FAN CONTROL ---- #

@app.route("/control/<device>/<state>", methods=["POST"])
def control_api(device, state):
    if "user" in session:
        if control_device(device, state):
            return jsonify({"status": f"{device} turned {state}"})
        return jsonify({"error": "Invalid device or state"}), 400
    return jsonify({"error": "Unauthorized"}), 403

# Cleanup GPIO on exit
@app.teardown_appcontext
def cleanup_gpio(exception=None):
    print("Cleaning up GPIO...")  # Debugging output
    

# Run the Flask App
if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("Flask App Stopped!")
    finally:
        GPIO.cleanup()
