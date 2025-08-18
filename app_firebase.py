import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from firebase_database import firebase_db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# Import admin routes (will need to be updated for Firebase)
# from admin_routes_firebase import admin_bp
# app.register_blueprint(admin_bp)

def parse_datetime(date_obj):
    """Parse datetime object and return formatted string"""
    if not date_obj:
        return 'Unknown date'
    try:
        if isinstance(date_obj, str):
            dt = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        else:
            dt = date_obj
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return str(date_obj)

@app.before_request
def load_logged_in_user():
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        user = firebase_db.get_user_by_username(username)
        if user is None:
            g.user = None
        else:
            g.user = {"id": user["id"], "username": user["username"], "role": user["role"]}

@app.route('/')
def index():
    if g.user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = firebase_db.get_user_by_username(username)
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html')
        
        # Create new user
        user_id, message = firebase_db.create_user(username, password, 'student')
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Registration failed: {message}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        user = firebase_db.verify_password(username, password)
        if user:
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    
    if g.user['role'] == 'admin' or g.user['role'] == 'subadmin':
        # Admin dashboard
        all_issues = firebase_db.get_all_issues()
        pending_issues = firebase_db.get_issues_by_status('pending')
        in_progress_issues = firebase_db.get_issues_by_status('in_progress')
        resolved_issues = firebase_db.get_issues_by_status('resolved')
        
        # Get user info for each issue
        for issue in all_issues:
            student = firebase_db.get_user_by_id(issue['student_id'])
            issue['student_username'] = student['username'] if student else 'Unknown'
            issue['created_at_formatted'] = parse_datetime(issue.get('created_at'))
        
        stats = {
            'total_issues': len(all_issues),
            'pending_issues': len(pending_issues),
            'in_progress_issues': len(in_progress_issues),
            'resolved_issues': len(resolved_issues)
        }
        
        return render_template('admin_dashboard.html', 
                             issues=all_issues, 
                             stats=stats,
                             user=g.user)
    else:
        # Student dashboard
        student_issues = firebase_db.get_issues_by_student(g.user['id'])
        
        # Format dates
        for issue in student_issues:
            issue['created_at_formatted'] = parse_datetime(issue.get('created_at'))
        
        return render_template('student_dashboard.html', 
                             issues=student_issues, 
                             user=g.user)

@app.route('/submit_issue', methods=['GET', 'POST'])
def submit_issue():
    if not g.user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        subject = request.form['subject']
        category = request.form['category']
        message = request.form['message']
        
        if not subject or not category or not message:
            flash('All fields are required.', 'error')
            return render_template('submit_issue.html')
        
        issue_id, result_message = firebase_db.create_issue(g.user['id'], subject, category, message)
        if issue_id:
            flash('Issue submitted successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(f'Failed to submit issue: {result_message}', 'error')
            return render_template('submit_issue.html')
    
    return render_template('submit_issue.html')

@app.route('/issue/<issue_id>')
def view_issue(issue_id):
    if not g.user:
        return redirect(url_for('login'))
    
    issue = firebase_db.get_issue_by_id(issue_id)
    if not issue:
        flash('Issue not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check permissions
    if g.user['role'] not in ['admin', 'subadmin'] and issue['student_id'] != g.user['id']:
        flash('You do not have permission to view this issue.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get student info
    student = firebase_db.get_user_by_id(issue['student_id'])
    issue['student_username'] = student['username'] if student else 'Unknown'
    issue['created_at_formatted'] = parse_datetime(issue.get('created_at'))
    
    return render_template('view_issue.html', issue=issue, user=g.user)

@app.route('/update_issue/<issue_id>', methods=['POST'])
def update_issue(issue_id):
    if not g.user or g.user['role'] not in ['admin', 'subadmin']:
        flash('You do not have permission to update issues.', 'error')
        return redirect(url_for('dashboard'))
    
    status = request.form['status']
    response = request.form.get('response', '')
    
    success, message = firebase_db.update_issue_status(issue_id, status, response)
    if success:
        flash('Issue updated successfully!', 'success')
    else:
        flash(f'Failed to update issue: {message}', 'error')
    
    return redirect(url_for('view_issue', issue_id=issue_id))

@app.route('/users')
def list_users():
    if not g.user or g.user['role'] not in ['admin', 'subadmin']:
        flash('You do not have permission to view users.', 'error')
        return redirect(url_for('dashboard'))
    
    users = firebase_db.get_all_users()
    role_counts = firebase_db.get_user_count_by_role()
    
    return render_template('users_list.html', 
                         users=users, 
                         role_counts=role_counts,
                         user=g.user)

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))
    
    user_details = firebase_db.get_user_by_id(g.user['id'])
    return render_template('profile.html', user_details=user_details)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not g.user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if not current_password or not new_password:
            flash('All fields are required.', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('change_password.html')
        
        # Verify current password
        user = firebase_db.verify_password(g.user['username'], current_password)
        if not user:
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html')
        
        # Update password
        success, message = firebase_db.update_user_password(g.user['username'], new_password)
        if success:
            flash('Password changed successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash(f'Failed to change password: {message}', 'error')
            return render_template('change_password.html')
    
    return render_template('change_password.html')

@app.route('/statistics')
def statistics():
    if not g.user or g.user['role'] not in ['admin', 'subadmin']:
        flash('You do not have permission to view statistics.', 'error')
        return redirect(url_for('dashboard'))
    
    user_stats = firebase_db.get_user_count_by_role()
    issue_stats = firebase_db.get_issue_count_by_status()
    
    return render_template('statistics.html', 
                         user_stats=user_stats,
                         issue_stats=issue_stats,
                         user=g.user)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
