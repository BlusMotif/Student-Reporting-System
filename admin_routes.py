from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from firebase_simple import simple_firebase_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    from app_firebase_fixed import parse_datetime
    
    # Check authorization - both subadmin and supaadmin can access
    if not g.user or g.user['role'] not in ['subadmin', 'supaadmin']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    # Get all issues for dashboard
    issues = simple_firebase_db.get_all_issues()
    
    # Add username to each issue
    for issue in issues:
        user = simple_firebase_db.get_user_by_id(issue['student_id'])
        issue['username'] = user['username'] if user else 'Unknown'
    
    return render_template('admin_dashboard.html', issues=issues, parse_datetime=parse_datetime)

@admin_bp.route('/admin/create-subadmin', methods=['GET', 'POST'])
def create_subadmin():
    # Only Supa Admin can create sub-admins
    if not g.user or g.user['role'] != 'supaadmin':
        flash('Access denied. Supa Admin privileges required.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        # Validate KTU institutional email
        if not email.endswith('@ktu.edu.gh'):
            flash('Email must be a KTU institutional email (@ktu.edu.gh)', 'error')
            return render_template('create_subadmin.html')

        # Create sub-admin user
        user_id, message = simple_firebase_db.create_user(
            username, password, 'subadmin',
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        if user_id:
            flash('Sub-admin account created successfully.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash(f'Failed to create sub-admin: {message}', 'error')

    return render_template('create_subadmin.html')

@admin_bp.route('/admin/resolve-issue/<string:issue_id>', methods=['POST'])
def resolve_issue(issue_id):
    # Only Sub Admin can resolve issues (Supa Admin manages system settings only)
    if not g.user or g.user['role'] != 'subadmin':
        flash('Access denied. Sub Admin privileges required for issue management.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    status = request.form.get('status')
    response = request.form.get('response')

    success, message = simple_firebase_db.update_issue_status(issue_id, status, response)
    
    if success:
        flash('Issue updated successfully.', 'success')
    else:
        flash(f'Failed to update issue: {message}', 'error')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/delete-issue/<string:issue_id>', methods=['POST'])
def admin_delete_issue(issue_id):
    # Only Sub Admin can delete issues
    if not g.user or g.user['role'] != 'subadmin':
        flash('Access denied. Sub Admin privileges required for issue management.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    # Delete from Firebase
    issue = simple_firebase_db.get_issue_by_id(issue_id)
    if issue:
        # Mark as deleted rather than actually delete
        success, message = simple_firebase_db.update_issue_status(issue_id, 'deleted', 'Issue deleted by admin')
        if success:
            flash('Issue deleted successfully.', 'success')
        else:
            flash(f'Failed to delete issue: {message}', 'error')
    else:
        flash('Issue not found.', 'error')

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    # Only Supa Admin can access system settings
    if not g.user or g.user['role'] != 'supaadmin':
        flash('Access denied. Supa Admin privileges required for system settings.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    # Get current user data
    user = simple_firebase_db.get_user_by_username(g.user['username'])
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        error = None
        if password:
            if password != password_confirm:
                error = 'Passwords do not match.'
            else:
                success, message = simple_firebase_db.update_user_password(g.user['username'], password)
                if not success:
                    error = f'Failed to update password: {message}'

        if error:
            flash(error, 'error')
        else:
            flash('Settings updated successfully.', 'success')

    return render_template('admin_settings.html', user=user)

@admin_bp.route('/admin/subadmin-settings', methods=['GET', 'POST'])
def subadmin_settings():
    # Only Sub Admin can access their settings
    if not g.user or g.user['role'] != 'subadmin':
        flash('Access denied. Sub Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    # Get current user data
    user = simple_firebase_db.get_user_by_username(g.user['username'])

    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        error = None
        if password:
            if password != password_confirm:
                error = 'Passwords do not match.'
            else:
                success, message = simple_firebase_db.update_user_password(g.user['username'], password)
                if not success:
                    error = f'Failed to update password: {message}'

        if error:
            flash(error, 'error')
        else:
            flash('Password updated successfully.', 'success')

    return render_template('subadmin_settings.html', user=user)

@admin_bp.route('/admin/system-settings', methods=['GET', 'POST'])
def system_settings():
    # Only Supa Admin can manage system-wide settings
    if not g.user or g.user['role'] != 'supaadmin':
        flash('Access denied. Supa Admin privileges required.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    # This will manage categories, index prefixes, and other dynamic settings
    return render_template('system_settings.html')