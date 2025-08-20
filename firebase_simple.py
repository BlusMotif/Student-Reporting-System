import os
import requests
import json
import secrets
import string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Firebase Realtime Database URL - configurable via environment variable
FIREBASE_URL = os.environ.get('FIREBASE_URL', "https://csp5-d0355-default-rtdb.firebaseio.com/")

class SimpleFirebaseDB:
    def __init__(self):
        self.base_url = FIREBASE_URL
        print("🔥 Simple Firebase connection initialized!")
    
    def _make_request(self, endpoint, method='GET', data=None):
        """Make HTTP request to Firebase"""
        url = f"{self.base_url}{endpoint}.json"
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'PUT':
                response = requests.put(url, json=data)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'DELETE':
                response = requests.delete(url)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"Firebase request failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"Firebase request error: {e}")
            return None
    
    # User Management
    def get_user_by_username(self, username):
        """Get user by username"""
        users = self._make_request('users')
        if users:
            for user_id, user_data in users.items():
                if user_data.get('username') == username:
                    user_data['id'] = user_id
                    return user_data
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        user = self._make_request(f'users/{user_id}')
        if user:
            user['id'] = user_id
            return user
        return None
    
    def verify_password(self, username, password):
        """Verify user password"""
        user = self.get_user_by_username(username)
        if user and check_password_hash(user.get('password_hash', user.get('password', '')), password):
            return user
        return None
    
    def get_all_users(self):
        """Get all users"""
        users = self._make_request('users')
        user_list = []
        if users:
            for user_id, user_data in users.items():
                user_data['id'] = user_id
                user_list.append(user_data)
        return sorted(user_list, key=lambda x: x.get('username', ''))
    
    def get_user_by_student_id(self, student_id):
        """Get user by student ID"""
        users = self._make_request('users')
        if users:
            for user_id, user_data in users.items():
                if user_data.get('student_id') == student_id:
                    user_data['id'] = user_id
                    return user_data
        return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        users = self._make_request('users')
        if users:
            for user_id, user_data in users.items():
                if user_data.get('email') == email:
                    user_data['id'] = user_id
                    return user_data
        return None
    
    def create_user(self, username, password, role, **additional_data):
        """Create new user with extended information"""
        # Check if user exists
        if self.get_user_by_username(username):
            return None, "User already exists"
        
        # Check if student ID already exists (if provided)
        student_id = additional_data.get('student_id')
        if student_id and self.get_user_by_student_id(student_id):
            return None, "Student ID already exists"
        
        # Check if email already exists (if provided)
        email = additional_data.get('email')
        if email and self.get_user_by_email(email):
            return None, "Email address already exists"
        
        user_data = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'role': role,
            'created_at': datetime.now().isoformat(),
            # Personal Information
            'first_name': additional_data.get('first_name', ''),
            'last_name': additional_data.get('last_name', ''),
            'email': additional_data.get('email', ''),
            'phone': additional_data.get('phone', ''),
            'date_of_birth': additional_data.get('date_of_birth', ''),
            'gender': additional_data.get('gender', ''),
            # Academic Information
            'student_id': additional_data.get('student_id', ''),
            'level': additional_data.get('level', ''),
            'department': additional_data.get('department', ''),
            'program': additional_data.get('program', ''),
            # Additional Information
            'address': additional_data.get('address', ''),
            'emergency_contact_name': additional_data.get('emergency_contact_name', ''),
            'emergency_contact_phone': additional_data.get('emergency_contact_phone', ''),
            # System fields
            'terms_accepted': additional_data.get('terms_accepted', False),
            'profile_complete': True
        }
        
        result = self._make_request('users', 'POST', user_data)
        if result:
            return result.get('name'), "User created successfully"
        return None, "Failed to create user"
    
    def update_user_password(self, username, new_password):
        """Update user password"""
        user = self.get_user_by_username(username)
        if not user:
            return False, "User not found"
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password)
        
        # Get current user data and update password
        user_id = user['id']
        current_user = self.get_user_by_id(user_id)
        if current_user:
            current_user['password'] = hashed_password
            current_user['updated_at'] = datetime.now().isoformat()
            
            result = self._make_request(f'users/{user_id}', 'PUT', current_user)
            if result:
                return True, "Password updated successfully"
        
        return False, "Failed to update password"
    
    def generate_verification_code(self):
        """Generate a 6-digit verification code"""
        import random
        return str(random.randint(100000, 999999))
    
    def store_verification_code(self, user_id, code, purpose='registration'):
        """Store verification code for email verification"""
        verification_data = {
            'user_id': user_id,
            'code': code,
            'purpose': purpose,
            'created_at': datetime.now().isoformat(),
            'used': False,
            'expires_at': (datetime.now() + timedelta(minutes=15)).isoformat()  # 15 min expiry
        }
        
        result = self._make_request('verification_codes', 'POST', verification_data)
        return result.get('name') if result else None
    
    def verify_code(self, code, purpose='registration'):
        """Verify and use a verification code"""
        codes = self._make_request('verification_codes')
        if codes:
            for code_id, code_data in codes.items():
                if (code_data.get('code') == code and 
                    code_data.get('purpose') == purpose and
                    not code_data.get('used', False)):
                    
                    # Check if not expired
                    expires_at = datetime.fromisoformat(code_data['expires_at'])
                    if datetime.now() < expires_at:
                        # Mark as used
                        code_data['used'] = True
                        code_data['used_at'] = datetime.now().isoformat()
                        self._make_request(f'verification_codes/{code_id}', 'PUT', code_data)
                        return code_data['user_id']
        return None
    
    def generate_reset_token(self):
        """Generate a secure reset token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def create_password_reset_token(self, user_id):
        """Create a password reset token for a user"""
        token = self.generate_reset_token()
        expires_at = (datetime.now() + timedelta(hours=1)).isoformat()  # Token expires in 1 hour
        
        reset_data = {
            'user_id': user_id,
            'token': token,
            'expires_at': expires_at,
            'created_at': datetime.now().isoformat(),
            'used': False
        }
        
        result = self._make_request('password_resets', 'POST', reset_data)
        if result:
            return token
        return None
    
    def verify_reset_token(self, token):
        """Verify if a reset token is valid and not expired"""
        resets = self._make_request('password_resets')
        if resets:
            for reset_id, reset_data in resets.items():
                if (reset_data.get('token') == token and 
                    not reset_data.get('used', False)):
                    
                    # Check if token is not expired
                    expires_at = datetime.fromisoformat(reset_data['expires_at'])
                    if datetime.now() < expires_at:
                        return reset_data['user_id'], reset_id
        return None, None
    
    def use_reset_token(self, reset_id):
        """Mark a reset token as used"""
        reset_data = self._make_request(f'password_resets/{reset_id}')
        if reset_data:
            reset_data['used'] = True
            reset_data['used_at'] = datetime.now().isoformat()
            self._make_request(f'password_resets/{reset_id}', 'PUT', reset_data)
            return True
        return False
    
    def reset_user_password(self, user_id, new_password):
        """Reset user password using user ID"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found"
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password)
        
        # Update user password
        user['password'] = hashed_password
        user['updated_at'] = datetime.now().isoformat()
        user['password_reset_at'] = datetime.now().isoformat()
        
        result = self._make_request(f'users/{user_id}', 'PUT', user)
        if result:
            return True, "Password reset successfully"
        
        return False, "Failed to reset password"
    
    def find_user_for_reset(self, contact_info, student_id, method):
        """Find user by email/phone and verify with student ID"""
        users = self._make_request('users')
        if users:
            for user_id, user_data in users.items():
                # Check if contact info matches email or phone based on method
                contact_match = False
                if method == 'email' and user_data.get('email') == contact_info:
                    contact_match = True
                elif method == 'phone' and user_data.get('phone') == contact_info:
                    contact_match = True
                
                # Verify student ID matches
                if contact_match and user_data.get('student_id') == student_id:
                    user_data['id'] = user_id
                    return user_data
        return None
    
    # Issue Management
    def get_all_issues(self):
        """Get all issues"""
        issues = self._make_request('issues')
        issue_list = []
        if issues:
            for issue_id, issue_data in issues.items():
                issue_data['id'] = issue_id
                issue_list.append(issue_data)
        return sorted(issue_list, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_issues_by_student(self, student_id):
        """Get issues by student ID"""
        issues = self.get_all_issues()
        return [issue for issue in issues if issue.get('student_id') == student_id]
    
    def get_issues_by_status(self, status):
        """Get issues by status"""
        issues = self.get_all_issues()
        return [issue for issue in issues if issue.get('status') == status]
    
    def get_issue_by_id(self, issue_id):
        """Get issue by ID"""
        issue = self._make_request(f'issues/{issue_id}')
        if issue:
            issue['id'] = issue_id
            return issue
        return None
    
    def create_issue(self, student_id, subject, category, message):
        """Create new issue"""
        issue_data = {
            'student_id': student_id,
            'subject': subject,
            'category': category,
            'message': message,
            'status': 'pending',
            'response': '',
            'created_at': datetime.now().isoformat()
        }
        
        result = self._make_request('issues', 'POST', issue_data)
        if result:
            return result.get('name'), "Issue created successfully"
        return None, "Failed to create issue"
    
    def update_issue_status(self, issue_id, status, response=None):
        """Update issue status"""
        update_data = {
            'status': status,
            'updated_at': datetime.now().isoformat()
        }
        if response:
            update_data['response'] = response
        
        # Get current issue data
        current_issue = self.get_issue_by_id(issue_id)
        if current_issue:
            current_issue.update(update_data)
            result = self._make_request(f'issues/{issue_id}', 'PUT', current_issue)
            if result:
                return True, "Issue updated successfully"
        return False, "Failed to update issue"
    
    # System Settings Management
    def get_system_settings(self):
        """Get all system settings"""
        settings = self._make_request('system_settings')
        if not settings:
            # Return default settings if none exist
            return self.get_default_system_settings()
        return settings
    
    def get_default_system_settings(self):
        """Get default system settings"""
        return {
            'system_info': {
                'name': 'KTU Student Portal',
                'full_name': 'Koforidua Technical University Student Portal',
                'description': 'Submit and track your academic concerns',
                'contact_email': 'support@ktu.edu.gh',
                'phone': '+233-000-000-000'
            },
            'categories': {
                'academic': {'name': 'Academic', 'description': 'Course content, schedules, lecturer issues'},
                'exams_grades': {'name': 'Exams & Grades', 'description': 'Missing grades, exam timetables, remark requests'},
                'technical': {'name': 'Technical', 'description': 'Portal issues, software problems'},
                'administration': {'name': 'Administration', 'description': 'Registration, ID cards, fee clearance'},
                'facilities': {'name': 'Facilities', 'description': 'Library, labs, study spaces'},
                'welfare': {'name': 'Welfare', 'description': 'Counseling, conflicts, special needs'},
                'other': {'name': 'Other', 'description': 'Any other concerns'}
            },
            'academic_levels': {
                '100': 'Level 100',
                '200': 'Level 200',
                '300': 'Level 300',
                '400': 'Level 400',
                'graduate': 'Graduate',
                'postgraduate': 'Postgraduate'
            },
            'index_prefixes': {
                'CS': 'Computer Science',
                'IT': 'Information Technology',
                'EE': 'Electrical Engineering',
                'ME': 'Mechanical Engineering',
                'CE': 'Civil Engineering',
                'BA': 'Business Administration'
            },
            'email_settings': {
                'from_name': 'KTU Student Portal',
                'from_email': 'noreply@ktu.edu.gh',
                'support_email': 'support@ktu.edu.gh'
            },
            'registration_settings': {
                'require_email_verification': True,
                'allowed_email_domain': '@ktu.edu.gh',
                'min_password_length': 8,
                'require_index_prefix': False
            },
            'notification_messages': {
                'registration_success': 'Registration successful! Please check your email for verification code.',
                'email_verification_required': 'Please verify your email address before logging in.',
                'login_success': 'Login successful!',
                'invalid_credentials': 'Invalid username or password.',
                'access_denied': 'Access denied. Admin privileges required.'
            }
        }
    
    def update_system_settings(self, settings_data):
        """Update system settings"""
        result = self._make_request('system_settings', 'PUT', settings_data)
        return result is not None
    
    def get_setting(self, setting_path):
        """Get a specific setting by path (e.g., 'system_info.name')"""
        settings = self.get_system_settings()
        keys = setting_path.split('.')
        current = settings
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def update_setting(self, setting_path, value):
        """Update a specific setting by path"""
        settings = self.get_system_settings()
        keys = setting_path.split('.')
        current = settings
        
        # Navigate to the parent of the target setting
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Update the target setting
        current[keys[-1]] = value
        
        return self.update_system_settings(settings)
    
    def add_category(self, key, name, description):
        """Add a new concern category"""
        settings = self.get_system_settings()
        if 'categories' not in settings:
            settings['categories'] = {}
        
        settings['categories'][key] = {
            'name': name,
            'description': description
        }
        
        return self.update_system_settings(settings)
    
    def remove_category(self, key):
        """Remove a concern category"""
        settings = self.get_system_settings()
        if 'categories' in settings and key in settings['categories']:
            del settings['categories'][key]
            return self.update_system_settings(settings)
        return False
    
    def add_index_prefix(self, prefix, description):
        """Add a new index number prefix"""
        settings = self.get_system_settings()
        if 'index_prefixes' not in settings:
            settings['index_prefixes'] = {}
        
        settings['index_prefixes'][prefix] = description
        return self.update_system_settings(settings)
    
    def remove_index_prefix(self, prefix):
        """Remove an index number prefix"""
        settings = self.get_system_settings()
        if 'index_prefixes' in settings and prefix in settings['index_prefixes']:
            del settings['index_prefixes'][prefix]
            return self.update_system_settings(settings)
        return False
    
    def initialize_default_settings(self):
        """Initialize system with default settings if none exist"""
        current_settings = self._make_request('system_settings')
        if not current_settings:
            default_settings = self.get_default_system_settings()
            return self.update_system_settings(default_settings)
        return True
    
    # Statistics
    def get_user_count_by_role(self):
        """Get user count by role"""
        users = self.get_all_users()
        role_counts = {}
        for user in users:
            role = user.get('role', 'unknown')
            role_counts[role] = role_counts.get(role, 0) + 1
        return role_counts
    
    def get_issue_count_by_status(self):
        """Get issue count by status"""
        issues = self.get_all_issues()
        status_counts = {}
        for issue in issues:
            status = issue.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts

# Global instance
simple_firebase_db = SimpleFirebaseDB()
