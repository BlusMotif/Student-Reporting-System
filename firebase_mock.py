"""
Mock Firebase implementation for testing and development
This allows the app to run without a real Firebase project initially
"""

import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class MockFirestore:
    def __init__(self):
        self.data_file = 'mock_firestore_data.json'
        self.data = self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {'users': {}, 'issues': {}, 'counters': {'users': 0, 'issues': 0}}
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def collection(self, collection_name):
        return MockCollection(self, collection_name)

class MockCollection:
    def __init__(self, db, collection_name):
        self.db = db
        self.collection_name = collection_name
    
    def document(self, doc_id):
        return MockDocument(self.db, self.collection_name, doc_id)
    
    def add(self, data):
        # Generate new document ID
        counter_key = self.collection_name
        self.db.data['counters'][counter_key] = self.db.data['counters'].get(counter_key, 0) + 1
        doc_id = str(self.db.data['counters'][counter_key])
        
        # Add document
        if self.collection_name not in self.db.data:
            self.db.data[self.collection_name] = {}
        
        self.db.data[self.collection_name][doc_id] = data
        self.db.save_data()
        
        return (None, MockDocument(self.db, self.collection_name, doc_id))
    
    def where(self, field, operator, value):
        return MockQuery(self.db, self.collection_name, field, operator, value)
    
    def order_by(self, field, direction=None):
        return MockQuery(self.db, self.collection_name).order_by(field, direction)
    
    def get(self):
        """Get all documents in collection"""
        if self.collection_name not in self.db.data:
            return []
        
        docs = []
        for doc_id, doc_data in self.db.data[self.collection_name].items():
            docs.append(MockDocumentSnapshot(doc_id, doc_data))
        
        return docs

class MockDocument:
    def __init__(self, db, collection_name, doc_id):
        self.db = db
        self.collection_name = collection_name
        self.doc_id = doc_id
        self.id = doc_id
    
    def set(self, data):
        if self.collection_name not in self.db.data:
            self.db.data[self.collection_name] = {}
        
        self.db.data[self.collection_name][self.doc_id] = data
        self.db.save_data()
    
    def get(self):
        if (self.collection_name in self.db.data and 
            self.doc_id in self.db.data[self.collection_name]):
            return MockDocumentSnapshot(self.doc_id, self.db.data[self.collection_name][self.doc_id])
        return MockDocumentSnapshot(self.doc_id, None)
    
    def update(self, data):
        if (self.collection_name in self.db.data and 
            self.doc_id in self.db.data[self.collection_name]):
            self.db.data[self.collection_name][self.doc_id].update(data)
            self.db.save_data()
    
    def delete(self):
        if (self.collection_name in self.db.data and 
            self.doc_id in self.db.data[self.collection_name]):
            del self.db.data[self.collection_name][self.doc_id]
            self.db.save_data()

class MockDocumentSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self.data = data
        self.exists = data is not None
    
    def to_dict(self):
        return self.data if self.data else {}

class MockQuery:
    def __init__(self, db, collection_name, field=None, operator=None, value=None):
        self.db = db
        self.collection_name = collection_name
        self.field = field
        self.operator = operator
        self.value = value
        self.order_field = None
        self.order_direction = None
        self.limit_count = None
    
    def where(self, field, operator, value):
        return MockQuery(self.db, self.collection_name, field, operator, value)
    
    def order_by(self, field, direction=None):
        self.order_field = field
        self.order_direction = direction
        return self
    
    def limit(self, count):
        self.limit_count = count
        return self
    
    def get(self):
        if self.collection_name not in self.db.data:
            return []
        
        docs = []
        for doc_id, doc_data in self.db.data[self.collection_name].items():
            # Apply where filter
            if self.field and self.operator and self.value is not None:
                if self.operator == '==' and doc_data.get(self.field) != self.value:
                    continue
            
            docs.append(MockDocumentSnapshot(doc_id, doc_data))
        
        # Apply ordering
        if self.order_field:
            reverse = self.order_direction == 'DESCENDING'
            docs.sort(key=lambda x: x.to_dict().get(self.order_field, ''), reverse=reverse)
        
        # Apply limit
        if self.limit_count:
            docs = docs[:self.limit_count]
        
        return docs

class MockFirebaseConfig:
    def __init__(self):
        self.db = MockFirestore()
        print("🔥 Mock Firebase initialized for development!")
    
    def get_db(self):
        return self.db

# Create global instance
mock_firebase_config = MockFirebaseConfig()
