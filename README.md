# EmailListVerify Python SDK

Official Python SDK for the EmailListVerify API - Email validation and verification service.

## Installation

Install via pip:

```bash
pip install emaillistverify
```

## Usage

### Basic Usage

```python
from emaillistverify import EmailListVerifyClient

# Initialize client with your API key
client = EmailListVerifyClient('your-api-key-here')

# Verify a single email
result = client.verify_email('test@example.com')
print(result)  # Returns: ok, invalid, invalid_mx, accept_all, ok_for_all, disposable, role, email_disabled, dead_server, or unknown

# Verify multiple emails
emails = ['test@example.com', 'invalid@domain.com', 'user@gmail.com']
results = client.verify_emails(emails)

for email, status in results.items():
    print(f"Email: {email} - Status: {status}")
```

### Context Manager Usage

```python
from emaillistverify import EmailListVerifyClient

# Using context manager (recommended)
with EmailListVerifyClient('your-api-key-here') as client:
    result = client.verify_email('test@example.com')
    print(f"Result: {result}")
```

### Response Values

The API returns simple text responses:

- `ok` - Valid email address
- `invalid` - Invalid email format or domain
- `invalid_mx` - Domain has no valid MX records
- `accept_all` - Server accepts all emails (catch-all)
- `ok_for_all` - Valid but may be catch-all
- `disposable` - Temporary/disposable email address
- `role` - Role-based email (e.g., admin@, info@)
- `email_disabled` - Email account is disabled
- `dead_server` - Mail server is not responding
- `unknown` - Unable to determine status

### Error Handling

```python
from emaillistverify import EmailListVerifyClient, EmailListVerifyError

try:
    client = EmailListVerifyClient('your-api-key-here')
    result = client.verify_email('test@example.com')
    print(f"Result: {result}")
except EmailListVerifyError as e:
    print(f"Error: {e}")
```

### Advanced Usage

```python
from emaillistverify import EmailListVerifyClient

# Initialize with custom timeout
client = EmailListVerifyClient('your-api-key-here', timeout=60)

# Verify multiple emails with custom delay between requests
emails = ['email1@example.com', 'email2@example.com', 'email3@example.com']
results = client.verify_emails(emails, delay=0.5)  # 0.5 second delay between requests

# Process results
valid_emails = [email for email, status in results.items() if status == 'ok']
invalid_emails = [email for email, status in results.items() if status == 'invalid']

print(f"Valid emails: {valid_emails}")
print(f"Invalid emails: {invalid_emails}")
```

## Requirements

- Python 3.8 or higher
- httpx >= 0.27

## API Endpoint

This SDK uses the EmailListVerify API endpoint:
- **URL**: https://apps.emaillistverify.com/api/verifyEmail
- **Method**: GET
- **Parameters**: 
  - `secret` (API key)
  - `email` (email address to verify)

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/EmailListVerify-com/emaillistverify-sdk-python.git
cd emaillistverify-sdk-python

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run code formatting
black .

# Run linting
flake8
```

## License

MIT License - see LICENSE file for details.

## Support

For API documentation and support, visit [EmailListVerify.com](https://emaillistverify.com)
