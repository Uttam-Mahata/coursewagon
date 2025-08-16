# DNS Configuration Guide for CourseWagon Email Setup

## Current Issue
The email service is working on the backend, but emails are not being delivered due to DNS configuration issues.

## Required DNS Records for Mailgun + Cloudflare

### 1. Delete Existing Conflicting SPF Records
Remove these records from your Cloudflare DNS:
- `TXT coursewagon.live "v=spf1 include:_spf.mx.cloudflare.net ~all"`
- `TXT coursewagon.live "v=spf1 include:mailgun.org ~all"`

### 2. Add New Combined SPF Record
**Type**: TXT  
**Name**: coursewagon.live  
**Value**: `v=spf1 include:mailgun.org include:_spf.mx.cloudflare.net ~all`

### 3. Add Required Mailgun DNS Records
Add these records to your Cloudflare DNS:

#### A. MX Records for mg.coursewagon.live
**Type**: MX  
**Name**: mg  
**Value**: mxa.mailgun.org  
**Priority**: 10

**Type**: MX  
**Name**: mg  
**Value**: mxb.mailgun.org  
**Priority**: 10

#### B. TXT Record for Domain Verification
**Type**: TXT  
**Name**: mg  
**Value**: `v=spf1 include:mailgun.org ~all`

#### C. CNAME Record for Tracking
**Type**: CNAME  
**Name**: email.mg  
**Value**: mailgun.org

#### D. DKIM Records (Get these from your Mailgun dashboard)
You'll need to get the DKIM records from your Mailgun control panel:
1. Go to https://app.mailgun.com/
2. Navigate to Sending > Domains
3. Click on mg.coursewagon.live
4. Copy the DKIM records and add them to Cloudflare

### 4. Additional Recommendations

#### A. DMARC Record (Optional but recommended)
**Type**: TXT  
**Name**: _dmarc  
**Value**: `v=DMARC1; p=none; rua=mailto:dmarc@coursewagon.live`

#### B. Dedicated IP (If using Mailgun Pro)
If you're using a dedicated IP, make sure to add it to your SPF record.

## Testing After DNS Changes

### 1. Wait for DNS Propagation
DNS changes can take up to 24-48 hours to fully propagate.

### 2. Check DNS Propagation
Use these tools to verify your DNS changes:
- https://dnschecker.org/
- https://mxtoolbox.com/spf.aspx

### 3. Test Email Delivery
```bash
cd /home/uttam/PycharmProjects/coursewagon-backend
/home/uttam/PycharmProjects/coursewagon-backend/.venv/bin/python test_email_service.py
```

### 4. Check Email Headers
When you receive test emails, check the email headers for any authentication failures.

## Troubleshooting

### If emails still don't arrive:
1. Check your spam/junk folder
2. Verify all DNS records are correct using MXToolbox
3. Check Mailgun logs for delivery status
4. Ensure your Mailgun domain is verified

### Common Issues:
- **Multiple SPF records**: Only one SPF record per domain is allowed
- **DNS propagation delay**: Changes can take time to propagate
- **DKIM not set up**: DKIM records are required for good deliverability
- **Reputation issues**: New domains may have delivery issues initially

## Mailgun Dashboard Verification
1. Log into https://app.mailgun.com/
2. Go to Sending > Domains
3. Verify that mg.coursewagon.live shows "Verified" status
4. Check that all DNS records show green checkmarks

## Alternative: Use Mailgun's Sandbox Domain for Testing
If you want to test immediately while waiting for DNS propagation:
1. Use Mailgun's sandbox domain for testing
2. Add authorized recipients in Mailgun dashboard
3. Update the .env file temporarily with sandbox domain

Remember: Once DNS is properly configured, deliverability should improve significantly.
