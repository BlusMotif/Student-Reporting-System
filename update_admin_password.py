import sqlite3
from werkzeug.security import generate_password_hash

def update_admin_password():
    conn = sqlite3.connect('university_issues.db')
    cursor = conn.cursor()
    new_password_hash = generate_password_hash("adminpass")
    cursor.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_password_hash,))
    conn.commit()
    conn.close()
    print("Admin password updated to 'adminpass'")

if __name__ == '__main__':
    update_admin_password()
