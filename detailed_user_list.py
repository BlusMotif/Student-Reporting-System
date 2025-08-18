import sqlite3

def get_detailed_user_list():
    conn = sqlite3.connect('university_issues.db')
    cursor = conn.cursor()
    
    # Get all users with their details
    cursor.execute('SELECT id, username, role FROM users ORDER BY id')
    users = cursor.fetchall()
    
    print("=" * 70)
    print("STUDENT REPORT SYSTEM - USER ACCOUNTS AND DETAILS")
    print("=" * 70)
    print(f"Total Users: {len(users)}")
    print()
    
    print(f"{'ID':<4} | {'Username':<35} | {'Role':<15}")
    print("-" * 70)
    
    for user in users:
        user_id, username, role = user
        print(f"{user_id:<4} | {username:<35} | {role:<15}")
    
    print("=" * 70)
    
    # Get role summary
    cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
    role_counts = cursor.fetchall()
    
    print("\nROLE SUMMARY:")
    for role, count in role_counts:
        print(f"  {role.capitalize()}: {count} users")
    
    conn.close()

if __name__ == '__main__':
    get_detailed_user_list()
