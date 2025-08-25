"""
EmailListVerify Python SDK Examples
"""

from emaillistverify import EmailListVerifyClient, EmailValidator, BulkVerificationManager


def example_single_verification():
    """Example: Verify a single email address"""
    
    # Initialize client with your API key
    client = EmailListVerifyClient('YOUR_API_KEY_HERE')
    
    # Verify single email
    result = client.verify_email('test@example.com')
    print(f"Email: {result['email']}")
    print(f"Status: {result['status']}")
    print(f"Timestamp: {result['timestamp']}")
    
    # Verify with detailed information
    detailed_result = client.verify_email_detailed('test@example.com')
    print(f"Detailed result: {detailed_result}")


def example_batch_verification():
    """Example: Verify multiple emails in batch"""
    
    client = EmailListVerifyClient('YOUR_API_KEY_HERE')
    
    # List of emails to verify
    emails = [
        'valid@example.com',
        'invalid@fake-domain-123456.com',
        'test@gmail.com',
        'info@company.com'
    ]
    
    # Verify batch
    results = client.verify_batch(emails, max_batch_size=50)
    
    # Process results
    for result in results:
        status = result.get('status', 'unknown')
        email = result.get('email', '')
        print(f"{email}: {status}")


def example_bulk_file_verification():
    """Example: Bulk verify emails from CSV file"""
    
    client = EmailListVerifyClient('YOUR_API_KEY_HERE')
    manager = BulkVerificationManager(client)
    
    # Process CSV file
    job_info = manager.process_csv_file(
        input_file='emails.csv',
        output_file='verified_emails.csv',
        wait_for_completion=True
    )
    
    print(f"Job completed: {job_info['file_id']}")
    print(f"Results saved to: {job_info['output_file']}")


def example_async_bulk_verification():
    """Example: Start bulk verification without waiting"""
    
    client = EmailListVerifyClient('YOUR_API_KEY_HERE')
    
    # Upload file for verification
    file_id = client.bulk_upload('emails.csv', 'my_email_list.csv')
    print(f"File uploaded with ID: {file_id}")
    
    # Check status periodically
    import time
    
    while True:
        status = client.get_bulk_status(file_id)
        print(f"Status: {status.get('status')}")
        print(f"Progress: {status.get('progress', 0)}%")
        
        if status.get('status') == 'completed':
            # Download results
            all_results = client.download_bulk_result(file_id, 'all')
            clean_results = client.download_bulk_result(file_id, 'clean')
            
            # Save results
            with open('all_results.csv', 'w') as f:
                f.write(all_results)
            
            with open('clean_results.csv', 'w') as f:
                f.write(clean_results)
            
            print("Results downloaded successfully!")
            break
        
        time.sleep(10)  # Wait 10 seconds before next check


def example_email_validation():
    """Example: Use validation utilities"""
    
    validator = EmailValidator()
    
    emails = [
        'valid@example.com',
        'invalid-email',
        'test@tempmail.com',
        'user@gmail.com'
    ]
    
    for email in emails:
        print(f"\nEmail: {email}")
        print(f"Valid syntax: {validator.is_valid_syntax(email)}")
        
        domain = validator.extract_domain(email)
        if domain:
            print(f"Domain: {domain}")
            print(f"Disposable: {validator.is_disposable_domain(domain)}")


def example_get_credits():
    """Example: Check account credits"""
    
    client = EmailListVerifyClient('YOUR_API_KEY_HERE')
    
    credits = client.get_credits()
    print(f"Available credits: {credits.get('credits', 0)}")
    print(f"Used credits: {credits.get('used_credits', 0)}")
    print(f"Free credits: {credits.get('free_credits', 0)}")


def example_error_handling():
    """Example: Handle API errors properly"""
    
    from emaillistverify import EmailListVerifyException
    
    client = EmailListVerifyClient('YOUR_API_KEY_HERE')
    
    try:
        # Attempt to verify email
        result = client.verify_email('test@example.com')
        
        if result['status'] == 'ok':
            print("Email is valid!")
        elif result['status'] == 'failed':
            print("Email verification failed")
        else:
            print(f"Unknown status: {result['status']}")
            
    except EmailListVerifyException as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run examples (remember to set your API key first)
    print("EmailListVerify Python SDK Examples")
    print("=" * 40)
    
    # Uncomment to run examples:
    # example_single_verification()
    # example_batch_verification()
    # example_bulk_file_verification()
    # example_email_validation()
    # example_get_credits()
    # example_error_handling()