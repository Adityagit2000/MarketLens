"""
Risk Management Engine

Trade structuring, position sizing, and portfolio risk management.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np

from app.engines.base import BaseEngine
from app.config.settings import settings


class RiskManagementEngine(BaseEngine):
    """
    Engine 6: Risk Management & Trade Structuring
    
    Responsibilities:
    - Quality filtering (reject low-probability setups)
    - Stop-loss and target calculation
    - Position sizing (fixed risk + Kelly criterion)
    - Portfolio-level constraints
    - Regime-based risk adjustment
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("risk_management", config)
        self.min_probability = settings.MIN_PROBABILITY_THRESHOLD
        self.min_rr_ratio = settings.MIN_RISK_REWARD_RATIO
        self.default_risk_pct = settings.DEFAULT_RISK_PER_TRADE

    async def process(
        self,
        symbol: str,
        prediction: Dict[str, Any],
        technical: Dict[str, Any],
        account_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Structure a trade plan or reject if quality thresholds not met.
        """
        self._set_status("processing")
        
        try:
            # Step 1: Quality filter
            passed, rejection_reason = self._quality_filter(
                prediction, technical
            )
            
            if not passed:
                return {
                    "status": "rejected",
                    "symbol": symbol,
                    "reason": rejection_reason,
                }
            
            # Step 2: Calculate entry, stop, targets
            entry_price = technical.get("entry_price", prediction.get("current_price", 0))
            support = technical.get("support", entry_price * 0.97)
            atr = technical.get("atr", entry_price * 0.02)
            
            stop_loss = self._calculate_stop_loss(entry_price, support, atr)
            targets = self._calculate_targets(
                entry_price, stop_loss, prediction
            )
            
            if targets is None:
                return {
                    "status": "rejected",
                    "symbol": symbol,
                    "reason": "Insufficient risk-reward ratio",
                }
            
            # Step 3: Position sizing
            risk_pct = self._adjust_risk_for_regime(
                account_info.get("regime", "neutral"),
                account_info.get("recent_performance", {}),
            )
            
            position_size, capital_required = self._calculate_position_size(
                account_info["capital"],
                risk_pct,
                entry_price,
                stop_loss,
            )
            
            # Step 4: Build trade plan
            risk_amount = position_size * (entry_price - stop_loss)
            
            trade_plan = {
                "status": "approved",
                "symbol": symbol,
                "entry_price": round(entry_price, 2),
                "stop_loss": round(stop_loss, 2),
                "target_1": round(targets["target_1"], 2),
                "target_2": round(targets.get("target_2", targets["target_1"] * 1.5), 2),
                "position_size": position_size,
                "capital_required": round(capital_required, 2),
                "risk_amount": round(risk_amount, 2),
                "risk_pct": round(risk_amount / account_info["capital"] * 100, 2),
                "expected_return": prediction.get("return_50th_percentile", 0.03),
                "probability_win": prediction.get("prob_positive_return", 0.6),
                "confidence_score": prediction.get("confidence_score", 0.65),
                "rr_ratio_t1": round(targets["rr_ratio_t1"], 2),
                "rr_ratio_t2": round(targets.get("rr_ratio_t2", targets["rr_ratio_t1"] * 1.5), 2),
                "rationale": technical.get("signals", []),
            }
            
            self._update_run_time()
            return trade_plan
            
        except Exception as e:
            self.logger.error(f"Risk management failed: {e}")
            return {
                "status": "error",
                "symbol": symbol,
                "error": str(e),
            }
        finally:
            self._set_status("ready")

    def _quality_filter(
        self,
        prediction: Dict[str, Any],
        technical: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """Apply quality filters to reject low-probability setups."""
        
        prob = prediction.get("prob_positive_return", 0)
        if prob < self.min_probability:
            return False, f"Probability {prob:.0%} below threshold {self.min_probability:.0%}"
        
        confidence = prediction.get("confidence_score", 0)
        if confidence < settings.MIN_CONFIDENCE_THRESHOLD:
            return False, f"Confidence {confidence:.0%} below threshold"
        
        tech_score = technical.get("score", 0)
        if tech_score < 5:
            return False, f"Technical score {tech_score} below threshold 5"
        
        return True, None

    def _calculate_stop_loss(
        self,
        entry_price: float,
        support: float,
        atr: float,
    ) -> float:
        """Calculate stop-loss at logical invalidation point."""
        # Stop below support with ATR cushion
        technical_stop = support - 0.5 * atr
        
        # Percentage-based max stop
        max_stop = entry_price * 0.95
        
        return max(technical_stop, max_stop)

    def _calculate_targets(
        self,
        entry_price: float,
        stop_loss: float,
        prediction: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Calculate target prices ensuring minimum risk-reward."""
        risk_per_share = entry_price - stop_loss
        
        # Target from prediction
        expected_return = prediction.get("return_50th_percentile", 0.03)
        target_1 = entry_price * (1 + expected_return)
        
        reward = target_1 - entry_price
        rr_ratio = reward / risk_per_share if risk_per_share > 0 else 0
        
        if rr_ratio < self.min_rr_ratio:
            return None
        
        # Target 2 from 75th percentile
        optimistic_return = prediction.get("return_75th_percentile", expected_return * 1.5)
        target_2 = entry_price * (1 + optimistic_return)
        rr_ratio_2 = (target_2 - entry_price) / risk_per_share
        
        return {
            "target_1": target_1,
            "rr_ratio_t1": rr_ratio,
            "target_2": target_2,
            "rr_ratio_t2": rr_ratio_2,
        }

    def _calculate_position_size(
        self,
        capital: float,
        risk_pct: float,
        entry_price: float,
        stop_loss: float,
    ) -> Tuple[int, float]:
        """Calculate position size based on fixed risk percentage."""
        risk_amount = capital * (risk_pct / 100)
        risk_per_share = entry_price - stop_loss
        
        if risk_per_share <= 0:
            return 0, 0.0
        
        position_size = int(risk_amount / risk_per_share)
        capital_required = position_size * entry_price
        
        return position_size, capital_required

    def _adjust_risk_for_regime(
        self,
        regime: str,
        recent_performance: Dict[str, Any],
    ) -> float:
        """Dynamically adjust risk based on regime and performance."""
        risk_pct = self.default_risk_pct
        
        # Regime adjustments
        if "high_vol" in regime or "bear" in regime:
            risk_pct *= 0.5
        elif "ranging" in regime:
            risk_pct *= 0.75
        
        # Performance adjustments
        losing_streak = recent_performance.get("consecutive_losses", 0)
        if losing_streak >= 3:
            risk_pct *= 0.5
        
        return max(0.5, min(risk_pct, 3.0))
