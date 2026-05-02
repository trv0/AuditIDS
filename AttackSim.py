import tkinter as tk
from datetime import datetime
import random
import sqlite3 

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")

# Clear existing data (optional for repeat runs)
cursor.execute("DELETE FROM users")

# Insert 4 sample users
users = [
    ("admin", "4321"),
    ("troy", "1234"),
    ("guest", "0000"),
    ("yousef", "1111")
]

cursor.executemany("INSERT INTO users VALUES (?, ?)", users)

conn.commit()
conn.close()

def log_attempt(username, password, success):
    """Log the login attempt to network_log.txt in a format similar to OpenSSH logs."""
    timestamp = datetime.now().strftime("%b %d %H:%M:%S")
    ip = "192.0.2.0"
    pid = random.randint(10000, 99999)  # Fake PID
    if success:
        content = f"Accepted password for {username} from {ip} port 22 ssh2"
    else:
        content = f"Failed password for invalid user {username} from {ip} port 22 ssh2"
    with open("network_log.txt", "a") as f:
        f.write(f"{timestamp} sshd[{pid}]: {content}\n")

def login():
    user = username_entry.get()
    pwd = password_entry.get()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Vulnerable query (DO NOT USE IN REAL SYSTEMS)
    query = f"SELECT * FROM users WHERE username = '{user}' AND password = '{pwd}'"
    cursor.execute(query)

    result = cursor.fetchone()

    if result:
        status_label.config(text="Login successful")
        log_attempt(user, pwd, True)
    else:
        status_label.config(text="Login failed")
        log_attempt(user, pwd, False)

    conn.close()

    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)


def brute_force():
    """Try every 4-digit PIN for the entered username."""
    target_username = username_entry.get().strip() or "admin"

    for pin in range(10000):
        candidate = f"{pin:04d}"
        username_entry.delete(0, tk.END)
        username_entry.insert(0, target_username)
        password_entry.delete(0, tk.END)
        password_entry.insert(0, candidate)
        root.update_idletasks()

        login()

        if status_label.cget("text") == "Login successful":
            break

def reveal_compromised():
    status_label.config(text=f"Compromised user: troy (password: 1234)")


# GUI setup
root = tk.Tk()
root.title("Intrusion Simulator")

tk.Label(root, text="Username:").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Login", command=login).pack()
tk.Button(root, text="Brute Force", command=brute_force).pack()
tk.Button(root, text="Reveal Compromised User", command=reveal_compromised).pack()

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()