# Clinic Management (Flask + PyMongo)

Stack: Flask, Flask-Login, Flask-PyMongo, Bootstrap 5, HTML + jQuery.

## Structure
- `clinic_flask/` Flask application (blueprints for owner, reception, doctor, auth)
  - `app/` code
  - `run.py` entrypoint
  - `requirements.txt` Flask deps

## Setup
```bash
cd clinic_flask
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Configure MongoDB
Set environment variables:
```bash
export MONGODB_URI="mongodb://127.0.0.1:27017"
export MONGODB_DB="hems_dental"
```

Seed an owner user (for login):
```bash
python - <<'PY'
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
client = MongoClient(os.environ.get("MONGODB_URI","mongodb://127.0.0.1:27017"))
db = client[os.environ.get("MONGODB_DB","hems_dental")]
db.users.insert_one({"username":"owner","password_hash":generate_password_hash("owner123"),"role":"OWNER"})
print("Seeded: owner / owner123")
PY
```

## Run
```bash
python run.py
```
- Login: `/auth/login`
- Owner dashboard: `/owner/dashboard`
- Reception dashboard: `/reception/dashboard`
- Doctor dashboard: `/doctor/dashboard`

## Notes
- Requires a running MongoDB instance (local or Atlas).
- Extend blueprints to implement full clinic workflows (patients, doctors, appointments, billing, prescriptions).

