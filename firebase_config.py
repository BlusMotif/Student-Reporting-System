import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseConfig:
    def __init__(self):
        self.db = None
        self.app = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # For development, you can use a service account key file
                # For production, use environment variables or default credentials
                
                # Option 1: Using service account key file (recommended for development)
                # cred = credentials.Certificate("path/to/serviceAccountKey.json")
                
                # Option 2: Using environment variables (recommended for production)
                # Make sure to set GOOGLE_APPLICATION_CREDENTIALS environment variable
                
                # Option 3: Using default credentials (for Google Cloud environments)
                cred = credentials.ApplicationDefault()
                
                self.app = firebase_admin.initialize_app(cred, {
                    'projectId': os.getenv('FIREBASE_PROJECT_ID', 'your-project-id')
                })
            else:
                self.app = firebase_admin.get_app()
                
            # Initialize Firestore
            self.db = firestore.client()
            print("Firebase initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            print("Please ensure you have:")
            print("1. Set up a Firebase project")
            print("2. Generated a service account key")
            print("3. Set the GOOGLE_APPLICATION_CREDENTIALS environment variable")
            print("4. Or placed the serviceAccountKey.json file in the project root")
    
    def get_db(self):
        """Get Firestore database instance"""
        return self.db

# Global Firebase instance
firebase_config = FirebaseConfig()
