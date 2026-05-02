import requests

API_URL = "http://194.87.115.67:5000/generate"
DELETE_API_URL = "http://194.87.115.67:5000/delete"

# (опционально, но очень рекомендую)
API_KEY = "337a076c50f7017bfc523e549b43b0db33e779e3e64c1a311b9c5b30644c9cbe"


# ---------------- GENERATE CONFIG ----------------
def generate_config(user_id: int):
    try:
        response = requests.post(
            API_URL,
            json={"user_id": user_id},
            headers={"X-API-KEY": API_KEY},
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        # 🔒 проверка ответа
        if "config" not in data or "public_key" not in data:
            raise Exception(f"Bad API response: {data}")

        config = data["config"]
        public_key = data["public_key"]

        # защита от пустого конфига
        if not config or len(config) < 50:
            raise Exception("Invalid VPN config")

        return config, public_key

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {e}")

    except ValueError:
        raise Exception(f"Invalid JSON: {response.text}")

    except Exception as e:
        raise Exception(f"VPN API error: {e}")


# ---------------- DELETE PEER ----------------
def delete_peer(public_key: str):
    try:
        response = requests.post(
            DELETE_API_URL,
            json={"public_key": public_key},
            headers={"X-API-KEY": API_KEY},
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            raise Exception(f"Delete failed: {data}")

        return True

    except requests.exceptions.RequestException as e:
        raise Exception(f"Delete request error: {e}")

    except Exception as e:
        raise Exception(f"Delete error: {e}")