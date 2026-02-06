import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Portfolio endpoints
export async function fetchPortfolio() {
  const { data } = await api.get('/portfolio/')
  return data
}

export async function fetchPositions() {
  const { data } = await api.get('/portfolio/positions')
  return data
}

// Market endpoints
export async function fetchMarketRegime() {
  const { data } = await api.get('/market/regime')
  return data
}

export async function fetchSectorAnalysis() {
  const { data } = await api.get('/market/sectors')
  return data
}

// Opportunities endpoints
export async function fetchOpportunities(params?: {
  regime?: string
  min_probability?: number
}) {
  const { data } = await api.get('/opportunities/', { params })
  return data
}

export async function fetchOpportunityDetail(symbol: string) {
  const { data } = await api.get(`/opportunities/${symbol}`)
  return data
}

export async function approveOpportunity(symbol: string) {
  const { data } = await api.post(`/opportunities/${symbol}/approve`)
  return data
}

// Trade endpoints
export async function logTradeEntry(entry: {
  plan_id?: number
  symbol: string
  entry_price: number
  quantity: number
  order_type?: string
}) {
  const { data } = await api.post('/trades/entry', entry)
  return data
}

export async function logTradeExit(exit: {
  trade_id: number
  exit_price: number
  quantity?: number
  exit_type?: string
}) {
  const { data } = await api.post('/trades/exit', exit)
  return data
}

export async function fetchTrades(params?: {
  status?: string
  symbol?: string
}) {
  const { data } = await api.get('/trades/', { params })
  return data
}

// Performance endpoints
export async function fetchPerformanceSummary(period: string = 'monthly') {
  const { data } = await api.get('/performance/summary', { params: { period } })
  return data
}

export async function fetchDisciplineReport(period: string = 'monthly') {
  const { data } = await api.get('/performance/discipline', { params: { period } })
  return data
}

export async function fetchModelPerformance() {
  const { data } = await api.get('/performance/model')
  return data
}
