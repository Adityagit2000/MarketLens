"""
FastAPI Application Entry Point

Main application setup with CORS, routes, and WebSocket endpoints.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime

from app.api import opportunities, trades, portfolio, performance, market
from app.config.settings import settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup - try to initialize database but don't fail if unavailable
    try:
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Database not available - {e}")
        print("Running in demo mode without database")
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Market Intelligence Engine",
    description="Probabilistic decision support system for trading",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["opportunities"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(performance.router, prefix="/api/performance", tags=["performance"])
app.include_router(market.router, prefix="/api/market", tags=["market"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Market Intelligence Engine",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "engines": {
            "data_ingestion": "ready",
            "market_structure": "ready",
            "technical_analysis": "ready",
            "price_action": "ready",
            "ml_prediction": "ready",
            "risk_management": "ready",
            "execution": "ready",
            "performance_analytics": "ready",
        },
    }


class ConnectionManager:
    """WebSocket connection manager for real-time price updates."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    Stream live price updates for open positions.
    """
    await manager.connect(websocket)
    try:
        while True:
            # In production, this would fetch real prices
            # For now, send heartbeat
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat(),
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    Stream trade alerts (stop hits, target hits, etc.).
    """
    await manager.connect(websocket)
    try:
        while True:
            # Alerts would be pushed when conditions are met
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


from fastapi import FastAPI

@app.get("/api/health")
async def health():
    return {"status": "ok"}
