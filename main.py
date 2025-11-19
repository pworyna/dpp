from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
from users_db import USERS_DB

app = FastAPI()

SECRET_KEY = "super_secret_key"
ALGORITHM = "HS256"

class LoginData(BaseModel):
    username: str
    password: str

class NewUser(BaseModel):
    username: str
    password: str
    role: str = "ROLE_USER"

def create_token(username: str, role: str):
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ")[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/login")
def login(data: LoginData):
    username = data.username
    password = data.password.encode("utf-8")

    if username not in USERS_DB:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    hashed_pw = USERS_DB[username]["password"]
    if not bcrypt.checkpw(password, hashed_pw):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role = USERS_DB[username]["role"]
    token = create_token(username, role)

    return {"access_token": token, "token_type": "bearer"}


@app.post("/users")
def add_user(data: NewUser, authorization: str = Header(default=None)):
    decoded = verify_token(authorization)

    if decoded["role"] != "ROLE_ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    if data.username in USERS_DB:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())
    USERS_DB[data.username] = {"password": hashed_pw, "role": data.role}

    return {"message": "User created successfully"}


@app.get("/user_details")
def user_details(authorization: str = Header(default=None)):
    decoded = verify_token(authorization)
    return {"username": decoded["sub"], "role": decoded["role"]}


@app.get("/protected")
def protected(authorization: str = Header(default=None)):
    verify_token(authorization)
    return {"message": "Access granted to protected resource"}
