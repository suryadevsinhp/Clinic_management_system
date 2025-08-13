import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017")
    MONGODB_DB = os.environ.get("MONGODB_DB", "hems_dental")
    # Flask-PyMongo uses MONGO_URI
    MONGO_URI = MONGODB_URI