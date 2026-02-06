"""
Technical Analysis Engine

Multi-timeframe indicator analysis with context-aware interpretation.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from app.engines.base import BaseEngine


class TechnicalAnalysisEngine(BaseEngine):
    """
    Engine 3: Technical Analysis Intelligence Layer
    
    Computes and interprets technical indicators across multiple timeframes.
    Provides confluence scoring and plain-English signal explanations.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("technical_analysis", config)

    async def process(
        self,
        symbol: str,
        ohlcv_data: pd.DataFrame,
        regime: str = "bull_trend_low_vol",
    ) -> Dict[str, Any]:
        """
        Analyze technical indicators for a symbol.
        """
        self._set_status("processing")
        
        results = {
            "symbol": symbol,
            "score": 0,
            "signals": [],
            "indicators": {},
            "support_resistance": {},
            "relative_strength": {},
        }
        
        try:
            # Calculate indicators
            results["indicators"] = self._calculate_indicators(ohlcv_data)
            
            # Calculate score
            results["score"], results["signals"] = self._calculate_score(
                results["indicators"], regime
            )
            
            # Find support/resistance
            results["support_resistance"] = self._find_support_resistance(ohlcv_data)
            
            self._update_run_time()
            
        except Exception as e:
            self.logger.error(f"Technical analysis failed: {e}")
            results["error"] = str(e)
        
        self._set_status("ready")
        return results

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators."""
        close = df["close"].values
        high = df["high"].values
        low = df["low"].values
        volume = df["volume"].values
        
        # Moving Averages
        ma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
        ma_50 = pd.Series(close).rolling(50).mean().iloc[-1]
        ma_200 = pd.Series(close).rolling(200).mean().iloc[-1] if len(close) >= 200 else None
        
        # RSI
        rsi = self._calculate_rsi(close, 14)
        
        # MACD
        macd, signal, histogram = self._calculate_macd(close)
        
        # Bollinger Bands
        bb_upper, bb_lower, bb_width = self._calculate_bollinger(close)
        
        # Volume
        avg_volume = pd.Series(volume).rolling(20).mean().iloc[-1]
        volume_ratio = volume[-1] / avg_volume if avg_volume > 0 else 1.0
        
        return {
            "ma_20": round(ma_20, 2),
            "ma_50": round(ma_50, 2),
            "ma_200": round(ma_200, 2) if ma_200 else None,
            "rsi": round(rsi, 2),
            "macd": round(macd, 4),
            "macd_signal": round(signal, 4),
            "macd_histogram": round(histogram, 4),
            "bb_upper": round(bb_upper, 2),
            "bb_lower": round(bb_lower, 2),
            "bb_width": round(bb_width, 4),
            "volume_ratio": round(volume_ratio, 2),
            "current_price": round(close[-1], 2),
        }

    def _calculate_rsi(self, close: np.ndarray, period: int = 14) -> float:
        """Calculate RSI."""
        deltas = np.diff(close)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = pd.Series(gains).rolling(period).mean().iloc[-1]
        avg_loss = pd.Series(losses).rolling(period).mean().iloc[-1]
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def _calculate_macd(
        self, close: np.ndarray
    ) -> tuple[float, float, float]:
        """Calculate MACD."""
        ema_12 = pd.Series(close).ewm(span=12).mean().iloc[-1]
        ema_26 = pd.Series(close).ewm(span=26).mean().iloc[-1]
        
        macd_line = ema_12 - ema_26
        
        # Signal line (9-period EMA of MACD)
        macd_series = pd.Series(close).ewm(span=12).mean() - pd.Series(close).ewm(span=26).mean()
        signal_line = macd_series.ewm(span=9).mean().iloc[-1]
        
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram

    def _calculate_bollinger(
        self, close: np.ndarray, period: int = 20, std_dev: float = 2.0
    ) -> tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        series = pd.Series(close)
        ma = series.rolling(period).mean().iloc[-1]
        std = series.rolling(period).std().iloc[-1]
        
        upper = ma + std_dev * std
        lower = ma - std_dev * std
        width = (upper - lower) / ma
        
        return upper, lower, width

    def _calculate_score(
        self, indicators: Dict[str, Any], regime: str
    ) -> tuple[int, list]:
        """Calculate technical score and generate signals."""
        score = 0
        signals = []
        
        price = indicators["current_price"]
        ma_50 = indicators["ma_50"]
        ma_200 = indicators["ma_200"]
        rsi = indicators["rsi"]
        macd_hist = indicators["macd_histogram"]
        volume_ratio = indicators["volume_ratio"]
        
        # Trend alignment
        if ma_200 and price > ma_50 > ma_200:
            score += 2
            signals.append("Strong trend alignment (price > MA50 > MA200)")
        elif ma_200 and price > ma_200:
            score += 1
            signals.append("Above long-term moving average")
        
        # RSI (regime-adjusted)
        if regime.startswith("bull") and rsi < 40:
            score += 1
            signals.append(f"RSI oversold in uptrend ({rsi:.0f})")
        elif rsi > 70:
            score -= 1
            signals.append(f"RSI overbought ({rsi:.0f})")
        
        # MACD
        if macd_hist > 0:
            score += 1
            signals.append("Positive MACD momentum")
        
        # Volume
        if volume_ratio > 1.5:
            score += 1
            signals.append(f"High volume ({volume_ratio:.1f}x average)")
        
        return score, signals

    def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Find support and resistance levels."""
        high = df["high"].values[-50:]
        low = df["low"].values[-50:]
        close = df["close"].values[-1]
        
        # Simple approach: recent swing highs/lows
        resistance = float(np.percentile(high, 90))
        support = float(np.percentile(low, 10))
        
        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "distance_to_support_pct": round((close - support) / close * 100, 2),
            "distance_to_resistance_pct": round((resistance - close) / close * 100, 2),
        }
