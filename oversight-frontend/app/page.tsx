import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-green-900">
      {/* NAV */}
      <nav className="border-b border-white/10 p-6 flex justify-between items-center backdrop-blur-md sticky top-0 z-50">
        <div className="text-2xl font-bold tracking-tighter">OVERSIGHT.</div>
        <div className="flex gap-6 text-sm font-medium text-gray-400">
          <Link href="#features" className="hover:text-white transition">PROTOCOL</Link>
          <Link href="#governance" className="hover:text-white transition">GOVERNANCE</Link>
          <Link href="/dashboard" className="text-green-400 hover:text-green-300 transition">LOGIN_</Link>
        </div>
      </nav>

      {/* HERO */}
      <section className="max-w-6xl mx-auto px-6 py-32 text-center">
        <div className="inline-block border border-green-900 bg-green-900/10 text-green-400 px-4 py-1 rounded-full text-xs font-mono mb-8">
          SYSTEM ONLINE: V1.0 STABLE
        </div>
        <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-8 leading-tight">
          The Central Bank <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-600">
            For AI Agents.
          </span>
        </h1>
        <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-12">
          Identity, Spend Control, and Automated Tax Compliance for the Agentic Economy. 
          Stop rogue AI spending before it settles.
        </p>
        <div className="flex justify-center gap-4">
          <button className="bg-white text-black px-8 py-4 font-bold hover:bg-gray-200 transition rounded-sm">
            READ WHITE PAPER
          </button>
          <Link href="/dashboard">
            <button className="border border-white/20 px-8 py-4 font-bold hover:bg-white/10 transition rounded-sm">
              DEPLOY NODE
            </button>
          </Link>
        </div>
      </section>

      {/* STATS */}
      <section className="border-y border-white/10 bg-white/5">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-white/10">
          <div className="p-12 text-center">
            <div className="text-4xl font-bold font-mono mb-2">$0.00</div>
            <div className="text-sm text-gray-500">FRAUD LOSSES</div>
          </div>
          <div className="p-12 text-center">
            <div className="text-4xl font-bold font-mono mb-2">&lt; 200ms</div>
            <div className="text-sm text-gray-500">LATENCY</div>
          </div>
          <div className="p-12 text-center">
            <div className="text-4xl font-bold font-mono mb-2">100%</div>
            <div className="text-sm text-gray-500">TAX COMPLIANCE</div>
          </div>
        </div>
      </section>

      {/* GRID */}
      <section id="features" className="max-w-6xl mx-auto px-6 py-32">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-4xl font-bold mb-6">The "Velvet Rope" for AI.</h2>
            <p className="text-gray-400 text-lg mb-8 leading-relaxed">
              Anonymous agents are a liability. Oversight enforces strict 
              <strong> KYB (Know Your Business)</strong> checks. 
              Only verified corporations can mint wallets. 
              Unverified bots are blocked at the protocol level.
            </p>
            <ul className="space-y-4 font-mono text-sm text-green-400">
              <li className="flex items-center gap-3">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Corporate Identity Binding
              </li>
              <li className="flex items-center gap-3">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Deterministic Spend Limits
              </li>
              <li className="flex items-center gap-3">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Vendor Whitelisting
              </li>
            </ul>
          </div>
          <div className="border border-white/10 bg-white/5 p-8 rounded-xl relative overflow-hidden">
             {/* Fake Code Block Visual */}
             <div className="font-mono text-xs text-gray-500">
                <div className="mb-2 text-blue-400">POST /process-payment</div>
                <div className="pl-4">{"{"}</div>
                <div className="pl-8 text-white">"amount": 50000,</div>
                <div className="pl-8 text-white">"vendor": "UNKNOWN_LLC"</div>
                <div className="pl-4">{"}"}</div>
                <div className="mt-4 text-red-500">error: TRANSACTION_DENIED</div>
                <div className="pl-4">reason: OVER_LIMIT</div>
             </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-white/10 py-12 text-center text-gray-600 text-sm">
        <p>&copy; 2026 OVERSIGHT PROTOCOL INC. ALL RIGHTS RESERVED.</p>
        <p className="mt-2">SAN FRANCISCO • NEW YORK • DUBAI</p>
      </footer>
    </div>
  );
}