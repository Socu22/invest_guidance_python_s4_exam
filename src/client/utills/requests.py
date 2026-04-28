import requests
import json

BASE_URL = ""  # Replace with your actual base URL

def request(endpoint, options=None):
    if options is None:
        options = {}

    headers = {
        "Content-Type": "application/json",
        **(options.get("headers", {}))
    }

    try:
        response = requests.request(
            method=options.get("method", "GET"),
            url=f"{BASE_URL}{endpoint}",
            headers=headers,
            cookies=options.get("cookies", {}),
            data=json.dumps(options.get("body", {})) if options.get("body") else None,
            allow_redirects=True,
        )

        data = response.json()

        return {
            "ok": response.ok,
            "status": response.status_code,
            "data": data
        }

    except requests.exceptions.RequestException as error:
        print(f"Fetch error: {error}")

        return {
            "ok": False,
            "status": 0,
            "data": {"errorMessage": "Network error"}
        }

def fetch_get(endpoint):
    return request(endpoint, {"method": "GET"})

def fetch_post(endpoint, body):
    return request(endpoint, {"method": "POST", "body": body})

def fetch_put(endpoint, body):
    return request(endpoint, {"method": "PUT", "body": body})

def fetch_patch(endpoint, body):
    return request(endpoint, {"method": "PATCH", "body": body})

def fetch_delete(endpoint):
    return request(endpoint, {"method": "DELETE"})
