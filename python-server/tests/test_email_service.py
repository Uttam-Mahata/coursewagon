#!/usr/bin/env python3
"""
Test script for Mailgun email service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.email_service import EmailService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_service():
    """Test the email service"""
    logger.info("Testing Mailgun email service...")
    
    email_service = EmailService()
    
    if not email_service.is_configured:
        logger.error("Email service is not properly configured!")
        return False
    
    # Test simple message
    logger.info("Sending test email...")
    success = email_service.send_simple_test_message("uttambav@gmail.com")
    
    if success:
        logger.info("✅ Test email sent successfully!")
        return True
    else:
        logger.error("❌ Failed to send test email!")
        return False

def test_welcome_email():
    """Test welcome email template"""
    logger.info("Testing welcome email template...")
    
    email_service = EmailService()
    
    # Create a mock user object
    class MockUser:
        def __init__(self):
            self.email = "uttambav@gmail.com"
            self.first_name = "Uttam"
            self.last_name = "Mahata"
    
    user = MockUser()
    success = email_service.send_welcome_email(user)
    
    if success:
        logger.info("✅ Welcome email sent successfully!")
        return True
    else:
        logger.error("❌ Failed to send welcome email!")
        return False

if __name__ == "__main__":
    print("=== Course Wagon Email Service Test ===")
    
    # Test basic email functionality
    test_result_1 = test_email_service()
    
    # Test welcome email
    test_result_2 = test_welcome_email()
    
    if test_result_1 and test_result_2:
        print("\n🎉 All email tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some email tests failed!")
        sys.exit(1)
