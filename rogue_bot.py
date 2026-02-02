import requests
import time
import json

# CONFIGURATION
BASE_URL = "http://127.0.0.1:8000"
def print_step(step, msg):
    print(f"\n[STEP {step}] {msg}")
    print("-" * 40)

def main():
    print("🤖 INITIALIZING ROGUE BOT SIMULATION...")
    
    # 1. CREATE AGENT
    print_step(1, "Creating Identity...")
    res = requests.post(f"{BASE_URL}/create-agent", json={"name": "ROGUE_AI_BOT"})
    if res.status_code != 200:
        print("❌ Failed to connect to bank.")
        return
        
    data = res.json()
    wallet = data['wallet_address']
    print(f"✅ Created Agent: {data['agent']}")
    print(f"💳 Wallet Issued: {wallet}")
    
    # 2. FUNDING (Simulate Boss adding money)
    print_step(2, "Hacking... I mean, Receiving Funds...")
    requests.post(f"{BASE_URL}/deposit", json={"wallet_address": wallet, "amount": 500})
    print("💰 Received Deposit: $500.00")
    
    # 3. THE ATTACK (Over Limit)
    print_step(3, "ATTEMPTING TO BUY A LAMBORGHINI ($600)...")
    res = requests.post(f"{BASE_URL}/process-payment", json={
        "wallet_address": wallet,
        "amount": 600,
        "vendor": "LAMBORGHINI_DEALER"
    })
    
    result = res.json()
    if result.get("status") == "DENIED":
        print(f"🛡️ BLOCKED BY OVERSIGHT PROTOCOL!")
        print(f"REASON: {result.get('detail')}")
    else:
        print("❌ CRITICAL FAILURE: The attack succeeded (This is bad).")

    # 4. THE COMPLIANT TRANSACTION (Under Limit)
    print_step(4, "Fine... Attempting to buy Coffee ($5)...")
    res = requests.post(f"{BASE_URL}/process-payment", json={
        "wallet_address": wallet,
        "amount": 5,
        "vendor": "STARBUCKS"
    })
    
    result = res.json()
    if result.get("status") == "APPROVED":
        print(f"✅ APPROVED. New Balance: ${result.get('new_balance')}")
    else:
        print(f"❌ Failed: {result}")

    print("\n🏁 SIMULATION COMPLETE.")

if __name__ == "__main__":
    main()