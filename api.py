from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

API_KEY = "337a076c50f7017bfc523e549b43b0db33e779e3e64c1a311b9c5b30644c9cbe"

WG_CONF = "/etc/wireguard/wg0.conf"
SERVER_PUBLIC_KEY = open("/root/server_public.key").read().strip()
ENDPOINT = "194.87.115.67:51820"


def check_key(req):
    return req.headers.get("X-API-KEY") == API_KEY


def get_next_ip():
    base = "10.0.0."
    with open(WG_CONF, "r") as f:
        content = f.read()

    for i in range(2, 255):
        ip = f"{base}{i}"
        if ip not in content:
            return ip
    return None


# ---------------- GENERATE ----------------
@app.route("/generate", methods=["POST"])
def generate():
    if not check_key(request):
        return jsonify({"error": "forbidden"}), 403

    data = request.json or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "no user_id"}), 400

    try:
        # генерим ключи
        private = subprocess.check_output("wg genkey", shell=True).decode().strip()
        public = subprocess.check_output(
            f"echo {private} | wg pubkey", shell=True
        ).decode().strip()

        ip = get_next_ip()

        if not ip:
            return jsonify({"error": "no free ip"}), 500

        # добавляем peer в WG
        subprocess.run(
            f"wg set wg0 peer {public} allowed-ips {ip}/32",
            shell=True,
            check=True
        )

        # сохраняем в конфиг
        with open(WG_CONF, "a") as f:
            f.write(
                f"\n[Peer]\nPublicKey = {public}\nAllowedIPs = {ip}/32\n"
            )

        # генерим клиентский конфиг
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
            "public_key": public
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- DELETE ----------------
def remove_from_conf(public_key):
    with open(WG_CONF, "r") as f:
        lines = f.readlines()

    new_lines = []
    skip = False

    for line in lines:
        if "PublicKey" in line and public_key in line:
            skip = True
            continue

        if skip:
            if line.strip() == "":
                skip = False
            continue

        new_lines.append(line)

    with open(WG_CONF, "w") as f:
        f.writelines(new_lines)


@app.route("/delete", methods=["POST"])
def delete():
    if not check_key(request):
        return jsonify({"error": "forbidden"}), 403

    data = request.json or {}
    public_key = data.get("public_key")

    if not public_key:
        return jsonify({"error": "no key"}), 400

    try:
        subprocess.run(
            ["wg", "set", "wg0", "peer", public_key, "remove"],
            check=True
        )

        remove_from_conf(public_key)

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)