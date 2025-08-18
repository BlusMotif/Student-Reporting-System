import sqlite3
import json
from datetime import datetime
from firebase_config import firebase_config

def export_sqlite_data():
    """Export all data from SQLite database"""
    conn = sqlite3.connect('university_issues.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
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
    
    print(f"Exported {len(data['users'])} users and {len(data['issues'])} issues")
    return data

def migrate_to_firebase(data):
    """Migrate data to Firebase Firestore"""
    db = firebase_config.get_db()
    
    if not db:
        print("Firebase not initialized. Please check your configuration.")
        return False
    
    try:
        # Migrate users
        print("Migrating users...")
        users_ref = db.collection('users')
        
        for user in data['users']:
            # Use the original SQLite ID as document ID for consistency
            doc_ref = users_ref.document(str(user['id']))
            doc_ref.set({
                'username': user['username'],
                'password': user['password'],
                'role': user['role'],
                'created_at': datetime.now(),
                'sqlite_id': user['id']  # Keep reference to original ID
            })
        
        print(f"✅ Migrated {len(data['users'])} users")
        
        # Migrate issues
        print("Migrating issues...")
        issues_ref = db.collection('issues')
        
        for issue in data['issues']:
            doc_ref = issues_ref.document(str(issue['id']))
            doc_ref.set({
                'student_id': str(issue['student_id']),  # Reference to user document
                'subject': issue['subject'],
                'category': issue['category'],
                'message': issue['message'],
                'status': issue['status'],
                'response': issue['response'] or '',
                'created_at': datetime.fromisoformat(issue['created_at'].replace(' ', 'T')) if issue['created_at'] else datetime.now(),
                'sqlite_id': issue['id']
            })
        
        print(f"✅ Migrated {len(data['issues'])} issues")
        
        # Create indexes for better query performance
        print("Creating indexes...")
        # Note: Firestore indexes are usually created through the Firebase Console
        # or using the Firebase CLI, but we can document the needed indexes here
        
        print("✅ Migration completed successfully!")
        print("\nRecommended Firestore indexes to create:")
        print("1. users collection: index on 'username' (ascending)")
        print("2. users collection: index on 'role' (ascending)")
        print("3. issues collection: index on 'student_id' (ascending)")
        print("4. issues collection: index on 'status' (ascending)")
        print("5. issues collection: index on 'created_at' (descending)")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to Firebase migration...")
    print("=" * 50)
    
    # Step 1: Export data from SQLite
    print("Step 1: Exporting data from SQLite...")
    data = export_sqlite_data()
    
    # Step 2: Migrate to Firebase
    print("\nStep 2: Migrating to Firebase...")
    success = migrate_to_firebase(data)
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("Next steps:")
        print("1. Update your Flask app to use Firebase")
        print("2. Test the application thoroughly")
        print("3. Create the recommended Firestore indexes")
        print("4. Update authentication to use Firebase Auth (optional)")
    else:
        print("\n❌ Migration failed. Please check the errors above.")

if __name__ == '__main__':
    main()
