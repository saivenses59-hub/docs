import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <--- NEW WEAPON
from pydantic import BaseModel

# 1. Load Secrets
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Missing Credentials")

# 2. Database Helper
def supabase_request(method, table, data=None):
    endpoint = f"{url}/rest/v1/{table}"
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
    return response.json()

# 3. Initialize App
app = FastAPI()

# 4. ENABLE CORS (THE BRIDGE) - ALLOW FRONTEND TO TALK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your website URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Data Model
class Agent(BaseModel):
    name: str

# 6. Endpoints
@app.post("/create-agent")
def create_agent(agent: Agent):
    try:
        data = {"name": agent.name, "is_active": True}
        result = supabase_request("POST", "agents", data)
        return {"status": "SUCCESS", "data": result}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}

@app.get("/")
def home():
    return {"message": "OVERSIGHT SYSTEM ONLINE"}