import { useQuery } from '@tanstack/react-query'
import { fetchPortfolio, fetchMarketRegime, fetchOpportunities } from '../services/api'

export default function Dashboard() {
  const { data: portfolio } = useQuery({
    queryKey: ['portfolio'],
    queryFn: fetchPortfolio,
  })

  const { data: regime } = useQuery({
    queryKey: ['regime'],
    queryFn: fetchMarketRegime,
  })

  const { data: opportunities } = useQuery({
    queryKey: ['opportunities'],
    queryFn: fetchOpportunities,
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Trading Dashboard</h1>

      {/* Market Regime Card */}
      <div className="card">
        <div className="card-header">Market Regime</div>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xl font-semibold text-blue-400">
              {regime?.regime_display || 'Loading...'}
            </p>
            <p className="text-sm text-terminal-muted mt-1">
              Confidence: {regime?.confidence ? `${(regime.confidence * 100).toFixed(0)}%` : '-'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-terminal-muted">Signal</p>
            <p className={`text-lg font-semibold ${
              regime?.signal?.type === 'FAVORABLE' ? 'text-profit' :
              regime?.signal?.type === 'AVOID' ? 'text-loss' : 'text-yellow-500'
            }`}>
              {regime?.signal?.type || '-'}
            </p>
          </div>
        </div>
        <p className="text-sm text-terminal-muted mt-3">
          {regime?.signal?.message || 'Loading market analysis...'}
        </p>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="card-header">Total Capital</div>
          <p className="stat-value">
            ₹{portfolio?.total_capital?.toLocaleString() || '0'}
          </p>
          <p className="stat-label">
            Deployed: {portfolio?.deployment_pct?.toFixed(0) || 0}%
          </p>
        </div>

        <div className="card">
          <div className="card-header">Today's P&L</div>
          <p className={`stat-value ${
            (portfolio?.unrealized_pnl?.amount || 0) >= 0 ? 'profit-text' : 'loss-text'
          }`}>
            {(portfolio?.unrealized_pnl?.amount || 0) >= 0 ? '+' : ''}
            ₹{portfolio?.unrealized_pnl?.amount?.toLocaleString() || '0'}
          </p>
          <p className="stat-label">
            {(portfolio?.unrealized_pnl?.pct || 0) >= 0 ? '+' : ''}
            {portfolio?.unrealized_pnl?.pct?.toFixed(2) || '0'}%
          </p>
        </div>

        <div className="card">
          <div className="card-header">Capital at Risk</div>
          <p className="stat-value">
            ₹{portfolio?.capital_at_risk?.toLocaleString() || '0'}
          </p>
          <p className="stat-label">
            {portfolio?.capital_at_risk_pct?.toFixed(2) || '0'}% of portfolio
          </p>
        </div>
      </div>

      {/* Opportunities */}
      <div className="card">
        <div className="card-header">
          Today's Opportunities ({opportunities?.count || 0})
        </div>
        <div className="space-y-3">
          {opportunities?.opportunities?.map((opp: any) => (
            <div
              key={opp.symbol}
              className="flex items-center justify-between p-3 bg-terminal-bg rounded-lg border border-terminal-border hover:border-blue-500 cursor-pointer transition-colors"
            >
              <div>
                <p className="font-semibold text-terminal-text">{opp.symbol}</p>
                <p className="text-sm text-terminal-muted">{opp.setup}</p>
              </div>
              <div className="text-right">
                <p className="text-sm">
                  Prob: <span className="font-semibold text-profit">{(opp.probability * 100).toFixed(0)}%</span>
                </p>
                <p className="text-sm text-terminal-muted">
                  RR: {opp.rr_ratio}:1
                </p>
              </div>
            </div>
          ))}
          {(!opportunities?.opportunities || opportunities.opportunities.length === 0) && (
            <p className="text-terminal-muted text-center py-4">
              No high-quality opportunities found today
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
