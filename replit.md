# Koforidua Technical University Student Issue Reporting System

## Overview

This is a Flask-based web application that allows Koforidua Technical University students to report issues to administrators (Dean, HOD, etc.). The system provides role-based access with separate interfaces for students and administrators, built using Python Flask with SQLite database and Bootstrap frontend with professional KTU branding.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with raw SQL queries
- **Authentication**: Session-based authentication using Flask sessions
- **Password Security**: Werkzeug password hashing (generate_password_hash/check_password_hash)
- **Architecture Pattern**: Traditional MVC with Flask blueprints structure

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Styling**: Custom CSS with Koforidua Technical University branding colors and professional login interface
- **Responsive Design**: Bootstrap responsive grid system
- **Logo**: Official KTU logo (PNG format) integrated throughout the system

### Database Design
- **Type**: SQLite (file-based database)
- **Connection Management**: Flask's application context (g object)
- **Schema**: Two main tables (users, issues) with foreign key relationships

## Key Components

### Authentication System
- **Session Management**: Flask sessions with user_id storage
- **Role-Based Access**: Two roles (student, admin) with different permissions
- **Password Security**: Werkzeug hashing with salt
- **User Context**: Global user object loaded before each request

### User Roles & Permissions
- **Students**: Can submit issues, view their own issues, see issue status
- **Admins**: Can view all issues, update issue status, respond to issues

### Issue Management
- **Issue Submission**: Students can create issues with subject, category, and detailed message
- **Status Tracking**: Three states (pending, in_progress, resolved)
- **Categories**: Predefined categories (academic, administrative, technical, etc.)
- **Admin Responses**: Admins can add responses to issues

## Data Flow

### Student Workflow
1. Login → Student Dashboard (shows issue statistics)
2. Submit Issue → Form with subject, category, message
3. View Issues → List of submitted issues with status and admin responses

### Admin Workflow
1. Login → Admin Dashboard (issue management interface)
2. View All Issues → Complete list with student information
3. Update Issues → Change status and add responses
4. Issue Resolution → Mark issues as resolved with explanatory responses

### Database Operations
- **User Authentication**: Query users table by username, verify password hash
- **Issue Creation**: Insert new records in issues table with student_id foreign key
- **Issue Updates**: Update status and response fields by admin users
- **Data Retrieval**: Join queries to get student names with issue data

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Werkzeug**: Password hashing and security utilities
- **SQLite3**: Database connectivity (built into Python)

### Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework from CDN
- **Font Awesome 6.4.0**: Icon library from CDN
- **Custom CSS**: KTU-branded styling with color variables

### Development Tools
- **Debug Mode**: Enabled for development with auto-reload
- **Session Secret**: Environment variable or default dev key

## Deployment Strategy

### Current Setup
- **Development**: Flask development server (app.run with debug=True)
- **Host Configuration**: Listens on 0.0.0.0:5000 for accessibility
- **Database**: SQLite file stored locally (university_issues.db)
- **Static Files**: Served by Flask development server

### Database Initialization
- **Automatic Setup**: Database and tables created on first run
- **Sample Data**: Default admin and student accounts created for testing
- **Password Defaults**: admin/admin123, student1/student123, student2/student123

## Recent Changes (July 23, 2025)
- Updated university branding to "Koforidua Technical University"
- Integrated official KTU logo (PNG format) throughout the system
- Redesigned login interface with professional styling and gradient background
- Removed demo account references from login page for production-ready appearance
- Enhanced CSS with professional login animations and responsive design
- Updated all page titles and footer to reflect correct university name

### Security Considerations
- **Session Secret**: Should be set via environment variable in production
- **Password Hashing**: Using Werkzeug's secure hashing
- **SQL Injection Protection**: Using parameterized queries
- **Role-Based Access**: Proper permission checks in routes

### Potential Production Considerations
- **Database**: Could be migrated to PostgreSQL for better performance
- **Web Server**: Should use production WSGI server (Gunicorn, uWSGI)
- **Static Files**: Should be served by web server (nginx) instead of Flask
- **Environment Variables**: All secrets should be externalized
- **HTTPS**: SSL/TLS termination for secure communication