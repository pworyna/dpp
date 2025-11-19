from fastapi.testclient import TestClient
from main import app
from users_db import USERS_DB
import bcrypt

client = TestClient(app)

def get_admin_token():
    response = client.post("/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_login_success():
    response = client.post("/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    response = client.post("/login", json={"username": "admin", "password": "zlehaslo"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_user_not_found():
    response = client.post("/login", json={"username": "nieistnieje", "password": "abc"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_add_user_with_admin_token():
    token = get_admin_token()
    response = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "nowy_user", "password": "test123", "role": "ROLE_USER"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"
    assert "nowy_user" in USERS_DB

def test_add_user_without_token():
    response = client.post(
        "/users",
        json={"username": "bez_tokena", "password": "test", "role": "ROLE_USER"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing token"

def test_add_user_with_user_role():
    hashed = bcrypt.hashpw(b"user123", bcrypt.gensalt())
    USERS_DB["zwykly"] = {"password": hashed, "role": "ROLE_USER"}

    response = client.post("/login", json={"username": "zwykly", "password": "user123"})
    token = response.json()["access_token"]

    response = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "nowy_zwykly", "password": "test123", "role": "ROLE_USER"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"

def test_user_details_valid_token():
    token = get_admin_token()
    response = client.get("/user_details", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "ROLE_ADMIN"

def test_user_details_missing_token():
    response = client.get("/user_details")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing token"
