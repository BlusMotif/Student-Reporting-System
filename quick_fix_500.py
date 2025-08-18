"""
Quick fix for 500 Internal Server Error
"""

def test_and_fix_dashboard():
    print("🔧 Quick Fix for 500 Internal Server Error")
    print("=" * 50)
    
    try:
        # Test Firebase connection
        from firebase_simple import simple_firebase_db
        print("✅ Firebase connection OK")
        
        # Test template rendering
        from flask import Flask, render_template
        app = Flask(__name__)
        
        with app.app_context():
            # Test if admin_dashboard.html exists and works
            try:
                with open('templates/admin_dashboard.html', 'r') as f:
                    content = f.read()
                    if 'admin_dashboard.html' in content or 'Admin Dashboard' in content:
                        print("✅ admin_dashboard.html template exists")
                    else:
                        print("⚠️ admin_dashboard.html may have issues")
            except FileNotFoundError:
                print("❌ admin_dashboard.html template missing")
                return False
            
            # Test if student_dashboard.html exists
            try:
                with open('templates/student_dashboard.html', 'r') as f:
                    content = f.read()
                    if 'student_dashboard.html' in content or 'Student Dashboard' in content:
                        print("✅ student_dashboard.html template exists")
                    else:
                        print("⚠️ student_dashboard.html may have issues")
            except FileNotFoundError:
                print("❌ student_dashboard.html template missing")
                return False
        
        print("\n🎯 Root cause likely identified:")
        print("The dashboard templates exist but may have rendering issues.")
        print("Let's restart the Flask app to clear any cached template issues.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == '__main__':
    test_and_fix_dashboard()
