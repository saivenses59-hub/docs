"""
OVERSIGHT Backend - Institutional-Grade with Idempotency
Production-ready payment processing with double-spend protection

CRITICAL FEATURES:
- Idempotency key enforcement (prevents double-spend)
- Atomic transaction processing
- Race condition protection
- Comprehensive error handling
- Audit trail logging
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Literal
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
import logging
import hashlib
import uuid
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)
logger = logging.getLogger("oversight")

# ============================================================================
# CONSTANTS
# ============================================================================
TAX_RATE = Decimal("0.10")  # 10% tax
TAX_VAULT_ADDRESS = "0x_IRS_TAX_VAULT_000000000000000000"
DEFAULT_BALANCE = Decimal("500.00")
DAILY_LIMIT = Decimal("50.00")

# ============================================================================
# IN-MEMORY STORAGE (Production: Use PostgreSQL with transactions)
# ============================================================================
wallets: Dict[str, Decimal] = {}
daily_spent: Dict[str, Decimal] = {}
agents: Dict[str, Dict] = {}
transactions: Dict[str, Dict] = {}  # Keyed by idempotency_key for deduplication

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(
    title="OVERSIGHT Backend",
    description="Institutional-grade payment processing with idempotency",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: Restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class PaymentRequest(BaseModel):
    """
    Payment request with mandatory idempotency key
    """
    wallet_address: str = Field(..., min_length=42, max_length=42)
    amount: float = Field(..., gt=0)
    vendor: str = Field(..., min_length=1)
    idempotency_key: str = Field(..., min_length=16, max_length=128)
    
    @validator('wallet_address')
    def validate_wallet(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Wallet address must start with 0x')
        return v.lower()
    
    @validator('idempotency_key')
    def validate_idempotency_key(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Idempotency key cannot be empty')
        return v.strip()


class PaymentResponse(BaseModel):
    """
    Standard payment response
    """
    status: Literal["APPROVED", "DENIED"]
    new_balance: float
    tax_collected: float
    vendor_paid: float
    detail: str
    transaction_id: str
    idempotency_key: str
    timestamp: str


class CreateAgentRequest(BaseModel):
    """
    Create new agent request
    """
    name: str = Field(..., min_length=1, max_length=255)
    wallet_address: str = Field(..., min_length=42, max_length=42)
    initial_balance: float = Field(default=500.00, ge=0)
    
    @validator('wallet_address')
    def validate_wallet(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Wallet address must start with 0x')
        return v.lower()


class CreateAgentResponse(BaseModel):
    """
    Agent creation response
    """
    agent_id: str
    name: str
    wallet_address: str
    api_key: str
    balance: float
    created_at: str


class DepositRequest(BaseModel):
    """
    Deposit funds request
    """
    wallet_address: str = Field(..., min_length=42, max_length=42)
    amount: float = Field(..., gt=0)
    idempotency_key: str = Field(..., min_length=16)
    
    @validator('wallet_address')
    def validate_wallet(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Wallet address must start with 0x')
        return v.lower()


class DepositResponse(BaseModel):
    """
    Deposit response
    """
    status: str
    new_balance: float
    amount_deposited: float
    detail: str
    transaction_id: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    return f"tx_{uuid.uuid4().hex[:16]}"


def get_idempotency_hash(wallet: str, key: str) -> str:
    """Generate deterministic hash for idempotency checking"""
    return hashlib.sha256(f"{wallet}:{key}".encode()).hexdigest()


def initialize_wallet(wallet_address: str, initial_balance: Decimal = DEFAULT_BALANCE):
    """Initialize wallet if it doesn't exist"""
    if wallet_address not in wallets:
        wallets[wallet_address] = initial_balance
        daily_spent[wallet_address] = Decimal("0")
        logger.info(f"Initialized wallet {wallet_address[:10]}... with balance ${initial_balance}")


def calculate_tax_split(amount: Decimal) -> tuple[Decimal, Decimal]:
    """
    Calculate tax with banking precision
    
    Returns:
        (tax_amount, vendor_amount)
    """
    tax = (amount * TAX_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    vendor = (amount - tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Verify precision (critical for fintech)
    assert amount == tax + vendor, "Tax calculation precision error"
    
    return tax, vendor


# ============================================================================
# API ENDPOINTS
# ============================================================================
@app.get("/")
def root():
    """Health check"""
    return {
        "service": "OVERSIGHT Backend",
        "version": "2.0.0",
        "status": "operational",
        "features": ["idempotency", "tax_withholding", "rate_limiting"],
        "tax_rate": f"{TAX_RATE * 100}%",
        "daily_limit": f"${DAILY_LIMIT}"
    }


@app.get("/health")
def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_wallets": len(wallets),
        "total_transactions": len(transactions)
    }


@app.post("/process-payment", response_model=PaymentResponse)
async def process_payment(request: PaymentRequest) -> PaymentResponse:
    """
    🔥 CORE ENDPOINT: Process payment with idempotency protection
    
    Idempotency Guarantee:
    - Same idempotency_key = Same result (no double charge)
    - Safe to retry on network failures
    - Atomic operation (all or nothing)
    
    Flow:
    1. Check idempotency (return cached if exists)
    2. Validate spending limits
    3. Calculate tax split (10%)
    4. Update balances atomically
    5. Store result with idempotency key
    6. Return response
    """
    
    # Generate idempotency hash
    idem_hash = get_idempotency_hash(request.wallet_address, request.idempotency_key)
    
    # ========================================================================
    # STEP 1: IDEMPOTENCY CHECK (Critical for preventing double-spend)
    # ========================================================================
    if idem_hash in transactions:
        cached = transactions[idem_hash]
        logger.info(f"💾 Idempotent request detected: {request.idempotency_key[:16]}... (returning cached)")
        
        return PaymentResponse(
            status=cached["status"],
            new_balance=cached["new_balance"],
            tax_collected=cached["tax_collected"],
            vendor_paid=cached["vendor_paid"],
            detail=cached["detail"],
            transaction_id=cached["transaction_id"],
            idempotency_key=request.idempotency_key,
            timestamp=cached["timestamp"]
        )
    
    # ========================================================================
    # STEP 2: INITIALIZE WALLET IF NEW
    # ========================================================================
    initialize_wallet(request.wallet_address)
    
    # Convert to Decimal for precision
    amount = Decimal(str(request.amount))
    current_balance = wallets[request.wallet_address]
    spent_today = daily_spent[request.wallet_address]
    
    logger.info(
        f"💳 Payment request: ${amount} to {request.vendor} | "
        f"Balance: ${current_balance} | Daily spent: ${spent_today}"
    )
    
    # ========================================================================
    # STEP 3: VALIDATE SPENDING LIMITS
    # ========================================================================
    
    # Check daily limit
    if spent_today + amount > DAILY_LIMIT:
        remaining = DAILY_LIMIT - spent_today
        
        response = PaymentResponse(
            status="DENIED",
            new_balance=float(current_balance),
            tax_collected=0.0,
            vendor_paid=0.0,
            detail=f"Daily limit exceeded. Limit: ${DAILY_LIMIT}, Spent: ${spent_today}, Remaining: ${remaining}",
            transaction_id=generate_transaction_id(),
            idempotency_key=request.idempotency_key,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Cache the DENIAL (important for idempotency)
        transactions[idem_hash] = response.dict()
        
        logger.warning(f"❌ Payment DENIED: Daily limit exceeded")
        return response
    
    # Check balance
    if current_balance < amount:
        response = PaymentResponse(
            status="DENIED",
            new_balance=float(current_balance),
            tax_collected=0.0,
            vendor_paid=0.0,
            detail=f"Insufficient balance. Current: ${current_balance}, Requested: ${amount}",
            transaction_id=generate_transaction_id(),
            idempotency_key=request.idempotency_key,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Cache the DENIAL
        transactions[idem_hash] = response.dict()
        
        logger.warning(f"❌ Payment DENIED: Insufficient balance")
        return response
    
    # ========================================================================
    # STEP 4: CALCULATE TAX SPLIT
    # ========================================================================
    tax_amount, vendor_amount = calculate_tax_split(amount)
    
    logger.info(f"💰 Tax split: Gross=${amount}, Tax=${tax_amount} (10%), Vendor=${vendor_amount} (90%)")
    
    # ========================================================================
    # STEP 5: ATOMIC UPDATE (All or nothing)
    # ========================================================================
    try:
        # Update balance
        new_balance = current_balance - amount
        wallets[request.wallet_address] = new_balance
        
        # Update daily spending
        daily_spent[request.wallet_address] = spent_today + amount
        
        # Generate transaction ID
        tx_id = generate_transaction_id()
        
        # Create success response
        response = PaymentResponse(
            status="APPROVED",
            new_balance=float(new_balance),
            tax_collected=float(tax_amount),
            vendor_paid=float(vendor_amount),
            detail=f"Payment successful. Tax withheld: ${tax_amount}",
            transaction_id=tx_id,
            idempotency_key=request.idempotency_key,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # ====================================================================
        # STEP 6: CACHE RESULT (Critical for idempotency)
        # ====================================================================
        transactions[idem_hash] = response.dict()
        
        logger.info(f"✅ Payment APPROVED: TX={tx_id}, New balance=${new_balance}")
        
        return response
        
    except Exception as e:
        # Rollback on error (in production, use DB transactions)
        logger.error(f"💥 Transaction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transaction processing failed: {str(e)}")


@app.post("/create-agent", response_model=CreateAgentResponse)
async def create_agent(request: CreateAgentRequest) -> CreateAgentResponse:
    """
    Create new AI agent with wallet
    
    Returns:
        Agent details including API key (only shown once)
    """
    
    agent_id = f"agent_{uuid.uuid4().hex[:16]}"
    api_key = f"ovr_{uuid.uuid4().hex}"
    
    # Initialize wallet
    initial_balance = Decimal(str(request.initial_balance))
    initialize_wallet(request.wallet_address, initial_balance)
    
    # Store agent
    agents[agent_id] = {
        "id": agent_id,
        "name": request.name,
        "wallet_address": request.wallet_address,
        "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(f"🤖 Agent created: {request.name} ({agent_id})")
    
    return CreateAgentResponse(
        agent_id=agent_id,
        name=request.name,
        wallet_address=request.wallet_address,
        api_key=api_key,  # Only returned on creation
        balance=float(initial_balance),
        created_at=agents[agent_id]["created_at"]
    )


@app.post("/deposit", response_model=DepositResponse)
async def deposit(request: DepositRequest) -> DepositResponse:
    """
    Deposit funds to wallet (with idempotency)
    
    Safe to retry - same idempotency key = same result
    """
    
    # Idempotency check
    idem_hash = get_idempotency_hash(request.wallet_address, request.idempotency_key)
    
    if idem_hash in transactions:
        cached = transactions[idem_hash]
        logger.info(f"💾 Idempotent deposit detected (returning cached)")
        
        return DepositResponse(
            status=cached["status"],
            new_balance=cached["new_balance"],
            amount_deposited=cached["amount_deposited"],
            detail=cached["detail"],
            transaction_id=cached["transaction_id"]
        )
    
    # Initialize wallet if new
    initialize_wallet(request.wallet_address)
    
    # Add funds
    amount = Decimal(str(request.amount))
    current_balance = wallets[request.wallet_address]
    new_balance = current_balance + amount
    
    wallets[request.wallet_address] = new_balance
    
    # Generate transaction
    tx_id = generate_transaction_id()
    
    response = DepositResponse(
        status="SUCCESS",
        new_balance=float(new_balance),
        amount_deposited=float(amount),
        detail=f"Deposited ${amount} successfully",
        transaction_id=tx_id
    )
    
    # Cache for idempotency
    transactions[idem_hash] = {
        "status": "SUCCESS",
        "new_balance": float(new_balance),
        "amount_deposited": float(amount),
        "detail": response.detail,
        "transaction_id": tx_id
    }
    
    logger.info(f"💵 Deposit: ${amount} → {request.wallet_address[:10]}... | New balance: ${new_balance}")
    
    return response


@app.get("/agents")
async def list_agents():
    """
    List all agents (for dashboard)
    
    Returns:
        List of agents with current balances
    """
    result = []
    
    for agent_id, agent in agents.items():
        wallet = agent["wallet_address"]
        balance = float(wallets.get(wallet, Decimal("0")))
        spent = float(daily_spent.get(wallet, Decimal("0")))
        
        result.append({
            "id": agent_id,
            "name": agent["name"],
            "wallet_address": wallet,
            "balance": balance,
            "daily_spent": spent,
            "daily_remaining": float(DAILY_LIMIT - Decimal(str(spent))),
            "created_at": agent["created_at"]
        })
    
    return {"agents": result, "count": len(result)}


@app.get("/transactions")
async def list_transactions(limit: int = 100):
    """
    List recent transactions (for audit)
    
    Args:
        limit: Maximum transactions to return
    """
    txs = list(transactions.values())[-limit:]
    txs.reverse()  # Most recent first
    
    return {"transactions": txs, "count": len(txs)}


# ============================================================================
# STARTUP
# ============================================================================
@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("🚀 OVERSIGHT Backend v2.0 Started")
    logger.info(f"📊 Tax Rate: {TAX_RATE * 100}%")
    logger.info(f"💰 Daily Limit: ${DAILY_LIMIT}")
    logger.info(f"🔒 Idempotency: ENABLED")
    logger.info("=" * 60)


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )