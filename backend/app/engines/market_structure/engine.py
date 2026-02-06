"""
Market Structure Engine

Analyzes market regime, volatility, breadth, and correlations.
Provides context for downstream engines to adapt strategies.
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from enum import Enum

from app.engines.base import BaseEngine
from app.config.settings import settings


class MarketRegime(str, Enum):
    """Market regime classifications."""
    BULL_TREND_LOW_VOL = "bull_trend_low_vol"
    BULL_TREND_HIGH_VOL = "bull_trend_high_vol"
    BEAR_TREND_LOW_VOL = "bear_trend_low_vol"
    BEAR_TREND_HIGH_VOL = "bear_trend_high_vol"
    RANGING_LOW_VOL = "ranging_low_vol"
    RANGING_HIGH_VOL = "ranging_high_vol"


class MarketStructureEngine(BaseEngine):
    """
    Engine 2: Market Structure & Regime Classification
    
    Responsibilities:
    - Classify market regime (trending vs ranging, volatility level)
    - Analyze market breadth
    - Track sector rotation
    - Compute correlation environment
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("market_structure", config)
        self.lookback_days = settings.REGIME_LOOKBACK_DAYS
        self.hmm_components = settings.HMM_N_COMPONENTS

    async def process(
        self,
        index_data: Optional[pd.DataFrame] = None,
        constituent_data: Optional[Dict[str, pd.DataFrame]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze current market structure.
        
        Returns regime classification and component metrics.
        """
        self._set_status("processing")
        
        # Use mock data if not provided
        if index_data is None:
            index_data = self._create_mock_index_data()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "regime": None,
            "regime_probability": 0.0,
            "components": {},
        }
        
        try:
            # 1. Trend Analysis
            trend = self._analyze_trend(index_data)
            results["components"]["trend"] = trend
            
            # 2. Volatility Analysis
            volatility = self._analyze_volatility(index_data)
            results["components"]["volatility"] = volatility
            
            # 3. Breadth Analysis
            breadth = self._analyze_breadth(constituent_data)
            results["components"]["breadth"] = breadth
            
            # 4. Classify Regime
            regime, probability = self._classify_regime(trend, volatility, breadth)
            results["regime"] = regime.value
            results["regime_probability"] = probability
            
            # 5. Generate Signal
            results["signal"] = self._generate_signal(regime, volatility)
            
            self._update_run_time()
            
        except Exception as e:
            self.logger.error(f"Market structure analysis failed: {e}")
            results["error"] = str(e)
        
        self._set_status("ready")
        return results

    def _create_mock_index_data(self) -> pd.DataFrame:
        """Create mock Nifty 50 data."""
        dates = pd.date_range(end=date.today(), periods=250, freq="B")
        np.random.seed(42)
        
        # Simulate trending market with some noise
        returns = np.random.normal(0.0005, 0.012, len(dates))
        prices = 20000 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            "date": dates,
            "close": prices,
            "high": prices * (1 + np.abs(np.random.normal(0, 0.008, len(dates)))),
            "low": prices * (1 - np.abs(np.random.normal(0, 0.008, len(dates)))),
            "volume": np.random.uniform(1e8, 5e8, len(dates)),
        })
        
        return df

    def _analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze trend using moving averages and ADX.
        """
        close = df["close"].values
        
        # Calculate moving averages
        ma_50 = pd.Series(close).rolling(50).mean().iloc[-1]
        ma_200 = pd.Series(close).rolling(200).mean().iloc[-1]
        current_price = close[-1]
        
        # MA slope (10-day rate of change)
        ma_50_series = pd.Series(close).rolling(50).mean()
        ma_slope = (ma_50_series.iloc[-1] - ma_50_series.iloc[-10]) / ma_50_series.iloc[-10]
        
        # Determine trend direction
        if current_price > ma_50 > ma_200 and ma_slope > 0:
            direction = "strong_up"
            strength = 0.8 + min(ma_slope * 10, 0.2)
        elif current_price > ma_200:
            direction = "up"
            strength = 0.6
        elif current_price < ma_50 < ma_200 and ma_slope < 0:
            direction = "strong_down"
            strength = 0.8 + min(abs(ma_slope) * 10, 0.2)
        elif current_price < ma_200:
            direction = "down"
            strength = 0.6
        else:
            direction = "sideways"
            strength = 0.3
        
        # Calculate ADX (simplified)
        adx = self._calculate_adx(df)
        
        return {
            "direction": direction,
            "strength": round(strength, 2),
            "ma_50": round(ma_50, 2),
            "ma_200": round(ma_200, 2),
            "ma_alignment": f"price {'>' if current_price > ma_50 else '<'} ma50 {'>' if ma_50 > ma_200 else '<'} ma200",
            "adx": round(adx, 2),
        }

    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average Directional Index."""
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        
        # True Range
        tr = np.maximum(
            high[1:] - low[1:],
            np.maximum(
                np.abs(high[1:] - close[:-1]),
                np.abs(low[1:] - close[:-1])
            )
        )
        
        # Simplified ADX calculation
        atr = pd.Series(tr).rolling(period).mean().iloc[-1]
        
        # Use volatility as proxy for ADX
        returns = np.diff(close) / close[:-1]
        recent_volatility = np.std(returns[-20:]) * np.sqrt(252)
        
        # Map volatility to ADX-like scale (0-100)
        adx = min(recent_volatility * 100, 50)
        
        return adx

    def _analyze_volatility(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze volatility regime.
        """
        close = df["close"].values
        returns = np.diff(close) / close[:-1]
        
        # 20-day rolling volatility (annualized)
        recent_vol = np.std(returns[-20:]) * np.sqrt(252)
        
        # Historical percentile (2-year lookback)
        historical_vols = pd.Series(returns).rolling(20).std() * np.sqrt(252)
        vol_percentile = (historical_vols < recent_vol).mean()
        
        # Classify volatility state
        if vol_percentile < 0.33:
            state = "low"
        elif vol_percentile < 0.67:
            state = "normal"
        else:
            state = "high"
        
        return {
            "state": state,
            "current": round(recent_vol * 100, 2),
            "percentile": round(vol_percentile * 100, 2),
            "expanding": recent_vol > np.std(returns[-40:-20]) * np.sqrt(252),
        }

    def _analyze_breadth(
        self, constituent_data: Optional[Dict[str, pd.DataFrame]]
    ) -> Dict[str, Any]:
        """
        Analyze market breadth.
        """
        # Mock breadth data
        return {
            "pct_above_200ma": 68.0,
            "pct_above_50ma": 72.0,
            "advance_decline_ratio": 1.4,
            "new_highs": 8,
            "new_lows": 2,
        }

    def _classify_regime(
        self,
        trend: Dict[str, Any],
        volatility: Dict[str, Any],
        breadth: Dict[str, Any],
    ) -> Tuple[MarketRegime, float]:
        """
        Classify market regime from components.
        """
        is_trending_up = trend["direction"] in ["up", "strong_up"]
        is_trending_down = trend["direction"] in ["down", "strong_down"]
        is_low_vol = volatility["state"] == "low"
        is_high_vol = volatility["state"] == "high"
        
        # Classification logic
        if is_trending_up:
            if is_low_vol:
                return MarketRegime.BULL_TREND_LOW_VOL, 0.78
            elif is_high_vol:
                return MarketRegime.BULL_TREND_HIGH_VOL, 0.72
            else:
                return MarketRegime.BULL_TREND_LOW_VOL, 0.65
        elif is_trending_down:
            if is_low_vol:
                return MarketRegime.BEAR_TREND_LOW_VOL, 0.75
            elif is_high_vol:
                return MarketRegime.BEAR_TREND_HIGH_VOL, 0.80
            else:
                return MarketRegime.BEAR_TREND_HIGH_VOL, 0.65
        else:
            if is_low_vol:
                return MarketRegime.RANGING_LOW_VOL, 0.70
            else:
                return MarketRegime.RANGING_HIGH_VOL, 0.68

    def _generate_signal(
        self, regime: MarketRegime, volatility: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate trading signal based on regime.
        """
        signals = {
            MarketRegime.BULL_TREND_LOW_VOL: {
                "type": "FAVORABLE",
                "message": "Favorable for momentum strategies",
                "recommendation": "Normal position sizing",
            },
            MarketRegime.BULL_TREND_HIGH_VOL: {
                "type": "CAUTION",
                "message": "Volatile bull market - take profits",
                "recommendation": "Reduced position sizing",
            },
            MarketRegime.BEAR_TREND_LOW_VOL: {
                "type": "DEFENSIVE",
                "message": "Bear market - watch for reversal",
                "recommendation": "Minimal new positions",
            },
            MarketRegime.BEAR_TREND_HIGH_VOL: {
                "type": "AVOID",
                "message": "High-risk bear market",
                "recommendation": "Stay in cash",
            },
            MarketRegime.RANGING_LOW_VOL: {
                "type": "NEUTRAL",
                "message": "Choppy market - mean reversion",
                "recommendation": "Selective trading",
            },
            MarketRegime.RANGING_HIGH_VOL: {
                "type": "AVOID",
                "message": "High-volatility chop",
                "recommendation": "Avoid trading",
            },
        }
        
        return signals.get(regime, signals[MarketRegime.RANGING_LOW_VOL])
