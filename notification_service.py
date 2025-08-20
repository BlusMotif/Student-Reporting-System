import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import json

class NotificationService:
    def __init__(self):
        # Email configuration - gmass.co SMTP
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmass.co')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.email_user = os.environ.get('EMAIL_USER', 'gmass')
        self.email_password = os.environ.get('EMAIL_PASSWORD', 'a7f361ce-fc7b-41c3-8b2f-d163dd30d95b')
        
        # SMS configuration (using a simple SMS API - you can replace with your preferred provider)
        self.sms_api_key = os.environ.get('SMS_API_KEY', '')
        self.sms_api_url = os.environ.get('SMS_API_URL', 'https://api.sms-provider.com/send')
        
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text part if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connect to server and send email with improved error handling
            if self.smtp_port == 465:
                # Use SSL for port 465
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                # Use STARTTLS for port 587
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            # Try authentication
            try:
                server.login(self.email_user, self.email_password)
            except smtplib.SMTPAuthenticationError as auth_error:
                server.quit()
                return False, f"Authentication failed: {str(auth_error)}. Check your app password."
            
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            return True, "Email sent successfully"
            
        except smtplib.SMTPException as smtp_error:
            return False, f"SMTP Error: {str(smtp_error)}"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def send_sms(self, phone_number, message):
        """Send SMS using SMS API"""
        try:
            # For demonstration, we'll use a mock SMS service
            # In production, replace with your preferred SMS provider (Twilio, etc.)
            
            if not self.sms_api_key:
                # Mock SMS sending for development
                print(f"SMS to {phone_number}: {message}")
                return True, "SMS sent successfully (mock)"
            
            payload = {
                'api_key': self.sms_api_key,
                'to': phone_number,
                'message': message,
                'from': 'KTU Portal'
            }
            
            response = requests.post(self.sms_api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True, "SMS sent successfully"
            else:
                return False, f"SMS API error: {response.status_code}"
                
        except Exception as e:
            return False, f"Failed to send SMS: {str(e)}"
    
    def send_password_reset_email(self, to_email, user_name, reset_url):
        """Send password reset email with HTML template"""
        subject = "Password Reset - KTU Student Concern Portal"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f8f9fa; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 30px; 
                    background-color: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                    <p>Koforidua Technical University - Student Concern Portal</p>
                </div>
                
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    
                    <p>We received a request to reset your password for your KTU Student Concern Portal account.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset My Password</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul>
                            <li>This link will expire in 1 hour for security reasons</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Never share this link with anyone</li>
                        </ul>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background-color: #e9ecef; padding: 10px; border-radius: 3px;">
                        {reset_url}
                    </p>
                    
                    <p>If you need help, contact IT Support at itsupport@ktu.edu.gh</p>
                    
                    <p>Best regards,<br>
                    KTU IT Support Team</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Koforidua Technical University<br>
                    This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset - KTU Student Concern Portal
        
        Hello {user_name},
        
        We received a request to reset your password for your KTU Student Concern Portal account.
        
        Please click the following link to reset your password:
        {reset_url}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request this reset, please ignore this email.
        
        If you need help, contact IT Support at itsupport@ktu.edu.gh
        
        Best regards,
        KTU IT Support Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_sms(self, phone_number, user_name, reset_url):
        """Send password reset SMS"""
        message = f"""KTU Portal: Hello {user_name}, click this link to reset your password: {reset_url} 
        
Link expires in 1 hour. If you didn't request this, ignore this message."""
        
        return self.send_sms(phone_number, message)
    
    def send_verification_email(self, to_email, user_name, verification_code):
        """Send email verification code"""
        subject = "Email Verification - KTU Student Portal"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f8f9fa; }}
                .code {{ 
                    display: inline-block; 
                    padding: 15px 30px; 
                    background-color: #28a745; 
                    color: white; 
                    font-size: 24px;
                    font-weight: bold;
                    letter-spacing: 3px;
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 Email Verification</h1>
                    <p>Koforidua Technical University - Student Portal</p>
                </div>
                
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    
                    <p>Thank you for registering with the CS Department Student Portal!</p>
                    
                    <p>Please use the verification code below to complete your registration:</p>
                    
                    <div style="text-align: center;">
                        <div class="code">{verification_code}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul>
                            <li>This code will expire in 15 minutes</li>
                            <li>Enter this code on the verification page</li>
                            <li>If you didn't create an account, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>If you need help, contact IT Support at itsupport@ktu.edu.gh</p>
                    
                    <p>Best regards,<br>
                    IT Support Team<br>
                    Koforidua Technical University</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Koforidua Technical University<br>
                    This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Email Verification - CS Department Portal
        
        Hello {user_name},
        
        Thank you for registering with the CS Department Student Portal!
        
        Please use this verification code to complete your registration:
        {verification_code}
        
        This code will expire in 15 minutes.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        IT Support Team
        Koforidua Technical University
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

# Global instance
notification_service = NotificationService()
