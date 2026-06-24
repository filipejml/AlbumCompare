import json
import os
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash


DEFAULT_USERS_FILE = Path(__file__).resolve().parent / "users.json"


def users_file_path():
    configured_path = os.getenv("USERS_FILE")
    if configured_path:
        return Path(configured_path)
    return DEFAULT_USERS_FILE


def load_users():
    path = users_file_path()
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as users_file:
        payload = json.load(users_file)

    users = payload.get("users", [])
    return users if isinstance(users, list) else []


def save_users(users):
    path = users_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as users_file:
        json.dump({"users": users}, users_file, ensure_ascii=False, indent=2)
        users_file.write("\n")


def find_user(username):
    username = (username or "").strip()
    for user in load_users():
        if user.get("username") == username:
            return user
    return None


def create_user(username, password):
    username = (username or "").strip()
    password = password or ""

    if len(username) < 3:
        raise ValueError("O usuário deve ter pelo menos 3 caracteres.")
    if len(username) > 40:
        raise ValueError("O usuário deve ter no máximo 40 caracteres.")
    if len(password) < 6:
        raise ValueError("A senha deve ter pelo menos 6 caracteres.")
    if find_user(username):
        raise ValueError("Este usuário já está cadastrado.")

    users = load_users()
    role = "admin" if not users else "user"
    user = {
        "username": username,
        "role": role,
        "password_hash": generate_password_hash(password),
    }
    users.append(user)
    save_users(users)
    return {"username": user["username"], "role": user["role"]}


def authenticate_user(username, password):
    username = (username or "").strip()
    password = password or ""

    for user in load_users():
        if user.get("username") != username:
            continue
        if check_password_hash(user.get("password_hash", ""), password):
            return {
                "username": user.get("username"),
                "role": user.get("role", "user"),
            }

    return None
