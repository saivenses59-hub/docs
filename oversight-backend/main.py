import os
import requests
import secrets
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    
    if params:
        endpoint += f"?{params}"
        
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    if method == "POST":
        response = requests.post(endpoint, json=data, headers=headers)
    elif method == "GET":
        response = requests.get(endpoint, headers=headers)
    elif method == "PATCH":
        response = requests.patch(endpoint, json=data, headers=headers)
        
    return response.json()

# 3. Initialize App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Data Models
class Agent(BaseModel):
    name: str

class DepositRequest(BaseModel):
    wallet_address: str
    amount: float

class SpendRequest(BaseModel):
    wallet_address: str
    amount: float
    vendor: str

# 5. Helper
def generate_eth_address():
    return "0x" + secrets.token_hex(20)

# 6. ENDPOINTS

@app.get("/agents")
def get_agents():
    try:
        raw_data = supabase_request("GET", "agents", params="select=*,wallets(*)")
        formatted_list = []
        for agent in raw_data:
            wallet_list = agent.get('wallets', [])
            if wallet_list:
                wallet = wallet_list[0]
                formatted_list.append({
                    "name": agent['name'],
                    "wallet": wallet['wallet_address'],
                    "balance": wallet['balance_usd'],
                    "limit": wallet.get('max_transaction_limit', 50),
                    "time": agent['created_at']
                })
        formatted_list.reverse()
        return {"status": "SUCCESS", "data": formatted_list}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}

@app.post("/create-agent")
def create_agent(agent: Agent):
    try:
        # A. Create Agent
        agent_data = {"name": agent.name, "is_active": True}
        agent_res = supabase_request("POST", "agents", agent_data)
        new_agent_id = agent_res[0]['id']

        # B. Create Wallet (With Default Limit of $50)
        new_address = generate_eth_address()
        wallet_data = {
            "agent_id": new_agent_id,
            "wallet_address": new_address,
            "balance_usd": 0,
            "max_transaction_limit": 50.00,
            "network": "base-mainnet"
        }
        supabase_request("POST", "wallets", wallet_data)

        return {
            "status": "SUCCESS", 
            "agent": agent.name,
            "wallet_address": new_address,
            "balance": 0
        }
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}

@app.post("/deposit")
def deposit(req: DepositRequest):
    try:
        filter_query = f"wallet_address=eq.{req.wallet_address}"
        current_wallet = supabase_request("GET", "wallets", params=filter_query)
        
        if not current_wallet: raise HTTPException(status_code=404, detail="Wallet not found")
            
        current_balance = float(current_wallet[0]['balance_usd'])
        new_balance = current_balance + req.amount
        
        update_data = {"balance_usd": new_balance}
        supabase_request("PATCH", "wallets", update_data, params=filter_query)
        
        return {"status": "SUCCESS", "new_balance": new_balance}
    except Exception as e: return {"status": "ERROR", "detail": str(e)}

@app.post("/process-payment")
def process_payment(req: SpendRequest):
    try:
        # 1. GET WALLET DATA
        filter_query = f"wallet_address=eq.{req.wallet_address}"
        current_wallet = supabase_request("GET", "wallets", params=filter_query)
        
        if not current_wallet: 
            raise HTTPException(status_code=404, detail="Wallet not found")
            
        wallet_data = current_wallet[0]
        current_balance = float(wallet_data['balance_usd'])
        
        # --- NEW LOGIC: THE RULE CHECK ---
        # Get the limit (default to 50 if null)
        tx_limit = float(wallet_data.get('max_transaction_limit', 50.00))
        
                # RULE 1: Is this transaction too big?
        if req.amount > tx_limit:
             # RECORD THE CRIME
             tx_data = {
                "agent_id": wallet_data['agent_id'],
                "wallet_id": wallet_data['id'],
                "amount": req.amount,
                "currency": "USD",
                "status": "DENIED", # <--- Save as DENIED
                "to_address": req.vendor,
                "network": "base-mainnet",
                "metadata": {"reason": f"Over Limit (Max: ${tx_limit})"}
            }
             supabase_request("POST", "transactions", tx_data)
             
             return {
                 "status": "DENIED", 
                 "detail": f"OVER LIMIT (Max: ${tx_limit})"
             }
        
        # RULE 2: Do you have enough money?
        if current_balance < req.amount:
            return {"status": "DENIED", "detail": "INSUFFICIENT FUNDS"}
            
        # 3. EXECUTE SPEND (If rules passed)
        new_balance = current_balance - req.amount
        update_data = {"balance_usd": new_balance}
        supabase_request("PATCH", "wallets", update_data, params=filter_query)
        
        # 4. RECORD TRANSACTION
        tx_data = {
            "agent_id": wallet_data['agent_id'],
            "wallet_id": wallet_data['id'],
            "amount": req.amount,
            "currency": "USD",
            "status": "COMPLETED",
            "to_address": req.vendor,
            "network": "base-mainnet"
        }
        supabase_request("POST", "transactions", tx_data)
        
        return {"status": "APPROVED", "new_balance": new_balance}

    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}

@app.get("/")
def home():
    return {"message": "OVERSIGHT SYSTEM ONLINE"}