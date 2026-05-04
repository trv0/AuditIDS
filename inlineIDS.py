"""
MITRE-Attack Data courtesy of : https://github.com/mitre/cti/blob/master/enterprise-attack/enterprise-attack.json
"""
import time
import os
import re
from collections import defaultdict
from mitreattack.stix20 import MitreAttackData

FILE_PATH = "network_log.txt"
POLL_INTERVAL = 0.5

# --- Detection Config ---
BRUTE_FORCE_THRESHOLD = 5
TIME_WINDOW = 60  # seconds

SENSITIVE_USERS = {"troy"}

SQL_PATTERNS = [
    r"'--",
    r"' --",
    r"' OR",
    r"\" OR"
]

# --- State Tracking ---
failed_attempts = defaultdict(list)
techniques = {}

# --- MITRE fallback ---
FALLBACK = {
    "T1110": ("Brute Force", "Repeated login attempts to guess credentials."),
    "T1078": ("Valid Accounts", "Use of legitimate credentials."),
    "T1190": ("Exploit Public-Facing Application", "Injection attacks like SQLi.")
}

# --- File Monitoring ---
def wait_for_file(path):
    if not os.path.exists(path):
        print(f"Waiting for {path}...")
        while not os.path.exists(path):
            time.sleep(POLL_INTERVAL)

def follow(path):
    with open(path, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                yield line.strip()
            else:
                time.sleep(POLL_INTERVAL)

# --- Parsing ---
def parse_log(line):
    pattern = r'(\w+ \d+ \d+:\d+:\d+) sshd\[\d+\]: (.+)'
    match = re.match(pattern, line)
    if not match:
        return None

    timestamp = match.group(1)
    content = match.group(2)

    ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', content)
    user_match = re.search(r'for (invalid user )?(.+?) from', content)

    source_ip = ip_match.group(1) if ip_match else "unknown"
    username = user_match.group(2) if user_match else "unknown"

    return timestamp, content, source_ip, username

# --- MITRE Lookup ---
def get_technique(tech_id):
    if techniques:
        for tech in techniques:
            refs = tech.get("external_references", [])
            if refs and refs[0].get("external_id") == tech_id:
                return tech.get("name"), tech.get("description")
    return FALLBACK.get(tech_id, ("Unknown", "No description"))

# --- Alerting ---
def alert(timestamp, ip, tech_id):
    name, desc = get_technique(tech_id)
    
    print(f"\nALERT [{tech_id}] {name}")
    print(f"Time: {timestamp} | IP: {ip}")
    print(f"Description: {desc[:120]}...\n")

    with open("IDS_report.txt", "a") as f:
        f.write(f"{timestamp},{ip},{tech_id},{name},{desc}\n")
        f.write("-" * 80 + "\n")

# --- Detection Logic ---
def detect_failed_login(ip, timestamp):
    now = time.time()
    failed_attempts[ip].append(now)

    # Keep only recent attempts
    failed_attempts[ip] = [
        t for t in failed_attempts[ip]
        if now - t <= TIME_WINDOW
    ]

    count = len(failed_attempts[ip])

    if count >= BRUTE_FORCE_THRESHOLD:
        alert(timestamp, ip, "T1110")
    else:
        print(f"Failed login from {ip}")

def detect_success(content, username, ip, timestamp):
    # Compromised account detection
    if username in SENSITIVE_USERS:
        alert(timestamp, ip, "T1078")

def detect_sql_injection(content, ip, timestamp):
    for pattern in SQL_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            alert(timestamp, ip, "T1190")
            break

# --- Main IDS ---
def IDS(line):
    parsed = parse_log(line)
    if not parsed:
        return

    timestamp, content, ip, username = parsed

    # print(f"[LOG] {line}")

    # SQL Injection (check first)
    detect_sql_injection(content, ip, timestamp)

    # Failed login
    if "Failed password" in content or "Invalid user" in content:
        detect_failed_login(ip, timestamp)

    # Successful login
    elif "Accepted password" in content:
        detect_success(content, username, ip, timestamp)

# --- Main ---
def main():
    global techniques

    print("IDS started...\n")

    # Load MITRE
    try:
        mitre = MitreAttackData("enterprise-attack.json")
        techniques = mitre.get_techniques()
        print("MITRE ATT&CK loaded.\n")
    except Exception as e:
        print(f"MITRE load failed: {e}\nUsing fallback.\n")

    wait_for_file(FILE_PATH)

    try:
        for line in follow(FILE_PATH):
            IDS(line)
    except KeyboardInterrupt:
        print("\nIDS stopped.")

if __name__ == "__main__":
    main()