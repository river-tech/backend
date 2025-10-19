from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Email configuration
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class EmailService:
    def __init__(self):
        self.fastmail = FastMail(mail_config)
    
    async def send_otp_email(self, email: str, otp: str, otp_type: str = "email_verification"):
        """Send OTP email to user"""
        try:
            subject = "Your OTP Code - USITech"
            
            if otp_type == "email_verification":
                body = f"""
                <html>
                <body>
                    <h2>Email Verification - USITech</h2>
                    <p>Hello!</p>
                    <p>Your email verification code is:</p>
                    <h1 style="color: #007bff; font-size: 32px; text-align: center; padding: 20px; border: 2px solid #007bff; border-radius: 10px; display: inline-block;">{otp}</h1>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                    <br>
                    <p>Best regards,<br>USITech Team</p>
                </body>
                </html>
                """
            else:  # password_reset
                body = f"""
                <html>
                <body>
                    <h2>Password Reset - USITech</h2>
                    <p>Hello!</p>
                    <p>Your password reset code is:</p>
                    <h1 style="color: #dc3545; font-size: 32px; text-align: center; padding: 20px; border: 2px solid #dc3545; border-radius: 10px; display: inline-block;">{otp}</h1>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                    <br>
                    <p>Best regards,<br>USITech Team</p>
                </body>
                </html>
                """
            
            message = MessageSchema(
                subject=subject,
                recipients=[email],
                body=body,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"OTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {str(e)}")
            return False
    
    async def send_welcome_email(self, email: str, name: str):
        """Send welcome email to new user"""
        try:
            subject = "Welcome to USITech!"
            
            body = f"""
            <html>
            <body>
                <h2>Welcome to USITech!</h2>
                <p>Hello {name}!</p>
                <p>Welcome to USITech! Your account has been successfully created.</p>
                <p>You can now access all our features and services.</p>
                <br>
                <p>Best regards,<br>USITech Team</p>
            </body>
            </html>
            """
            
            message = MessageSchema(
                subject=subject,
                recipients=[email],
                body=body,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Welcome email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {str(e)}")
            return False

# Create global email service instance
email_service = EmailService()
