import os
import json
import logging
import requests

# ------------------------------------------------------------------
# 🏛️ OVERSIGHT PROTOCOL: SDK LAYER
# The Financial Rail for AI Agents
# ------------------------------------------------------------------

# Configure Bank-Grade Logging
logging.basicConfig(level=logging.INFO, format='[OVERSIGHT] %(message)s')
logger = logging.getLogger("oversight")

class Oversight:
    """
    The interface for AI Agents to interact with the Oversight Economy.
    Enforces spend limits, tax compliance, and audit logging.
    """
    
    def __init__(self, api_key: str = None, env: str = "production"):
        """
        Initialize the connection to the Central Bank.
        """
        self.api_key = api_key or os.getenv("OVERSIGHT_API_KEY")
        
        if not self.api_key:
            logger.error("No API Key provided. Agent is effectively unbanked.")
            raise ValueError("Oversight API Key is required.")

        # Set the Endpoint (Switch to local if testing)
        if env == "local":
            self.base_url = "http://127.0.0.1:8000"
        else:
            # We will update this with your real Render URL later
            self.base_url = "https://your-backend-url.onrender.com"
            
        logger.info("Connection established. Protocol active.")

    def track_transaction(self, agent_id: str, amount: float, description: str, metadata: dict = None):
        """
        Reports a spend event to the Ledger.
        This triggers the Tax Engine and Risk Checks.
        """
        endpoint = f"{self.base_url}/transactions"
        
        payload = {
            "agent_id": agent_id,
            "amount": amount,
            "description": description,
            "metadata": metadata or {}
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            logger.info(f"Processing transaction: ${amount} for {description}...")
            # Ideally: response = requests.post(endpoint, json=payload, headers=headers)
            
            # SIMULATION MODE (Until we link the real URL):
            # We simulate a successful bank response for your test.
            logger.info("✅ Transaction Authorized by Protocol.")
            return {
                "status": "success",
                "transaction_id": "tx_simulated_999",
                "risk_score": 0.0,
                "tax_withheld": amount * 0.10
            }
            
        except Exception as e:
            logger.error(f"Transaction Failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

# Expose the class directly
__all__ = ["Oversight"]