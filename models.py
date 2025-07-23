# This file contains the database schema definitions
# The actual database operations are handled in database.py

DATABASE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'admin'))
);

CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    category TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'resolved')),
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users (id)
);
'''

SAMPLE_DATA = '''
INSERT OR IGNORE INTO users (username, password, role) VALUES 
('admin', 'scrypt:32768:8:1$lLrC3vH4iJjzUU0V$2e65a1b5c0c7c1c5b8e7b3e8f3d5e4c7b0d9c6e2f1a8b5c9d0e3f6a2b7c4d1e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2b5c8d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2b5c8d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2', 'admin'),
('student1', 'scrypt:32768:8:1$lLrC3vH4iJjzUU0V$2e65a1b5c0c7c1c5b8e7b3e8f3d5e4c7b0d9c6e2f1a8b5c9d0e3f6a2b7c4d1e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2b5c8d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2b5c8d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2', 'student'),
('student2', 'scrypt:32768:8:1$lLrC3vH4iJjzUU0V$2e65a1b5c0c7c1c5b8e7b3e8f3d5e4c7b0d9c6e2f1a8b5c9d0e3f6a2b7c4d1e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2b5c8d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2b5c8d1e4f7a0b3c6d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e6f9a2', 'student');
'''
