import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your service account key
cred_path = "firebase_key.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
