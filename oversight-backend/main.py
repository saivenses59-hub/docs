import os
import requests
import secrets
import io
import csv
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 1. Load Secrets
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Missing Credentials")

# 2. Database Helper
def supabase_request(method, table, data=None, params=None):
    endpoint = f"{url}/rest/v1/{table}"
    if params: endpoint += f"?{params}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    if method == "POST": response = requests.post(endpoint, json=data, headers=headers)
    elif method == "GET": response = requests.get(endpoint, headers=headers)
    elif method == "PATCH": response = requests.patch(endpoint, json=data, headers=headers)
    
    try:
        response.raise_for_status()
        return response.json()
    except:
        return []

# 3. Initialize App
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONFIG
ORGANIZATION_TAX_RATE = 0.10
GOVERNMENT_VAULT = "0x_IRS_TAX_VAULT_000000000000000000" 

# 4. Models
class OrganizationRegister(BaseModel):
    name: str
    tax_id: str

class Agent(BaseModel):
    name: str
    organization_id: str

class DepositRequest(BaseModel):
    wallet_address: str
    amount: float

class SpendRequest(BaseModel):
    wallet_address: str
    amount: float
    vendor: str

def generate_eth_address():
    return "0x" + secrets.token_hex(20)

# 5. ENDPOINTS

@app.post("/register-org")
def register_org(org: OrganizationRegister):
    try:
        org_data = {"name": org.name, "tax_id": org.tax_id, "is_verified": True}
        res = supabase_request("POST", "organizations", org_data)
        return {"status": "SUCCESS", "org_id": res[0]['id'], "name": res[0]['name']}
    except Exception as e: return {"status": "ERROR", "detail": str(e)}

@app.get("/agents")
def get_agents():
    try:
        raw_data = supabase_request("GET", "agents", params="select=*,wallets(*),organizations(*)")
        formatted_list = []
        for agent in raw_data:
            wallet_list = agent.get('wallets', [])
            org = agent.get('organizations', {})
            org_name = org.get('name') if org else "Unregistered"
            if wallet_list:
                wallet = wallet_list[0]
                formatted_list.append({
                    "name": agent['name'], "org": org_name,
                    "wallet": wallet['wallet_address'], "balance": wallet['balance_usd'],
                    "limit": wallet.get('max_transaction_limit', 50), "time": agent['created_at']
                })
        formatted_list.reverse()
        return {"status": "SUCCESS", "data": formatted_list}
    except Exception as e: return {"status": "ERROR", "detail": str(e)}

@app.post("/create-agent")
def create_agent(agent: Agent):
    try:
        # Check Org Verification
        org_res = supabase_request("GET", "organizations", params=f"id=eq.{agent.organization_id}")
        if not org_res or org_res[0]['is_verified'] is False:
             return {"status": "DENIED", "detail": "ORGANIZATION NOT VERIFIED"}

        agent_data = {"name": agent.name, "is_active": True, "organization_id": agent.organization_id}
        agent_res = supabase_request("POST", "agents", agent_data)
        new_agent_id = agent_res[0]['id']

        wallet_data = {
            "agent_id": new_agent_id, "wallet_address": generate_eth_address(),
            "balance_usd": 0, "max_transaction_limit": 50.00, "network": "base-mainnet"
        }
        res = supabase_request("POST", "wallets", wallet_data)
        
        return {"status": "SUCCESS", "agent": agent.name, "wallet_address": res[0]['wallet_address']}
    except Exception as e: return {"status": "ERROR", "detail": str(e)}

@app.post("/deposit")
def deposit(req: DepositRequest):
    try:
        filter_query = f"wallet_address=eq.{req.wallet_address}"
        current_wallet = supabase_request("GET", "wallets", params=filter_query)
        if not current_wallet: raise HTTPException(status_code=404) 
        new_bal = float(current_wallet[0]['balance_usd']) + req.amount
        supabase_request("PATCH", "wallets", {"balance_usd": new_bal}, params=filter_query)
        return {"status": "SUCCESS", "new_balance": new_bal}
    except Exception as e: return {"status": "ERROR", "detail": str(e)}

@app.post("/process-payment")
def process_payment(req: SpendRequest):
    try:
        filter_query = f"wallet_address=eq.{req.wallet_address}"
        current_wallet = supabase_request("GET", "wallets", params=filter_query)
        if not current_wallet: raise HTTPException(status_code=404)
        wallet = current_wallet[0]
        bal = float(wallet['balance_usd'])
        limit = float(wallet.get('max_transaction_limit', 50.00))
        
        # Rule Checks
        if req.amount > limit:
             supabase_request("POST", "transactions", {
                "agent_id": wallet['agent_id'], "wallet_id": wallet['id'],
                "amount": req.amount, "currency": "USD", "status": "DENIED",
                "to_address": req.vendor, "metadata": {"reason": "Over Limit"}
            })
             return {"status": "DENIED", "detail": f"OVER LIMIT (Max: ${limit})"}
        
        if bal < req.amount: return {"status": "DENIED", "detail": "INSUFFICIENT FUNDS"}

        # Tax Split
        tax = req.amount * ORGANIZATION_TAX_RATE
        vendor_amt = req.amount - tax
        new_bal = bal - req.amount
        
        supabase_request("PATCH", "wallets", {"balance_usd": new_bal}, params=filter_query)
        
        # Log Transactions
        supabase_request("POST", "transactions", {
            "agent_id": wallet['agent_id'], "wallet_id": wallet['id'],
            "amount": vendor_amt, "currency": "USD", "status": "COMPLETED",
            "to_address": req.vendor, "metadata": {"type": "VENDOR_PAYMENT"}
        })
        supabase_request("POST", "transactions", {
            "agent_id": wallet['agent_id'], "wallet_id": wallet['id'],
            "amount": tax, "currency": "USD", "status": "COMPLETED",
            "to_address": GOVERNMENT_VAULT, "metadata": {"type": "TAX_WITHHOLDING"}
        })
        
        return {"status": "APPROVED", "new_balance": new_bal, "tax_collected": tax, "vendor_paid": vendor_amt}
    except Exception as e: return {"status": "ERROR", "detail": str(e)}

# --- NEW: AUDIT EXPORT ---
@app.get("/export-audit")
def export_audit():
    try:
        # Fetch Data (Simulated join for CSV)
        txs = supabase_request("GET", "transactions", params="select=*,agents(name),wallets(wallet_address)")
        
        # Create CSV
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["TIMESTAMP", "AGENT", "WALLET", "TYPE", "AMOUNT", "STATUS", "RECIPIENT", "METADATA"])
        
        for tx in txs:
            agent_name = tx.get('agents', {}).get('name', 'Unknown') if tx.get('agents') else 'Unknown'
            wallet_addr = tx.get('wallets', {}).get('wallet_address', 'Unknown') if tx.get('wallets') else 'Unknown'
            meta = tx.get('metadata', {})
            tx_type = meta.get('type', 'Standard')
            
            writer.writerow([
                tx['created_at'], agent_name, wallet_addr, tx_type, 
                tx['amount'], tx['status'], tx['to_address'], str(meta)
            ])
            
        stream.seek(0)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=OVERSIGHT_AUDIT_LOG.csv"
        return response
    except Exception as e: return {"status": "ERROR", "detail": str(e)}

@app.get("/")
def home(): return {"message": "OVERSIGHT SYSTEM ONLINE"}