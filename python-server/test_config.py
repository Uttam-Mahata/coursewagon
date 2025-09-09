#!/usr/bin/env python3
"""
Test script to verify configuration loading for both local and Cloud Run environments.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def test_config():
    print("🧪 Testing Configuration Loading...")
    print("=" * 50)
    
    # Test critical configurations
    config_tests = [
        ("Database Host", Config.DB_HOST),
        ("Database User", Config.DB_USER),
        ("Database Name", Config.DB_NAME),
        ("JWT Secret Key", Config.JWT_SECRET_KEY),
        ("Secret Key", Config.SECRET_KEY),
        ("Mail Server", Config.MAIL_SERVER),
        ("Mail Username", Config.MAIL_USERNAME),
        ("GCS Bucket Name", Config.GCS_BUCKET_NAME),
        ("GCS Project ID", Config.GCS_PROJECT_ID),
        ("Azure Storage Account", Config.AZURE_STORAGE_ACCOUNT_NAME),
        ("Storage Provider", Config.STORAGE_PROVIDER),
        ("Debug Mode", Config.DEBUG),
    ]
    
    success_count = 0
    total_count = len(config_tests)
    
    for name, value in config_tests:
        status = "✅ LOADED" if value else "❌ MISSING"
        masked_value = "***HIDDEN***" if any(secret in name.lower() for secret in ['secret', 'password', 'key']) else value
        print(f"{name:<20}: {status:<10} {masked_value}")
        if value:
            success_count += 1
    
    print("=" * 50)
    print(f"Configuration Test Results: {success_count}/{total_count} loaded successfully")
    
    if success_count == total_count:
        print("🎉 All configurations loaded successfully!")
        return True
    else:
        print("⚠️  Some configurations are missing. Check your .env file or Cloud Run secrets.")
        return False

if __name__ == "__main__":
    test_config()
