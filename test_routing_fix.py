"""
Test to verify that the routing BuildError has been fixed
"""

def test_routing_fix():
    print("🔍 Testing Routing Fix for BuildError")
    print("=" * 50)
    
    try:
        from app_firebase_simple import app
        
        # Test with a mock session
        with app.test_client() as client:
            # Set up a mock session for admin user
            with client.session_transaction() as sess:
                sess['username'] = 'admin'
            
            # Test dashboard route
            print("Testing dashboard route...")
            response = client.get('/dashboard')
            print(f"Dashboard response: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Dashboard route working - BuildError fixed!")
                return True
            elif response.status_code == 500:
                print("❌ Still getting 500 error")
                return False
            else:
                print(f"⚠️ Unexpected status code: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == '__main__':
    success = test_routing_fix()
    if success:
        print("\n🎉 Routing issues have been successfully resolved!")
        print("Your Student Report System should now be working properly.")
    else:
        print("\n❌ There may still be some routing issues to resolve.")
