"use client";
import { useState, useEffect } from "react";
import Analytics from "./Analytics"; 

// CONFIGURATION
const API_URL = "http://127.0.0.1:8000"; 

export default function Dashboard() {
  const [orgName, setOrgName] = useState("");
  const [taxId, setTaxId] = useState("");
  const [currentOrg, setCurrentOrg] = useState<any>(null); 
  const [agentName, setAgentName] = useState("");
  const [status, setStatus] = useState("");
  const [agents, setAgents] = useState<any[]>([]);

  useEffect(() => { fetchAgents(); }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_URL}/agents`);
      const data = await response.json();
      if (data.status === "SUCCESS") setAgents(data.data);
    } catch (e) { console.error("Backend Offline"); }
  };

  const registerCompany = async () => {
    setStatus("Verifying Corporate Identity...");
    try {
        const response = await fetch(`${API_URL}/register-org`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: orgName, tax_id: taxId }),
        });
        const data = await response.json();
        if (data.status === "SUCCESS") {
            setStatus("IDENTITY VERIFIED. ACCESS GRANTED.");
            setCurrentOrg({ id: data.org_id, name: data.name });
        } else { setStatus("VERIFICATION FAILED."); }
    } catch (e) { setStatus("System Error"); }
  };

  const createAgent = async () => {
    if (!currentOrg) { setStatus("ERROR: MUST REGISTER ORGANIZATION FIRST."); return; }
    setStatus("Deploying Agent...");
    try {
      const response = await fetch(`${API_URL}/create-agent`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: agentName, organization_id: currentOrg.id }),
      });
      const data = await response.json();
      if (data.status === "SUCCESS") {
        setStatus("Agent Deployed."); setAgentName(""); fetchAgents(); 
      } else { setStatus("Error: " + data.detail); }
    } catch (error) { setStatus("System Error"); }
  };

  const deposit = async (wallet: string) => {
    setStatus(`Depositing...`);
    try {
      const response = await fetch(`${API_URL}/deposit`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wallet_address: wallet, amount: 100 }), 
      });
      const data = await response.json();
      if (data.status === "SUCCESS") { setStatus(`Deposit Confirmed.`); fetchAgents(); }
    } catch (e) { setStatus("Network Error"); }
  };

  const spend = async (wallet: string, amountToSpend: number) => {
    setStatus(`Processing Payment...`);
    try {
      const response = await fetch(`${API_URL}/process-payment`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wallet_address: wallet, amount: amountToSpend, vendor: "AWS" }), 
      });
      const data = await response.json();
      if (data.status === "APPROVED") {
        setStatus(`APPROVED. Tax Withheld: $${data.tax_collected}`); fetchAgents(); 
      } else if (data.status === "DENIED") { setStatus(`DENIED: ${data.detail}`); }
    } catch (e) { setStatus("Network Error"); }
  };

  const exportAudit = () => {
    window.open(`${API_URL}/export-audit`, '_blank');
  }

  return (
    <div className="min-h-screen bg-black text-green-500 font-mono p-6 md:p-10">
      
      {/* HEADER */}
      <div className="border-b border-green-800 pb-4 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-widest text-white">OVERSIGHT<span className="text-green-600">_PROTOCOL</span></h1>
          <div className="text-xs text-gray-500 mt-1 uppercase tracking-widest">Institutional AI Banking Layer</div>
        </div>
        
        {/* THE YELLOW BUTTON */}
        <div className="text-right mt-4 md:mt-0 flex flex-col items-end gap-3">
            <div className="text-xs border border-green-900 bg-green-900/20 px-3 py-1 text-green-400">SYSTEM: ONLINE</div>
            
            <button 
                onClick={exportAudit}
                className="bg-yellow-500 hover:bg-yellow-400 text-black font-bold px-6 py-3 rounded-sm tracking-widest shadow-[0_0_15px_rgba(234,179,8,0.5)] transition"
            >
                ⬇ DOWNLOAD CFO AUDIT
            </button>
        </div>
      </div>

      <Analytics />

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* CONTROLS */}
        <div className="md:col-span-4 border border-green-900 bg-gray-900/20 h-fit p-6">
          {!currentOrg ? (
            <div className="mb-8 border-b border-green-900/50 pb-8">
                <div className="flex items-center gap-2 mb-4">
                    <span className="bg-white text-black text-xs font-bold px-2 py-0.5">STEP 1</span>
                    <h2 className="text-sm font-bold text-white tracking-widest">CORPORATE KYB</h2>
                </div>
                <div className="space-y-3">
                    <input type="text" value={orgName} onChange={(e) => setOrgName(e.target.value)}
                        className="w-full bg-black border border-green-800 p-3 text-sm focus:border-green-500 outline-none transition" placeholder="COMPANY NAME" />
                    <input type="text" value={taxId} onChange={(e) => setTaxId(e.target.value)}
                        className="w-full bg-black border border-green-800 p-3 text-sm focus:border-green-500 outline-none transition" placeholder="TAX ID / EIN" />
                    <button onClick={registerCompany} className="w-full bg-white hover:bg-gray-200 text-black p-3 text-sm font-bold tracking-widest transition">
                        VERIFY IDENTITY
                    </button>
                </div>
            </div>
          ) : (
             <div className="mb-8 border-b border-green-900/50 pb-8 opacity-50 pointer-events-none">
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-green-500">✓</span>
                    <h2 className="text-sm font-bold text-green-300 tracking-widest">IDENTITY VERIFIED: {currentOrg.name}</h2>
                </div>
            </div>
          )}

          <div className={!currentOrg ? "opacity-30 pointer-events-none" : ""}>
            <div className="flex items-center gap-2 mb-4">
                <span className="bg-green-900 text-white text-xs font-bold px-2 py-0.5">STEP 2</span>
                <h2 className="text-sm font-bold text-white tracking-widest">DEPLOY NODE</h2>
            </div>
            <div className="space-y-3">
                <input type="text" value={agentName} onChange={(e) => setAgentName(e.target.value)}
                className="w-full bg-black border border-green-800 p-3 text-sm focus:border-green-500 outline-none" placeholder="AGENT DESIGNATION" />
                <button onClick={createAgent} className="w-full bg-green-700 hover:bg-green-600 text-white p-3 text-sm font-bold tracking-widest transition">
                INITIALIZE AGENT
                </button>
            </div>
          </div>
          
          <div className="mt-6 border border-green-900/30 bg-black p-4 min-h-[60px]">
            <p className="text-[10px] text-gray-500 mb-1">SYSTEM CONSOLE</p>
            <div className="text-xs text-yellow-400 font-mono">
              {status || "> Ready for command..."}
            </div>
          </div>
        </div>

        {/* FLEET */}
        <div className="md:col-span-8 border border-green-900 bg-gray-900/20 h-[600px] overflow-y-auto p-6">
          <div className="flex justify-between items-center mb-6 border-b border-green-900/50 pb-2">
             <h2 className="text-sm font-bold text-white tracking-widest">LIVE FLEET STATUS</h2>
             <span className="text-xs text-green-500">{agents.length} NODES ACTIVE</span>
          </div>

          <div className="space-y-3">
            {agents.map((agent, i) => (
              <div key={i} className="border border-green-800/50 bg-black/40 hover:bg-green-900/10 transition p-4 group">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <div>
                        <span className="font-bold text-white block">{agent.name}</span>
                        <span className="text-[10px] text-gray-500 uppercase tracking-wider">{agent.org} CORP</span>
                    </div>
                  </div>
                  <div className="text-right mt-2 md:mt-0">
                    <div className="text-xs text-gray-500 mb-0.5">AVAILABLE LIQUIDITY</div>
                    <span className="text-2xl font-mono font-bold text-white tracking-tighter">${agent.balance.toFixed(2)}</span>
                  </div>
                </div>
                
                <div className="bg-gray-900/50 p-2 rounded mb-4 flex items-center justify-between border border-white/5">
                    <span className="text-[10px] text-gray-500 font-mono">WALLET_ID</span>
                    <span className="text-[10px] text-green-300 font-mono">{agent.wallet}</span>
                </div>

                <div className="grid grid-cols-3 gap-2 opacity-50 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => deposit(agent.wallet)} className="bg-blue-900/30 hover:bg-blue-900 text-blue-200 text-[10px] py-2 border border-blue-900/50">+ DEPOSIT $100</button>
                    <button onClick={() => spend(agent.wallet, 50)} className="bg-gray-800 hover:bg-gray-700 text-white text-[10px] py-2 border border-gray-700">- SPEND $50</button>
                    <button onClick={() => spend(agent.wallet, 1000)} className="bg-red-900/20 hover:bg-red-900/50 text-red-200 text-[10px] py-2 border border-red-900/50">TEST ATTACK ($1k)</button>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}