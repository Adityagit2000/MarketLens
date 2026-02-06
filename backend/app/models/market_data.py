"""
Market Data Models

Database models for OHLCV data, corporate actions, and symbol mappings.
"""

from sqlalchemy import Column, String, Numeric, BigInteger, DateTime, Boolean, Index, Date
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from app.db.database import Base


class OHLCV(Base):
    """
    OHLCV (Open, High, Low, Close, Volume) price data.
    
    This is the core time-series table, optimized with TimescaleDB hypertable.
    Stores both raw and adjusted prices.
    """
    __tablename__ = "ohlcv"

    symbol = Column(String(50), primary_key=True, index=True)
    date = Column(DateTime(timezone=True), primary_key=True)
    
    # Raw prices
    open = Column(Numeric(12, 2), nullable=False)
    high = Column(Numeric(12, 2), nullable=False)
    low = Column(Numeric(12, 2), nullable=False)
    close = Column(Numeric(12, 2), nullable=False)
    
    # Volume data
    volume = Column(BigInteger, nullable=False)
    turnover = Column(Numeric(18, 2), nullable=True)
    
    # NSE-specific: Delivery data (indicates conviction)
    delivery_qty = Column(BigInteger, nullable=True)
    delivery_pct = Column(Numeric(5, 2), nullable=True)
    
    # Adjusted prices (for splits, bonuses, dividends)
    adjusted_close = Column(Numeric(12, 2), nullable=True)
    adjustment_factor = Column(Numeric(10, 6), default=1.0)
    
    # Data quality flags
    is_valid = Column(Boolean, default=True)
    anomaly_flags = Column(JSONB, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_ohlcv_symbol_date", "symbol", "date", postgresql_using="btree"),
        Index("idx_ohlcv_date", "date", postgresql_using="btree"),
    )


class CorporateAction(Base):
    """
    Corporate actions that affect price continuity.
    
    Includes splits, bonuses, dividends, rights issues.
    Used to calculate adjustment factors.
    """
    __tablename__ = "corporate_actions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    ex_date = Column(Date, nullable=False, index=True)
    
    # Action details
    action_type = Column(String(20), nullable=False)  # 'split', 'bonus', 'dividend', 'rights'
    ratio = Column(Numeric(10, 6), nullable=True)  # For splits/bonuses
    amount = Column(Numeric(12, 2), nullable=True)  # For dividends
    
    # Original announcement details
    record_date = Column(Date, nullable=True)
    announcement_date = Column(Date, nullable=True)
    description = Column(String(500), nullable=True)
    
    # Verification status
    verified = Column(Boolean, default=False)
    source = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_corp_action_symbol_date", "symbol", "ex_date"),
    )


class SymbolMapping(Base):
    """
    Symbol name changes and mappings.
    
    Companies rename, merge, etc. This maintains continuity.
    """
    __tablename__ = "symbol_mappings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    old_symbol = Column(String(50), nullable=False, index=True)
    new_symbol = Column(String(50), nullable=False, index=True)
    effective_date = Column(Date, nullable=False)
    
    # Reason for change
    change_type = Column(String(50), nullable=True)  # 'rename', 'merger', 'demerger'
    description = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class IndexConstituent(Base):
    """
    Index constituents tracking.
    
    Tracks which stocks are in Nifty 50, Nifty Bank, etc.
    """
    __tablename__ = "index_constituents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    index_name = Column(String(50), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    
    # Membership period
    added_date = Column(Date, nullable=False)
    removed_date = Column(Date, nullable=True)
    
    # Weight in index
    weight = Column(Numeric(8, 4), nullable=True)
    
    # Sector classification
    sector = Column(String(50), nullable=True)
    industry = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_constituent_index", "index_name", "symbol"),
    )
