# Email & SMS Setup Guide

This guide will help you configure email and SMS functionality for the password reset feature.

## 📧 Email Configuration (Gmail)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Enable 2-Step Verification

### Step 2: Generate App Password
1. Go to Security → 2-Step Verification → App passwords
2. Select "Mail" and your device
3. Copy the generated 16-character password

### Step 3: Update Environment Variables
Create a `.env` file in your project root:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
```

## 📱 SMS Configuration

### Option 1: Mock SMS (Development)
Leave SMS_API_KEY empty for development mode:
```env
SMS_API_KEY=
```
This will print SMS messages to console instead of sending them.

### Option 2: Twilio (Recommended)
1. Sign up at https://www.twilio.com/
2. Get your Account SID and Auth Token
3. Update your `.env`:

```env
SMS_API_KEY=your-twilio-auth-token
SMS_API_URL=https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json
```

### Option 3: Africa's Talking (For African Numbers)
1. Sign up at https://africastalking.com/
2. Get your API key
3. Update your `.env`:

```env
SMS_API_KEY=your-africastalking-api-key
SMS_API_URL=https://api.africastalking.com/version1/messaging
```

## 🧪 Testing

### Test Email Functionality
1. Register a user with a valid email
2. Go to forgot password page
3. Select "Email Address" option
4. Enter the registered email and student ID
5. Check your email inbox (and spam folder)

### Test SMS Functionality
1. Register a user with a valid phone number (+233XXXXXXXXX format)
2. Go to forgot password page
3. Select "Phone Number" option
4. Enter the registered phone and student ID
5. Check your phone for SMS

## 🔧 Troubleshooting

### Email Issues
- **"Authentication failed"**: Check your app password is correct
- **"Connection refused"**: Verify SMTP server and port
- **Email not received**: Check spam folder, verify email address

### SMS Issues
- **"SMS API error"**: Check your API credentials
- **SMS not received**: Verify phone number format (+233XXXXXXXXX)
- **Mock mode**: Check console output for SMS content

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use app passwords, not your regular Gmail password
- Regularly rotate your API keys
- Monitor your SMS usage to avoid unexpected charges

## 📞 Support

If you need help:
- Email: itsupport@ktu.edu.gh
- Check the console logs for detailed error messages
- Verify all environment variables are set correctly
