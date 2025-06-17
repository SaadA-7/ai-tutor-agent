import os
import json
import firebase_admin
from firebase_admin import auth as admin_auth, credentials

# Load Firebase service account from Streamlit Cloud secret
if not firebase_admin._apps:
    service_account_info = json.loads(os.environ["firebase_service_account"])
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

# Export the Firebase auth module
auth = admin_auth
