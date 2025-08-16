#!/usr/bin/env python3
"""
DNS and Email Delivery Checker for CourseWagon
"""
import subprocess
import socket
import requests
import dns.resolver
import sys
import os

def check_spf_record(domain):
    """Check SPF record for the domain"""
    try:
        result = dns.resolver.resolve(domain, 'TXT')
        spf_records = []
        for rdata in result:
            txt_string = str(rdata).strip('"')
            if txt_string.startswith('v=spf1'):
                spf_records.append(txt_string)
        
        print(f"SPF Records for {domain}:")
        if spf_records:
            for record in spf_records:
                print(f"  ✅ {record}")
        else:
            print(f"  ❌ No SPF record found")
        
        if len(spf_records) > 1:
            print(f"  ⚠️  WARNING: Multiple SPF records found! This will cause issues.")
        
        return spf_records
    except Exception as e:
        print(f"  ❌ Error checking SPF record: {e}")
        return []

def check_mx_record(domain):
    """Check MX record for the domain"""
    try:
        result = dns.resolver.resolve(domain, 'MX')
        print(f"MX Records for {domain}:")
        for rdata in result:
            print(f"  ✅ {rdata.preference} {rdata.exchange}")
        return True
    except Exception as e:
        print(f"  ❌ Error checking MX record: {e}")
        return False

def check_mailgun_domain_verification():
    """Check if Mailgun domain is properly configured"""
    print("\n=== Mailgun Domain Configuration Check ===")
    
    # Check main domain SPF
    print("\n1. Checking main domain SPF record:")
    check_spf_record("coursewagon.live")
    
    # Check Mailgun subdomain
    print("\n2. Checking Mailgun subdomain SPF record:")
    check_spf_record("mg.coursewagon.live")
    
    # Check MX records for Mailgun subdomain
    print("\n3. Checking Mailgun subdomain MX records:")
    check_mx_record("mg.coursewagon.live")

def test_mailgun_api():
    """Test Mailgun API connectivity"""
    print("\n=== Mailgun API Test ===")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('MAILGUN_API_KEY')
    domain = os.getenv('MAILGUN_DOMAIN', 'mg.coursewagon.live')
    
    if not api_key:
        print("❌ MAILGUN_API_KEY not found in environment variables")
        return False
    
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    
    try:
        # Test with a simple message
        response = requests.post(
            url,
            auth=("api", api_key),
            data={
                "from": f"Test <noreply@{domain}>",
                "to": "uttambav@gmail.com",
                "subject": "DNS Configuration Test",
                "text": "This is a test email to verify DNS configuration is working.",
                "html": "<p>This is a test email to verify DNS configuration is working.</p>"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Mailgun API test successful!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Mailgun API test failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing Mailgun API: {e}")
        return False

def main():
    """Main function to run all checks"""
    print("=== CourseWagon Email Delivery Diagnostic Tool ===\n")
    
    # Check DNS records
    check_mailgun_domain_verification()
    
    # Test Mailgun API
    test_mailgun_api()
    
    print("\n=== Recommendations ===")
    print("1. Ensure only ONE SPF record exists per domain")
    print("2. Make sure all Mailgun DNS records are added to Cloudflare")
    print("3. Wait 24-48 hours for DNS propagation")
    print("4. Check spam/junk folders for test emails")
    print("5. Verify domain in Mailgun dashboard: https://app.mailgun.com/")

if __name__ == "__main__":
    try:
        import dns.resolver
    except ImportError:
        print("Installing required package: dnspython")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "dnspython"])
        import dns.resolver
    
    main()
