import requests
import json

def access_token(refresh_token):
    url = "https://business-api.tiktok.com/open_api/v1.3/tt_user/oauth2/refresh_token/"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "client_id": "7402852352790626320",
        "client_secret": "1892f5143bf70ff2c0ccebad572fd4948f673885",
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0 and data.get("message") == "OK":
            print("TikTok Access Token Obtained: " + data["data"]["access_token"])
            return data["data"]["access_token"], data["data"]["open_id"]
        else:
            raise Exception(f"API error: {data.get('message')}")
    else:
        raise Exception(f"HTTP error: {response.status_code}")

# Example usage
if __name__ == "__main__":
    refresh_token = "rft.ySKKMj4o6Mp0ovmhwFrAge5y8ecRZYctj5DZx4EGVRAIjZACLkA6twgqfg7m!6362.u1"
    try:
        new_access_token, open_id = access_token(refresh_token)
        print(f"New access token: {new_access_token}")
        print(f"New open id: {open_id}")

    except Exception as e:
        print(f"Error: {str(e)}")