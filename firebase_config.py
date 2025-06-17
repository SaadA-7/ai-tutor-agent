import firebase_admin
from firebase_admin import auth as admin_auth, credentials

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)

# Export 'auth' so the rest of your app can use: from firebase_config import auth
auth = admin_auth
