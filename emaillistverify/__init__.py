"""
EmailListVerify Python SDK
Simple Python wrapper for EmailListVerify REST API
"""

import requests
import time
from typing import List, Dict, Union

__version__ = "1.0.0"
__all__ = ["EmailListVerify", "EmailListVerifyException"]


class EmailListVerifyException(Exception):
    """Exception raised for EmailListVerify API errors."""
    pass


class EmailListVerify:
    """
    EmailListVerify API client for email validation and verification.
    
    This client provides methods to verify single or multiple email addresses
    using the EmailListVerify API.
    """
    
    BASE_URL = "https://apps.emaillistverify.com/api"
    VERSION = "1.0.0"
    
    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize EmailListVerify client.
        
        Args:
            api_key (str): Your EmailListVerify API key
            timeout (int): Request timeout in seconds (default: 30)
            
        Raises:
            EmailListVerifyException: If API key is empty
        """
        if not api_key:
            raise EmailListVerifyException("API key is required")
        
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'EmailListVerify-Python-SDK/{self.VERSION}'
        })
    
    def verify_email(self, email: str) -> str:
        """
        Verify a single email address.
        
        Args:
            email (str): Email address to verify
            
        Returns:
            str: Verification result (ok, invalid, invalid_mx, accept_all, 
                 ok_for_all, disposable, role, email_disabled, dead_server, unknown)
                 
        Raises:
            EmailListVerifyException: If email is empty or request fails
        """
        if not email:
            raise EmailListVerifyException("Email address is required")
        
        url = f"{self.BASE_URL}/verifyEmail"
        params = {
            'secret': self.api_key,
            'email': email
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.text.strip()
            
        except requests.exceptions.RequestException as e:
            raise EmailListVerifyException(f"Request failed: {str(e)}")
    
    def verify_emails(self, emails: List[str], delay: float = 0.1) -> Dict[str, str]:
        """
        Verify multiple email addresses.
        
        Args:
            emails (List[str]): List of email addresses to verify
            delay (float): Delay between requests in seconds (default: 0.1)
            
        Returns:
            Dict[str, str]: Dictionary mapping email addresses to verification results
            
        Raises:
            EmailListVerifyException: If emails is not a list
        """
        if not isinstance(emails, list):
            raise EmailListVerifyException("Emails must be a list")
        
        results = {}
        
        for email in emails:
            try:
                results[email] = self.verify_email(email)
                # Add delay to avoid rate limiting
                if delay > 0:
                    time.sleep(delay)
            except EmailListVerifyException as e:
                results[email] = f"error: {str(e)}"
        
        return results
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()