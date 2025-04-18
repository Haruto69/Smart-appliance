# 🏠 Smart Appliance Control System

A Flask-based web application to remotely control lights and fans using Raspberry Pi GPIO pins. It includes secure user authentication via SQLite and mock GPIO support for development on non-RPi systems.

---

## 💡 Features

- 🔐 Secure user login with hashed passwords stored in `users.db`
- 💻 Web interface for turning individual devices ON/OFF
- 💡 One-click control to switch all lights ON or OFF
- 📜 Logging of failed login attempts with timestamps
- 🧪 Mock GPIO support for development on non-Raspberry Pi devices
- 🔌 Clean modular code for easy customization

---

## 📦 Requirements

- Python 3.x
- Flask
- bcrypt
- sqlite3
- RPi.GPIO *(automatically mocked if not found)*

Install dependencies:

```bash
pip install -r requirements.txt
