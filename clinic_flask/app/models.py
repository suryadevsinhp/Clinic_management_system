from dataclasses import dataclass
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson import ObjectId
from flask import current_app
from .extensions import mongo


class Roles:
    OWNER = "OWNER"
    RECEPTION = "RECEPTION"
    DOCTOR = "DOCTOR"


@dataclass
class User(UserMixin):
    id: str
    username: str
    role: str
    doctor_id: Optional[str] = None

    @staticmethod
    def from_document(doc) -> "User":
        return User(
            id=str(doc["_id"]),
            username=doc["username"],
            role=doc.get("role", Roles.RECEPTION),
            doctor_id=str(doc.get("doctor_id")) if doc.get("doctor_id") else None,
        )


def get_users_collection():
    db = mongo.cx.get_database(current_app.config["MONGODB_DB"])
    return db["users"]


def find_user_by_username(username: str) -> Optional[User]:
    doc = get_users_collection().find_one({"username": username})
    return User.from_document(doc) if doc else None


def find_user_by_id(user_id: str) -> Optional[User]:
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    doc = get_users_collection().find_one({"_id": oid})
    return User.from_document(doc) if doc else None


def create_user(username: str, password: str, role: str, doctor_id: Optional[str] = None) -> str:
    password_hash = generate_password_hash(password)
    result = get_users_collection().insert_one({
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "doctor_id": ObjectId(doctor_id) if doctor_id else None,
    })
    return str(result.inserted_id)


def verify_user_password(username: str, password: str) -> Optional[User]:
    doc = get_users_collection().find_one({"username": username})
    if not doc:
        return None
    if not check_password_hash(doc.get("password_hash", ""), password):
        return None
    return User.from_document(doc)