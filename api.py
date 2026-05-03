from flask import Flask, request, jsonify
import subprocess
import threading

app = Flask(__name__)

API_KEY = "337a076c50f7017bfc523e549b43b0db33e779e3e64c1a311b9c5b30644c9cbe"

WG_CONF = "/etc/wireguard/wg0.conf"
IP_POOL_FILE = "/root/ip_pool"
SERVER_PUBLIC_KEY = open("/root/server_public.key").read().strip()
ENDPOINT = "194.87.115.67:51820"

lock = threading.Lock()


def check_key(req):
    return req.headers.get("X-API-KEY") == API_KEY


def run(cmd):
    return subprocess.check_output(cmd).decode().strip()


def get_next_ip():
    with open(IP_POOL_FILE, "r") as f:
        pool = [x.strip() for x in f.readlines() if x.strip()]

    with open(WG_CONF, "r") as f:
        used = f.read()

    for ip in pool:
        if ip not in used:
            return ip
    return None


def sync_wg():
    subprocess.run(["wg-quick", "down", "wg0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["wg-quick", "up", "wg0"], check=True)


# ---------------- GENERATE ----------------
@app.route("/generate", methods=["POST"])
def generate():
    if not check_key(request):
        return jsonify({"error": "forbidden"}), 403

    data = request.json or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "no user_id"}), 400

    with lock:
        try:
            private = run(["wg", "genkey"])
            public = subprocess.check_output(
                ["wg", "pubkey"],
                input=private.encode()
            ).decode().strip()

            ip = get_next_ip()
            if not ip:
                return jsonify({"error": "no free ip"}), 500

            # runtime add
            subprocess.run([
                "wg", "set", "wg0",
                "peer", public,
                "allowed-ips", f"{ip}/32"
            ], check=True)

            # persist config safely
            peer_block = f"""
# USER:{user_id}
[Peer]
PublicKey = {public}
AllowedIPs = {ip}/32
"""

            with open(WG_CONF, "a") as f:
                f.write(peer_block)

            # sync config (ВАЖНО)
            sync_wg()

            config = f"""[Interface]
PrivateKey = {private}
Address = {ip}/24
DNS = 1.1.1.1

[Peer]
PublicKey = {SERVER_PUBLIC_KEY}
Endpoint = {ENDPOINT}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""

            return jsonify({
                "config": config,
                "public_key": public,
                "ip": ip
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500


# ---------------- DELETE ----------------
@app.route("/delete", methods=["POST"])
def delete():
    if not check_key(request):
        return jsonify({"error": "forbidden"}), 403

    data = request.json or {}
    public_key = data.get("public_key")

    if not public_key:
        return jsonify({"error": "no key"}), 400

    with lock:
        try:
            subprocess.run([
                "wg", "set", "wg0",
                "peer", public_key,
                "remove"
            ], check=True)

            # чистим конфиг
            with open(WG_CONF, "r") as f:
                lines = f.readlines()

            new = []
            skip = False

            for line in lines:
                if public_key in line:
                    skip = True
                    continue
                if skip and line.strip() == "":
                    skip = False
                    continue
                if not skip:
                    new.append(line)

            with open(WG_CONF, "w") as f:
                f.writelines(new)

            sync_wg()

            return jsonify({"status": "deleted"})

        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)