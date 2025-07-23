import sqlite3
import click
from flask import current_app, g
from werkzeug.security import generate_password_hash
from models import DATABASE_SCHEMA

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('university_issues.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with tables and sample users."""
    db = sqlite3.connect('university_issues.db')
    db.executescript(DATABASE_SCHEMA)
    
    # Create default admin and sample student accounts with proper password hashing
    admin_password = generate_password_hash('admin123')
    student1_password = generate_password_hash('student123')
    student2_password = generate_password_hash('student123')
    
    try:
        db.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('admin', admin_password, 'admin')
        )
        db.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('student1', student1_password, 'student')
        )
        db.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('student2', student2_password, 'student')
        )
        db.commit()
    except sqlite3.IntegrityError:
        # Users already exist
        pass
    
    db.close()
