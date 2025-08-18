"""
Test script to verify Firebase connection and basic functionality
Run this after setting up your Firebase credentials
"""

def test_firebase_connection():
    try:
        from firebase_config import firebase_config
        
        print("🔥 Testing Firebase Connection...")
        print("=" * 50)
        
        db = firebase_config.get_db()
        if db:
            print("✅ Firebase connection successful!")
            
            # Test basic Firestore operations
            test_collection = db.collection('test')
            doc_ref = test_collection.document('connection_test')
            doc_ref.set({
                'message': 'Firebase connection test',
                'timestamp': '2025-01-15'
            })
            
            # Read the test document
            doc = doc_ref.get()
            if doc.exists:
                print("✅ Firestore read/write operations working!")
                print(f"Test document data: {doc.to_dict()}")
                
                # Clean up test document
                doc_ref.delete()
                print("✅ Test document cleaned up")
            else:
                print("❌ Could not read test document")
                
        else:
            print("❌ Firebase connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Firebase connection error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you have created a Firebase project")
        print("2. Download the service account key JSON file")
        print("3. Set up your .env file with correct values")
        print("4. Install required dependencies: pip install firebase-admin python-dotenv")
        return False
    
    return True

if __name__ == '__main__':
    success = test_firebase_connection()
    if success:
        print("\n🎉 Firebase setup is ready for migration!")
    else:
        print("\n❌ Please fix the Firebase setup before proceeding with migration.")
