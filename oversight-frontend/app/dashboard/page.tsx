'use client'

/**
 * OVERSIGHT Dashboard - Production-Grade Frontend
 * 
 * CRITICAL FEATURES:
 * - Idempotency keys on all mutations (prevents double-spend)
 * - Safe null handling (no .toFixed crashes)
 * - Real-time balance updates
 * - Comprehensive error handling
 * - Audit trail export
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  AlertCircle, 
  CheckCircle, 
  TrendingUp, 
  DollarSign, 
  Download,
  RefreshCw,
  Shield
} from 'lucide-react'

// ============================================================================
// TYPES
// ============================================================================
interface Agent {
  id: string
  name: string
  wallet_address: string
  balance: number
  daily_spent: number
  daily_remaining: number
  created_at: string
}

interface Transaction {
  transaction_id: string
  status: 'APPROVED' | 'DENIED'
  vendor_paid: number
  tax_collected: number
  new_balance: number
  detail: string
  timestamp: string
  idempotency_key: string
}

// ============================================================================
// CONSTANTS
// ============================================================================
const API_BASE_URL = "https://oversight-protocol.onrender.com"
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

// ============================================================================
// MAIN COMPONENT
// ============================================================================
export default function DashboardPage() {
  // State
  const [agents, setAgents] = useState<Agent[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Form state
  const [selectedAgent, setSelectedAgent] = useState<string>('')
  const [amount, setAmount] = useState<string>('')
  const [vendor, setVendor] = useState<string>('')
  const [processing, setProcessing] = useState(false)

  // ========================================================================
  // DATA FETCHING (with safe null handling)
  // ========================================================================
  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/agents`)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      const data = await response.json()
      
      // ⚠️ CRITICAL: Safe null handling to prevent .toFixed crashes
      const safeAgents = (data.agents || []).map((agent: any) => ({
        ...agent,
        balance: Number(agent.balance) || 0,
        daily_spent: Number(agent.daily_spent) || 0,
        daily_remaining: Number(agent.daily_remaining) || 0,
      }))
      
      setAgents(safeAgents)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch agents:', err)
      setError('Failed to load agents. Please refresh.')
      setAgents([]) // Set empty array on error
    }
  }

  const fetchTransactions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/transactions?limit=50`)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      const data = await response.json()
      
      // Safe null handling
      const safeTxs = (data.transactions || []).map((tx: any) => ({
        ...tx,
        vendor_paid: Number(tx.vendor_paid) || 0,
        tax_collected: Number(tx.tax_collected) || 0,
        new_balance: Number(tx.new_balance) || 0,
      }))
      
      setTransactions(safeTxs)
    } catch (err) {
      console.error('Failed to fetch transactions:', err)
      setTransactions([]) // Set empty array on error
    }
  }

  const loadData = async () => {
    setLoading(true)
    await Promise.all([fetchAgents(), fetchTransactions()])
    setLoading(false)
  }

  useEffect(() => {
    loadData()
  }, [])

  // ========================================================================
  // PAYMENT PROCESSING (with idempotency)
  // ========================================================================
  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!selectedAgent || !amount || !vendor) {
      setError('Please fill in all fields')
      return
    }

    const amountNum = parseFloat(amount)
    if (isNaN(amountNum) || amountNum <= 0) {
      setError('Invalid amount')
      return
    }

    const agent = agents.find(a => a.id === selectedAgent)
    if (!agent) {
      setError('Agent not found')
      return
    }

    setProcessing(true)
    setError(null)
    setSuccess(null)

    try {
      // 🔑 CRITICAL: Generate idempotency key (prevents double-spend)
      const idempotencyKey = `web_${crypto.randomUUID()}`
      
      console.log(`🔑 Generated idempotency key: ${idempotencyKey}`)

      const response = await fetch(`${API_BASE_URL}/process-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: agent.wallet_address,
          amount: amountNum,
          vendor: vendor.trim(),
          idempotency_key: idempotencyKey, // Critical: Include key
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`)
      }

      // Handle response
      if (data.status === 'APPROVED') {
        setSuccess(
          `✅ Payment approved! Vendor received $${(data.vendor_paid || 0).toFixed(2)}, ` +
          `Tax: $${(data.tax_collected || 0).toFixed(2)}`
        )
        
        // Reset form
        setAmount('')
        setVendor('')
        
        // Refresh data
        await loadData()
      } else {
        setError(`❌ Payment denied: ${data.detail}`)
      }
    } catch (err: any) {
      console.error('Payment error:', err)
      setError(err.message || 'Payment failed. Please try again.')
    } finally {
      setProcessing(false)
    }
  }

  // ========================================================================
  // DEPOSIT FUNDS (with idempotency)
  // ========================================================================
  const handleDeposit = async (agentId: string) => {
    const agent = agents.find(a => a.id === agentId)
    if (!agent) return

    const depositAmount = prompt('Enter deposit amount:', '100')
    if (!depositAmount) return

    const amount = parseFloat(depositAmount)
    if (isNaN(amount) || amount <= 0) {
      alert('Invalid amount')
      return
    }

    try {
      // 🔑 Generate idempotency key
      const idempotencyKey = `deposit_${crypto.randomUUID()}`

      const response = await fetch(`${API_BASE_URL}/deposit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: agent.wallet_address,
          amount: amount,
          idempotency_key: idempotencyKey, // Critical: Include key
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Deposit failed')
      }

      setSuccess(`💵 Deposited $${amount.toFixed(2)} successfully!`)
      await loadData()
    } catch (err: any) {
      setError(err.message || 'Deposit failed')
    }
  }

  // ========================================================================
  // EXPORT AUDIT LOG
  // ========================================================================
  const exportAudit = () => {
    try {
      const csvContent = [
        ['Transaction ID', 'Status', 'Vendor Paid', 'Tax', 'Balance', 'Detail', 'Timestamp', 'Idempotency Key'].join(','),
        ...transactions.map(tx => [
          tx.transaction_id,
          tx.status,
          (tx.vendor_paid || 0).toFixed(2),
          (tx.tax_collected || 0).toFixed(2),
          (tx.new_balance || 0).toFixed(2),
          `"${tx.detail}"`,
          tx.timestamp,
          tx.idempotency_key
        ].join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `oversight-audit-${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)

      setSuccess('📥 Audit log exported successfully!')
    } catch (err) {
      setError('Failed to export audit log')
    }
  }

  // ========================================================================
  // CHARTS DATA (with safe calculations)
  // ========================================================================
  const spendingData = transactions
    .filter(tx => tx.status === 'APPROVED')
    .slice(0, 10)
    .reverse()
    .map(tx => ({
      name: tx.transaction_id.substring(0, 8),
      vendor: tx.vendor_paid || 0,
      tax: tx.tax_collected || 0,
    }))

  const taxData = [
    { 
      name: 'Vendor Paid', 
      value: transactions
        .filter(tx => tx.status === 'APPROVED')
        .reduce((sum, tx) => sum + (tx.vendor_paid || 0), 0) 
    },
    { 
      name: 'Tax Collected', 
      value: transactions
        .filter(tx => tx.status === 'APPROVED')
        .reduce((sum, tx) => sum + (tx.tax_collected || 0), 0) 
    },
  ]

  // ========================================================================
  // STATISTICS (with safe calculations)
  // ========================================================================
  const totalBalance = agents.reduce((sum, a) => sum + (a.balance || 0), 0)
  const totalSpent = agents.reduce((sum, a) => sum + (a.daily_spent || 0), 0)
  const totalTax = transactions
    .filter(tx => tx.status === 'APPROVED')
    .reduce((sum, tx) => sum + (tx.tax_collected || 0), 0)
  const approvalRate = transactions.length > 0
    ? (transactions.filter(tx => tx.status === 'APPROVED').length / transactions.length * 100)
    : 0

  // ========================================================================
  // RENDER
  // ========================================================================
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">OVERSIGHT Dashboard</h1>
          <p className="text-muted-foreground">AI Agent Payment Platform with Idempotency Protection</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={exportAudit} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Audit
          </Button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 text-green-900 border-green-200">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalBalance.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">Across {agents.length} agents</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Spent</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalSpent.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">Limit: $50.00/day</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tax Collected</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalTax.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">10% withholding rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approval Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{approvalRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">{transactions.length} transactions</p>
          </CardContent>
        </Card>
      </div>

      {/* Payment Form */}
      <Card>
        <CardHeader>
          <CardTitle>Process Payment</CardTitle>
          <CardDescription>Send payment with automatic tax withholding (10%)</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePayment} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <label className="text-sm font-medium">Agent</label>
                <select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  className="w-full mt-1 p-2 border rounded-md"
                  disabled={processing}
                >
                  <option value="">Select agent...</option>
                  {agents.map(agent => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name} (${(agent.balance || 0).toFixed(2)})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">Amount ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  disabled={processing}
                  className="mt-1"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Vendor</label>
                <Input
                  type="text"
                  value={vendor}
                  onChange={(e) => setVendor(e.target.value)}
                  placeholder="e.g., OpenAI"
                  disabled={processing}
                  className="mt-1"
                />
              </div>
            </div>

            <Button type="submit" disabled={processing} className="w-full">
              {processing ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                'Process Payment'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Agents List */}
      <Card>
        <CardHeader>
          <CardTitle>AI Agents</CardTitle>
          <CardDescription>Manage your AI agent wallets</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {agents.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">
                No agents found. Create your first agent to get started.
              </p>
            ) : (
              agents.map(agent => (
                <div key={agent.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-semibold">{agent.name}</h3>
                    <p className="text-sm text-muted-foreground">{agent.wallet_address}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">Balance: ${(agent.balance || 0).toFixed(2)}</p>
                      <p className="text-xs text-muted-foreground">
                        Spent today: ${(agent.daily_spent || 0).toFixed(2)} / $50.00
                      </p>
                    </div>
                    <Button onClick={() => handleDeposit(agent.id)} variant="outline" size="sm">
                      Deposit
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Spending</CardTitle>
            <CardDescription>Last 10 approved transactions</CardDescription>
          </CardHeader>
          <CardContent>
            {spendingData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={spendingData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="vendor" stroke="#8884d8" name="Vendor Paid" />
                  <Line type="monotone" dataKey="tax" stroke="#82ca9d" name="Tax" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-muted-foreground py-20">No transactions yet</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tax Distribution</CardTitle>
            <CardDescription>Vendor vs Tax breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            {taxData[0].value > 0 || taxData[1].value > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={taxData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: $${entry.value.toFixed(2)}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {taxData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-muted-foreground py-20">No data yet</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
          <CardDescription>Last 10 transactions with idempotency tracking</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {transactions.slice(0, 10).map(tx => (
              <div key={tx.transaction_id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Badge variant={tx.status === 'APPROVED' ? 'default' : 'destructive'}>
                      {tx.status}
                    </Badge>
                    <span className="text-sm font-mono">{tx.transaction_id}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{tx.detail}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    🔑 Idempotency: {tx.idempotency_key.substring(0, 24)}...
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">Vendor: ${(tx.vendor_paid || 0).toFixed(2)}</p>
                  <p className="text-xs text-muted-foreground">Tax: ${(tx.tax_collected || 0).toFixed(2)}</p>
                  <p className="text-xs text-muted-foreground">{new Date(tx.timestamp).toLocaleString()}</p>
                </div>
              </div>
            ))}
            {transactions.length === 0 && (
              <p className="text-center text-muted-foreground py-8">No transactions yet</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}