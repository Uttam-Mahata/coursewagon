#!/usr/bin/env python3
"""
Test script for Gmail SMTP email service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.email_service import EmailService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gmail_smtp():
    """Test the Gmail SMTP email service"""
    logger.info("Testing Gmail SMTP email service...")
    
    email_service = EmailService()
    
    if not email_service.is_configured:
        logger.error("Email service is not properly configured!")
        return False
    
    # Test SMTP connection
    logger.info("Testing SMTP connection...")
    connection_test = email_service.test_smtp_connection()
    
    if not connection_test:
        logger.error("SMTP connection failed!")
        return False
    
    # Test simple email
    logger.info("Sending test email...")
    success = email_service.send_simple_test_message("uttambav@gmail.com")
    
    if success:
        logger.info("✅ Test email sent successfully!")
        return True
    else:
        logger.error("❌ Failed to send test email!")
        return False

def test_comprehensive():
    """Run comprehensive email tests"""
    logger.info("Running comprehensive Gmail SMTP tests...")
    
    email_service = EmailService()
    return email_service.test_email_delivery_comprehensive("uttambav@gmail.com")

if __name__ == "__main__":
    print("=== Course Wagon Gmail SMTP Email Service Test ===")
    
    # Test basic functionality
    print("\n1. Testing basic Gmail SMTP functionality...")
    test_result_1 = test_gmail_smtp()
    
    # Test comprehensive functionality
    print("\n2. Running comprehensive tests...")
    test_result_2 = test_comprehensive()
    
    if test_result_1 and test_result_2:
        print("\n🎉 All Gmail SMTP email tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some Gmail SMTP email tests failed!")
        sys.exit(1)
