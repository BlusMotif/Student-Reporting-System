import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

from admin_routes import admin_bp
app.register_blueprint(admin_bp)

def parse_datetime(date_string):
    """Parse datetime string from database and return formatted string"""
    if not date_string:
        return 'Unknown date'
    try:
        dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return date_string

def get_db_connection():
    conn = sqlite3.connect('university_issues.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def load_logged_in_user():
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user is None:
            g.user = None
        else:
            g.user = {"username": user["username"], "role": user["role"]}

@app.route('/')
def index():
    if g.user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        role = 'student'  # default role for self-registration

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists.', 'danger')
            conn.close()
            return render_template('register.html')

        password_hash = generate_password_hash(password)

        conn.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            (username, password_hash, role)
        )
        conn.commit()
        conn.close()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        error = None
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['username'] = username
            return redirect(url_for('dashboard'))

        flash(error, 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if g.user is None:
        return redirect(url_for('login'))

    if g.user['role'] == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif g.user['role'] == 'subadmin':
        return redirect(url_for('admin.admin_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('university_issues.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/student/dashboard')
def student_dashboard():
    if g.user is None or g.user['role'] != 'student':
        return redirect(url_for('login'))
    conn = get_db_connection()
    username = g.user['username']
    issues = conn.execute('SELECT * FROM issues WHERE student_id = (SELECT id FROM users WHERE username = ?)', (username,)).fetchall()
    conn.close()

    stats = {
        'pending': sum(1 for issue in issues if issue['status'] == 'pending'),
        'in_progress': sum(1 for issue in issues if issue['status'] == 'in_progress'),
        'resolved': sum(1 for issue in issues if issue['status'] == 'resolved'),
    }
    recent_issues = issues[-5:] if len(issues) > 5 else issues
    return render_template('student_dashboard.html', recent_issues=recent_issues, stats=stats, parse_datetime=parse_datetime)

@app.route('/submit_issue', methods=['GET', 'POST'])
def submit_issue():
    if g.user is None or g.user['role'] != 'student':
        return redirect(url_for('login'))

    if request.method == 'POST':
        subject = request.form['subject']
        category = request.form['category']
        message = request.form['message']
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        student_username = g.user['username']

        conn = get_db_connection()
        # Debug: print users table contents
        users_data = conn.execute('SELECT * FROM users').fetchall()
        print("Users table contents:")
        for user in users_data:
            print(dict(user))

        student_id_row = conn.execute('SELECT id FROM users WHERE username = ?', (student_username,)).fetchone()
        if student_id_row is None:
            flash('User not found.', 'danger')
            conn.close()
            return redirect(url_for('submit_issue'))
        student_id = student_id_row['id']

        conn.execute(
            'INSERT INTO issues (subject, category, message, status, created_at, student_id) VALUES (?, ?, ?, ?, ?, ?)',
            (subject, category, message, 'pending', created_at, student_id)
        )
        conn.commit()
        conn.close()

        flash('Issue submitted successfully.', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('submit_issue.html')

@app.route('/my_issues')
def my_issues():
    if g.user is None or g.user['role'] != 'student':
        return redirect(url_for('login'))

    conn = get_db_connection()
    username = g.user['username']
    issues = conn.execute('SELECT * FROM issues WHERE student_id = (SELECT id FROM users WHERE username = ?)', (username,)).fetchall()
    conn.close()

    return render_template('my_issues.html', issues=issues, parse_datetime=parse_datetime)

@app.route('/delete_issue/<int:issue_id>', methods=['POST'])
def delete_issue(issue_id):
    if g.user is None or g.user['role'] != 'student':
        return redirect(url_for('login'))

    conn = get_db_connection()
    issue = conn.execute('SELECT * FROM issues WHERE id = ? AND student_id = (SELECT id FROM users WHERE username = ?)', (issue_id, g.user['username'])).fetchone()
    if issue:
        conn.execute('DELETE FROM issues WHERE id = ?', (issue_id,))
        conn.commit()
        flash('Issue deleted successfully.', 'success')
    else:
        flash('Issue not found or unauthorized.', 'danger')
    conn.close()
    return redirect(url_for('my_issues'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if g.user is None:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (g.user['username'],)).fetchone()

    if request.method == 'POST':
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        error = None
        if password:
            if password != password_confirm:
                error = 'Passwords do not match.'
            else:
                from werkzeug.security import generate_password_hash
                password_hash = generate_password_hash(password)
                conn.execute('UPDATE users SET password = ? WHERE username = ?', (password_hash, g.user['username']))
                conn.commit()

        if error:
            flash(error, 'danger')
        else:
            flash('Settings updated successfully.', 'success')

    conn.close()
    return render_template('settings.html', user=user)

from flask import g

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_reset_email(email, token):
    """Send password reset email using Outlook SMTP with proper authentication."""
    try:
        msg = MIMEMultipart()
        msg['From'] = 'blusmotif1@outlook.com'
        msg['To'] = email
        msg['Subject'] = 'Password Reset Request - Student Report System'

        body = f'''Hello,

You have requested to reset your password for the Student Report System.

Please click the following link to reset your password:
http://127.0.0.1:5000/reset_password/{token}

If you did not request this password reset, please ignore this email.

Best regards,
Student Report System Team'''
        
        msg.attach(MIMEText(body, 'plain'))

        # Use environment variables for security
        email_address = os.environ.get('SMTP_EMAIL', 'blusmotif1@outlook.com')
        email_password = os.environ.get('SMTP_PASSWORD')  # Use app password here
        
        if not email_password:
            # For development only - you should use environment variables
            print("Warning: SMTP_PASSWORD not set in environment variables")
            return False

        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
            
        print(f"Password reset email sent successfully to {email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email_or_phone = request.form['email'] if request.form['reset_method'] == 'email' else request.form['phone']
        student_id = request.form['student_id']
        
        # Generate a token (this is a placeholder, implement your own token generation)
        token = "generated_token"  # Replace with actual token generation logic
        
        send_reset_email(email_or_phone, token)
        flash('Reset link has been sent!', 'success')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # This would be implemented with proper token validation
    return render_template('reset_password.html', token=token)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
