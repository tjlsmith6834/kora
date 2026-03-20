import firebase_admin
from firebase_admin import credentials
import os
import json
import tempfile

def initialize_firebase():
    if firebase_admin._apps:
        return

    env = os.getenv("ENVIRONMENT", "local")
    raw_cred = os.environ["FIREBASE_APPLICATION_CREDENTIALS"]

    if env == "production":
        # Already a JSON string from ECS secret
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(raw_cred)
            tmp.flush()
            cred = credentials.Certificate(tmp.name)
    else:
        # Local dev: treat as file path
        cred = credentials.Certificate(raw_cred)

    firebase_admin.initialize_app(cred)