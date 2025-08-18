import traceback
import sys
from datetime import datetime

def diagnose_authentication_error():
    """Comprehensive diagnostic for authentication errors"""
    print("🔍 COMPREHENSIVE AUTHENTICATION DIAGNOSTIC")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    errors_found = []
    
    try:
        # Test 1: Import Firebase module
        print("1. Testing Firebase module import...")
        from firebase_simple import simple_firebase_db
        print("   ✅ Firebase module imported successfully")
        
        # Test 2: Firebase connection
        print("\n2. Testing Firebase connection...")
        users = simple_firebase_db.get_all_users()
        print(f"   ✅ Connected to Firebase - Found {len(users)} users")
        
        # Test 3: User retrieval
        print("\n3. Testing user retrieval...")
        admin_user = simple_firebase_db.get_user_by_username('admin')
        if admin_user:
            print(f"   ✅ Admin user found: {admin_user['username']}")
            print(f"   ✅ Admin ID: {admin_user['id']}")
            print(f"   ✅ Admin role: {admin_user['role']}")
        else:
            print("   ❌ Admin user not found")
            errors_found.append("Admin user missing")
        
        # Test 4: Password verification
        print("\n4. Testing password verification...")
        verified_admin = simple_firebase_db.verify_password('admin', 'admin123')
        if verified_admin:
            print("   ✅ Admin password verification successful")
        else:
            print("   ❌ Admin password verification failed")
            errors_found.append("Admin password verification failed")
        
        # Test 5: Flask app import
        print("\n5. Testing Flask app import...")
        from app_firebase_simple import app
        print("   ✅ Flask app imported successfully")
        
        # Test 6: Session handling
        print("\n6. Testing session handling...")
        with app.test_client() as client:
            # Test login page
            response = client.get('/login')
            if response.status_code == 200:
                print("   ✅ Login page accessible")
            else:
                print(f"   ❌ Login page error: {response.status_code}")
                errors_found.append(f"Login page error: {response.status_code}")
            
            # Test login POST
            login_data = {'username': 'admin', 'password': 'admin123'}
            response = client.post('/login', data=login_data, follow_redirects=True)
            if response.status_code == 200:
                print("   ✅ Login POST request successful")
            else:
                print(f"   ❌ Login POST error: {response.status_code}")
                errors_found.append(f"Login POST error: {response.status_code}")
        
        # Test 7: All user credentials
        print("\n7. Testing all user credentials...")
        test_credentials = [
            ('admin', 'admin123'),
            ('student1', 'student123'),
            ('student2', 'student123')
        ]
        
        for username, password in test_credentials:
            user = simple_firebase_db.verify_password(username, password)
            if user:
                print(f"   ✅ {username} login working")
            else:
                print(f"   ❌ {username} login failed")
                errors_found.append(f"{username} login failed")
        
        # Test 8: Check for common issues
        print("\n8. Checking for common issues...")
        
        # Check if requests module is working
        try:
            import requests
            response = requests.get("https://student-concern-portal-default-rtdb.firebaseio.com/users.json")
            if response.status_code == 200:
                print("   ✅ Direct Firebase API access working")
            else:
                print(f"   ❌ Firebase API access failed: {response.status_code}")
                errors_found.append(f"Firebase API error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Requests module error: {e}")
            errors_found.append(f"Requests error: {e}")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR DURING DIAGNOSIS:")
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print("\nFull traceback:")
        traceback.print_exc()
        errors_found.append(f"Critical error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if not errors_found:
        print("✅ ALL TESTS PASSED - No authentication errors detected")
        print("\nIf you're still experiencing issues, please describe:")
        print("1. What specific error message you're seeing")
        print("2. What action triggers the error")
        print("3. Which page/feature is not working")
    else:
        print(f"❌ FOUND {len(errors_found)} ISSUES:")
        for i, error in enumerate(errors_found, 1):
            print(f"   {i}. {error}")
        
        print("\n🔧 RECOMMENDED FIXES:")
        if "Admin user missing" in errors_found:
            print("   - Run: python fix_auth.py")
        if "Firebase API error" in errors_found:
            print("   - Check Firebase rules and project status")
        if "Login POST error" in errors_found:
            print("   - Check Flask app configuration")
    
    return len(errors_found) == 0

if __name__ == '__main__':
    success = diagnose_authentication_error()
    if not success:
        print("\n🚨 Please share the output above to get specific help with your authentication issues.")
