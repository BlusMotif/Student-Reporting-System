import sqlite3
import json
import requests
from datetime import datetime

# Firebase Realtime Database URL
FIREBASE_URL = "https://student-concern-portal-default-rtdb.firebaseio.com/"

def export_sqlite_data():
    """Export all data from SQLite database"""
    conn = sqlite3.connect('university_issues.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {}
    
    # Export users
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    data['users'] = {}
    for user in users:
        user_id = f"user_{user['id']}"
        data['users'][user_id] = {
            'username': user['username'],
            'password': user['password'],  # Keep hashed password
            'role': user['role'],
            'created_at': datetime.now().isoformat(),
            'sqlite_id': user['id']
        }
    
    # Export issues
    cursor.execute('SELECT * FROM issues')
    issues = cursor.fetchall()
    data['issues'] = {}
    for issue in issues:
        issue_id = f"issue_{issue['id']}"
        data['issues'][issue_id] = {
            'student_id': f"user_{issue['student_id']}",  # Reference to user
            'subject': issue['subject'],
            'category': issue['category'],
            'message': issue['message'],
            'status': issue['status'],
            'response': issue['response'] or '',
            'created_at': issue['created_at'] or datetime.now().isoformat(),
            'sqlite_id': issue['id']
        }
    
    conn.close()
    
    # Save to JSON file for backup
    with open('sqlite_backup.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(data['users'])} users and {len(data['issues'])} issues")
    return data

def upload_to_firebase(data):
    """Upload data to Firebase Realtime Database using REST API"""
    try:
        # Upload users
        users_url = f"{FIREBASE_URL}users.json"
        users_response = requests.put(users_url, json=data['users'])
        
        if users_response.status_code == 200:
            print(f"✅ Successfully uploaded {len(data['users'])} users to Firebase")
        else:
            print(f"❌ Failed to upload users: {users_response.status_code}")
            return False
        
        # Upload issues
        issues_url = f"{FIREBASE_URL}issues.json"
        issues_response = requests.put(issues_url, json=data['issues'])
        
        if issues_response.status_code == 200:
            print(f"✅ Successfully uploaded {len(data['issues'])} issues to Firebase")
        else:
            print(f"❌ Failed to upload issues: {issues_response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading to Firebase: {e}")
        return False

def verify_firebase_data():
    """Verify data was uploaded correctly"""
    try:
        # Check users
        users_url = f"{FIREBASE_URL}users.json"
        users_response = requests.get(users_url)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            if users_data:
                print(f"✅ Verified: {len(users_data)} users in Firebase")
            else:
                print("⚠️ No users found in Firebase")
        
        # Check issues
        issues_url = f"{FIREBASE_URL}issues.json"
        issues_response = requests.get(issues_url)
        
        if issues_response.status_code == 200:
            issues_data = issues_response.json()
            if issues_data:
                print(f"✅ Verified: {len(issues_data)} issues in Firebase")
            else:
                print("⚠️ No issues found in Firebase")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying Firebase data: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to Firebase Realtime Database migration...")
    print("=" * 60)
    print(f"Firebase URL: {FIREBASE_URL}")
    print()
    
    # Step 1: Export data from SQLite
    print("Step 1: Exporting data from SQLite...")
    data = export_sqlite_data()
    print()
    
    # Step 2: Upload to Firebase
    print("Step 2: Uploading to Firebase Realtime Database...")
    success = upload_to_firebase(data)
    print()
    
    if success:
        # Step 3: Verify migration
        print("Step 3: Verifying migration...")
        verify_firebase_data()
        
        print("\n🎉 Migration completed successfully!")
        print("\n📊 Migration Summary:")
        print(f"  • Users migrated: {len(data['users'])}")
        print(f"  • Issues migrated: {len(data['issues'])}")
        print(f"  • Firebase URL: {FIREBASE_URL}")
        print(f"  • Backup file: sqlite_backup.json")
        
        print("\n🔗 You can view your data at:")
        print(f"  • Users: {FIREBASE_URL}users.json")
        print(f"  • Issues: {FIREBASE_URL}issues.json")
        
        print("\n✅ Next steps:")
        print("1. Update main.py to use app_firebase_realtime.py")
        print("2. Test the application with Firebase backend")
        print("3. Your original SQLite data is safely backed up")
        
    else:
        print("\n❌ Migration failed. Please check the errors above.")

if __name__ == '__main__':
    main()
