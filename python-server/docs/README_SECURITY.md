# Security Settings for CourseWagon

## Encryption Key Setup

1. Generate a secure encryption key:

```bash
python -c "import os; print(os.urandom(32).hex())"
```

2. Add the generated key to your environment variables:

For development:
```bash
export ENCRYPTION_KEY="your_generated_key_here"
export ENCRYPTION_SALT="your_custom_salt_here"  # Optional, default salt is provided
```


Record type	Hostname	Priority	Value	
TXT	coursewagon.live		"v=spf1 include:_spf.mx.cloudflare.net ~all"	Delete
TXT	coursewagon.live		"v=spf1 include:mailgun.org ~all"	Delete


For production, add these to your server's environment configuration.

3. Never commit the encryption key to your repository.

## Security Notes

- The encryption key must be the same across all instances of your application
- If the encryption key is lost, all stored API keys will be unrecoverable
- Backup your encryption key securely
- Rotate the encryption key periodically (this will require re-encrypting all stored API keys)
