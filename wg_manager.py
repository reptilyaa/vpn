from vpn.ssh_client import run_ssh
import subprocess
import random


SERVER_PUBLIC_KEY = "E3xko3P5bs51CJ4jRND+DPmlst1wCngeweSy0aFIJnM="
SERVER_IP = "194.87.115.67"  # твой IP


def generate_keys():
    private = subprocess.check_output("wg genkey", shell=True).decode().strip()
    public = subprocess.check_output(f"echo {private} | wg pubkey", shell=True).decode().strip()
    return private, public


def generate_config(user_id):
    ip = f"10.0.0.{random.randint(2, 200)}"

    private, public = generate_keys()

    # 👉 добавляем peer на VPS
    run_ssh(f"wg set wg0 peer {public} allowed-ips {ip}/32")

    config = f"""
[Interface]
PrivateKey = {private}
Address = {ip}/32
DNS = 1.1.1.1

[Peer]
PublicKey = {SERVER_PUBLIC_KEY}
Endpoint = {SERVER_IP}:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""

    return config