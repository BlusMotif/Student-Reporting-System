import sqlite3

def list_users():
    conn = sqlite3.connect('university_issues.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, role FROM users')
    users = cursor.fetchall()
    conn.close()
    print("Available users:")
    for user in users:
        print(f"Username: {user[0]}, Role: {user[1]}")

if __name__ == '__main__':
    list_users()
