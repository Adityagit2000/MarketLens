"""
Trades API

Endpoints for trade execution, logging, and management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db

router = APIRouter()


class TradeEntryRequest(BaseModel):
    """Request model for logging trade entry."""
    plan_id: Optional[int] = None
    symbol: str
    entry_price: float
    quantity: int
    order_type: str = "limit"  # market, limit
    stop_loss_placed: bool = False
    notes: Optional[str] = None


class TradeExitRequest(BaseModel):
    """Request model for logging trade exit."""
    trade_id: int
    exit_price: float
    quantity: Optional[int] = None  # Partial exit if not full
    exit_type: str = "manual"  # stop_loss, target_1, target_2, manual
    notes: Optional[str] = None


@router.post("/entry")
async def log_trade_entry(
    entry: TradeEntryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Log a trade entry after execution.
    
    Records actual fill details and calculates slippage.
    """
    # In production, this would:
    # 1. Fetch the trade plan
    # 2. Calculate slippage
    # 3. Create trade record
    # 4. Create position record
    # 5. Update portfolio allocation
    
    planned_price = 2450.00  # Would come from plan
    slippage_pct = ((entry.entry_price - planned_price) / planned_price) * 100
    
    return {
        "status": "success",
        "trade_id": 12345,
        "symbol": entry.symbol.upper(),
        "entry_price": entry.entry_price,
        "quantity": entry.quantity,
        "slippage_pct": round(slippage_pct, 4),
        "position_created": True,
        "message": f"Trade logged successfully. Entry slippage: {slippage_pct:+.2f}%",
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/exit")
async def log_trade_exit(
    exit_req: TradeExitRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Log a trade exit.
    
    Records exit details and calculates P&L.
    """
    # Simulated values
    entry_price = 2448.00
    quantity = exit_req.quantity or 120
    gross_pnl = (exit_req.exit_price - entry_price) * quantity
    charges = 150.00  # Brokerage + taxes
    net_pnl = gross_pnl - charges
    return_pct = ((exit_req.exit_price / entry_price) - 1) * 100
    
    return {
        "status": "success",
        "trade_id": exit_req.trade_id,
        "exit_price": exit_req.exit_price,
        "quantity": quantity,
        "exit_type": exit_req.exit_type,
        "gross_pnl": gross_pnl,
        "charges": charges,
        "net_pnl": net_pnl,
        "return_pct": round(return_pct, 4),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/")
async def get_trades(
    status: Optional[str] = None,  # open, closed
    symbol: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of trades with optional filters.
    """
    # Sample data
    trades = [
        {
            "id": 12345,
            "symbol": "RELIANCE",
            "status": "open",
            "direction": "long",
            "entry_price": 2448.00,
            "quantity": 120,
            "current_price": 2465.00,
            "unrealized_pnl": 2040.00,
            "stop_loss": 2390.00,
            "target_1": 2570.00,
            "entry_date": "2026-02-04",
            "days_held": 2,
        },
        {
            "id": 12344,
            "symbol": "INFY",
            "status": "closed",
            "direction": "long",
            "entry_price": 1450.00,
            "exit_price": 1511.00,
            "quantity": 150,
            "net_pnl": 9150.00,
            "return_pct": 4.2,
            "entry_date": "2026-01-20",
            "exit_date": "2026-01-25",
        },
    ]
    
    if status:
        trades = [t for t in trades if t["status"] == status]
    if symbol:
        trades = [t for t in trades if t["symbol"] == symbol.upper()]
    
    return {
        "count": len(trades),
        "trades": trades[:limit],
    }


@router.get("/{trade_id}")
async def get_trade_detail(
    trade_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific trade.
    """
    return {
        "id": trade_id,
        "symbol": "RELIANCE",
        "status": "open",
        "direction": "long",
        "plan": {
            "entry_price": 2450.00,
            "stop_loss": 2390.00,
            "target_1": 2570.00,
            "target_2": 2650.00,
            "position_size": 120,
        },
        "execution": {
            "entry_price": 2448.00,
            "entry_slippage_pct": -0.08,
            "quantity": 120,
            "entry_time": "2026-02-04T10:15:00",
            "order_type": "limit",
        },
        "current_state": {
            "current_price": 2465.00,
            "unrealized_pnl": 2040.00,
            "unrealized_pnl_pct": 0.69,
            "progress_to_target": 14,  # Percentage
            "progress_to_stop": -130,  # Negative = moving away from stop
        },
        "context": {
            "regime_at_entry": "bull_trend_low_vol",
            "technical_score_at_entry": 7,
            "rationale": [
                "Price testing 50-day MA support",
                "High volume with conviction",
            ],
        },
        "deviations": [],
        "notes": None,
    }


@router.put("/{trade_id}/stop")
async def update_stop_loss(
    trade_id: int,
    new_stop: float,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Update stop-loss for an open trade.
    """
    return {
        "status": "success",
        "trade_id": trade_id,
        "old_stop": 2390.00,
        "new_stop": new_stop,
        "reason": reason or "Manual adjustment",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/{trade_id}/postmortem")
async def get_trade_postmortem(
    trade_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get post-mortem analysis for a closed trade.
    """
    return {
        "trade_id": trade_id,
        "symbol": "INFY",
        "outcome": {
            "planned_return": 0.035,
            "actual_return": 0.042,
            "outcome_vs_plan": 0.007,
            "exit_type": "target_1",
            "days_held": 5,
        },
        "execution_quality": {
            "entry_slippage": -0.1,
            "exit_slippage": 0.2,
            "total_charges_pct": 0.08,
        },
        "model_performance": {
            "prediction_accuracy": "correct",
            "predicted_prob": 0.64,
            "actual_outcome": "win",
        },
        "what_worked": [
            "Entry at support (50-day MA) was precise",
            "IT sector rotation played out as predicted",
            "Volume confirmation validated setup",
        ],
        "lessons_learned": [
            "Pullback entries in strong uptrends work well",
            "Consider trailing stop to Target 2 next time",
        ],
        "deviations": [],
        "emotion_tag": "DISCIPLINED",
    }
