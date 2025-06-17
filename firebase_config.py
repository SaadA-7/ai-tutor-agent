import os
import json
import firebase_admin
from firebase_admin import credentials, auth as admin_auth
import streamlit as st

# Initialize Firebase only once
if not firebase_admin._apps:
    # Load from Streamlit secrets
    service_account_info = json.loads(st.secrets["firebase_service_account"])
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

auth = admin_auth
