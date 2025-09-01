"""
EmailListVerify API Client
"""

from typing import Optional, Dict, Any, List
import httpx
import time
from datetime import datetime
import os


DEFAULT_BASE_URL = "https://apps.emaillistverify.com/api"


class EmailListVerifyError(Exception):
    """Exception raised for EmailListVerify API errors"""
    pass


class EmailListVerifyClient:
    """
    EmailListVerify API client for email verification and validation.
    
    This client provides methods to verify single or multiple email addresses,
    perform bulk verification, and manage account credits using the EmailListVerify API.
    """
    
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        """
        Initialize EmailListVerify client.
        
        Args:
            api_key: Your EmailListVerify API key
            base_url: API base URL (default: https://apps.emaillistverify.com/api)
            timeout: Request timeout in seconds (default: 30.0)
            
        Raises:
            EmailListVerifyError: If API key is empty
        """
        if not api_key:
            raise EmailListVerifyError("API key is required")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "User-Agent": "EmailListVerify-Python-SDK/1.0.0",
            }
        )
    
    def _url(self, path: str) -> str:
        """Build full URL for API endpoint"""
        return f"{self.base_url}/{path.lstrip('/')}"
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None,
                     files: Optional[Dict] = None) -> Any:
        """
        Make HTTP request to API
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            data: Request body data
            files: Files to upload
            
        Returns:
            Response data
            
        Raises:
            EmailListVerifyError: On API errors
        """
        url = self._url(endpoint)
        
        if params is None:
            params = {}
        params["secret"] = self.api_key
        
        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files
            )
            
            if response.status_code == 401:
                raise EmailListVerifyError("Unauthorized: invalid API key")
            
            response.raise_for_status()
            
            # Try to parse JSON response, fallback to text
            try:
                return response.json()
            except ValueError:
                return response.text.strip()
                
        except httpx.HTTPError as e:
            raise EmailListVerifyError(f"Request failed: {str(e)}") from e
    
    def verify_email(self, email: str) -> str:
        """
        Verify a single email address.
        
        Args:
            email: Email address to verify
            
        Returns:
            Verification result (ok, invalid, invalid_mx, accept_all, 
            ok_for_all, disposable, role, email_disabled, dead_server, unknown)
            
        Raises:
            EmailListVerifyError: If email is empty or request fails
        """
        if not email:
            raise EmailListVerifyError("Email address is required")
        
        result = self._make_request("verifyEmail", params={"email": email})
        return result if isinstance(result, str) else str(result)
    
    def verify_email_detailed(self, email: str) -> Dict[str, Any]:
        """
        Verify email with detailed information.
        
        Args:
            email: Email address to verify
            
        Returns:
            Detailed verification result
            
        Raises:
            EmailListVerifyError: If email is empty or request fails
        """
        if not email:
            raise EmailListVerifyError("Email address is required")
        
        result = self._make_request("verifyEmailDetailed", params={"email": email})
        
        if isinstance(result, str):
            return {
                "email": email,
                "status": result,
                "timestamp": datetime.now().isoformat()
            }
        return result
    
    def verify_emails(self, emails: List[str], delay: float = 0.1) -> Dict[str, str]:
        """
        Verify multiple email addresses.
        
        Args:
            emails: List of email addresses to verify
            delay: Delay between requests in seconds (default: 0.1)
            
        Returns:
            Dictionary mapping email addresses to verification results
            
        Raises:
            EmailListVerifyError: If emails is not a list
        """
        if not isinstance(emails, list):
            raise EmailListVerifyError("Emails must be a list")
        
        results = {}
        
        for email in emails:
            try:
                results[email] = self.verify_email(email)
                if delay > 0:
                    time.sleep(delay)
            except EmailListVerifyError as e:
                results[email] = f"error: {str(e)}"
        
        return results
    
    def get_credits(self) -> Dict[str, Any]:
        """
        Get account credits information.
        
        Returns:
            Account credits info
        """
        result = self._make_request("getCredits")
        
        if isinstance(result, str):
            return {"credits": result}
        return result
    
    def bulk_upload(self, file_path: str, filename: Optional[str] = None) -> str:
        """
        Upload file for bulk verification.
        
        Args:
            file_path: Path to CSV file with emails
            filename: Optional custom filename
            
        Returns:
            File ID for tracking
            
        Raises:
            EmailListVerifyError: If file doesn't exist or upload fails
        """
        if not os.path.exists(file_path):
            raise EmailListVerifyError(f"File not found: {file_path}")
        
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
            return result
        elif isinstance(result, dict) and 'file_id' in result:
            return result['file_id']
        else:
            raise EmailListVerifyError("Failed to get file ID from response")
    
    def get_bulk_status(self, file_id: str) -> Dict[str, Any]:
        """
        Get bulk verification status.
        
        Args:
            file_id: File ID from bulk_upload
            
        Returns:
            Verification status and progress
        """
        if not file_id:
            raise EmailListVerifyError("File ID is required")
        
        return self._make_request('getApiFileInfo', params={'file_id': file_id})
    
    def download_bulk_result(self, file_id: str, result_type: str = 'all') -> str:
        """
        Download bulk verification results.
        
        Args:
            file_id: File ID from bulk_upload
            result_type: 'all' or 'clean' (default: 'all')
            
        Returns:
            CSV content with results
        """
        if not file_id:
            raise EmailListVerifyError("File ID is required")
        
        if result_type not in ['all', 'clean']:
            raise EmailListVerifyError("result_type must be 'all' or 'clean'")
        
        endpoint = 'downloadApiFile' if result_type == 'all' else 'downloadCleanFile'
        return self._make_request(endpoint, params={'file_id': file_id})
    
    def wait_for_bulk_completion(self, file_id: str, 
                                check_interval: int = 10,
                                max_wait: int = 3600) -> Dict[str, Any]:
        """
        Wait for bulk verification to complete.
        
        Args:
            file_id: File ID from bulk_upload
            check_interval: Seconds between status checks (default: 10)
            max_wait: Maximum seconds to wait (default: 3600)
            
        Returns:
            Final status when completed
            
        Raises:
            EmailListVerifyError: On timeout or error
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_bulk_status(file_id)
            
            if status.get('status') == 'completed':
                return status
            elif status.get('status') == 'failed':
                raise EmailListVerifyError(f"Bulk verification failed: {status.get('error', 'Unknown error')}")
            
            time.sleep(check_interval)
        
        raise EmailListVerifyError(f"Timeout waiting for bulk verification (waited {max_wait}s)")
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()