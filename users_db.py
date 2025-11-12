import bcrypt

hashed_admin = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
hashed_user = bcrypt.hashpw(b"user123", bcrypt.gensalt())

USERS_DB = {
    "admin": {"password": hashed_admin, "role": "ROLE_ADMIN"},
    "user": {"password": hashed_user, "role": "ROLE_USER"},
}
