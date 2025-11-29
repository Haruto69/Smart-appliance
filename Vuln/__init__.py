import sqlite3

# Define user credentials
USERNAME = "admin"
PASSWORD = "Letshavepizzatoday!626$$"

# Connect to database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create users table (password as TEXT, not BLOB)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# Insert user with PLAIN TEXT password (no hashing)
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (USERNAME, PASSWORD))

# Commit and close
conn.commit()
conn.close()

print("✅ users.db has been created with a plain text password!")
