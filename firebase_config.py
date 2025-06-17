import firebase_admin
from firebase_admin import credentials, auth as admin_auth

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)

# Export for use in app.py
auth = admin_auth
