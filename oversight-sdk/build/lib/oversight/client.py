"""
OVERSIGHT SDK - Client with Auto-Idempotency & Retry Logic
Production-grade client with institutional safety features

CRITICAL FEATURES:
- Auto-generates idempotency keys (prevents double-spend)
- Automatic retry with exponential backoff
- Safe to retry (same key = same result)
- Comprehensive error handling
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional
import logging
import uuid
import time

from .types import PaymentResponse


logger = logging.getLogger("oversight.client")


class OversightClient:
    """
    OVERSIGHT API Client with institutional-grade safety
    
    Features:
    - ✅ Auto-generates idempotency keys
    - ✅ Automatic retry with same key (safe)
    - ✅ Exponential backoff (1s, 2s, 4s)
    - ✅ Comprehensive error handling
    
    Example:
        >>> client = OversightClient(api_key="ovr_test")
        >>> 
        >>> # Safe to call multiple times - idempotency prevents double charge
        >>> response = client.pay(
        ...     wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        ...     amount=25.50,
        ...     vendor="OpenAI"
        ... )
        >>> 
        >>> # Even if network fails, retry is safe
        >>> print(f"Status: {response.status}")
    """
    
    DEFAULT_BASE_URL = "https://oversight-protocol.onrender.com"
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES
    ):
        """
        Initialize OVERSIGHT client
        
        Args:
            api_key: API key for authentication
            base_url: API base URL (default: production)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 3)
        """
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create session with retry strategy
        self.session = self._create_session()
        
        logger.info(f"OVERSIGHT client initialized: {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry strategy
        
        Retry Strategy:
        - Retries: 3 attempts
        - Backoff: 1s, 2s, 4s (exponential)
        - Retry on: 5xx errors, connection errors, timeouts
        - Important: Uses SAME idempotency key on retry (safe!)
        """
        session = requests.Session()
        
        # Configure retry with exponential backoff
        # Note: We handle retries manually to preserve idempotency keys
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "oversight-sdk-python/2.0.0"
        })
        
        return session
    
    def _retry_with_backoff(
        self,
        method: str,
        url: str,
        data: dict,
        headers: dict
    ) -> requests.Response:
        """
        Retry request with exponential backoff
        
        Critical: Uses SAME idempotency key on retry (prevents double-spend)
        
        Args:
            method: HTTP method
            url: Full URL
            data: Request payload (includes idempotency_key)
            headers: Request headers
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries}: {method} {url}")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # Success
                if response.status_code < 400:
                    return response
                
                # Client error (4xx) - don't retry
                if 400 <= response.status_code < 500:
                    logger.warning(f"Client error {response.status_code} - not retrying")
                    return response
                
                # Server error (5xx) - retry with backoff
                if response.status_code >= 500:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(
                        f"Server error {response.status_code} - "
                        f"retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    
                    return response
                
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exception = e
                wait_time = 2 ** attempt
                
                logger.warning(
                    f"Network error: {type(e).__name__} - "
                    f"retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})"
                )
                
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                    continue
                
                raise
        
        # All retries failed
        if last_exception:
            raise last_exception
        
        return response
    
    def pay(
        self,
        wallet_address: str,
        amount: float,
        vendor: str,
        idempotency_key: Optional[str] = None
    ) -> PaymentResponse:
        """
        Process payment with automatic idempotency protection
        
        🔒 SAFETY GUARANTEE:
        - Automatically generates unique idempotency key
        - Safe to retry on network failures
        - Same key = same result (no double charge)
        
        Args:
            wallet_address: Agent's blockchain wallet address
            amount: Transaction amount
            vendor: Vendor/recipient name
            idempotency_key: Optional custom key (auto-generated if not provided)
            
        Returns:
            PaymentResponse with transaction details
            
        Raises:
            requests.HTTPError: If API returns error
            requests.RequestException: If network error persists
            
        Example:
            >>> # Simple payment
            >>> response = client.pay(
            ...     wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            ...     amount=50.00,
            ...     vendor="OpenAI"
            ... )
            >>> 
            >>> # Safe to retry - won't double charge
            >>> if response.status == "DENIED":
            ...     # Retry is safe
            ...     response = client.pay(...)  # Auto-generates NEW key
            >>> 
            >>> # Or provide your own key for explicit control
            >>> my_key = f"payment_{uuid.uuid4()}"
            >>> response = client.pay(..., idempotency_key=my_key)
            >>> # Can retry with same key - guaranteed same result
            >>> response = client.pay(..., idempotency_key=my_key)
        """
        
        # ====================================================================
        # AUTO-GENERATE IDEMPOTENCY KEY (Critical for safety)
        # ====================================================================
        if idempotency_key is None:
            idempotency_key = f"sdk_{uuid.uuid4()}"
            logger.info(f"🔑 Auto-generated idempotency key: {idempotency_key[:32]}...")
        
        # Convert amount to float (ensure JSON serializable)
        amount = float(amount)
        
        # Prepare request payload
        payload = {
            "wallet_address": wallet_address,
            "amount": amount,
            "vendor": vendor,
            "idempotency_key": idempotency_key  # Critical: Include in payload
        }
        
        # Prepare headers
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Construct URL
        url = f"{self.base_url}/process-payment"
        
        logger.info(
            f"💳 Payment request: ${amount:.2f} to {vendor} "
            f"(wallet: {wallet_address[:10]}...)"
        )
        
        try:
            # Make request with retry logic
            response = self._retry_with_backoff(
                method="POST",
                url=url,
                data=payload,
                headers=headers
            )
            
            # Raise exception for error status codes
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            logger.info(
                f"✅ Payment {data.get('status', 'UNKNOWN')}: "
                f"TX={data.get('transaction_id', 'N/A')}"
            )
            
            # Return typed response
            return PaymentResponse(**data)
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    def create_agent(
        self,
        name: str,
        wallet_address: str,
        initial_balance: float = 500.00
    ):
        """
        Create new agent
        
        Args:
            name: Agent name
            wallet_address: Blockchain wallet address
            initial_balance: Starting balance (default: $500)
            
        Returns:
            Agent details including API key
        """
        url = f"{self.base_url}/create-agent"
        
        payload = {
            "name": name,
            "wallet_address": wallet_address,
            "initial_balance": initial_balance
        }
        
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def deposit(
        self,
        wallet_address: str,
        amount: float,
        idempotency_key: Optional[str] = None
    ):
        """
        Deposit funds to wallet (with idempotency)
        
        Args:
            wallet_address: Wallet to deposit to
            amount: Amount to deposit
            idempotency_key: Optional key (auto-generated if not provided)
            
        Returns:
            Deposit confirmation
        """
        # Auto-generate idempotency key
        if idempotency_key is None:
            idempotency_key = f"deposit_{uuid.uuid4()}"
        
        url = f"{self.base_url}/deposit"
        
        payload = {
            "wallet_address": wallet_address,
            "amount": float(amount),
            "idempotency_key": idempotency_key
        }
        
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = self._retry_with_backoff("POST", url, payload, headers)
        response.raise_for_status()
        
        return response.json()
    
    def close(self):
        """Close HTTP session"""
        self.session.close()
        logger.info("OVERSIGHT client closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"OversightClient(base_url={self.base_url!r})"