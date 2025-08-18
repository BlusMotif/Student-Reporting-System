from firebase_simple import simple_firebase_db

def test_authentication():
    print("🔍 Testing Firebase Authentication System...")
    print("=" * 50)
    
    try:
        # Test 1: Check Firebase connection
        print("1. Testing Firebase connection...")
        users = simple_firebase_db.get_all_users()
        print(f"   ✅ Found {len(users)} users in Firebase")
        
        # Test 2: Test admin user
        print("\n2. Testing admin user...")
        admin = simple_firebase_db.get_user_by_username('admin')
        if admin:
            print(f"   ✅ Admin user found: {admin['username']}")
            print(f"   ✅ Admin role: {admin.get('role')}")
            print(f"   ✅ Admin ID: {admin.get('id')}")
        else:
            print("   ❌ Admin user not found!")
        
        # Test 3: Test password verification
        print("\n3. Testing password verification...")
        if admin:
            # Try to verify with common passwords
            test_passwords = ['admin123', 'admin', 'password', '123456']
            for pwd in test_passwords:
                verified_user = simple_firebase_db.verify_password('admin', pwd)
                if verified_user:
                    print(f"   ✅ Admin password verified with: {pwd}")
                    break
            else:
                print("   ❌ Could not verify admin password with common passwords")
                print("   ℹ️  Password hash:", admin.get('password', 'N/A')[:50] + '...')
        
        # Test 4: List all users and their roles
        print("\n4. All users in Firebase:")
        for i, user in enumerate(users, 1):
            print(f"   {i}. {user.get('username', 'N/A')} - {user.get('role', 'N/A')} (ID: {user.get('id', 'N/A')})")
        
        # Test 5: Test student user
        print("\n5. Testing student users...")
        student_users = [u for u in users if u.get('role') == 'student']
        if student_users:
            test_student = student_users[0]
            print(f"   ✅ Found student: {test_student['username']}")
            
            # Try common student passwords
            test_passwords = ['student123', 'student', 'password']
            for pwd in test_passwords:
                verified_student = simple_firebase_db.verify_password(test_student['username'], pwd)
                if verified_student:
                    print(f"   ✅ Student password verified with: {pwd}")
                    break
            else:
                print("   ❌ Could not verify student password")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

if __name__ == '__main__':
    test_authentication()
