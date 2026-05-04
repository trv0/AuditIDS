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
root.title("AttackSim - Login")
root.geometry("400x250")

# Center the grid
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)

# --- Title ---
title_label = tk.Label(root, text="TotallyRealWebsite.com", font=("Arial", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(15, 10))

# --- Username ---
tk.Label(root, text="Username:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
username_entry = tk.Entry(root)
username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")

# --- Password ---
tk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="we")

# --- Buttons ---
login_btn = tk.Button(root, text="Login", command=login)
login_btn.grid(row=3, column=0, padx=10, columnspan=2,pady=10, sticky="we")

brute_btn = tk.Button(root, text="Brute Force", command=brute_force)
brute_btn.grid(row=4, column=1, padx=10, pady=10, sticky="we")

reveal_btn = tk.Button(root, text="Reveal Compromised User", command=reveal_compromised)
reveal_btn.grid(row=4, column=0, padx=10, pady=10, sticky="we")

# --- Status label ---
status_label = tk.Label(root, text="", fg="blue")
status_label.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()