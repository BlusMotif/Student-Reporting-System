import pyrebase
from datetime import datetime
import json

# Firebase configuration for Realtime Database
firebase_config = {
    "apiKey": "your-api-key",  # This can be empty for server-side operations
    "authDomain": "student-concern-portal.firebaseapp.com",
    "databaseURL": "https://student-concern-portal-default-rtdb.firebaseio.com/",
    "projectId": "student-concern-portal",
    "storageBucket": "student-concern-portal.appspot.com",
    "messagingSenderId": "your-sender-id",
    "appId": "your-app-id"
}

class FirebaseRealtimeDB:
    def __init__(self):
        try:
            # Initialize Firebase
            firebase = pyrebase.initialize_app(firebase_config)
            self.db = firebase.database()
            print("🔥 Firebase Realtime Database connected successfully!")
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            print("Using mock database for development...")
            self.db = None
    
    def get_db(self):
        return self.db

# Global Firebase instance
firebase_realtime = FirebaseRealtimeDB()
