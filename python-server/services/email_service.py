import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Initialize email service with Gmail SMTP configuration"""
        # Gmail SMTP configuration
        self.smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('MAIL_PORT', 587))
        self.smtp_username = os.environ.get('MAIL_USERNAME')  # Gmail address
        self.smtp_password = os.environ.get('MAIL_PASSWORD')  # App password
        self.use_tls = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
        self.use_ssl = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
        
        # Email settings
        self.sender_email = os.environ.get('MAIL_DEFAULT_SENDER', self.smtp_username)
        self.contact_email = os.environ.get('MAIL_CONTACT_EMAIL', 'contact@coursewagon.live')
        self.app_name = os.environ.get('APP_NAME', 'Course Wagon')
        self.frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:4200')
        
        logger.debug(f"Email service using Gmail SMTP: {self.smtp_server}:{self.smtp_port}")
        
        # Set up Jinja2 environment for email templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'emails')
        if not os.path.exists(template_dir):
            # Create templates directory if it doesn't exist
            os.makedirs(template_dir, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        # Check if email service is properly configured
        self.is_configured = all([self.smtp_username, self.smtp_password, self.sender_email])
        
        if not self.is_configured:
            missing_vars = []
            if not self.smtp_username:
                missing_vars.append("MAIL_USERNAME")
            if not self.smtp_password:
                missing_vars.append("MAIL_PASSWORD")
            if not self.sender_email:
                missing_vars.append("MAIL_DEFAULT_SENDER")
            
            logger.warning(f"Email service not configured properly. Missing: {', '.join(missing_vars)}")
        else:
            logger.info(f"Email service configured successfully using Gmail SMTP: {self.smtp_server}")

    def send_email(self, to_email, subject, html_content=None, text_content=None):
        """
        Send an email using Gmail SMTP
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content of the email
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.error("Email service not configured. Cannot send email.")
            logger.error(f"Missing config: USERNAME={bool(self.smtp_username)}, PASSWORD={bool(self.smtp_password)}, SENDER={self.sender_email}")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.app_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = f"{self.app_name} - {subject}"

            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML content
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)

            # If no content provided, use a default message
            if not text_content and not html_content:
                default_text = f"Hello from {self.app_name}!"
                text_part = MIMEText(default_text, 'plain')
                msg.attach(text_part)

            logger.info(f"Attempting to send email to {to_email} via Gmail SMTP")
            
            # Connect to Gmail SMTP server and send email
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()

            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            logger.exception("Detailed email sending exception:")
            return False

    def send_template_email(self, to_email, subject, template_name, context=None):
        """
        Send an email using a Jinja2 template
        
        Args:
            to_email: Recipient email
            subject: Email subject
            template_name: Name of the template file
            context: Dictionary with template variables
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if context is None:
            context = {}

        # Add default context variables
        context.update({
            'app_name': self.app_name,
            'frontend_url': self.frontend_url,
            'contact_email': self.contact_email,
            'current_year': 2025
        })

        try:
            # Load and render template
            template = self.env.get_template(template_name)
            html_content = template.render(context)
            
            # Create text version (simple fallback)
            text_content = self._html_to_text(html_content)
            
            return self.send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            # Fallback to simple email
            return self._send_fallback_email(to_email, subject, template_name, context)

    def _html_to_text(self, html_content):
        """Convert HTML content to plain text (simple implementation)"""
        import re
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html_content)
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Clean up
        return text.strip()

    def _send_fallback_email(self, to_email, subject, template_name, context):
        """Send a simple fallback email when template is not available"""
        try:
            fallback_content = f"""
            Hello from {self.app_name}!
            
            This email was generated from template: {template_name}
            
            Best regards,
            The {self.app_name} Team
            
            ---
            {self.frontend_url}
            """
            
            return self.send_email(to_email, subject, None, fallback_content)
            
        except Exception as e:
            logger.error(f"Failed to send fallback email: {str(e)}")
            return False

    def send_welcome_email(self, user):
        """Send welcome email to newly registered user"""
        try:
            # Handle both user object and dict
            if hasattr(user, 'to_dict'):
                user_data = user.to_dict()
                user_email = user.email
                user_first_name = user.first_name or 'User'
            else:
                user_data = user
                user_email = user.get('email', '')
                user_first_name = user.get('first_name', 'User')
            
            context = {
                'first_name': user_first_name,
                'email': user_email,
                'login_url': f"{self.frontend_url}/auth"
            }
            
            result = self.send_template_email(
                user_email,
                "Welcome to Course Wagon!",
                "welcome.html",
                context
            )
            
            if result:
                logger.info(f"Welcome email sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send welcome email to {user_email}")
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False

    def send_password_reset_email(self, user, reset_token, frontend_url=None):
        """Send password reset email with link"""
        try:
            if frontend_url is None:
                frontend_url = self.frontend_url
                
            reset_url = f"{frontend_url}/reset-password?token={reset_token}"
            
            # Handle both user object and dict
            if hasattr(user, 'to_dict'):
                user_email = user.email
                user_first_name = user.first_name or 'User'
            else:
                user_email = user.get('email', '')
                user_first_name = user.get('first_name', 'User')
            
            context = {
                'first_name': user_first_name,
                'email': user_email,
                'reset_link': reset_url,
                'expires_in': '24 hours'
            }
            
            result = self.send_template_email(
                user_email,
                "Password Reset Request",
                "password_reset.html",
                context
            )
            
            if result:
                logger.info(f"Password reset email sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send password reset email to {user_email}")
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False

    def send_password_changed_email(self, user):
        """Send notification that password was changed"""
        try:
            # Handle both user object and dict
            if hasattr(user, 'to_dict'):
                user_email = user.email
                user_first_name = user.first_name or 'User'
            else:
                user_email = user.get('email', '')
                user_first_name = user.get('first_name', 'User')

            context = {
                'first_name': user_first_name,
                'email': user_email,
                'login_url': f"{self.frontend_url}/auth"
            }

            result = self.send_template_email(
                user_email,
                "Password Changed Successfully",
                "password_changed.html",
                context
            )

            if result:
                logger.info(f"Password changed email sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send password changed email to {user_email}")

            return result

        except Exception as e:
            logger.error(f"Failed to send password changed email: {str(e)}")
            return False

    def send_verification_email(self, user, verification_token, frontend_url=None):
        """Send email verification link"""
        try:
            if frontend_url is None:
                frontend_url = self.frontend_url

            verification_url = f"{frontend_url}/verify-email?token={verification_token}"

            # Handle both user object and dict
            if hasattr(user, 'to_dict'):
                user_email = user.email
                user_first_name = user.first_name or 'User'
            else:
                user_email = user.get('email', '')
                user_first_name = user.get('first_name', 'User')

            context = {
                'first_name': user_first_name,
                'email': user_email,
                'verification_link': verification_url,
                'expires_in': '24 hours'
            }

            result = self.send_template_email(
                user_email,
                "Verify Your Email Address",
                "verify_email.html",
                context
            )

            if result:
                logger.info(f"Verification email sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send verification email to {user_email}")

            return result

        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False

    def send_simple_test_message(self, to_email="uttambav@gmail.com"):
        """Send a simple test message to verify Gmail SMTP configuration"""
        try:
            subject = "Hello from Course Wagon"
            text_content = "Congratulations! You just sent an email with Gmail SMTP! Course Wagon email service is working!"
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">🎉 Gmail SMTP Configuration Test Successful!</h2>
                    <p>Congratulations! Your Gmail SMTP configuration is working correctly.</p>
                    <div style="background-color: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #1d4ed8; margin-top: 0;">✅ Configuration Details:</h3>
                        <ul>
                            <li>SMTP Server: {self.smtp_server}</li>
                            <li>SMTP Port: {self.smtp_port}</li>
                            <li>TLS Enabled: {self.use_tls}</li>
                            <li>Sender Email: {self.sender_email}</li>
                        </ul>
                    </div>
                    <p>This email was sent using Gmail SMTP from CourseWagon.</p>
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        Best regards,<br>
                        The Course Wagon Team
                    </p>
                </div>
            </body>
            </html>
            """
            
            return self.send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return False

    def test_smtp_connection(self):
        """Test SMTP connection to Gmail"""
        try:
            logger.info("Testing Gmail SMTP connection...")
            
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()

            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            
            logger.info("✅ Gmail SMTP connection test successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Gmail SMTP connection test failed: {str(e)}")
            return False

    def test_email_delivery_comprehensive(self, to_email="uttambav@gmail.com"):
        """
        Comprehensive email delivery test for Gmail SMTP
        """
        logger.info("Starting comprehensive Gmail SMTP email delivery test...")
        
        results = {}
        
        # Step 1: Test SMTP connection
        logger.info("1. Testing SMTP connection...")
        results['smtp_connection'] = self.test_smtp_connection()
        
        # Step 2: Send test email
        logger.info("2. Sending test email...")
        results['test_email'] = self.send_simple_test_message(to_email)
        
        # Step 3: Test welcome email template
        logger.info("3. Testing welcome email template...")
        test_user = {'name': 'Test User', 'email': to_email}
        results['welcome_email'] = self.send_welcome_email(test_user)
        
        # Step 4: Test password reset email template
        logger.info("4. Testing password reset email template...")
        results['password_reset'] = self.send_password_reset_email(test_user, 'test-token-123')
        
        # Summary
        logger.info("\n=== Gmail SMTP Test Results ===")
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        all_passed = all(results.values())
        if all_passed:
            logger.info("🎉 All Gmail SMTP tests passed!")
        else:
            logger.warning("⚠️ Some Gmail SMTP tests failed!")
        
        return all_passed
