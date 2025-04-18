from flask import Flask, request, render_template_string
import logging

app = Flask(__name__)

# Configure logging for failed logins
logger = logging.getLogger('login_logger')
handler = logging.FileHandler('/var/log/webapp.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Dummy user for example
USERNAME = "admin"
PASSWORD = "Letshavepizzatoday!626$$"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ip = request.remote_addr

        if username == USERNAME and password == PASSWORD:
            return f"Welcome, {username}!"
        else:
            logger.info(f"Failed login attempt from {ip}")
            return "Invalid credentials"

    return render_template_string('''
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <button type="submit">Login</button>
        </form>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)