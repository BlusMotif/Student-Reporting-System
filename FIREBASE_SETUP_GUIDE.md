# Firebase Migration Setup Guide

## Prerequisites

1. **Firebase Project Setup**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project or use an existing one
   - Enable Firestore Database
   - Generate a service account key:
     - Go to Project Settings → Service Accounts
     - Click "Generate new private key"
     - Save the JSON file as `serviceAccountKey.json` in your project root

2. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Update the values in `.env`:
     ```
     FIREBASE_PROJECT_ID=your-actual-firebase-project-id
     GOOGLE_APPLICATION_CREDENTIALS=serviceAccountKey.json
     FLASK_SECRET_KEY=your-secure-secret-key
     FLASK_ENV=development
     ```

## Installation Steps

1. **Install Firebase Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Migration**
   ```bash
   python migrate_to_firebase.py
   ```
   This will:
   - Export all data from SQLite to `sqlite_backup.json`
   - Import all data to Firebase Firestore
   - Create the necessary collections: `users` and `issues`

3. **Update Flask App**
   - The updated `app_firebase.py` uses Firebase instead of SQLite
   - Replace your current `app.py` with `app_firebase.py`

4. **Test the Application**
   ```bash
   python main.py
   ```

## Firebase Collections Structure

### Users Collection
```
users/
  {document_id}/
    username: string
    password: string (hashed)
    role: string (admin|student|subadmin)
    created_at: timestamp
    sqlite_id: number (reference to original ID)
```

### Issues Collection
```
issues/
  {document_id}/
    student_id: string (reference to user document ID)
    subject: string
    category: string
    message: string
    status: string (pending|in_progress|resolved)
    response: string
    created_at: timestamp
    sqlite_id: number (reference to original ID)
```

## Recommended Firestore Indexes

Create these indexes in Firebase Console for optimal performance:

1. **users collection**:
   - Single field index on `username` (ascending)
   - Single field index on `role` (ascending)

2. **issues collection**:
   - Single field index on `student_id` (ascending)
   - Single field index on `status` (ascending)
   - Single field index on `created_at` (descending)
   - Composite index on `student_id` (ascending) and `created_at` (descending)

## Security Rules

Update your Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
      allow read: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'subadmin'];
    }
    
    // Issues access control
    match /issues/{issueId} {
      allow read, write: if request.auth != null && 
        (resource.data.student_id == request.auth.uid || 
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'subadmin']);
      allow create: if request.auth != null;
    }
  }
}
```

## Troubleshooting

1. **Firebase Authentication Error**
   - Ensure `serviceAccountKey.json` is in the correct location
   - Check that `GOOGLE_APPLICATION_CREDENTIALS` path is correct
   - Verify Firebase project ID is correct

2. **Permission Denied**
   - Check Firestore security rules
   - Ensure the service account has proper permissions

3. **Migration Issues**
   - Check that SQLite database exists and is accessible
   - Verify Firebase project is properly configured
   - Check console output for specific error messages

## Next Steps

1. Test all functionality (login, registration, issue creation, admin panel)
2. Update any remaining SQLite references in your code
3. Consider implementing Firebase Authentication for enhanced security
4. Set up proper production environment variables
5. Deploy to your preferred hosting platform

## Backup

- Your original SQLite data is backed up in `sqlite_backup.json`
- Keep this file safe until you're confident the migration is successful
- The original `university_issues.db` file remains unchanged
