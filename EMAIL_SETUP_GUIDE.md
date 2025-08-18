# Email Setup Guide - Fix SMTP Authentication Error

## Problem
You're encountering `smtplib.SMTPAuthenticationError: (535, b'5.7.139 Authentication unsuccessful, basic authentication is disabled')` when trying to send emails from your Flask application.

## Solution

### Step 1: Enable App Passwords (Recommended)

#### For Outlook/Hotmail:
1. Go to https://account.microsoft.com/security
2. Sign in with your Outlook account (blusmotif1@outlook.com)
3. Enable **Two-factor authentication** if not already enabled
4. Under **Advanced security options**, find **App passwords**
5. Click **Create a new app password**
6. Give it a name like "Student Report System"
7. Copy the generated 16-character password
8. Use this password instead of your regular password

#### For Gmail:
1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification**
3. Go to **App passwords**
4. Generate a new app password for "Mail"
5. Use this 16-character password

### Step 2: Set Environment Variables

Create a `.env` file in your project root:

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your actual credentials
SMTP_EMAIL=blusmotif1@outlook.com
SMTP_PASSWORD=your-16-character-app-password
SESSION_SECRET=your-secret-key-here
```

### Step 3: Install Required Dependencies

```bash
pip install python-dotenv
```

### Step 4: Update Your Application

The email sending function has been updated to use environment variables. The application will now:
- Use secure app passwords instead of regular passwords
- Handle errors gracefully
- Log email sending status

### Step 5: Test Email Functionality

Test the email functionality by:
1. Starting your application: `python app.py`
2. Navigating to the forgot password page
3. Entering an email address
4. Checking if the email is received

## Alternative Solutions

### Option 1: Use Gmail SMTP
If Outlook continues to have issues, you can switch to Gmail:
1. Create a Gmail account
2. Enable 2FA and generate app password
3. Update the SMTP settings:
   - SMTP_SERVER: smtp.gmail.com
   - SMTP_PORT: 587

### Option 2: Use Email Service Providers
Consider using services like:
- **SendGrid**: Free tier with 100 emails/day
- **Mailgun**: Free tier with 100 emails/day
- **Mailjet**: Free tier with 200 emails/day

### Option 3: Disable Email Feature (Development Only)
For development, you can disable email functionality and use console output instead.

## Troubleshooting

### Common Issues:
1. **"Authentication unsuccessful"**: Check app password is correct
2. **"Connection timeout"**: Check firewall settings
3. **"Invalid credentials"**: Ensure 2FA is enabled for app passwords

### Debug Commands:
```python
# Test email configuration
from email_config import EmailConfig
print(EmailConfig.get_config_summary())

# Test SMTP connection
import smtplib
server = smtplib.SMTP('smtp.office365.com', 587)
server.starttls()
server.login('your-email', 'your-app-password')
```

## Security Notes
- Never commit actual passwords to version control
- Always use environment variables for sensitive data
- Regularly rotate app passwords
- Monitor email sending limits
