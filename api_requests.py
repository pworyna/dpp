import requests

def main():
    BASE_URL = "http://127.0.0.1:8000"

    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    login_resp = requests.post(f"{BASE_URL}/login", json=login_data)

    if login_resp.status_code != 200:
        print("Błąd logowania:", login_resp.status_code, login_resp.text)
        return

    token = login_resp.json()["access_token"]
    print("Zalogowano. Token JWT:", token)

    headers = {"Authorization": f"Bearer {token}"}

    protected_resp = requests.get(f"{BASE_URL}/protected", headers=headers)
    print("\n/protected")
    print("Status:", protected_resp.status_code)
    print(protected_resp.json())

    user_details_resp = requests.get(f"{BASE_URL}/user_details", headers=headers)
    print("\n--- /user_details ---")
    print("Status:", user_details_resp.status_code)
    print(user_details_resp.json())

    new_user_data = {
        "username": "nowyuser3",
        "password": "haslo123",
        "role": "ROLE_USER"
    }

    add_user_resp = requests.post(f"{BASE_URL}/users", json=new_user_data, headers=headers)
    print("\n--- /users (dodanie nowego użytkownika) ---")
    print("Status:", add_user_resp.status_code)
    print(add_user_resp.json())

if __name__ == "__main__":
    main()
