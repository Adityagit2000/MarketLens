"""
Performance API

Endpoints for performance analytics and reporting.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.db.database import get_db

router = APIRouter()


@router.get("/summary")
async def get_performance_summary(
    period: str = Query("monthly", pattern="^(weekly|monthly|quarterly|yearly)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get performance summary for specified period.
    """
    return {
        "period": period,
        "period_start": "2026-01-01",
        "period_end": "2026-02-06",
        "trade_statistics": {
            "total_trades": 24,
            "winners": 15,
            "losers": 9,
            "win_rate": 62.5,
        },
        "return_statistics": {
            "avg_win_pct": 3.8,
            "avg_loss_pct": -1.6,
            "largest_win_pct": 8.2,
            "largest_loss_pct": -2.8,
            "expectancy": 1.7,
        },
        "risk_adjusted": {
            "profit_factor": 2.8,
            "sharpe_ratio": 2.1,
            "sortino_ratio": 2.8,
            "max_drawdown_pct": 3.2,
        },
        "portfolio_returns": {
            "total_return_pct": 4.21,
            "annualized_return": None,  # Calculated for yearly
        },
        "execution_quality": {
            "avg_entry_slippage": 0.08,
            "avg_exit_slippage": 0.12,
            "total_charges": 4200.00,
        },
    }


@router.get("/discipline")
async def get_discipline_report(
    period: str = Query("monthly"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get discipline and behavioral analysis report.
    """
    return {
        "period": period,
        "plan_adherence": {
            "total_trades": 24,
            "followed_plan": 21,
            "adherence_rate": 87.5,
        },
        "deviations": {
            "total": 3,
            "by_type": {
                "premature_exit": 2,
                "entry_chase": 1,
                "stop_not_honored": 0,
            },
        },
        "deviation_impact": {
            "premature_exits": {
                "count": 2,
                "avg_missed_gain": 2.4,
                "description": "Winners cut short averaged +2.1%, targets were +4.5%",
            },
            "entry_chase": {
                "count": 1,
                "slippage_cost": 0.8,
                "description": "Chased entry resulted in worse fill",
            },
        },
        "emotion_distribution": {
            "DISCIPLINED": 21,
            "FEAR": 2,
            "FOMO": 1,
            "HOPE": 0,
        },
        "recommendations": [
            "Practice holding winners to target",
            "Use limit orders more consistently",
        ],
    }


@router.get("/model")
async def get_model_performance(
    db: AsyncSession = Depends(get_db),
):
    """
    Get ML model performance metrics.
    """
    return {
        "overall": {
            "prediction_accuracy": 65.2,
            "brier_score": 0.18,
            "calibration_status": "well_calibrated",
        },
        "by_probability_bucket": [
            {"bucket": "<50%", "predicted": 45, "actual": 42, "error": -3},
            {"bucket": "50-60%", "predicted": 55, "actual": 52, "error": -3},
            {"bucket": "60-70%", "predicted": 65, "actual": 67, "error": 2},
            {"bucket": "70-80%", "predicted": 75, "actual": 71, "error": -4},
            {"bucket": ">80%", "predicted": 85, "actual": 78, "error": -7},
        ],
        "by_regime": [
            {
                "regime": "bull_trend_low_vol",
                "trades": 12,
                "accuracy": 73,
                "avg_return": 3.2,
            },
            {
                "regime": "bull_trend_high_vol",
                "trades": 5,
                "accuracy": 60,
                "avg_return": 1.8,
            },
            {
                "regime": "ranging_low_vol",
                "trades": 7,
                "accuracy": 57,
                "avg_return": 0.9,
            },
        ],
        "feature_importance": [
            {"feature": "trend_alignment", "importance": 0.18},
            {"feature": "support_proximity", "importance": 0.15},
            {"feature": "volume_profile", "importance": 0.12},
            {"feature": "rsi_regime_adjusted", "importance": 0.10},
            {"feature": "sector_momentum", "importance": 0.08},
        ],
        "recommendations": [
            "Model performs best in bull_trend_low_vol regime",
            "Consider reducing trading in ranging_low_vol markets",
            "Trend alignment is the most predictive feature",
        ],
    }


@router.get("/trades")
async def get_trade_history(
    limit: int = Query(50, ge=1, le=200),
    outcome: Optional[str] = Query(None, pattern="^(win|loss)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get trade history with outcomes.
    """
    trades = [
        {
            "id": 1,
            "symbol": "INFY",
            "entry_date": "2026-01-20",
            "exit_date": "2026-01-25",
            "return_pct": 4.2,
            "outcome": "win",
            "exit_type": "target_1",
            "plan_followed": True,
        },
        {
            "id": 2,
            "symbol": "SBIN",
            "entry_date": "2026-01-22",
            "exit_date": "2026-01-24",
            "return_pct": -1.8,
            "outcome": "loss",
            "exit_type": "stop_loss",
            "plan_followed": True,
        },
        {
            "id": 3,
            "symbol": "WIPRO",
            "entry_date": "2026-01-25",
            "exit_date": "2026-01-30",
            "return_pct": 2.9,
            "outcome": "win",
            "exit_type": "manual",
            "plan_followed": False,
        },
    ]
    
    if outcome:
        trades = [t for t in trades if t["outcome"] == outcome]
    
    return {
        "count": len(trades),
        "trades": trades[:limit],
    }


@router.get("/report")
async def generate_report(
    period: str = Query("monthly"),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate comprehensive performance report.
    """
    return {
        "report_type": period,
        "generated_at": datetime.now().isoformat(),
        "period": {
            "start": "2026-01-01",
            "end": "2026-02-06",
        },
        "sections": {
            "summary": "/api/performance/summary",
            "discipline": "/api/performance/discipline",
            "model": "/api/performance/model",
            "trades": "/api/performance/trades",
        },
        "highlights": [
            "Win rate: 62.5% (target: 60%)",
            "Profit factor: 2.8 (excellent)",
            "Plan adherence: 87.5%",
            "Best performing regime: Bull Trend Low Vol",
        ],
        "areas_for_improvement": [
            "Premature exits costing an average of 2.4% per trade",
            "Model slightly overconfident in >80% probability bucket",
        ],
    }
