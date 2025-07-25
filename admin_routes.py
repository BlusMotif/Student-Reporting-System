from werkzeug.security import generate_password_hash
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash

admin_bp = Blueprint('admin', __name__)

def get_db_connection():
    conn = sqlite3.connect('university_issues.db')
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    from app import parse_datetime
    conn = get_db_connection()
    issues = conn.execute('SELECT issues.*, users.username FROM issues JOIN users ON issues.student_id = users.id ORDER BY issues.created_at DESC').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', issues=issues, parse_datetime=parse_datetime)

@admin_bp.route('/admin/create-subadmin', methods=['GET', 'POST'])
def create_subadmin():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists.', 'danger')
            conn.close()
            return render_template('create_subadmin.html')

        password_hash = generate_password_hash(password)

        conn.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            (username, password_hash, 'subadmin')
        )
        conn.commit()
        conn.close()

        flash('Sub-admin account created successfully.', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('create_subadmin.html')

@admin_bp.route('/admin/resolve-issue/<int:issue_id>', methods=['POST'])
def resolve_issue(issue_id):
    status = request.form.get('status')
    response = request.form.get('response')

    conn = get_db_connection()
    conn.execute(
        'UPDATE issues SET status = ?, response = ? WHERE id = ?',
        (status, response, issue_id)
    )
    conn.commit()
    conn.close()

    flash('Issue updated successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/delete-issue/<int:issue_id>', methods=['POST'])
def admin_delete_issue(issue_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM issues WHERE id = ?', (issue_id,))
    conn.commit()
    conn.close()

    flash('Issue deleted successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    from flask import g
    if not g.user or g.user['role'] not in ['admin', 'subadmin']:
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
    return render_template('admin_settings.html', user=user)

@admin_bp.route('/admin/subadmin-settings', methods=['GET', 'POST'])
def subadmin_settings():
    from flask import g
    if not g.user or g.user['role'] != 'subadmin':
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
            flash('Password updated successfully.', 'success')

    conn.close()
    return render_template('subadmin_settings.html', user=user)
