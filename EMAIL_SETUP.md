# Email Configuration Guide

## Gmail Setup Instructions

### 1. Enable 2-Factor Authentication
- Go to your Google Account settings
- Enable 2-Factor Authentication

### 2. Generate App Password
- Go to Google Account → Security → App passwords
- Generate a new app password for "Mail"
- Copy the 16-character password

### 3. Update .env file
Add these lines to your `.env` file:

```env
# Email Configuration (Gmail)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False
```

### 4. Example Configuration
```env
MAIL_USERNAME=ahmobile17022005@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop
MAIL_FROM=ahmobile17022005@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False
```

### 5. Test Email
After configuration, test the email service by:
1. Register a new user
2. Check the console logs for email status
3. Check the recipient's email inbox

## Troubleshooting

### Common Issues:
1. **Authentication failed**: Check app password
2. **Connection refused**: Check Gmail settings
3. **SSL/TLS errors**: Verify MAIL_TLS=True

### Alternative Email Providers:
- **Outlook**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **Custom SMTP**: Use your provider's settings
