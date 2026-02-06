"""
Prediction Models

Database models for ML predictions and regime classification.
"""

from sqlalchemy import Column, String, Numeric, BigInteger, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime

from app.db.database import Base


class Prediction(Base):
    """
    ML model predictions for individual stocks.
    
    Stores probability distributions, not point estimates.
    """
    __tablename__ = "predictions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    
    # Prediction horizon
    horizon_days = Column(BigInteger, nullable=False)  # 5, 10, 20 days
    
    # Return distribution (percentiles)
    return_10th = Column(Numeric(8, 4), nullable=False)
    return_25th = Column(Numeric(8, 4), nullable=False)
    return_50th = Column(Numeric(8, 4), nullable=False)  # Median
    return_75th = Column(Numeric(8, 4), nullable=False)
    return_90th = Column(Numeric(8, 4), nullable=False)
    
    # Probability estimates
    prob_positive_return = Column(Numeric(5, 4), nullable=False)
    prob_beat_market = Column(Numeric(5, 4), nullable=True)  # vs index
    
    # Volatility forecast
    expected_volatility = Column(Numeric(8, 4), nullable=False)
    volatility_10th = Column(Numeric(8, 4), nullable=True)
    volatility_90th = Column(Numeric(8, 4), nullable=True)
    
    # Confidence metrics
    confidence_score = Column(Numeric(5, 4), nullable=False)  # 0-1
    model_agreement = Column(Numeric(5, 4), nullable=True)  # Ensemble agreement
    
    # Model details
    model_version = Column(String(50), nullable=True)
    ensemble_weights = Column(JSONB, nullable=True)
    
    # Feature importance for this prediction
    top_features = Column(JSONB, nullable=True)
    
    # Historical pattern matches
    similar_patterns = Column(JSONB, nullable=True)  # Historical analog outcomes
    pattern_count = Column(BigInteger, nullable=True)
    pattern_win_rate = Column(Numeric(5, 4), nullable=True)
    
    # Context
    regime_at_prediction = Column(String(50), nullable=True)
    technical_score = Column(Numeric(4, 1), nullable=True)
    
    # Actual outcome (filled after horizon passes)
    actual_return = Column(Numeric(8, 4), nullable=True)
    prediction_error = Column(Numeric(8, 4), nullable=True)
    was_correct = Column(String(10), nullable=True)  # correct, incorrect, neutral
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    prediction_date = Column(DateTime, nullable=False)  # Date prediction is for
    expires_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_prediction_symbol_date", "symbol", "created_at"),
    )


class RegimeState(Base):
    """
    Market regime classification history.
    
    Tracks regime transitions and probabilities.
    """
    __tablename__ = "regime_states"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Current regime
    regime = Column(String(50), nullable=False)  # bull_trend_low_vol, bear_trend_high_vol, etc.
    regime_probability = Column(Numeric(5, 4), nullable=False)
    
    # Regime components
    trend_direction = Column(String(20), nullable=False)  # up, down, sideways
    trend_strength = Column(Numeric(5, 4), nullable=False)  # ADX-based
    volatility_state = Column(String(20), nullable=False)  # low, normal, high
    volatility_percentile = Column(Numeric(5, 4), nullable=False)
    
    # Market breadth
    breadth_pct = Column(Numeric(5, 4), nullable=True)  # % stocks above 200 MA
    advance_decline_ratio = Column(Numeric(8, 4), nullable=True)
    
    # Correlation environment
    avg_correlation = Column(Numeric(5, 4), nullable=True)
    correlation_regime = Column(String(20), nullable=True)  # high, normal, low
    
    # Index levels
    nifty_close = Column(Numeric(12, 2), nullable=True)
    nifty_50_ma = Column(Numeric(12, 2), nullable=True)
    nifty_200_ma = Column(Numeric(12, 2), nullable=True)
    vix = Column(Numeric(8, 2), nullable=True)
    
    # Regime probabilities (from HMM)
    all_regime_probs = Column(JSONB, nullable=True)  # {regime: probability}
    
    # Transition probabilities
    transition_probs = Column(JSONB, nullable=True)  # Next likely regimes
    
    # Model details
    model_version = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_regime_date", "date"),
    )


class FeatureStore(Base):
    """
    Computed features for ML models.
    
    Pre-computed technical indicators and derived features.
    """
    __tablename__ = "feature_store"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Feature vector (stored as JSONB for flexibility)
    features = Column(JSONB, nullable=False)
    
    # Feature groups for selective retrieval
    price_features = Column(JSONB, nullable=True)
    volume_features = Column(JSONB, nullable=True)
    momentum_features = Column(JSONB, nullable=True)
    volatility_features = Column(JSONB, nullable=True)
    pattern_features = Column(JSONB, nullable=True)
    regime_features = Column(JSONB, nullable=True)
    
    # Version tracking
    feature_version = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_feature_symbol_date", "symbol", "date"),
    )
