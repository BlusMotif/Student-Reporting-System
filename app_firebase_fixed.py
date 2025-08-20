import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from firebase_simple import simple_firebase_db
from notification_service import notification_service

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

def parse_datetime(date_string):
    """Parse datetime string and return formatted string"""
    if not date_string:
        return 'Unknown date'
    try:
        if 'T' in date_string:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return str(date_string)

@app.before_request
def load_logged_in_user():
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        user = simple_firebase_db.get_user_by_username(username)
        if user is None:
            g.user = None
        else:
            g.user = {"id": user["id"], "username": user["username"], "role": user["role"]}
    
    # Load system settings for all templates
    g.dynamic_settings = simple_firebase_db.get_system_settings()
    
    # Initialize default settings if none exist (first time setup)
    if not g.dynamic_settings or not g.dynamic_settings.get('system_info'):
        simple_firebase_db.initialize_default_settings()
        g.dynamic_settings = simple_firebase_db.get_system_settings()

@app.route('/')
def index():
    if g.user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Basic required fields for CS Department
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Personal information
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        
        # CS Department academic information
        student_id = request.form.get('student_id', '').strip().upper()  # Index number
        level = request.form.get('level', '')
        gender = request.form.get('gender', '')
        
        # Validation for CS Department
        if not all([username, password, first_name, last_name, email, student_id, level, gender]):
            flash('All required fields must be filled.', 'error')
            return render_template('register.html')
        
        # Get dynamic email domain from settings
        allowed_domain = simple_firebase_db.get_setting('registration_settings.allowed_email_domain') or '@ktu.edu.gh'
        if not email.endswith(allowed_domain):
            flash(f'Email must be from the institutional domain ({allowed_domain})', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Get dynamic password length from settings
        min_length = simple_firebase_db.get_setting('registration_settings.min_password_length') or 8
        if len(password) < min_length:
            flash(f'Password must be at least {min_length} characters long.', 'error')
            return render_template('register.html')
        
        if gender not in ['M', 'F']:
            flash('Gender must be M (Male) or F (Female)', 'error')
            return render_template('register.html')
        
        # Prepare student registration data
        additional_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'student_id': student_id,
            'level': level,
            'gender': gender,
            'email_verified': False,  # Email verification required
            'verification_code': None
        }
        
        # Create new student user
        user_id, message = simple_firebase_db.create_user(username, password, 'student', **additional_data)
        if user_id:
            # Generate and send verification code
            verification_code = simple_firebase_db.generate_verification_code()
            simple_firebase_db.store_verification_code(user_id, verification_code, 'registration')
            
            # Send verification email
            success, email_message = notification_service.send_verification_email(
                email, first_name + ' ' + last_name, verification_code
            )
            
            if success:
                success_msg = simple_firebase_db.get_setting('notification_messages.registration_success') or 'Registration successful! Please check your email for verification code.'
                flash(success_msg, 'success')
                return redirect(url_for('verify_email', user_id=user_id))
            else:
                flash('Registration successful but failed to send verification email. Please contact support.', 'warning')
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
        
        user = simple_firebase_db.verify_password(username, password)
        if user:
            session['username'] = user['username']
            success_msg = simple_firebase_db.get_setting('notification_messages.login_success') or 'Login successful!'
            flash(success_msg, 'success')
            return redirect(url_for('dashboard'))
        else:
            error_msg = simple_firebase_db.get_setting('notification_messages.invalid_credentials') or 'Invalid username or password.'
            flash(error_msg, 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        reset_method = request.form.get('reset_method', 'email')
        student_id = request.form.get('student_id', '').strip()
        
        if reset_method == 'email':
            contact_info = request.form.get('email', '').strip()
        else:
            contact_info = request.form.get('phone', '').strip()
        
        if not contact_info or not student_id:
            flash('Please fill in all required fields.', 'error')
            return render_template('forgot_password.html')
        
        # Find user by contact info and verify with student ID
        user = simple_firebase_db.find_user_for_reset(contact_info, student_id, reset_method)
        if not user:
            flash('No account found with the provided information. Please check your details and try again.', 'error')
            return render_template('forgot_password.html')
        
        # Generate reset token
        reset_token = simple_firebase_db.create_password_reset_token(user['id'])
        if reset_token:
            reset_url = url_for('reset_password', token=reset_token, _external=True)
            user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get('username', 'Student')
            
            # Send reset link via email or SMS
            if reset_method == 'email':
                success, message = notification_service.send_password_reset_email(
                    contact_info, user_name, reset_url
                )
                if success:
                    flash('Password reset link has been sent to your email address. Please check your inbox and spam folder.', 'success')
                else:
                    flash(f'Failed to send email: {message}. Please try again or contact IT support.', 'error')
                    return render_template('forgot_password.html')
            else:
                success, message = notification_service.send_password_reset_sms(
                    contact_info, user_name, reset_url
                )
                if success:
                    flash('Password reset link has been sent to your phone via SMS. It may take a few minutes to arrive.', 'success')
                else:
                    flash(f'Failed to send SMS: {message}. Please try again or contact IT support.', 'error')
                    return render_template('forgot_password.html')
            
            return redirect(url_for('login'))
        else:
            flash('Failed to generate reset token. Please try again.', 'error')
            return render_template('forgot_password.html')
    
    return render_template('forgot_password.html')

@app.route('/verify_email/<string:user_id>', methods=['GET', 'POST'])
def verify_email(user_id):
    if request.method == 'POST':
        verification_code = request.form.get('verification_code', '').strip()
        
        if not verification_code:
            flash('Please enter the verification code.', 'error')
            return render_template('verify_email.html', user_id=user_id)
        
        # Verify the code
        verified_user_id = simple_firebase_db.verify_code(verification_code, 'registration')
        
        if verified_user_id == user_id:
            # Mark user as email verified
            user = simple_firebase_db.get_user_by_id(user_id)
            if user:
                user['email_verified'] = True
                user['verified_at'] = datetime.now().isoformat()
                success = simple_firebase_db._make_request(f'users/{user_id}', 'PUT', user)
                
                if success:
                    success_msg = simple_firebase_db.get_setting('notification_messages.email_verified_success') or 'Email verified successfully! You can now log in.'
                    flash(success_msg, 'success')
                    return redirect(url_for('login'))
                else:
                    flash('Failed to update verification status. Please try again.', 'error')
            else:
                flash('User not found.', 'error')
        else:
            flash('Invalid or expired verification code. Please try again.', 'error')
        
        return render_template('verify_email.html', user_id=user_id)
    
    # GET request - show verification form
    user = simple_firebase_db.get_user_by_id(user_id)
    if not user:
        flash('Invalid verification link.', 'error')
        return redirect(url_for('register'))
    
    return render_template('verify_email.html', user_id=user_id, user=user)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verify token
    user_id, reset_id = simple_firebase_db.verify_reset_token(token)
    if not user_id:
        flash('Invalid or expired reset token. Please request a new password reset.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not new_password or not confirm_password:
            flash('Please fill in all required fields.', 'error')
            return render_template('reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('reset_password.html', token=token)
        
        # Reset password
        success, message = simple_firebase_db.reset_user_password(user_id, new_password)
        if success:
            # Mark token as used
            simple_firebase_db.use_reset_token(reset_id)
            flash('Password reset successfully! You can now log in with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Failed to reset password: {message}', 'error')
            return render_template('reset_password.html', token=token)
    
    return render_template('reset_password.html', token=token)

@app.route('/dashboard')
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    
    if g.user['role'] == 'supaadmin' or g.user['role'] == 'subadmin':
        # Admin dashboard - simplified version
        all_issues = simple_firebase_db.get_all_issues()
        pending_issues = simple_firebase_db.get_issues_by_status('pending')
        in_progress_issues = simple_firebase_db.get_issues_by_status('in_progress')
        resolved_issues = simple_firebase_db.get_issues_by_status('resolved')
        
        # Get user info for each issue
        for issue in all_issues:
            student = simple_firebase_db.get_user_by_id(issue['student_id'])
            issue['student_username'] = student['username'] if student else 'Unknown'
            issue['created_at_formatted'] = parse_datetime(issue.get('created_at'))
        
        stats = {
            'total_issues': len(all_issues),
            'pending_issues': len(pending_issues),
            'in_progress_issues': len(in_progress_issues),
            'resolved_issues': len(resolved_issues)
        }
        
        return render_template('dashboard_admin.html', 
                             issues=all_issues, 
                             stats=stats,
                             user=g.user)
    else:
        # Student dashboard - simplified version
        student_issues = simple_firebase_db.get_issues_by_student(g.user['id'])
        
        # Format dates
        for issue in student_issues:
            issue['created_at_formatted'] = parse_datetime(issue.get('created_at'))
        
        return render_template('dashboard_student.html', 
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
            error_msg = g.dynamic_settings.get('notification_messages', {}).get('all_fields_required') if g.dynamic_settings else 'All fields are required.'
            flash(error_msg, 'error')
            return render_template('submit_issue.html')
        
        issue_id, result_message = simple_firebase_db.create_issue(g.user['id'], subject, category, message)
        if issue_id:
            success_msg = g.dynamic_settings.get('notification_messages', {}).get('issue_submitted_success') if g.dynamic_settings else 'Issue submitted successfully!'
            flash(success_msg, 'success')
            return redirect(url_for('dashboard'))
        else:
            error_msg = g.dynamic_settings.get('notification_messages', {}).get('issue_submission_failed') if g.dynamic_settings else f'Failed to submit issue: {result_message}'
            flash(error_msg, 'error')
            return render_template('submit_issue.html')
    
    return render_template('submit_issue.html')

@app.route('/issue/<issue_id>')
def view_issue(issue_id):
    if not g.user:
        return redirect(url_for('login'))
    
    issue = simple_firebase_db.get_issue_by_id(issue_id)
    if not issue:
        flash('Issue not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check permissions
    if g.user['role'] not in ['admin', 'subadmin'] and issue['student_id'] != g.user['id']:
        flash('You do not have permission to view this issue.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get student info
    student = simple_firebase_db.get_user_by_id(issue['student_id'])
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
    
    success, message = simple_firebase_db.update_issue_status(issue_id, status, response)
    if success:
        flash('Issue updated successfully!', 'success')
    else:
        flash(f'Failed to update issue: {message}', 'error')
    
    return redirect(url_for('view_issue', issue_id=issue_id))

@app.route('/users', endpoint='users')
@app.route('/list_users', endpoint='list_users')
def list_users():
    if not g.user or g.user['role'] not in ['admin', 'subadmin']:
        flash('You do not have permission to view users.', 'error')
        return redirect(url_for('dashboard'))
    
    users = simple_firebase_db.get_all_users()
    role_counts = simple_firebase_db.get_user_count_by_role()
    
    return render_template('users_list.html', 
                         users=users, 
                         role_counts=role_counts,
                         user=g.user)

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))
    
    user_details = simple_firebase_db.get_user_by_id(g.user['id'])
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
        user = simple_firebase_db.verify_password(g.user['username'], current_password)
        if not user:
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html')
        
        # Update password
        success, message = simple_firebase_db.update_user_password(g.user['username'], new_password)
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
    
    user_stats = simple_firebase_db.get_user_count_by_role()
    issue_stats = simple_firebase_db.get_issue_count_by_status()
    
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
