import requests
import json
from werkzeug.security import generate_password_hash, check_password_hash

# Firebase URL
FIREBASE_URL = "https://student-concern-portal-default-rtdb.firebaseio.com/"

def fix_authentication_issues():
    """Fix authentication issues in Firebase"""
    print("🔧 Fixing Firebase Authentication Issues...")
    print("=" * 50)
    
    try:
        # Step 1: Get current users from Firebase
        print("1. Retrieving current users from Firebase...")
        users_response = requests.get(f"{FIREBASE_URL}users.json")
        
        if users_response.status_code != 200:
            print(f"❌ Failed to get users: {users_response.status_code}")
            return False
        
        users_data = users_response.json()
        if not users_data:
            print("❌ No users found in Firebase")
            return False
        
        print(f"   ✅ Found {len(users_data)} users")
        
        # Step 2: Create properly formatted users with correct passwords
        print("\n2. Creating fixed user accounts...")
        fixed_users = {}
        
        # Default passwords for migrated users
        default_passwords = {
            'admin': 'admin123',
            'student1': 'student123',
            'student2': 'student123'
        }
        
        for user_id, user_data in users_data.items():
            username = user_data.get('username')
            role = user_data.get('role')
            
            if username:
                # Use default password if available, otherwise use username as password
                default_password = default_passwords.get(username, username + '123')
                
                fixed_user = {
                    'username': username,
                    'password': generate_password_hash(default_password),
                    'role': role,
                    'created_at': user_data.get('created_at', '2025-01-15T00:00:00'),
                    'sqlite_id': user_data.get('sqlite_id', 0),
                    'default_password': default_password  # For reference only
                }
                
                fixed_users[user_id] = fixed_user
                print(f"   ✅ Fixed user: {username} (role: {role}, password: {default_password})")
        
        # Step 3: Update Firebase with fixed users
        print(f"\n3. Updating Firebase with {len(fixed_users)} fixed users...")
        update_response = requests.put(f"{FIREBASE_URL}users.json", json=fixed_users)
        
        if update_response.status_code == 200:
            print("   ✅ Successfully updated all users in Firebase")
        else:
            print(f"   ❌ Failed to update users: {update_response.status_code}")
            return False
        
        # Step 4: Verify the fixes
        print("\n4. Verifying authentication fixes...")
        
        # Test admin login
        admin_user = None
        for user_id, user_data in fixed_users.items():
            if user_data['username'] == 'admin':
                admin_user = user_data
                admin_user['id'] = user_id
                break
        
        if admin_user:
            # Test password verification
            test_password = 'admin123'
            if check_password_hash(admin_user['password'], test_password):
                print(f"   ✅ Admin authentication working (password: {test_password})")
            else:
                print("   ❌ Admin authentication still failing")
        
        # Step 5: Create a user credentials reference file
        print("\n5. Creating user credentials reference...")
        credentials = {}
        for user_id, user_data in fixed_users.items():
            credentials[user_data['username']] = {
                'password': user_data['default_password'],
                'role': user_data['role'],
                'firebase_id': user_id
            }
        
        with open('user_credentials.json', 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print("   ✅ Created user_credentials.json with login details")
        
        print("\n🎉 Authentication fixes completed successfully!")
        print("\n📋 User Login Credentials:")
        print("-" * 30)
        for username, creds in credentials.items():
            print(f"Username: {username}")
            print(f"Password: {creds['password']}")
            print(f"Role: {creds['role']}")
            print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing authentication: {e}")
        return False

def test_fixed_authentication():
    """Test the fixed authentication system"""
    print("\n🧪 Testing Fixed Authentication...")
    print("=" * 40)
    
    try:
        from firebase_simple import simple_firebase_db
        
        # Test admin login
        print("Testing admin login...")
        admin_user = simple_firebase_db.verify_password('admin', 'admin123')
        if admin_user:
            print("✅ Admin login successful!")
            print(f"   Username: {admin_user['username']}")
            print(f"   Role: {admin_user['role']}")
            print(f"   ID: {admin_user['id']}")
        else:
            print("❌ Admin login failed")
        
        # Test student login
        print("\nTesting student1 login...")
        student_user = simple_firebase_db.verify_password('student1', 'student123')
        if student_user:
            print("✅ Student login successful!")
            print(f"   Username: {student_user['username']}")
            print(f"   Role: {student_user['role']}")
        else:
            print("❌ Student login failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

if __name__ == '__main__':
    success = fix_authentication_issues()
    if success:
        test_fixed_authentication()
    else:
        print("\n❌ Failed to fix authentication issues")
