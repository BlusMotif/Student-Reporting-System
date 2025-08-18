import sqlite3
import json
from datetime import datetime
from firebase_realtime_database import firebase_realtime_db

def export_sqlite_data():
    """Export all data from SQLite database"""
    conn = sqlite3.connect('university_issues.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {}
    
    # Export users
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    data['users'] = []
    for user in users:
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'password': user['password'],  # Keep hashed password
            'role': user['role']
        }
        data['users'].append(user_data)
    
    # Export issues
    cursor.execute('SELECT * FROM issues')
    issues = cursor.fetchall()
    data['issues'] = []
    for issue in issues:
        issue_data = {
            'id': issue['id'],
            'student_id': issue['student_id'],
            'subject': issue['subject'],
            'category': issue['category'],
            'message': issue['message'],
            'status': issue['status'],
            'response': issue['response'],
            'created_at': issue['created_at']
        }
        data['issues'].append(issue_data)
    
    conn.close()
    
    # Save to JSON file for backup
    with open('sqlite_backup.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(data['users'])} users and {len(data['issues'])} issues")
    return data

def migrate_to_firebase_realtime(data):
    """Migrate data to Firebase Realtime Database"""
    db = firebase_realtime_db.db
    
    if not db:
        print("❌ Firebase not connected. Please check your configuration.")
        return False
    
    try:
        print("🔥 Starting migration to Firebase Realtime Database...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("🗑️ Clearing existing data...")
        db.child("users").remove()
        db.child("issues").remove()
        
        # Migrate users
        print("👥 Migrating users...")
        users_data = {}
        user_id_mapping = {}  # Map old SQLite IDs to new Firebase IDs
        
        for user in data['users']:
            # Use SQLite ID as Firebase key for consistency
            firebase_user_id = f"user_{user['id']}"
            user_id_mapping[user['id']] = firebase_user_id
            
            users_data[firebase_user_id] = {
                'username': user['username'],
                'password': user['password'],
                'role': user['role'],
                'created_at': datetime.now().isoformat(),
                'sqlite_id': user['id']
            }
        
        # Batch write users
        db.child("users").set(users_data)
        print(f"✅ Migrated {len(users_data)} users")
        
        # Migrate issues
        print("📋 Migrating issues...")
        issues_data = {}
        
        for issue in data['issues']:
            firebase_issue_id = f"issue_{issue['id']}"
            # Map student_id to new Firebase user ID
            firebase_student_id = user_id_mapping.get(issue['student_id'], f"user_{issue['student_id']}")
            
            issues_data[firebase_issue_id] = {
                'student_id': firebase_student_id,
                'subject': issue['subject'],
                'category': issue['category'],
                'message': issue['message'],
                'status': issue['status'],
                'response': issue['response'] or '',
                'created_at': issue['created_at'] or datetime.now().isoformat(),
                'sqlite_id': issue['id']
            }
        
        # Batch write issues
        db.child("issues").set(issues_data)
        print(f"✅ Migrated {len(issues_data)} issues")
        
        print("✅ Migration completed successfully!")
        print("\n📊 Migration Summary:")
        print(f"  • Users: {len(users_data)}")
        print(f"  • Issues: {len(issues_data)}")
        print(f"  • Database URL: https://student-concern-portal-default-rtdb.firebaseio.com/")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        # Test user retrieval
        users = firebase_realtime_db.get_all_users()
        print(f"✅ Found {len(users)} users in Firebase")
        
        # Test issue retrieval
        issues = firebase_realtime_db.get_all_issues()
        print(f"✅ Found {len(issues)} issues in Firebase")
        
        # Test user authentication
        admin_user = firebase_realtime_db.get_user_by_username('admin')
        if admin_user:
            print("✅ Admin user found and accessible")
        
        print("✅ Migration verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to Firebase Realtime Database migration...")
    print("=" * 60)
    
    # Step 1: Export data from SQLite
    print("Step 1: Exporting data from SQLite...")
    data = export_sqlite_data()
    
    # Step 2: Migrate to Firebase
    print("\nStep 2: Migrating to Firebase Realtime Database...")
    success = migrate_to_firebase_realtime(data)
    
    if success:
        # Step 3: Verify migration
        verify_success = verify_migration()
        
        if verify_success:
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. ✅ Your data is now in Firebase Realtime Database")
            print("2. ✅ Use app_firebase_realtime.py as your new Flask app")
            print("3. ✅ Test the application thoroughly")
            print("4. ✅ Your original SQLite data is backed up in sqlite_backup.json")
        else:
            print("\n⚠️ Migration completed but verification failed. Please check manually.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")

if __name__ == '__main__':
    main()
