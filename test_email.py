#!/usr/bin/env python3
"""
Test script to verify email configuration
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_config():
    """Test email configuration"""
    try:
        # Check if environment variables are set
        email = os.environ.get('SMTP_EMAIL')
        password = os.environ.get('SMTP_PASSWORD')
        
        if not email or not password:
            print("❌ Error: SMTP_EMAIL and SMTP_PASSWORD environment variables not set")
            print("Please set these variables or create a .env file")
            return False
            
        print(f"✅ Email: {email}")
        print(f"✅ Password: {'*' * len(password) if password else 'Not set'}")
        
        # Test SMTP connection
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(email, password)
        print("✅ SMTP connection successful")
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing email configuration...")
    test_email_config()
