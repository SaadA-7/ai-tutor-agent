import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

# Load Firebase credentials from Streamlit secrets or local file
if "firebase_service_account" in st.secrets:
    service_account_info = dict(st.secrets["firebase_service_account"])
    admin_cred = credentials.Certificate(service_account_info)
else:
    with open("firebase-service-account.json") as f:
        service_account_info = json.load(f)
    admin_cred = credentials.Certificate(service_account_info)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    firebase_admin.initialize_app(admin_cred)

# Initialize Firestore client
db = firestore.client()

# Pyrebase client setup (needed for user login/signup)
firebase_config = {
    "apiKey": st.secrets["firebase_config"]["apiKey"],
    "authDomain": st.secrets["firebase_config"]["authDomain"],
    "projectId": st.secrets["firebase_config"]["projectId"],
    "storageBucket": st.secrets["firebase_config"]["storageBucket"],
    "messagingSenderId": st.secrets["firebase_config"]["messagingSenderId"],
    "appId": st.secrets["firebase_config"]["appId"],
    "databaseURL": st.secrets["firebase_config"]["databaseURL"]
}


firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
