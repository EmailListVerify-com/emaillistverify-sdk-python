"""
EmailListVerify Python SDK
A Python wrapper for EmailListVerify REST API
"""

import requests
import json
import time
from typing import Dict, List, Optional, Union
from datetime import datetime
import hashlib
import os


class EmailListVerifyException(Exception):
    """Custom exception for EmailListVerify API errors"""
    pass


class EmailListVerifyClient:
    """Main client for EmailListVerify API"""
    
    BASE_URL = "https://apps.emaillistverify.com/api"
    
    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize EmailListVerify client
        
        Args:
            api_key: Your EmailListVerify API key
            timeout: Request timeout in seconds (default: 30)
        """
        if not api_key:
            raise EmailListVerifyException("API key is required")
        
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EmailListVerify-Python-SDK/1.0.0'
        })
    
    def _make_request(self, endpoint: str, method: str = 'GET', 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None,
                     files: Optional[Dict] = None) -> Union[Dict, str]:
        """
        Make HTTP request to API
        
        Args:
            endpoint: API endpoint
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data
            files: Files to upload
            
        Returns:
            API response as dict or string
            
        Raises:
            EmailListVerifyException: On API errors
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params['secret'] = self.api_key
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
                
        except requests.exceptions.RequestException as e:
            raise EmailListVerifyException(f"Request failed: {str(e)}")
    
    def verify_email(self, email: str) -> Dict:
        """
        Verify a single email address
        
        Args:
            email: Email address to verify
            
        Returns:
            Verification result as dict
            
        Example:
            >>> client = EmailListVerifyClient('your_api_key')
            >>> result = client.verify_email('test@example.com')
            >>> print(result['status'])  # 'ok', 'failed', or 'unknown'
        """
        if not email:
            raise EmailListVerifyException("Email address is required")
        
        result = self._make_request('verifyEmail', params={'email': email})
        
        # Parse response
        if isinstance(result, str):
            # Simple response format
            return {
                'email': email,
                'status': result.strip(),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return result
    
    def verify_email_detailed(self, email: str) -> Dict:
        """
        Verify email with detailed information
        
        Args:
            email: Email address to verify
            
        Returns:
            Detailed verification result
        """
        if not email:
            raise EmailListVerifyException("Email address is required")
        
        return self._make_request('verifyEmailDetailed', params={'email': email})
    
    def get_credits(self) -> Dict:
        """
        Get account credits information
        
        Returns:
            Account credits info
        """
        return self._make_request('getCredits')
    
    def bulk_upload(self, file_path: str, filename: Optional[str] = None) -> str:
        """
        Upload file for bulk verification
        
        Args:
            file_path: Path to CSV file with emails
            filename: Optional custom filename
            
        Returns:
            File ID for tracking
        """
        if not os.path.exists(file_path):
            raise EmailListVerifyException(f"File not found: {file_path}")
        
        if filename is None:
            filename = f"bulk_verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(file_path, 'rb') as f:
            files = {'file_contents': (filename, f, 'text/csv')}
            result = self._make_request(
                'verifApiFile',
                method='POST',
                params={'filename': filename},
                files=files
            )
        
        if isinstance(result, str):
            return result.strip()
        elif isinstance(result, dict) and 'file_id' in result:
            return result['file_id']
        else:
            raise EmailListVerifyException("Failed to get file ID from response")
    
    def get_bulk_status(self, file_id: str) -> Dict:
        """
        Get bulk verification status
        
        Args:
            file_id: File ID from bulk_upload
            
        Returns:
            Verification status and progress
        """
        if not file_id:
            raise EmailListVerifyException("File ID is required")
        
        return self._make_request('getApiFileInfo', params={'file_id': file_id})
    
    def download_bulk_result(self, file_id: str, result_type: str = 'all') -> str:
        """
        Download bulk verification results
        
        Args:
            file_id: File ID from bulk_upload
            result_type: 'all' or 'clean' (default: 'all')
            
        Returns:
            CSV content with results
        """
        if not file_id:
            raise EmailListVerifyException("File ID is required")
        
        if result_type not in ['all', 'clean']:
            raise EmailListVerifyException("result_type must be 'all' or 'clean'")
        
        endpoint = 'downloadApiFile' if result_type == 'all' else 'downloadCleanFile'
        return self._make_request(endpoint, params={'file_id': file_id})
    
    def verify_batch(self, emails: List[str], max_batch_size: int = 100) -> List[Dict]:
        """
        Verify multiple emails in batches
        
        Args:
            emails: List of email addresses
            max_batch_size: Maximum emails per request (default: 100)
            
        Returns:
            List of verification results
        """
        results = []
        
        for i in range(0, len(emails), max_batch_size):
            batch = emails[i:i + max_batch_size]
            
            for email in batch:
                try:
                    result = self.verify_email(email)
                    results.append(result)
                    time.sleep(0.1)  # Rate limiting
                except EmailListVerifyException as e:
                    results.append({
                        'email': email,
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return results
    
    def wait_for_bulk_completion(self, file_id: str, 
                                check_interval: int = 10,
                                max_wait: int = 3600) -> Dict:
        """
        Wait for bulk verification to complete
        
        Args:
            file_id: File ID from bulk_upload
            check_interval: Seconds between status checks (default: 10)
            max_wait: Maximum seconds to wait (default: 3600)
            
        Returns:
            Final status when completed
            
        Raises:
            EmailListVerifyException: On timeout or error
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_bulk_status(file_id)
            
            if status.get('status') == 'completed':
                return status
            elif status.get('status') == 'failed':
                raise EmailListVerifyException(f"Bulk verification failed: {status.get('error', 'Unknown error')}")
            
            time.sleep(check_interval)
        
        raise EmailListVerifyException(f"Timeout waiting for bulk verification (waited {max_wait}s)")


class EmailValidator:
    """Helper class for email validation utilities"""
    
    @staticmethod
    def is_valid_syntax(email: str) -> bool:
        """
        Check if email has valid syntax
        
        Args:
            email: Email address to check
            
        Returns:
            True if syntax is valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def extract_domain(email: str) -> Optional[str]:
        """
        Extract domain from email address
        
        Args:
            email: Email address
            
        Returns:
            Domain part or None
        """
        if '@' in email:
            return email.split('@')[1].lower()
        return None
    
    @staticmethod
    def is_disposable_domain(domain: str) -> bool:
        """
        Check if domain is in common disposable email domains list
        
        Args:
            domain: Domain to check
            
        Returns:
            True if domain appears to be disposable
        """
        # Common disposable email domains (partial list)
        disposable_domains = {
            'tempmail.com', 'throwaway.email', 'guerrillamail.com',
            'mailinator.com', '10minutemail.com', 'trashmail.com',
            'yopmail.com', 'temp-mail.org', 'fakeinbox.com'
        }
        return domain.lower() in disposable_domains


class BulkVerificationManager:
    """Manager for handling bulk email verification workflows"""
    
    def __init__(self, client: EmailListVerifyClient):
        """
        Initialize bulk verification manager
        
        Args:
            client: EmailListVerifyClient instance
        """
        self.client = client
        self.active_jobs = {}
    
    def process_csv_file(self, input_file: str, output_file: str, 
                        wait_for_completion: bool = True) -> Dict:
        """
        Process CSV file with email verification
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to save results
            wait_for_completion: Whether to wait for completion
            
        Returns:
            Job information
        """
        # Upload file
        file_id = self.client.bulk_upload(input_file)
        
        job_info = {
            'file_id': file_id,
            'input_file': input_file,
            'output_file': output_file,
            'start_time': datetime.now().isoformat(),
            'status': 'processing'
        }
        
        self.active_jobs[file_id] = job_info
        
        if wait_for_completion:
            # Wait for completion
            final_status = self.client.wait_for_bulk_completion(file_id)
            
            # Download results
            results = self.client.download_bulk_result(file_id, 'all')
            
            # Save to output file
            with open(output_file, 'w') as f:
                f.write(results)
            
            job_info['status'] = 'completed'
            job_info['end_time'] = datetime.now().isoformat()
            job_info['final_status'] = final_status
        
        return job_info
    
    def get_job_status(self, file_id: str) -> Dict:
        """
        Get status of a verification job
        
        Args:
            file_id: File ID to check
            
        Returns:
            Job status information
        """
        if file_id not in self.active_jobs:
            raise EmailListVerifyException(f"Unknown job ID: {file_id}")
        
        status = self.client.get_bulk_status(file_id)
        self.active_jobs[file_id]['last_status'] = status
        
        return self.active_jobs[file_id]