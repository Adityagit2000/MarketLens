"""
Portfolio Models

Database models for portfolio state and snapshots.
"""

from sqlalchemy import Column, String, Numeric, BigInteger, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from app.db.database import Base


class Portfolio(Base):
    """
    Portfolio account configuration and state.
    
    Stores account parameters and current allocation.
    """
    __tablename__ = "portfolios"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    
    # Capital
    total_capital = Column(Numeric(16, 2), nullable=False)
    deployed_capital = Column(Numeric(16, 2), default=0)
    available_capital = Column(Numeric(16, 2), nullable=False)
    
    # Risk parameters
    risk_per_trade_pct = Column(Numeric(5, 2), default=2.0)
    max_positions = Column(BigInteger, default=10)
    max_sector_concentration_pct = Column(Numeric(5, 2), default=30.0)
    max_capital_deployment_pct = Column(Numeric(5, 2), default=80.0)
    
    # Current state
    open_positions_count = Column(BigInteger, default=0)
    total_unrealized_pnl = Column(Numeric(14, 2), default=0)
    total_capital_at_risk = Column(Numeric(14, 2), default=0)
    
    # Performance (current period)
    realized_pnl_today = Column(Numeric(14, 2), default=0)
    realized_pnl_mtd = Column(Numeric(14, 2), default=0)
    realized_pnl_ytd = Column(Numeric(14, 2), default=0)
    
    # Sector exposure (JSONB: {sector: amount})
    sector_exposure = Column(JSONB, nullable=True)
    
    # Active status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PortfolioSnapshot(Base):
    """
    Daily portfolio snapshots for historical tracking.
    
    Records end-of-day portfolio state for performance analysis.
    """
    __tablename__ = "portfolio_snapshots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    portfolio_id = Column(BigInteger, nullable=False, index=True)
    snapshot_date = Column(DateTime, nullable=False, index=True)
    
    # Capital state
    total_capital = Column(Numeric(16, 2), nullable=False)
    deployed_capital = Column(Numeric(16, 2), nullable=False)
    available_capital = Column(Numeric(16, 2), nullable=False)
    
    # P&L
    unrealized_pnl = Column(Numeric(14, 2), nullable=False)
    realized_pnl_day = Column(Numeric(14, 2), nullable=False)
    cumulative_realized_pnl = Column(Numeric(14, 2), nullable=False)
    
    # Equity curve
    equity_value = Column(Numeric(16, 2), nullable=False)  # Total capital + unrealized
    daily_return_pct = Column(Numeric(8, 4), nullable=True)
    
    # Risk metrics
    capital_at_risk = Column(Numeric(14, 2), nullable=False)
    portfolio_var_95 = Column(Numeric(14, 2), nullable=True)  # Value at Risk
    
    # Position summary
    open_positions = Column(BigInteger, nullable=False)
    positions_detail = Column(JSONB, nullable=True)  # Summary of each position
    
    # Regime context
    market_regime = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class PerformanceMetrics(Base):
    """
    Aggregated performance metrics for reporting.
    
    Calculated periodically (weekly, monthly, quarterly).
    """
    __tablename__ = "performance_metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    portfolio_id = Column(BigInteger, nullable=False, index=True)
    
    # Period
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Trade statistics
    total_trades = Column(BigInteger, nullable=False)
    winning_trades = Column(BigInteger, nullable=False)
    losing_trades = Column(BigInteger, nullable=False)
    win_rate = Column(Numeric(5, 4), nullable=False)
    
    # Return statistics
    avg_win_pct = Column(Numeric(8, 4), nullable=True)
    avg_loss_pct = Column(Numeric(8, 4), nullable=True)
    largest_win_pct = Column(Numeric(8, 4), nullable=True)
    largest_loss_pct = Column(Numeric(8, 4), nullable=True)
    
    # Risk-adjusted returns
    expectancy = Column(Numeric(8, 4), nullable=True)  # Expected value per trade
    profit_factor = Column(Numeric(8, 4), nullable=True)  # Gross profit / Gross loss
    sharpe_ratio = Column(Numeric(8, 4), nullable=True)
    sortino_ratio = Column(Numeric(8, 4), nullable=True)
    max_drawdown_pct = Column(Numeric(8, 4), nullable=True)
    
    # Portfolio returns
    total_return_pct = Column(Numeric(8, 4), nullable=False)
    annualized_return = Column(Numeric(8, 4), nullable=True)
    
    # Execution quality
    avg_entry_slippage = Column(Numeric(6, 4), nullable=True)
    avg_exit_slippage = Column(Numeric(6, 4), nullable=True)
    total_charges = Column(Numeric(12, 2), nullable=True)
    
    # Discipline
    trades_with_deviations = Column(BigInteger, nullable=True)
    deviation_rate = Column(Numeric(5, 4), nullable=True)
    
    # Streak analysis
    max_winning_streak = Column(BigInteger, nullable=True)
    max_losing_streak = Column(BigInteger, nullable=True)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
