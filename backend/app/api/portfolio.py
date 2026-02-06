"""
Portfolio API

Endpoints for portfolio state, positions, and risk metrics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.db.database import get_db

router = APIRouter()


@router.get("/")
async def get_portfolio_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Get current portfolio summary.
    """
    return {
        "total_capital": 1000000.00,
        "deployed_capital": 620000.00,
        "available_capital": 380000.00,
        "deployment_pct": 62.0,
        "open_positions": 4,
        "capital_at_risk": 18500.00,
        "capital_at_risk_pct": 1.85,
        "portfolio_var_95": 24200.00,
        "unrealized_pnl": {
            "amount": 8400.00,
            "pct": 0.84,
        },
        "realized_pnl": {
            "today": 0.00,
            "mtd": 42100.00,
            "ytd": 85000.00,
        },
        "sector_exposure": {
            "Energy": 294000.00,
            "Banking": 180000.00,
            "IT": 146000.00,
        },
        "last_updated": datetime.now().isoformat(),
    }


@router.get("/positions")
async def get_open_positions(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all open positions with current state.
    """
    positions = [
        {
            "id": 1,
            "symbol": "RELIANCE",
            "direction": "long",
            "quantity": 120,
            "avg_entry": 2448.00,
            "current_price": 2465.00,
            "unrealized_pnl": 2040.00,
            "unrealized_pnl_pct": 0.69,
            "stop_loss": 2390.00,
            "target_1": 2570.00,
            "target_2": 2650.00,
            "progress_to_target": 14,
            "capital_at_risk": 6960.00,
            "days_held": 2,
            "entry_date": "2026-02-04",
            "status": "on_track",
        },
        {
            "id": 2,
            "symbol": "HDFCBANK",
            "direction": "long",
            "quantity": 150,
            "avg_entry": 1580.00,
            "current_price": 1592.00,
            "unrealized_pnl": 1800.00,
            "unrealized_pnl_pct": 0.76,
            "stop_loss": 1550.00,
            "target_1": 1620.00,
            "target_2": 1650.00,
            "progress_to_target": 30,
            "capital_at_risk": 4500.00,
            "days_held": 5,
            "entry_date": "2026-02-01",
            "status": "slow_progress",
        },
    ]
    
    return {
        "count": len(positions),
        "total_unrealized_pnl": sum(p["unrealized_pnl"] for p in positions),
        "total_capital_at_risk": sum(p["capital_at_risk"] for p in positions),
        "positions": positions,
    }


@router.get("/positions/{position_id}")
async def get_position_detail(
    position_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific position.
    """
    return {
        "id": position_id,
        "symbol": "RELIANCE",
        "direction": "long",
        "quantity": 120,
        "avg_entry": 2448.00,
        "current_price": 2465.00,
        "unrealized_pnl": 2040.00,
        "unrealized_pnl_pct": 0.69,
        "stop_loss": 2390.00,
        "target_1": 2570.00,
        "target_2": 2650.00,
        "progress": {
            "to_target_1": 14,
            "to_stop": -130,
            "days_held": 2,
            "max_favorable": 0.85,  # Max % gain reached
            "max_adverse": -0.12,  # Max % loss reached
        },
        "alerts": [
            {
                "type": "info",
                "message": "Position progressing as expected",
                "timestamp": "2026-02-06T14:00:00",
            }
        ],
        "trade_plan": {
            "expected_return": 0.049,
            "probability_win": 0.68,
            "confidence": 0.73,
            "rationale": [
                "Price testing 50-day MA support",
                "High volume with conviction",
            ],
        },
    }


@router.get("/risk")
async def get_portfolio_risk(
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed portfolio risk metrics.
    """
    return {
        "total_capital": 1000000.00,
        "capital_at_risk": 18500.00,
        "capital_at_risk_pct": 1.85,
        "portfolio_var_95": 24200.00,
        "portfolio_var_99": 31500.00,
        "max_drawdown_mtd": 2.1,
        "correlations": {
            "avg_position_correlation": 0.35,
            "highest_correlation": {
                "pair": ["RELIANCE", "HDFCBANK"],
                "correlation": 0.45,
            },
        },
        "concentration": {
            "by_sector": {
                "Energy": 47.4,
                "Banking": 29.0,
                "IT": 23.5,
            },
            "by_position": {
                "RELIANCE": 47.4,
                "HDFCBANK": 29.0,
                "TCS": 23.5,
            },
        },
        "constraints": {
            "max_positions": {"limit": 10, "current": 4, "available": 6},
            "max_sector_concentration": {"limit": 30.0, "max_current": 29.4},
            "max_capital_deployment": {"limit": 80.0, "current": 62.0},
        },
    }


@router.get("/equity-curve")
async def get_equity_curve(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """
    Get historical equity curve data.
    """
    # Sample data points
    return {
        "period_days": days,
        "starting_value": 1000000.00,
        "ending_value": 1042100.00,
        "total_return_pct": 4.21,
        "data_points": [
            {"date": "2026-01-07", "equity": 1000000.00},
            {"date": "2026-01-14", "equity": 1012000.00},
            {"date": "2026-01-21", "equity": 1025000.00},
            {"date": "2026-01-28", "equity": 1031000.00},
            {"date": "2026-02-04", "equity": 1038000.00},
            {"date": "2026-02-06", "equity": 1042100.00},
        ],
    }
