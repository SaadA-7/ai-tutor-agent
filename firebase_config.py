import pyrebase

firebase_config = {
    "apiKey": "AIzaSyAJGJmTnkc7ybIEOFTfFXtONUCGK99gEUs",
    "authDomain": "ai-tutor-agent-v1.firebaseapp.com",
    "databaseURL": "",
    "projectId": "ai-tutor-agent-v1",
    "storageBucket": "ai-tutor-agent-v1.appspot.com",
    "messagingSenderId": "36461042628",
    "appId": "1:36461042628:web:6a6051217d94d88f9ee291",
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()