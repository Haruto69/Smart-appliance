🏠 Smart Appliance Control System
A Flask-based web application to remotely control home appliances like lights and fans using Raspberry Pi GPIO pins. Includes user authentication with SQLite, mock GPIO support for non-RPi development, and a clean UI.

💡 Features
🔒 Secure Login System with hashed passwords using SQLite (users.db)

🌐 Web Interface to control individual appliances (lights and fans)

💡 Bulk Light Control (Turn all lights ON or OFF)

📄 Failed Login Logging for basic security/monitoring

🧪 Mock GPIO for testing on non-Raspberry Pi devices

📦 Modular Python Structure for easy expansion

🛠️ Requirements
Python 3.x
Flask
bcrypt
sqlite3
RPi.GPIO (only for Raspberry Pi)

Install dependencies:
pip install -r requirements.txt

📂 Project Structure:
Smart-appliance/
├── app.py                 # Main Flask app
├── templates/             # HTML files (login, welcome, device control)
├── static/                # CSS / JS / assets
├── users.db               # SQLite DB for login credentials
├── failed_logins.log      # Logs failed login attempts
├── requirements.txt
└── README.md

⚙️ Usage
1. Clone the repository
git clone https://github.com/Haruto69/Smart-appliance.git
cd Smart-appliance

2. Run the app
python app.py
Then open your browser at http://localhost:5000

🧪 Development on Non-Raspberry Pi
If RPi.GPIO is not available (e.g., Windows or Mac), the system uses unittest.mock.MagicMock() to safely simulate GPIO behavior.

🔐 Logging
All failed login attempts are logged to failed_logins.log with IP and timestamp for security analysis or Fail2Ban integration.
