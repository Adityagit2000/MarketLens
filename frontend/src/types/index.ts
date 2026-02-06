// Market Types
export interface MarketRegime {
  regime: string
  regime_display: string
  confidence: number
  components: {
    trend: TrendAnalysis
    volatility: VolatilityAnalysis
    breadth: BreadthAnalysis
  }
  signal: {
    type: 'FAVORABLE' | 'CAUTION' | 'NEUTRAL' | 'AVOID'
    message: string
    recommendation: string
  }
}

export interface TrendAnalysis {
  direction: string
  strength: number
  ma_alignment: string
  adx: number
}

export interface VolatilityAnalysis {
  state: 'low' | 'normal' | 'high'
  percentile: number
  vix?: number
}

export interface BreadthAnalysis {
  pct_above_200ma: number
  advance_decline_ratio: number
}

// Portfolio Types
export interface Portfolio {
  total_capital: number
  deployed_capital: number
  available_capital: number
  deployment_pct: number
  open_positions: number
  capital_at_risk: number
  capital_at_risk_pct: number
  unrealized_pnl: {
    amount: number
    pct: number
  }
  realized_pnl: {
    today: number
    mtd: number
    ytd: number
  }
}

export interface Position {
  id: number
  symbol: string
  direction: 'long' | 'short'
  quantity: number
  avg_entry: number
  current_price: number
  unrealized_pnl: number
  unrealized_pnl_pct: number
  stop_loss: number
  target_1: number
  target_2?: number
  progress_to_target: number
  capital_at_risk: number
  days_held: number
  status: string
}

// Opportunity Types
export interface Opportunity {
  symbol: string
  setup: string
  probability: number
  expected_return: number
  rr_ratio: number
  confidence: 'low' | 'medium' | 'high'
  technical_score: number
  regime: string
  rationale: string[]
}

export interface TradePlan {
  status: 'approved' | 'rejected'
  symbol: string
  entry_price: number
  stop_loss: number
  target_1: number
  target_2?: number
  position_size: number
  capital_required: number
  risk_amount: number
  risk_pct: number
  rr_ratio_t1: number
  rr_ratio_t2?: number
}

// Trade Types
export interface Trade {
  id: number
  symbol: string
  status: 'open' | 'closed'
  direction: 'long' | 'short'
  entry_price: number
  exit_price?: number
  quantity: number
  unrealized_pnl?: number
  net_pnl?: number
  return_pct?: number
  stop_loss: number
  target_1: number
  entry_date: string
  exit_date?: string
  days_held: number
}

// Performance Types
export interface PerformanceMetrics {
  total_trades: number
  winners: number
  losers: number
  win_rate: number
  avg_win_pct: number
  avg_loss_pct: number
  expectancy: number
  profit_factor: number
  sharpe_ratio: number
  max_drawdown_pct: number
}
