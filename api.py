from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

API_KEY = "337a076c50f7017bfc523e549b43b0db33e779e3e64c1a311b9c5b30644c9cbe"


def check_key(req):
    return req.headers.get("X-API-KEY") == API_KEY


# ---------------- GENERATE ----------------
@app.route("/generate", methods=["POST"])
def generate():
    if not check_key(request):
        return jsonify({"error": "forbidden"}), 403

    data = request.json
    user_id = data.get("user_id")

    # ⚠️ тут должна быть твоя логика генерации WG
    # пример (заглушка):

    config = f"CONFIG_FOR_{user_id}"
    public_key = f"KEY_{user_id}"

    return jsonify({
        "config": config,
        "public_key": public_key
    })


# ---------------- DELETE ----------------
@app.route("/delete", methods=["POST"])
def delete():
    if not check_key(request):
        return jsonify({"error": "forbidden"}), 403

    data = request.json
    public_key = data.get("public_key")

    if not public_key:
        return jsonify({"error": "no key"}), 400

    try:
        subprocess.run(
            ["wg", "set", "wg0", "peer", public_key, "remove"],
            check=True
        )

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)