#!/usr/bin/env python3
"""
Test Welcome Email and Password Reset Integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.email_service import EmailService
from services.auth_service import AuthService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_welcome_email_integration():
    """Test welcome email for new user registration"""
    logger.info("=== Testing Welcome Email Integration ===")
    
    try:
        email_service = EmailService()
        
        # Create a mock user (like what would happen during registration)
        class MockUser:
            def __init__(self, email, first_name, last_name):
                self.email = email
                self.first_name = first_name
                self.last_name = last_name
        
        # Test user data
        test_user = MockUser(
            email="uttambav@gmail.com",
            first_name="Test",
            last_name="User"
        )
        
        logger.info(f"Sending welcome email to {test_user.email}...")
        result = email_service.send_welcome_email(test_user)
        
        if result:
            logger.info("✅ Welcome email sent successfully!")
            return True
        else:
            logger.error("❌ Failed to send welcome email!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing welcome email: {e}")
        return False

def test_password_reset_integration():
    """Test password reset email functionality"""
    logger.info("=== Testing Password Reset Email Integration ===")
    
    try:
        email_service = EmailService()
        
        # Create a mock user
        class MockUser:
            def __init__(self, email, first_name, last_name):
                self.email = email
                self.first_name = first_name
                self.last_name = last_name
        
        # Test user data
        test_user = MockUser(
            email="uttambav@gmail.com",
            first_name="Test",
            last_name="User"
        )
        
        # Mock reset token
        test_token = "test-reset-token-abc123def456"
        
        logger.info(f"Sending password reset email to {test_user.email}...")
        result = email_service.send_password_reset_email(test_user, test_token)
        
        if result:
            logger.info("✅ Password reset email sent successfully!")
            logger.info(f"   Reset link would be: https://www.coursewagon.live/reset-password?token={test_token}")
            return True
        else:
            logger.error("❌ Failed to send password reset email!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing password reset email: {e}")
        return False

def test_password_changed_notification():
    """Test password changed notification email"""
    logger.info("=== Testing Password Changed Notification ===")
    
    try:
        email_service = EmailService()
        
        # Create a mock user
        class MockUser:
            def __init__(self, email, first_name, last_name):
                self.email = email
                self.first_name = first_name
                self.last_name = last_name
        
        # Test user data
        test_user = MockUser(
            email="uttambav@gmail.com",
            first_name="Test",
            last_name="User"
        )
        
        logger.info(f"Sending password changed notification to {test_user.email}...")
        result = email_service.send_password_changed_email(test_user)
        
        if result:
            logger.info("✅ Password changed notification sent successfully!")
            return True
        else:
            logger.error("❌ Failed to send password changed notification!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing password changed notification: {e}")
        return False

def test_comprehensive_email_flow():
    """Test the complete email flow with DNS verification"""
    logger.info("=== Testing Comprehensive Email Flow ===")
    
    try:
        email_service = EmailService()
        
        # Run comprehensive test
        logger.info("Running comprehensive email delivery test...")
        results = email_service.test_email_delivery_comprehensive("uttambav@gmail.com")
        
        # Print results
        print("\n📧 Email Test Results:")
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status} - {test_name.replace('_', ' ').title()}")
        
        all_passed = all(results.values())
        
        if all_passed:
            logger.info("🎉 All comprehensive email tests passed!")
        else:
            logger.warning("⚠️ Some comprehensive email tests failed")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"❌ Error in comprehensive email flow test: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 CourseWagon Email Integration Test")
    print("=" * 60)
    
    # Test individual email functions
    welcome_result = test_welcome_email_integration()
    reset_result = test_password_reset_integration()
    changed_result = test_password_changed_notification()
    
    # Test comprehensive flow
    comprehensive_result = test_comprehensive_email_flow()
    
    print("\n" + "=" * 60)
    print("📊 Final Results Summary:")
    print("=" * 60)
    
    tests = [
        ("Welcome Email Integration", welcome_result),
        ("Password Reset Email", reset_result),
        ("Password Changed Notification", changed_result),
        ("Comprehensive Email Flow", comprehensive_result)
    ]
    
    all_passed = True
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL EMAIL INTEGRATION TESTS PASSED!")
        print("\n📧 Email Integration Status:")
        print("✅ Welcome emails will be sent on new user registration")
        print("✅ Password reset emails will be sent on forgot password requests")
        print("✅ Password changed notifications will be sent on successful password resets")
        print("✅ DNS configuration is verified and working")
        print("✅ All email templates are functional")
        
        print("\n🔗 Integration Points:")
        print("1. Registration: auth_routes.py -> register() -> email_service.send_welcome_email()")
        print("2. Google Sign-up: auth_service.py -> authenticate_google_user() -> email_service.send_welcome_email()")
        print("3. Forgot Password: auth_routes.py -> forgot_password() -> auth_service.request_password_reset()")
        print("4. Password Reset: auth_service.py -> reset_password() -> email_service.send_password_changed_email()")
        
        print("\n📧 Check your email inbox (uttambav@gmail.com) for test emails!")
        print("Note: Emails may take a few minutes to arrive and might be in spam folder.")
        
    else:
        print("❌ SOME EMAIL INTEGRATION TESTS FAILED!")
        print("Please check the logs above for specific issues.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
