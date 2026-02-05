"""
OVERSIGHT SDK - Type Definitions
Matches the existing backend API contract exactly
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class PaymentResponse(BaseModel):
    """
    Payment response from OVERSIGHT backend
    
    Matches exact API contract:
    POST /process-payment returns:
    {
        "status": "APPROVED" | "DENIED",
        "new_balance": float,
        "tax_collected": float,
        "vendor_paid": float,
        "detail": str
    }
    
    Attributes:
        status: Payment status (APPROVED or DENIED)
        new_balance: Agent's wallet balance after transaction
        tax_collected: Amount withheld as tax (10%)
        vendor_paid: Amount sent to vendor (90%)
        detail: Human-readable transaction description
    
    Example:
        >>> response = PaymentResponse(
        ...     status="APPROVED",
        ...     new_balance=450.00,
        ...     tax_collected=10.00,
        ...     vendor_paid=90.00,
        ...     detail="Payment successful"
        ... )
    """
    status: Literal["APPROVED", "DENIED"] = Field(
        ...,
        description="Payment approval status"
    )
    new_balance: float = Field(
        ...,
        description="Wallet balance after transaction"
    )
    tax_collected: float = Field(
        ...,
        description="Tax amount withheld (10%)"
    )
    vendor_paid: float = Field(
        ...,
        description="Amount paid to vendor (90%)"
    )
    detail: str = Field(
        ...,
        description="Transaction detail message"
    )
    
    class Config:
        # Allow extra fields in case backend adds more
        extra = "allow"
        json_schema_extra = {
            "example": {
                "status": "APPROVED",
                "new_balance": 450.00,
                "tax_collected": 10.00,
                "vendor_paid": 90.00,
                "detail": "Payment successful. Tax withheld: $10.00"
            }
        }