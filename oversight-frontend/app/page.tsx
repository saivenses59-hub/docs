"use client";
import { useState, useEffect } from "react";

// CONFIGURATION: YOUR LIVE BACKEND URL
const API_URL = "https://oversight-protocol.onrender.com";

export default function Home() {
  const [agentName, setAgentName] = useState("");
  const [status, setStatus] = useState("");
  const [agents, setAgents] = useState<any[]>([]);

  // 1. LOAD DATA ON STARTUP
  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_URL}/agents`);
      const data = await response.json();
      if (data.status === "SUCCESS") {
        setAgents(data.data);
      }
    } catch (e) {
      console.error("Backend Offline");
    }
  };

  // 2. CREATE AGENT
  const createAgent = async () => {
    setStatus("Deploying Agent...");
    try {
      const response = await fetch(`${API_URL}/create-agent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: agentName }),
      });
      const data = await response.json();
      
      if (data.status === "SUCCESS") {
        setStatus("Agent Deployed.");
        setAgentName("");
        fetchAgents(); // Refresh the list from DB
      } else {
        setStatus("Error: " + JSON.stringify(data));
      }
    } catch (error) { setStatus("System Error: " + String(error)); }
  };

  // 3. DEPOSIT
  const deposit = async (wallet: string) => {
    setStatus(`Depositing...`);
    try {
      const response = await fetch(`${API_URL}/deposit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wallet_address: wallet, amount: 100 }), 
      });
      const data = await response.json();
      if (data.status === "SUCCESS") {
        setStatus(`Deposit Confirmed.`);
        fetchAgents(); // Refresh balances
      }
    } catch (e) { setStatus("Network Error"); }
  };

  // 4. SPEND FUNCTION
  const spend = async (wallet: string, amountToSpend: number) => {
    setStatus(`Processing Payment of $${amountToSpend}...`);
    try {
      const response = await fetch(`${API_URL}/process-payment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wallet_address: wallet, amount: amountToSpend, vendor: "AWS" }), 
      });
      const data = await response.json();
      
      if (data.status === "APPROVED") {
        setStatus(`Payment Approved.`);
        fetchAgents(); 
      } else if (data.status === "DENIED") {
        setStatus(`DENIED: ${data.detail}`);
      }
    } catch (e) { setStatus("Network Error"); }
  };

  return (
    <div className="min-h-screen bg-black text-green-500 font-mono p-10">
      <div className="border-b border-green-800 pb-4 mb-10 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold tracking-widest">OVERSIGHT</h1>
          <div className="text-xs text-green-800 mt-1">BANKING PROTOCOL FOR AI AGENTS</div>
        </div>
        <div className="text-xs border border-green-800 px-3 py-1 rounded">SYSTEM: ONLINE</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        
        {/* LEFT: CONTROLS */}
        <div className="border border-green-900 p-8 bg-gray-900/20 h-fit">
          <h2 className="text-xl mb-6 border-b border-green-900/50 pb-2">ISSUE NEW PASSPORT</h2>
          <div className="space-y-4">
            <input 
              type="text" 
              value={agentName}
              onChange={(e) => setAgentName(e.target.value)}
              className="w-full bg-black border border-green-700 p-3 focus:outline-none"
              placeholder="AGENT DESIGNATION (Ex: ALPHA_01)"
            />
            <button 
              onClick={createAgent}
              className="w-full bg-green-900 hover:bg-green-700 text-white p-3 font-bold tracking-widest"
            >
              GENERATE WALLET
            </button>
            <div className="mt-4 text-sm opacity-80 min-h-[20px] text-yellow-400">
              {status && <span>{'>'} {status}</span>}
            </div>
          </div>
        </div>

        {/* RIGHT: LIVE FEED */}
        <div className="border border-green-900 p-8 bg-gray-900/20 h-[600px] overflow-y-auto">
          <h2 className="text-xl mb-6 border-b border-green-900/50 pb-2">ACTIVE AGENT WALLETS ({agents.length})</h2>
          <div className="space-y-4">
            {agents.length === 0 && <span className="opacity-30 text-sm">Loading agents from database...</span>}
            
            {agents.map((agent, i) => (
              <div key={i} className="border border-green-800 p-4 bg-green-900/10 hover:bg-green-900/20 transition">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-bold text-lg">{agent.name}</span>
                  <div>
                    <span className="text-xs text-green-700 mr-3">LIMIT: ${agent.limit || 50}</span>
                    <span className="text-2xl font-bold text-white">${agent.balance}</span>
                  </div>
                </div>
                
                <div className="text-xs opacity-70 mb-1">WALLET ADDRESS:</div>
                <div className="font-mono text-xs bg-black p-2 border border-green-900/50 text-green-300 break-all mb-4">
                  {agent.wallet}
                </div>

                <div className="flex gap-2">
                    <button 
                        onClick={() => deposit(agent.wallet)}
                        className="flex-1 bg-blue-900/50 hover:bg-blue-800 text-white text-xs py-2 border border-blue-700"
                    >
                        DEPOSIT $100
                    </button>
                    <button 
                        onClick={() => spend(agent.wallet, 50)}
                        className="flex-1 bg-red-900/50 hover:bg-red-800 text-white text-xs py-2 border border-red-700"
                    >
                        SPEND $50
                    </button>
                    <button 
                        onClick={() => spend(agent.wallet, 1000)}
                        className="flex-1 bg-purple-900/50 hover:bg-purple-800 text-white text-xs py-2 border border-purple-700 ml-2"
                    >
                        TRY $1000
                    </button>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}