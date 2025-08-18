import traceback
from flask import Flask
from firebase_simple import simple_firebase_db

def debug_dashboard_error():
    """Debug the 500 error occurring in dashboard"""
    print("🔍 Debugging Dashboard 500 Error...")
    print("=" * 50)
    
    try:
        # Test Firebase connection
        print("1. Testing Firebase connection...")
        users = simple_firebase_db.get_all_users()
        print(f"   ✅ Firebase working - {len(users)} users found")
        
        # Test issue retrieval
        print("2. Testing issue retrieval...")
        all_issues = simple_firebase_db.get_all_issues()
        print(f"   ✅ Issues retrieved - {len(all_issues)} issues found")
        
        # Test specific issue operations
        print("3. Testing issue operations...")
        pending_issues = simple_firebase_db.get_issues_by_status('pending')
        in_progress_issues = simple_firebase_db.get_issues_by_status('in_progress')
        resolved_issues = simple_firebase_db.get_issues_by_status('resolved')
        
        print(f"   ✅ Pending: {len(pending_issues)}")
        print(f"   ✅ In Progress: {len(in_progress_issues)}")
        print(f"   ✅ Resolved: {len(resolved_issues)}")
        
        # Test user lookup for issues
        print("4. Testing user lookup for issues...")
        if all_issues:
            test_issue = all_issues[0]
            student = simple_firebase_db.get_user_by_id(test_issue['student_id'])
            if student:
                print(f"   ✅ User lookup working - Found: {student['username']}")
            else:
                print(f"   ❌ User lookup failed for student_id: {test_issue['student_id']}")
                return False
        
        # Test Flask app import
        print("5. Testing Flask app...")
        from app_firebase_simple import app
        print("   ✅ Flask app imported successfully")
        
        # Test dashboard route with mock session
        print("6. Testing dashboard route...")
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = 'admin'
            
            response = client.get('/dashboard')
            print(f"   Dashboard response status: {response.status_code}")
            
            if response.status_code == 500:
                print("   ❌ 500 Error detected in dashboard")
                return False
            else:
                print("   ✅ Dashboard working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = debug_dashboard_error()
    if not success:
        print("\n🔧 Issue found - will need to fix the dashboard error")
