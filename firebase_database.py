from firebase_config import firebase_config
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from google.cloud.firestore import Query

class FirebaseDatabase:
    def __init__(self):
        self.db = firebase_config.get_db()
    
    # User Management Functions
    def create_user(self, username, password, role):
        """Create a new user in Firebase"""
        try:
            # Check if user already exists
            users_ref = self.db.collection('users')
            existing_user = users_ref.where('username', '==', username).limit(1).get()
            
            if existing_user:
                return None, "User already exists"
            
            # Create new user
            user_data = {
                'username': username,
                'password': generate_password_hash(password),
                'role': role,
                'created_at': datetime.now()
            }
            
            doc_ref = users_ref.add(user_data)
            return doc_ref[1].id, "User created successfully"
            
        except Exception as e:
            return None, f"Error creating user: {str(e)}"
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            users_ref = self.db.collection('users')
            users = users_ref.where('username', '==', username).limit(1).get()
            
            if users:
                user_doc = users[0]
                user_data = user_doc.to_dict()
                user_data['id'] = user_doc.id
                return user_data
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user_doc = self.db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                user_data['id'] = user_doc.id
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
            users_ref = self.db.collection('users')
            users = users_ref.order_by('username').get()
            
            user_list = []
            for user_doc in users:
                user_data = user_doc.to_dict()
                user_data['id'] = user_doc.id
                user_list.append(user_data)
            
            return user_list
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def update_user_password(self, username, new_password):
        """Update user password"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return False, "User not found"
            
            hashed_password = generate_password_hash(new_password)
            self.db.collection('users').document(user['id']).update({
                'password': hashed_password,
                'updated_at': datetime.now()
            })
            
            return True, "Password updated successfully"
            
        except Exception as e:
            return False, f"Error updating password: {str(e)}"
    
    # Issue Management Functions
    def create_issue(self, student_id, subject, category, message):
        """Create a new issue"""
        try:
            issue_data = {
                'student_id': student_id,
                'subject': subject,
                'category': category,
                'message': message,
                'status': 'pending',
                'response': '',
                'created_at': datetime.now()
            }
            
            doc_ref = self.db.collection('issues').add(issue_data)
            return doc_ref[1].id, "Issue created successfully"
            
        except Exception as e:
            return None, f"Error creating issue: {str(e)}"
    
    def get_issues_by_student(self, student_id):
        """Get all issues for a specific student"""
        try:
            issues_ref = self.db.collection('issues')
            issues = issues_ref.where('student_id', '==', student_id).order_by('created_at', direction=Query.DESCENDING).get()
            
            issue_list = []
            for issue_doc in issues:
                issue_data = issue_doc.to_dict()
                issue_data['id'] = issue_doc.id
                issue_list.append(issue_data)
            
            return issue_list
            
        except Exception as e:
            print(f"Error getting student issues: {e}")
            return []
    
    def get_all_issues(self):
        """Get all issues"""
        try:
            issues_ref = self.db.collection('issues')
            issues = issues_ref.order_by('created_at', direction=Query.DESCENDING).get()
            
            issue_list = []
            for issue_doc in issues:
                issue_data = issue_doc.to_dict()
                issue_data['id'] = issue_doc.id
                issue_list.append(issue_data)
            
            return issue_list
            
        except Exception as e:
            print(f"Error getting all issues: {e}")
            return []
    
    def get_issue_by_id(self, issue_id):
        """Get issue by ID"""
        try:
            issue_doc = self.db.collection('issues').document(issue_id).get()
            if issue_doc.exists:
                issue_data = issue_doc.to_dict()
                issue_data['id'] = issue_doc.id
                return issue_data
            return None
            
        except Exception as e:
            print(f"Error getting issue by ID: {e}")
            return None
    
    def update_issue_status(self, issue_id, status, response=None):
        """Update issue status and response"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.now()
            }
            
            if response:
                update_data['response'] = response
            
            self.db.collection('issues').document(issue_id).update(update_data)
            return True, "Issue updated successfully"
            
        except Exception as e:
            return False, f"Error updating issue: {str(e)}"
    
    def get_issues_by_status(self, status):
        """Get issues by status"""
        try:
            issues_ref = self.db.collection('issues')
            issues = issues_ref.where('status', '==', status).order_by('created_at', direction=Query.DESCENDING).get()
            
            issue_list = []
            for issue_doc in issues:
                issue_data = issue_doc.to_dict()
                issue_data['id'] = issue_doc.id
                issue_list.append(issue_data)
            
            return issue_list
            
        except Exception as e:
            print(f"Error getting issues by status: {e}")
            return []
    
    def delete_issue(self, issue_id):
        """Delete an issue"""
        try:
            self.db.collection('issues').document(issue_id).delete()
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
firebase_db = FirebaseDatabase()
