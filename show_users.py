import sqlite3

conn = sqlite3.connect('university_issues.db')
cursor = conn.cursor()

cursor.execute('SELECT id, username, role FROM users ORDER BY id')
users = cursor.fetchall()

print("STUDENT REPORT SYSTEM - USER ACCOUNTS")
print("=====================================")
print(f"Total Users: {len(users)}")
print()

for user in users:
    print(f"ID: {user[0]} | Username: {user[1]} | Role: {user[2]}")

print()
cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
role_counts = cursor.fetchall()

print("ROLE SUMMARY:")
for role, count in role_counts:
    print(f"  {role}: {count} users")

conn.close()
