"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, ShieldAlert, Coins, Building2 } from 'lucide-react';

// SIMULATED HISTORICAL DATA (In Prod, this comes from Supabase)
const data = [
  { time: '00:00', spend: 400, tax: 40, blocked: 0 },
  { time: '04:00', spend: 300, tax: 30, blocked: 0 },
  { time: '08:00', spend: 850, tax: 85, blocked: 2 },
  { time: '12:00', spend: 1200, tax: 120, blocked: 5 },
  { time: '16:00', spend: 900, tax: 90, blocked: 1 },
  { time: '20:00', spend: 1500, tax: 150, blocked: 12 }, // The Attack Spike
  { time: '23:59', spend: 600, tax: 60, blocked: 0 },
];

export default function Analytics() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
      
      {/* CARD 1: TOTAL VOLUME */}
      <div className="bg-gray-900/30 border border-green-900/50 p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-xs text-green-600 mb-1">24H VOLUME</p>
            <h3 className="text-2xl text-white font-bold">$54,230.00</h3>
          </div>
          <Activity className="text-green-500 w-5 h-5" />
        </div>
        <div className="h-24 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <Line type="monotone" dataKey="spend" stroke="#22c55e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CARD 2: TAX HELD */}
      <div className="bg-gray-900/30 border border-green-900/50 p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-xs text-green-600 mb-1">TAX WITHHELD</p>
            <h3 className="text-2xl text-white font-bold">$5,423.00</h3>
          </div>
          <Building2 className="text-blue-500 w-5 h-5" />
        </div>
        <div className="h-24 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <Area type="monotone" dataKey="tax" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CARD 3: THREATS BLOCKED */}
      <div className="bg-gray-900/30 border border-red-900/30 p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-2 opacity-10">
            <ShieldAlert className="w-24 h-24 text-red-500" />
        </div>
        <div className="relative z-10">
            <p className="text-xs text-red-500 mb-1">THREATS NEUTRALIZED</p>
            <h3 className="text-4xl text-red-500 font-bold mb-2">20</h3>
            <p className="text-xs text-gray-500">Last attempt: 2 mins ago</p>
            <p className="text-xs text-gray-500">Vector: OVER_LIMIT</p>
        </div>
      </div>

      {/* CARD 4: LIQUIDITY */}
      <div className="bg-gray-900/30 border border-green-900/50 p-6">
         <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-xs text-green-600 mb-1">PROTOCOL LIQUIDITY</p>
            <h3 className="text-2xl text-white font-bold">$10.0M</h3>
          </div>
          <Coins className="text-yellow-500 w-5 h-5" />
        </div>
        <div className="space-y-2 mt-4">
            <div className="flex justify-between text-xs">
                <span className="text-gray-500">USDC RESERVES</span>
                <span className="text-green-400">100%</span>
            </div>
            <div className="w-full bg-gray-800 h-1">
                <div className="bg-green-500 h-1 w-full"></div>
            </div>
        </div>
      </div>
    </div>
  );
}