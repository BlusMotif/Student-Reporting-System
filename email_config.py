"""
Email configuration for Student Report System
This file provides configuration options for email services using SendGrid
"""

import os

class EmailConfig:
    """Email configuration settings - SendGrid SMTP"""
    
    # SendGrid SMTP Configuration
    SMTP_SERVER = 'smtp.sendgrid.net'
    SMTP_PORT = 587  # TLS port (alternative: 465 for SSL, 25 for unencrypted)
    SMTP_USE_TLS = True
    
    # Email credentials - use environment variables
    SMTP_EMAIL = os.environ.get('SMTP_EMAIL', 'blusmotif1@outlook.com')  # Can be any verified email
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')  # SendGrid API key goes here
    
    # Email settings
    DEFAULT_FROM_EMAIL = SMTP_EMAIL
    EMAIL_SUBJECT_PREFIX = '[Student Report System]'
    
    @classmethod
    def is_configured(cls):
        """Check if email is properly configured"""
        return cls.SMTP_PASSWORD is not None and len(cls.SMTP_PASSWORD) > 0
    
    @classmethod
    def get_config_summary(cls):
        """Get configuration summary for debugging"""
        return {
            'smtp_server': cls.SMTP_SERVER,
            'smtp_port': cls.SMTP_PORT,
            'from_email': cls.SMTP_EMAIL,
            'configured': cls.is_configured(),
            'service': 'SendGrid'
        }
    
    @classmethod
    def get_sendgrid_config(cls):
        """Get SendGrid-specific configuration"""
        return {
            'server': 'smtp.sendgrid.net',
            'ports': [25, 587, 465],
            'username': 'apikey',  # This is literal for SendGrid
            'password': cls.SMTP_PASSWORD
        }
