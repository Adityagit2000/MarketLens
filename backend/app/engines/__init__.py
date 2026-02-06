"""
Market Intelligence Engines

Core processing engines for the trading system:
- Data Ingestion: Fetch, validate, and normalize market data
- Market Structure: Regime classification and market analysis
- Technical Analysis: Multi-timeframe indicator analysis
- Price Action: Pattern recognition and price structure
- ML Prediction: Probabilistic forecasting with ensemble models
- Risk Management: Trade structuring and position sizing
- Execution: Trade preparation and fill tracking
- Performance Analytics: Post-mortem analysis and feedback loop
"""

from app.engines.base import BaseEngine

__all__ = ["BaseEngine"]
