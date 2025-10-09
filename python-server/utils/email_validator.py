import re
import dns.resolver
import smtplib
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class EmailValidator:
    """
    Validates email addresses by checking:
    1. Format/syntax validation
    2. DNS MX records (domain can receive emails)
    3. SMTP verification (optional - checks if mailbox exists)
    """

    # Common disposable/temporary email domains to block
    DISPOSABLE_DOMAINS = {
        'tempmail.com', 'throwaway.email', '10minutemail.com',
        'guerrillamail.com', 'mailinator.com', 'trash-mail.com',
        'yopmail.com', 'temp-mail.org', 'getnada.com'
    }

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format using regex
        """
        if not email or not isinstance(email, str):
            return False

        # RFC 5322 compliant email regex (simplified)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def check_mx_records(domain: str) -> Tuple[bool, Optional[str]]:
        """
        Check if domain has valid MX records

        Returns:
            Tuple[bool, Optional[str]]: (has_mx_records, error_message)
        """
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if len(mx_records) > 0:
                logger.debug(f"Found {len(mx_records)} MX records for {domain}")
                return True, None
            else:
                return False, f"No MX records found for domain {domain}"
        except dns.resolver.NXDOMAIN:
            return False, f"Domain {domain} does not exist"
        except dns.resolver.NoAnswer:
            return False, f"No MX records found for domain {domain}"
        except dns.resolver.Timeout:
            logger.warning(f"DNS timeout while checking MX records for {domain}")
            # Don't fail on timeout - allow registration
            return True, None
        except Exception as e:
            logger.error(f"Error checking MX records for {domain}: {str(e)}")
            # Don't fail on error - allow registration
            return True, None

    @staticmethod
    def verify_email_smtp(email: str, timeout: int = 10) -> Tuple[bool, Optional[str]]:
        """
        Verify email exists using SMTP (may not work with all mail servers)

        Args:
            email: Email address to verify
            timeout: SMTP connection timeout in seconds

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            domain = email.split('@')[1]

            # Get MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_host = str(mx_records[0].exchange)

            # Connect to SMTP server
            server = smtplib.SMTP(timeout=timeout)
            server.set_debuglevel(0)
            server.connect(mx_host)
            server.helo(server.local_hostname)
            server.mail('noreply@coursewagon.live')
            code, message = server.rcpt(email)
            server.quit()

            # Check response code
            if code == 250:
                logger.debug(f"SMTP verification successful for {email}")
                return True, None
            else:
                logger.debug(f"SMTP verification failed for {email}: {code} {message}")
                return False, f"Email address does not exist"

        except smtplib.SMTPServerDisconnected:
            logger.warning(f"SMTP server disconnected while verifying {email}")
            # Don't fail - many servers block SMTP verification
            return True, None
        except smtplib.SMTPConnectError:
            logger.warning(f"Could not connect to SMTP server for {email}")
            # Don't fail - allow registration
            return True, None
        except Exception as e:
            logger.warning(f"SMTP verification error for {email}: {str(e)}")
            # Don't fail on error - many servers block SMTP verification
            return True, None

    @staticmethod
    def is_disposable_email(email: str) -> bool:
        """
        Check if email is from a disposable/temporary email service
        """
        try:
            domain = email.split('@')[1].lower()
            return domain in EmailValidator.DISPOSABLE_DOMAINS
        except:
            return False

    @classmethod
    def validate_email_comprehensive(
        cls,
        email: str,
        check_smtp: bool = False,
        block_disposable: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive email validation

        Args:
            email: Email address to validate
            check_smtp: Whether to perform SMTP verification (can be slow/blocked)
            block_disposable: Whether to block disposable email addresses

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Step 1: Format validation
        if not cls.validate_email_format(email):
            return False, "Invalid email format"

        # Step 2: Check for disposable email
        if block_disposable and cls.is_disposable_email(email):
            return False, "Disposable email addresses are not allowed"

        # Step 3: Extract domain
        try:
            domain = email.split('@')[1]
        except:
            return False, "Invalid email format"

        # Step 4: Check MX records
        has_mx, mx_error = cls.check_mx_records(domain)
        if not has_mx:
            return False, mx_error or "Email domain cannot receive emails"

        # Step 5: Optional SMTP verification
        if check_smtp:
            is_valid, smtp_error = cls.verify_email_smtp(email)
            if not is_valid and smtp_error:
                return False, smtp_error

        return True, None


# Convenience function
def validate_email(email: str, check_smtp: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate email address

    Args:
        email: Email address to validate
        check_smtp: Whether to perform SMTP verification (slower, may not work)

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    return EmailValidator.validate_email_comprehensive(email, check_smtp=check_smtp)
