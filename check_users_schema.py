import sqlite3

def check_schema():
    conn = sqlite3.connect('university_issues.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
    schema = cursor.fetchone()
    conn.close()
    print("Users table schema:")
    print(schema[0] if schema else "No schema found")

if __name__ == '__main__':
    check_schema()
