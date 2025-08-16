#!/usr/bin/env python3
"""
Comprehensive Email Service Test with DNS Verification
This implements the DNS method approach for robust email delivery
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.email_service import EmailService
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_comprehensive_email_delivery():
    """Test comprehensive email delivery with DNS verification"""
    logger.info("=== Comprehensive Email Delivery Test ===")
    
    try:
        email_service = EmailService()
        
        if not email_service.is_configured:
            logger.error("❌ Email service is not properly configured!")
            return False
        
        # Run comprehensive test
        results = email_service.test_email_delivery_comprehensive("uttambav@gmail.com")
        
        # Print detailed results
        print("\n=== Test Results Summary ===")
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n🎉 All tests passed! Email service is fully functional.")
            print("\n📧 Check your email inbox (uttambav@gmail.com) for test emails:")
            print("   1. DNS Configuration Test Email")
            print("   2. Welcome Email Template Test")
            print("   3. Password Reset Email Template Test")
            print("\nNote: Emails may take a few minutes to arrive and might be in spam folder.")
        else:
            print("\n⚠️ Some tests failed. Check the logs above for details.")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"❌ Error running comprehensive email test: {e}")
        return False

def test_individual_email_features():
    """Test individual email features"""
    logger.info("\n=== Individual Email Features Test ===")
    
    email_service = EmailService()
    
    print("\n1. Testing DNS Configuration Check...")
    dns_result = email_service.check_dns_configuration()
    print(f"   DNS Check: {'✅ PASSED' if dns_result else '❌ FAILED'}")
    
    print("\n2. Testing Simple Email Send...")
    simple_result = email_service.send_email(
        "uttambav@gmail.com",
        "Simple Email Test",
        html_content="<p>This is a simple email test from CourseWagon.</p>",
        text_content="This is a simple email test from CourseWagon."
    )
    print(f"   Simple Email: {'✅ SENT' if simple_result else '❌ FAILED'}")
    
    print("\n3. Testing Email with DNS Check...")
    dns_email_result = email_service.send_email_with_dns_check(
        "uttambav@gmail.com",
        "DNS Verified Email Test",
        html_content="<p>This email was sent with DNS verification.</p>",
        text_content="This email was sent with DNS verification."
    )
    print(f"   DNS Email: {'✅ SENT' if dns_email_result else '❌ FAILED'}")
    
    return dns_result and simple_result and dns_email_result

def main():
    """Main function to run all tests"""
    print("=== CourseWagon Email Service Comprehensive Test ===")
    print("This test implements the DNS method for robust email delivery")
    print("=" * 60)
    
    # Test 1: Comprehensive email delivery
    comprehensive_result = test_comprehensive_email_delivery()
    
    # Test 2: Individual features
    individual_result = test_individual_email_features()
    
    print("\n" + "=" * 60)
    print("=== Final Results ===")
    
    if comprehensive_result and individual_result:
        print("🎉 ALL TESTS PASSED!")
        print("\nEmail service is fully functional with:")
        print("✅ DNS configuration verified")
        print("✅ Mailgun API connectivity confirmed")
        print("✅ Email templates working")
        print("✅ Welcome emails functional")
        print("✅ Password reset emails functional")
        print("\n📱 Next steps:")
        print("1. Check your email inbox for test emails")
        print("2. The email service is ready for production use")
        print("3. Welcome emails will be sent on user registration")
        print("4. Password reset emails will be sent on forgot password requests")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nPlease check the logs above for specific issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
