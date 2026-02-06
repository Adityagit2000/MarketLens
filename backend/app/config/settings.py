"""
Application Settings

Configuration management using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Market Intelligence Engine"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/market_intelligence"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Trading Parameters
    DEFAULT_RISK_PER_TRADE: float = 2.0  # Percentage
    MAX_RISK_PER_TRADE: float = 3.0
    MIN_RISK_REWARD_RATIO: float = 2.0
    MAX_POSITIONS: int = 10
    MAX_SECTOR_CONCENTRATION: float = 30.0  # Percentage
    MAX_CAPITAL_DEPLOYMENT: float = 80.0  # Percentage

    # Data Sources
    NSE_BHAVCOPY_BASE_URL: str = "https://nsearchives.nseindia.com/content/historical/EQUITIES"
    DATA_FETCH_TIME: str = "18:00"  # IST

    # ML Model Parameters
    PREDICTION_HORIZONS: List[int] = [5, 10, 20]  # Days
    MIN_PROBABILITY_THRESHOLD: float = 0.60
    MIN_CONFIDENCE_THRESHOLD: float = 0.65
    MODEL_RETRAIN_FREQUENCY: str = "weekly"

    # Feature Engineering
    TECHNICAL_LOOKBACK_PERIODS: List[int] = [5, 10, 20, 50, 100, 200]
    VOLATILITY_LOOKBACK: int = 20
    VOLUME_LOOKBACK: int = 20

    # Regime Classification
    REGIME_LOOKBACK_DAYS: int = 60
    HMM_N_COMPONENTS: int = 5

    # Alerts
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    ENABLE_PUSH_NOTIFICATIONS: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
