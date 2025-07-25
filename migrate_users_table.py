import sqlite3

def migrate_users_table():
    conn = sqlite3.connect('university_issues.db')
    cursor = conn.cursor()

    # Create new users table with corrected CHECK constraint including 'subadmin'
    cursor.execute('''
    CREATE TABLE users_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('student', 'admin', 'subadmin'))
    )
    ''')

    # Copy data from old users table to new users table
    cursor.execute('''
    INSERT INTO users_new (id, username, password, role)
    SELECT id, username, password, role FROM users
    ''')

    # Drop old users table
    cursor.execute('DROP TABLE users')

    # Rename new users table to users
    cursor.execute('ALTER TABLE users_new RENAME TO users')

    conn.commit()
    conn.close()
    print("Users table migrated successfully with updated role constraint.")

if __name__ == '__main__':
    migrate_users_table()
