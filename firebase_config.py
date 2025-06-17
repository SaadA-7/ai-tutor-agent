import json
import os
import firebase_admin
from firebase_admin import credentials, auth as admin_auth
import streamlit as st

# Initialize Firebase only once
if not firebase_admin._apps:
    if "firebase_service_account" in st.secrets:
        # Running on Streamlit Cloud: load from secrets
        service_account_info = json.loads(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(service_account_info)
    else:
        # Running locally: load from local JSON file
        cred = credentials.Certificate("firebase-service-account.json")

    firebase_admin.initialize_app(cred)

auth = admin_auth
