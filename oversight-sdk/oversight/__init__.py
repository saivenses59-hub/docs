"""
OVERSIGHT SDK - Python Client Library
Matches institutional backend contract exactly

Endpoint: POST /process-payment
Payload: {wallet_address, amount, vendor, idempotency_key}
"""

__version__ = "2.0.0"

from .client import OversightClient
from .types import PaymentResponse, CreateAgentResponse, DepositResponse

__all__ = [
    "OversightClient",
    "PaymentResponse",
    "CreateAgentResponse",
    "DepositResponse",
]