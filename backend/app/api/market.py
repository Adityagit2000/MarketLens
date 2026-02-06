"""
Market API

Endpoints for market regime and structure information.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.database import get_db

router = APIRouter()


@router.get("/regime")
async def get_current_regime(
    db: AsyncSession = Depends(get_db),
):
    """
    Get current market regime classification.
    """
    return {
        "regime": "bull_trend_low_vol",
        "regime_display": "Bull Trend - Low Volatility",
        "confidence": 0.78,
        "components": {
            "trend": {
                "direction": "up",
                "strength": 0.72,
                "ma_alignment": "price > ma50 > ma200",
            },
            "volatility": {
                "state": "low",
                "percentile": 0.22,
                "vix": 12.4,
            },
            "breadth": {
                "pct_above_200ma": 0.68,
                "advance_decline": 1.4,
            },
            "correlation": {
                "avg_correlation": 0.45,
                "state": "normal",
            },
        },
        "index_levels": {
            "nifty_50": 23450,
            "nifty_50_change_pct": 0.8,
            "nifty_50_ma": 23200,
            "nifty_200_ma": 22500,
        },
        "signal": {
            "type": "FAVORABLE",
            "message": "Favorable for momentum strategies",
            "recommendation": "Normal position sizing",
        },
        "regime_probabilities": {
            "bull_trend_low_vol": 0.78,
            "bull_trend_high_vol": 0.12,
            "ranging_low_vol": 0.08,
            "bear_trend": 0.02,
        },
        "transition_outlook": {
            "most_likely_next": "bull_trend_low_vol",
            "stability": 0.85,
        },
        "last_updated": datetime.now().isoformat(),
    }


@router.get("/regime/history")
async def get_regime_history(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """
    Get historical regime classifications.
    """
    return {
        "period_days": days,
        "history": [
            {"date": "2026-01-07", "regime": "bull_trend_low_vol", "confidence": 0.75},
            {"date": "2026-01-14", "regime": "bull_trend_low_vol", "confidence": 0.78},
            {"date": "2026-01-21", "regime": "bull_trend_low_vol", "confidence": 0.72},
            {"date": "2026-01-28", "regime": "ranging_low_vol", "confidence": 0.65},
            {"date": "2026-02-04", "regime": "bull_trend_low_vol", "confidence": 0.76},
        ],
        "regime_distribution": {
            "bull_trend_low_vol": 80,
            "ranging_low_vol": 20,
        },
    }


@router.get("/sectors")
async def get_sector_analysis(
    db: AsyncSession = Depends(get_db),
):
    """
    Get sector rotation and relative strength analysis.
    """
    return {
        "sectors": [
            {
                "name": "Energy",
                "relative_strength": 1.12,
                "momentum_20d": 3.2,
                "rank": 1,
                "signal": "strong_outperformer",
            },
            {
                "name": "Banking",
                "relative_strength": 1.05,
                "momentum_20d": 1.8,
                "rank": 2,
                "signal": "outperformer",
            },
            {
                "name": "IT",
                "relative_strength": 0.98,
                "momentum_20d": -0.5,
                "rank": 3,
                "signal": "neutral",
            },
            {
                "name": "Pharma",
                "relative_strength": 0.92,
                "momentum_20d": -2.1,
                "rank": 4,
                "signal": "underperformer",
            },
        ],
        "rotation_signal": {
            "leading": ["Energy", "Banking"],
            "lagging": ["Pharma", "Auto"],
            "recommendation": "Focus longs on Energy and Banking sectors",
        },
        "last_updated": datetime.now().isoformat(),
    }


@router.get("/breadth")
async def get_market_breadth(
    db: AsyncSession = Depends(get_db),
):
    """
    Get market breadth indicators.
    """
    return {
        "nifty_50": {
            "above_200ma": 68,
            "above_50ma": 72,
            "above_20ma": 65,
            "new_highs_20d": 8,
            "new_lows_20d": 2,
        },
        "advance_decline": {
            "today": {"advances": 32, "declines": 18, "ratio": 1.78},
            "5_day_avg": {"advances": 28, "declines": 22, "ratio": 1.27},
        },
        "cumulative_breadth": {
            "ad_line_trend": "up",
            "divergence": None,
        },
        "interpretation": {
            "overall": "Healthy breadth supporting market advance",
            "signals": [
                "Strong participation (68% above 200MA)",
                "Advance-decline ratio positive",
                "No bearish divergence detected",
            ],
        },
    }
