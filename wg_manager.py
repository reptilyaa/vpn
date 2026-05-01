import requests

API_URL = "http://194.87.115.67:5000/generate"


def generate_config(user_id: int) -> str:
    """
    Получает VPN конфиг с VPS API
    """

    try:
        response = requests.post(
            API_URL,
            json={"user_id": user_id},
            timeout=15
        )

        # если сервер упал / 500 / 404
        response.raise_for_status()

        data = response.json()

        # защита от кривого ответа
        if "config" not in data:
            raise Exception(f"Bad API response: {data}")

        config = data["config"]

        # финальная защита от пустого ответа
        if not config or len(config) < 50:
            raise Exception("Empty or invalid VPN config received")

        return config

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {e}")

    except ValueError:
        raise Exception(f"Invalid JSON from API: {response.text}")

    except Exception as e:
        raise Exception(f"VPN API error: {e}")