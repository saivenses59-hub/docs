"""
OVERSIGHT SDK - Type Definitions
EXACT MATCH to backend contract
"""

from typing import Literal
from pydantic import BaseModel, Field


class PaymentResponse(BaseModel):
    """
    Payment response - EXACT match to backend
    
    Backend returns:
    {
        "status": "APPROVED" | "DENIED",
        "new_balance": float,
        "tax_collected": float,
        "vendor_paid": float,
        "detail": str,
        "transaction_id": str,
        "idempotency_key": str,
        "timestamp": str
    }
    """
    status: Literal["APPROVED", "DENIED"]
    new_balance: float
    tax_collected: float
    vendor_paid: float
    detail: str
    transaction_id: str
    idempotency_key: str
    timestamp: str
    
    class Config:
        extra = "allow"


class CreateAgentResponse(BaseModel):
    """Agent creation response"""
    agent_id: str
    name: str
    wallet_address: str
    api_key: str
    balance: float
    created_at: str


class DepositResponse(BaseModel):
    """Deposit response"""
    status: str
    new_balance: float
    amount_deposited: float
    detail: str
    transaction_id: str