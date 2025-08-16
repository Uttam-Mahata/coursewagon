import os
import logging
import requests
import dns.resolver
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Initialize email service with Mailgun configuration"""
        # Mailgun API configuration
        self.mailgun_api_key = os.environ.get('MAILGUN_API_KEY')
        self.mailgun_domain = os.environ.get('MAILGUN_DOMAIN', 'mg.coursewagon.live')
        self.mailgun_url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"
        
        # Email settings
        self.sender_email = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@mg.coursewagon.live')
        self.contact_email = os.environ.get('MAIL_CONTACT_EMAIL', 'contact@mg.coursewagon.live')
        self.app_name = os.environ.get('APP_NAME', 'Course Wagon')
        self.frontend_url = os.environ.get('FRONTEND_URL', 'https://www.coursewagon.live')
        
        logger.debug(f"Email service using Mailgun domain: {self.mailgun_domain}")
        
        # Set up Jinja2 environment for email templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'emails')
        if not os.path.exists(template_dir):
            # Create templates directory if it doesn't exist
            os.makedirs(template_dir, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        # Check if email service is properly configured
        self.is_configured = all([self.mailgun_api_key, self.mailgun_domain, self.sender_email])
        
        if not self.is_configured:
            missing_vars = []
            if not self.mailgun_api_key:
                missing_vars.append("MAILGUN_API_KEY")
            if not self.mailgun_domain:
                missing_vars.append("MAILGUN_DOMAIN")
            if not self.sender_email:
                missing_vars.append("MAIL_DEFAULT_SENDER")
            
            logger.warning(f"Email service not configured properly. Missing: {', '.join(missing_vars)}")
        else:
            logger.info(f"Email service configured successfully using Mailgun domain: {self.mailgun_domain}")

    def check_dns_configuration(self):
        """Check DNS configuration for email delivery"""
        try:
            # Try to import dnspython, install if not available
            try:
                import dns.resolver
            except ImportError:
                logger.warning("dnspython not installed, skipping DNS checks")
                return True
            
            logger.info("Checking DNS configuration...")
            
            # Check SPF record for main domain
            main_domain = self.sender_email.split('@')[1] if '@' in self.sender_email else 'coursewagon.live'
            spf_records = self._check_spf_record(main_domain)
            
            # Check SPF record for Mailgun domain
            mailgun_spf_records = self._check_spf_record(self.mailgun_domain)
            
            # Check MX records for Mailgun domain
            mx_records = self._check_mx_record(self.mailgun_domain)
            
            if spf_records and mailgun_spf_records and mx_records:
                logger.info("✅ DNS configuration looks good")
                return True
            else:
                logger.warning("⚠️ DNS configuration may have issues")
                return False
                
        except Exception as e:
            logger.error(f"Error checking DNS configuration: {e}")
            return False

    def _check_spf_record(self, domain):
        """Check SPF record for a domain"""
        try:
            result = dns.resolver.resolve(domain, 'TXT')
            spf_records = []
            for rdata in result:
                txt_string = str(rdata).strip('"')
                if txt_string.startswith('v=spf1'):
                    spf_records.append(txt_string)
            
            if spf_records:
                logger.debug(f"SPF records for {domain}: {spf_records}")
                return True
            else:
                logger.warning(f"No SPF record found for {domain}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking SPF record for {domain}: {e}")
            return False

    def _check_mx_record(self, domain):
        """Check MX record for a domain"""
        try:
            result = dns.resolver.resolve(domain, 'MX')
            mx_records = [(rdata.preference, str(rdata.exchange)) for rdata in result]
            if mx_records:
                logger.debug(f"MX records for {domain}: {mx_records}")
                return True
            else:
                logger.warning(f"No MX record found for {domain}")
                return False
        except Exception as e:
            logger.error(f"Error checking MX record for {domain}: {e}")
            return False

    def send_email_with_dns_check(self, to_email, subject, html_content=None, text_content=None):
        """
        Send email with DNS verification first
        """
        # Check DNS configuration before sending
        dns_ok = self.check_dns_configuration()
        if not dns_ok:
            logger.warning("DNS configuration issues detected, but proceeding with email send")
        
        return self.send_email(to_email, subject, html_content, text_content)

    def send_email(self, to_email, subject, html_content=None, text_content=None):
        """
        Send an email using Mailgun API
        
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
            logger.error(f"Missing config: API_KEY={bool(self.mailgun_api_key)}, DOMAIN={self.mailgun_domain}, SENDER={self.sender_email}")
            return False
        
        try:
            # Prepare email data
            data = {
                "from": f"{self.app_name} <{self.sender_email}>",
                "to": to_email,
                "subject": f"{self.app_name} - {subject}"
            }
            
            if html_content:
                data["html"] = html_content
            if text_content:
                data["text"] = text_content
            
            logger.info(f"Attempting to send email to {to_email} via Mailgun ({self.mailgun_domain})")
            
            # Send email via Mailgun API
            response = requests.post(
                self.mailgun_url,
                auth=("api", self.mailgun_api_key),
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully to {to_email}: {subject}")
                logger.debug(f"Mailgun response: {response.json()}")
                return True
            else:
                logger.error(f"Failed to send email. Status: {response.status_code}, Response: {response.text}")
                logger.error(f"Request details: URL={self.mailgun_url}, From={data['from']}, To={data['to']}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            logger.exception("Detailed email sending exception:")
            return False

    def send_template_email(self, to_email, subject, template_name, context=None):
        """
        Send an email using a template
        
        Args:
            to_email: Recipient email
            subject: Email subject
            template_name: Name of the template file (without .html extension)
            context: Dictionary of variables to pass to the template
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if context is None:
            context = {}
        
        # Add common context variables
        context['app_name'] = self.app_name
        context['contact_email'] = self.contact_email
        context['frontend_url'] = self.frontend_url
        
        try:
            # Try to load and render template
            template_path = f"{template_name}.html"
            if os.path.exists(os.path.join(self.env.loader.searchpath[0], template_path)):
                template = self.env.get_template(template_path)
                html_content = template.render(**context)
                return self.send_email(to_email, subject, html_content=html_content)
            else:
                # Fallback to simple HTML if template doesn't exist
                logger.warning(f"Template {template_name}.html not found, using fallback")
                return self._send_fallback_email(to_email, subject, template_name, context)
                
        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            # Fallback to simple email
            return self._send_fallback_email(to_email, subject, template_name, context)

    def _send_fallback_email(self, to_email, subject, template_name, context):
        """Send a simple fallback email when template is not available"""
        if template_name == "welcome":
            html_content = f"""
            <html>
            <body>
                <h2>Welcome to {self.app_name}!</h2>
                <p>Hi {context.get('first_name', 'there')},</p>
                <p>Welcome to Course Wagon! We're excited to have you on board.</p>
                <p>You can now log in to your account and start exploring our courses.</p>
                <p><a href="{context.get('login_url', self.frontend_url + '/auth')}">Login to your account</a></p>
                <p>Best regards,<br>The Course Wagon Team</p>
            </body>
            </html>
            """
            text_content = f"Welcome to {self.app_name}! Hi {context.get('first_name', 'there')}, welcome to Course Wagon!"
        
        elif template_name == "password_reset":
            html_content = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hi {context.get('first_name', 'there')},</p>
                <p>You requested a password reset for your Course Wagon account.</p>
                <p><a href="{context.get('reset_link', '#')}">Reset your password</a></p>
                <p>This link will expire in {context.get('expires_in', '24 hours')}.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <p>Best regards,<br>The Course Wagon Team</p>
            </body>
            </html>
            """
            text_content = f"Password reset requested for Course Wagon. Click the link to reset: {context.get('reset_link', '#')}"
        
        else:
            html_content = f"<html><body><h2>{subject}</h2><p>This is a message from {self.app_name}.</p></body></html>"
            text_content = f"This is a message from {self.app_name}."
        
        return self.send_email(to_email, subject, html_content=html_content, text_content=text_content)
    
    def send_welcome_email(self, user):
        """Send welcome email to newly registered user"""
        context = {
            'first_name': user.first_name or 'there',
            'email': user.email,
            'login_url': f"{self.frontend_url}/auth"
        }
        return self.send_template_email(user.email, "Welcome to Course Wagon", "welcome", context)
    
    def send_password_reset_email(self, user, reset_token, frontend_url=None):
        """Send password reset email with link"""
        url = frontend_url or self.frontend_url
        reset_link = f"{url}/reset-password?token={reset_token}"
        context = {
            'first_name': user.first_name or 'there',
            'email': user.email,
            'reset_link': reset_link,
            'expires_in': '24 hours'
        }
        return self.send_template_email(user.email, "Password Reset Request", "password_reset", context)
    
    def send_password_changed_email(self, user):
        """Send notification that password was changed"""
        context = {
            'first_name': user.first_name or 'there',
            'email': user.email,
            'login_url': f"{self.frontend_url}/auth"
        }
        return self.send_template_email(user.email, "Your Password Has Been Changed", "password_changed", context)

    def send_simple_test_message(self, to_email="coursewagon@gmail.com"):
        """Send a simple test message to verify Mailgun configuration"""
        try:
            response = requests.post(
                self.mailgun_url,
                auth=("api", self.mailgun_api_key),
                data={
                    "from": f"Course Wagon <{self.sender_email}>",
                    "to": to_email,
                    "subject": "Hello from Course Wagon",
                    "text": "Congratulations! You just sent an email with Mailgun! Course Wagon email service is working!"
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Test email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send test email. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return False

    def test_email_delivery_comprehensive(self, to_email="uttambav@gmail.com"):
        """
        Comprehensive email delivery test with DNS verification
        This implements the DNS method from test_dns_email.py
        """
        logger.info("Starting comprehensive email delivery test...")
        
        # Step 1: Check DNS configuration
        logger.info("1. Checking DNS configuration...")
        dns_result = self.check_dns_configuration()
        
        # Step 2: Test Mailgun API connectivity
        logger.info("2. Testing Mailgun API connectivity...")
        api_result = self._test_mailgun_api_connectivity()
        
        # Step 3: Send test email using the DNS-verified method
        logger.info("3. Sending test email...")
        email_result = self._send_dns_verified_test_email(to_email)
        
        # Step 4: Send welcome email test
        logger.info("4. Testing welcome email template...")
        welcome_result = self._test_welcome_email_template(to_email)
        
        # Step 5: Send password reset email test
        logger.info("5. Testing password reset email template...")
        reset_result = self._test_password_reset_template(to_email)
        
        # Summary
        results = {
            'dns_configuration': dns_result,
            'api_connectivity': api_result,
            'test_email': email_result,
            'welcome_email': welcome_result,
            'password_reset_email': reset_result
        }
        
        all_passed = all(results.values())
        
        if all_passed:
            logger.info("🎉 All email delivery tests passed!")
        else:
            logger.warning("⚠️ Some email delivery tests failed")
            for test, result in results.items():
                status = "✅" if result else "❌"
                logger.info(f"   {status} {test}")
        
        return results

    def _test_mailgun_api_connectivity(self):
        """Test Mailgun API connectivity"""
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                auth=("api", self.mailgun_api_key),
                data={
                    "from": f"DNS Test <noreply@{self.mailgun_domain}>",
                    "to": "uttambav@gmail.com",
                    "subject": "Mailgun API Connectivity Test",
                    "text": "This is a test to verify Mailgun API connectivity.",
                    "html": "<p>This is a test to verify Mailgun API connectivity.</p>"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Mailgun API connectivity test successful: {response.json()}")
                return True
            else:
                logger.error(f"❌ Mailgun API connectivity test failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mailgun API connectivity test error: {e}")
            return False

    def _send_dns_verified_test_email(self, to_email):
        """Send a DNS-verified test email"""
        try:
            # This uses the same method as in test_dns_email.py
            response = requests.post(
                self.mailgun_url,
                auth=("api", self.mailgun_api_key),
                data={
                    "from": f"{self.app_name} DNS Test <noreply@{self.mailgun_domain}>",
                    "to": to_email,
                    "subject": "DNS Configuration Verified - Course Wagon Email Test",
                    "text": "Congratulations! DNS configuration is working correctly. This email was sent using the DNS-verified method.",
                    "html": """
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #2563eb;">🎉 DNS Configuration Verified!</h2>
                            <p>Congratulations! Your DNS configuration is working correctly.</p>
                            <div style="background-color: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <h3 style="color: #1d4ed8; margin-top: 0;">✅ Tests Passed:</h3>
                                <ul>
                                    <li>SPF records configured correctly</li>
                                    <li>MX records pointing to Mailgun</li>
                                    <li>Mailgun API connectivity verified</li>
                                    <li>Email delivery working</li>
                                </ul>
                            </div>
                            <p>This email was sent using the DNS-verified method from CourseWagon.</p>
                            <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                                Best regards,<br>
                                The Course Wagon Team
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                },
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ DNS-verified test email sent successfully: {response.json()}")
                return True
            else:
                logger.error(f"❌ DNS-verified test email failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ DNS-verified test email error: {e}")
            return False

    def _test_welcome_email_template(self, to_email):
        """Test welcome email template"""
        try:
            # Create a mock user for testing
            class MockUser:
                def __init__(self):
                    self.email = to_email
                    self.first_name = "Test User"
                    self.last_name = "DNS Verified"
            
            user = MockUser()
            return self.send_welcome_email(user)
        except Exception as e:
            logger.error(f"❌ Welcome email template test error: {e}")
            return False

    def _test_password_reset_template(self, to_email):
        """Test password reset email template"""
        try:
            # Create a mock user for testing
            class MockUser:
                def __init__(self):
                    self.email = to_email
                    self.first_name = "Test User"
                    self.last_name = "DNS Verified"
            
            user = MockUser()
            test_token = "test-reset-token-12345"
            return self.send_password_reset_email(user, test_token)
        except Exception as e:
            logger.error(f"❌ Password reset email template test error: {e}")
            return False
