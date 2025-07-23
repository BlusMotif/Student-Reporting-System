import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db

def parse_datetime(date_string):
    """Parse datetime string from database and return formatted string"""
    if not date_string:
        return 'Unknown date'
    try:
        dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return date_string

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Initialize database
init_db()

# Register the helper function for templates
app.jinja_env.globals['parse_datetime'] = parse_datetime

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()

@app.route('/')
def index():
    if g.user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        error = None
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        
        flash(error, 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if g.user is None:
        return redirect(url_for('login'))
    
    if g.user['role'] == 'admin':
        return redirect(url_for('admin_issues'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/student/dashboard')
def student_dashboard():
    if g.user is None or g.user['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db()
    recent_issues = db.execute(
        'SELECT * FROM issues WHERE student_id = ? ORDER BY created_at DESC LIMIT 5',
        (g.user['id'],)
    ).fetchall()
    
    # Count issues by status
    status_counts = db.execute(
        '''SELECT status, COUNT(*) as count 
           FROM issues WHERE student_id = ? 
           GROUP BY status''',
        (g.user['id'],)
    ).fetchall()
    
    stats = {'pending': 0, 'in_progress': 0, 'resolved': 0}
    for row in status_counts:
        stats[row['status']] = row['count']
    
    return render_template('student_dashboard.html', recent_issues=recent_issues, stats=stats)

@app.route('/submit-issue', methods=['GET', 'POST'])
def submit_issue():
    if g.user is None or g.user['role'] != 'student':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        subject = request.form['subject']
        category = request.form['category']
        message = request.form['message']
        
        error = None
        if not subject:
            error = 'Subject is required.'
        elif not category:
            error = 'Category is required.'
        elif not message:
            error = 'Message is required.'
        
        if error is None:
            db = get_db()
            db.execute(
                '''INSERT INTO issues (student_id, subject, category, message, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (g.user['id'], subject, category, message, 'pending', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()
            flash('Issue submitted successfully!', 'success')
            return redirect(url_for('my_issues'))
        
        flash(error, 'danger')
    
    return render_template('submit_issue.html')

@app.route('/my-issues')
def my_issues():
    if g.user is None or g.user['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db()
    issues = db.execute(
        'SELECT * FROM issues WHERE student_id = ? ORDER BY created_at DESC',
        (g.user['id'],)
    ).fetchall()
    
    return render_template('my_issues.html', issues=issues)

@app.route('/admin/issues')
def admin_issues():
    if g.user is None or g.user['role'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    issues = db.execute(
        '''SELECT i.*, u.username as student_name 
           FROM issues i 
           JOIN users u ON i.student_id = u.id 
           ORDER BY i.created_at DESC'''
    ).fetchall()
    
    return render_template('admin_dashboard.html', issues=issues)

@app.route('/admin/resolve/<int:issue_id>', methods=['POST'])
def resolve_issue(issue_id):
    if g.user is None or g.user['role'] != 'admin':
        return redirect(url_for('login'))
    
    new_status = request.form['status']
    response = request.form.get('response', '')
    
    db = get_db()
    db.execute(
        'UPDATE issues SET status = ?, response = ? WHERE id = ?',
        (new_status, response, issue_id)
    )
    db.commit()
    
    flash(f'Issue status updated to {new_status}!', 'success')
    return redirect(url_for('admin_issues'))

@app.route('/delete-issue/<int:issue_id>', methods=['POST'])
def delete_issue(issue_id):
    if g.user is None:
        return redirect(url_for('login'))
    
    db = get_db()
    
    # Check if the issue belongs to the current user (for students) or if user is admin
    if g.user['role'] == 'student':
        issue = db.execute(
            'SELECT * FROM issues WHERE id = ? AND student_id = ?',
            (issue_id, g.user['id'])
        ).fetchone()
    else:
        # Admin can delete any issue
        issue = db.execute(
            'SELECT * FROM issues WHERE id = ?',
            (issue_id,)
        ).fetchone()
    
    if issue is None:
        flash('Issue not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('my_issues') if g.user['role'] == 'student' else url_for('admin_issues'))
    
    # Delete the issue
    db.execute('DELETE FROM issues WHERE id = ?', (issue_id,))
    db.commit()
    
    flash('Issue deleted successfully!', 'success')
    return redirect(url_for('my_issues') if g.user['role'] == 'student' else url_for('admin_issues'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
