#!/usr/bin/env python3
"""
Test script to verify SendGrid email configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sendgrid_config():
    """Test SendGrid email configuration"""
    try:
        # Check if environment variables are set
        email = os.getenv('SMTP_EMAIL')
        password = os.getenv('SMTP_PASSWORD')
        
        if not email or not password:
            print("❌ Error: SMTP_EMAIL and SMTP_PASSWORD environment variables not set")
            print("Please check your .env file")
            print(f"SMTP_EMAIL: {email}")
            print(f"SMTP_PASSWORD: {'*' * len(password) if password else 'Not set'}")
            return False
            
        print(f"✅ Email: {email}")
        print(f"✅ SendGrid API Key: {'*' * 20}...")  # Mask API key
        
        # Test SMTP connection with SendGrid
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email  # Send to self for testing
        msg['Subject'] = 'Test Email - Student Report System (SendGrid)'
        
        body = 'This is a test email to verify SendGrid SMTP configuration.'
        msg.attach(MIMEText(body, 'plain'))
        
        # SendGrid SMTP configuration
        with smtplib.SMTP('smtp.sendgrid.net', 587) as server:
            server.starttls()
            server.login('apikey', password)  # Username is always 'apikey' for SendGrid
            server.send_message(msg)
            
        print("✅ Email sent successfully via SendGrid!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Hint: Make sure your SendGrid API key is valid and has SMTP permissions")
        return False

def test_sendgrid_api_key():
    """Test SendGrid API key format"""
    password = os.getenv('SMTP_PASSWORD')
    if password and password.startswith('SG.'):
        print("✅ SendGrid API key format appears valid")
        return True
    else:
        print("⚠️  Warning: API key doesn't start with 'SG.' - may not be a valid SendGrid key")
        return False

if __name__ == "__main__":
    print("Testing SendGrid email configuration...")
    print("=" * 50)
    test_sendgrid_api_key()
    test_sendgrid_config()
