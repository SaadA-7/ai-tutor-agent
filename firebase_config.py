import json
import streamlit as st
import firebase_admin
from firebase_admin import auth as admin_auth, credentials

# Load Firebase service account from Streamlit secrets
if not firebase_admin._apps:
    service_account_info = json.loads(st.secrets["firebaseServiceAccount"])
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

# Export the Firebase auth module
auth = admin_auth
