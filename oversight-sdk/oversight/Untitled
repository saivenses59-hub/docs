"""
OVERSIGHT SDK - Python Client Library
Simple SDK for OVERSIGHT payment processing

Usage:
    >>> from oversight import OversightClient
    >>> 
    >>> client = OversightClient(api_key="ovr_test")
    >>> response = client.pay(
    ...     wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    ...     amount=100.00,
    ...     vendor="OpenAI"
    ... )
    >>> 
    >>> print(f"Status: {response.status}")
    >>> print(f"Vendor paid: ${response.vendor_paid}")
"""

__version__ = "1.0.0"
__author__ = "OVERSIGHT Team"

from .client import OversightClient
from .types import PaymentResponse

__all__ = [
    "OversightClient",
    "PaymentResponse",
]