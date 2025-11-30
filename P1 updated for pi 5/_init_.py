import sqlite3
import bcrypt

# Define user credentials
USERNAME = "admin"
PASSWORD = "Letshavepizzatoday!626$$"

# Hash the password
hashed_password = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt())

# Connect to database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password BLOB NOT NULL
)
""")

# Insert user with hashed password
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (USERNAME, hashed_password))

# Commit and close
conn.commit()
conn.close()

print("✅ users.db has been created with a hashed password!")
