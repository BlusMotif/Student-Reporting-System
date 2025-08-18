from firebase_realtime_config import firebase_realtime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class FirebaseRealtimeDatabase:
    def __init__(self):
        self.db = firebase_realtime.get_db()
    
    def _generate_id(self):
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    # User Management Functions
    def create_user(self, username, password, role):
        """Create a new user in Firebase Realtime Database"""
        try:
            if not self.db:
                return None, "Database not connected"
            
            # Check if user already exists
            users = self.db.child("users").get()
            if users.val():
                for user_id, user_data in users.val().items():
                    if user_data.get('username') == username:
                        return None, "User already exists"
            
            # Create new user
            user_id = self._generate_id()
            user_data = {
                'username': username,
                'password': generate_password_hash(password),
                'role': role,
                'created_at': datetime.now().isoformat()
            }
            
            self.db.child("users").child(user_id).set(user_data)
            return user_id, "User created successfully"
            
        except Exception as e:
            return None, f"Error creating user: {str(e)}"
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            if not self.db:
                return None
            
            users = self.db.child("users").get()
            if users.val():
                for user_id, user_data in users.val().items():
                    if user_data.get('username') == username:
                        user_data['id'] = user_id
                        return user_data
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            if not self.db:
                return None
            
            user = self.db.child("users").child(user_id).get()
            if user.val():
                user_data = user.val()
                user_data['id'] = user_id
                return user_data
            return None
            
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def verify_password(self, username, password):
        """Verify user password"""
        user = self.get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            return user
        return None
    
    def get_all_users(self):
        """Get all users"""
        try:
            if not self.db:
                return []
            
            users = self.db.child("users").get()
            user_list = []
            
            if users.val():
                for user_id, user_data in users.val().items():
                    user_data['id'] = user_id
                    user_list.append(user_data)
            
            # Sort by username
            user_list.sort(key=lambda x: x.get('username', ''))
            return user_list
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def update_user_password(self, username, new_password):
        """Update user password"""
        try:
            if not self.db:
                return False, "Database not connected"
            
            user = self.get_user_by_username(username)
            if not user:
                return False, "User not found"
            
            hashed_password = generate_password_hash(new_password)
            self.db.child("users").child(user['id']).update({
                'password': hashed_password,
                'updated_at': datetime.now().isoformat()
            })
            
            return True, "Password updated successfully"
            
        except Exception as e:
            return False, f"Error updating password: {str(e)}"
    
    # Issue Management Functions
    def create_issue(self, student_id, subject, category, message):
        """Create a new issue"""
        try:
            if not self.db:
                return None, "Database not connected"
            
            issue_id = self._generate_id()
            issue_data = {
                'student_id': student_id,
                'subject': subject,
                'category': category,
                'message': message,
                'status': 'pending',
                'response': '',
                'created_at': datetime.now().isoformat()
            }
            
            self.db.child("issues").child(issue_id).set(issue_data)
            return issue_id, "Issue created successfully"
            
        except Exception as e:
            return None, f"Error creating issue: {str(e)}"
    
    def get_issues_by_student(self, student_id):
        """Get all issues for a specific student"""
        try:
            if not self.db:
                return []
            
            issues = self.db.child("issues").get()
            issue_list = []
            
            if issues.val():
                for issue_id, issue_data in issues.val().items():
                    if issue_data.get('student_id') == student_id:
                        issue_data['id'] = issue_id
                        issue_list.append(issue_data)
            
            # Sort by created_at (newest first)
            issue_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return issue_list
            
        except Exception as e:
            print(f"Error getting student issues: {e}")
            return []
    
    def get_all_issues(self):
        """Get all issues"""
        try:
            if not self.db:
                return []
            
            issues = self.db.child("issues").get()
            issue_list = []
            
            if issues.val():
                for issue_id, issue_data in issues.val().items():
                    issue_data['id'] = issue_id
                    issue_list.append(issue_data)
            
            # Sort by created_at (newest first)
            issue_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return issue_list
            
        except Exception as e:
            print(f"Error getting all issues: {e}")
            return []
    
    def get_issue_by_id(self, issue_id):
        """Get issue by ID"""
        try:
            if not self.db:
                return None
            
            issue = self.db.child("issues").child(issue_id).get()
            if issue.val():
                issue_data = issue.val()
                issue_data['id'] = issue_id
                return issue_data
            return None
            
        except Exception as e:
            print(f"Error getting issue by ID: {e}")
            return None
    
    def update_issue_status(self, issue_id, status, response=None):
        """Update issue status and response"""
        try:
            if not self.db:
                return False, "Database not connected"
            
            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            if response:
                update_data['response'] = response
            
            self.db.child("issues").child(issue_id).update(update_data)
            return True, "Issue updated successfully"
            
        except Exception as e:
            return False, f"Error updating issue: {str(e)}"
    
    def get_issues_by_status(self, status):
        """Get issues by status"""
        try:
            if not self.db:
                return []
            
            issues = self.db.child("issues").get()
            issue_list = []
            
            if issues.val():
                for issue_id, issue_data in issues.val().items():
                    if issue_data.get('status') == status:
                        issue_data['id'] = issue_id
                        issue_list.append(issue_data)
            
            # Sort by created_at (newest first)
            issue_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return issue_list
            
        except Exception as e:
            print(f"Error getting issues by status: {e}")
            return []
    
    def delete_issue(self, issue_id):
        """Delete an issue"""
        try:
            if not self.db:
                return False, "Database not connected"
            
            self.db.child("issues").child(issue_id).remove()
            return True, "Issue deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting issue: {str(e)}"
    
    # Statistics Functions
    def get_user_count_by_role(self):
        """Get count of users by role"""
        try:
            users = self.get_all_users()
            role_counts = {}
            
            for user in users:
                role = user.get('role', 'unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
            
            return role_counts
            
        except Exception as e:
            print(f"Error getting user count by role: {e}")
            return {}
    
    def get_issue_count_by_status(self):
        """Get count of issues by status"""
        try:
            issues = self.get_all_issues()
            status_counts = {}
            
            for issue in issues:
                status = issue.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return status_counts
            
        except Exception as e:
            print(f"Error getting issue count by status: {e}")
            return {}

# Global Firebase database instance
firebase_realtime_db = FirebaseRealtimeDatabase()
