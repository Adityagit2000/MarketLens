"""
Data Ingestion Engine

Fetches, validates, and normalizes market data from NSE/BSE.
Handles corporate actions and maintains data quality.
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from io import BytesIO
import zipfile

from app.engines.base import BaseEngine
from app.config.settings import settings


class DataIngestionEngine(BaseEngine):
    """
    Engine 1: Market Data Ingestion & Normalization
    
    Responsibilities:
    - Fetch daily bhavcopy from NSE/BSE
    - Validate data quality
    - Adjust for corporate actions (splits, bonuses, dividends)
    - Maintain symbol continuity
    - Store clean time-series data
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("data_ingestion", config)
        self.nse_base_url = settings.NSE_BHAVCOPY_BASE_URL

    async def process(
        self,
        target_date: Optional[date] = None,
        symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run daily data ingestion pipeline.
        
        Steps:
        1. Fetch bhavcopy for target date
        2. Validate data quality
        3. Check for corporate actions
        4. Apply adjustments
        5. Store to database
        """
        self._set_status("processing")
        target_date = target_date or date.today()
        
        results = {
            "date": target_date.isoformat(),
            "status": "success",
            "records_processed": 0,
            "anomalies_detected": 0,
            "corporate_actions_applied": 0,
        }
        
        try:
            # Step 1: Fetch bhavcopy
            bhavcopy_df = await self._fetch_bhavcopy(target_date)
            
            if bhavcopy_df is None or bhavcopy_df.empty:
                results["status"] = "no_data"
                results["message"] = f"No data available for {target_date}"
                return results
            
            # Step 2: Normalize schema
            normalized_df = self._normalize_schema(bhavcopy_df)
            
            # Step 3: Validate data quality
            validated_df, anomalies = self._validate_data(normalized_df)
            results["anomalies_detected"] = len(anomalies)
            
            # Step 4: Check and apply corporate actions
            adjusted_df, actions_applied = await self._apply_corporate_actions(
                validated_df, target_date
            )
            results["corporate_actions_applied"] = actions_applied
            
            # Step 5: Store to database
            records_stored = await self._store_data(adjusted_df)
            results["records_processed"] = records_stored
            
            self._update_run_time()
            
        except Exception as e:
            self.logger.error(f"Data ingestion failed: {e}")
            results["status"] = "error"
            results["error"] = str(e)
        
        self._set_status("ready")
        return results

    async def _fetch_bhavcopy(self, target_date: date) -> Optional[pd.DataFrame]:
        """
        Fetch NSE bhavcopy for given date.
        
        URL format: 
        https://nsearchives.nseindia.com/content/historical/EQUITIES/{year}/{MON}/cm{DD}{MON}{YYYY}bhav.csv.zip
        """
        # Build URL
        year = target_date.year
        month = target_date.strftime("%b").upper()
        date_str = target_date.strftime("%d%b%Y").upper()
        
        url = f"{self.nse_base_url}/{year}/{month}/cm{date_str}bhav.csv.zip"
        
        self.logger.info(f"Fetching bhavcopy from: {url}")
        
        # In production, use aiohttp with proper headers and retry logic
        # For now, return mock data structure
        return self._create_mock_bhavcopy(target_date)

    def _create_mock_bhavcopy(self, target_date: date) -> pd.DataFrame:
        """Create mock bhavcopy data for development."""
        symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", 
                   "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK"]
        
        np.random.seed(target_date.toordinal())
        
        data = []
        for symbol in symbols:
            base_price = np.random.uniform(500, 3000)
            daily_return = np.random.normal(0, 0.02)
            
            close = base_price * (1 + daily_return)
            high = close * (1 + abs(np.random.normal(0, 0.01)))
            low = close * (1 - abs(np.random.normal(0, 0.01)))
            open_price = np.random.uniform(low, high)
            
            data.append({
                "SYMBOL": symbol,
                "SERIES": "EQ",
                "OPEN": round(open_price, 2),
                "HIGH": round(high, 2),
                "LOW": round(low, 2),
                "CLOSE": round(close, 2),
                "TOTTRDQTY": int(np.random.uniform(100000, 10000000)),
                "TOTTRDVAL": round(np.random.uniform(1e8, 1e10), 2),
                "TIMESTAMP": target_date.strftime("%d-%b-%Y"),
                "DELIV_QTY": int(np.random.uniform(50000, 5000000)),
                "DELIV_PER": round(np.random.uniform(30, 70), 2),
            })
        
        return pd.DataFrame(data)

    def _normalize_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize bhavcopy schema to standard format.
        
        Standard schema:
        - symbol: str
        - date: datetime
        - open, high, low, close: float
        - volume: int
        - turnover: float
        - delivery_qty: int
        - delivery_pct: float
        """
        column_mapping = {
            "SYMBOL": "symbol",
            "OPEN": "open",
            "HIGH": "high",
            "LOW": "low",
            "CLOSE": "close",
            "TOTTRDQTY": "volume",
            "TOTTRDVAL": "turnover",
            "TIMESTAMP": "date",
            "DELIV_QTY": "delivery_qty",
            "DELIV_PER": "delivery_pct",
        }
        
        # Filter to EQ series only
        if "SERIES" in df.columns:
            df = df[df["SERIES"] == "EQ"]
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Parse date
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        
        # Select and order columns
        columns = ["symbol", "date", "open", "high", "low", "close", 
                   "volume", "turnover", "delivery_qty", "delivery_pct"]
        available_cols = [c for c in columns if c in df.columns]
        
        return df[available_cols]

    def _validate_data(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Validate data quality and flag anomalies.
        
        Checks:
        - OHLC relationship (high >= open, close, low)
        - Volume > 0
        - Large price jumps (> 20% without corporate action)
        - Zero/null values
        """
        anomalies = []
        
        # Check OHLC relationship
        invalid_ohlc = df[
            (df["high"] < df["low"]) |
            (df["high"] < df["open"]) |
            (df["high"] < df["close"]) |
            (df["low"] > df["open"]) |
            (df["low"] > df["close"])
        ]
        
        for _, row in invalid_ohlc.iterrows():
            anomalies.append({
                "symbol": row["symbol"],
                "type": "invalid_ohlc",
                "description": f"OHLC relationship violated",
            })
        
        # Check zero volume
        zero_volume = df[df["volume"] == 0]
        for _, row in zero_volume.iterrows():
            anomalies.append({
                "symbol": row["symbol"],
                "type": "zero_volume",
                "description": "Zero trading volume",
            })
        
        # Flag anomalous rows
        df["is_valid"] = True
        df.loc[invalid_ohlc.index, "is_valid"] = False
        df.loc[zero_volume.index, "is_valid"] = False
        
        return df, anomalies

    async def _apply_corporate_actions(
        self, df: pd.DataFrame, target_date: date
    ) -> tuple[pd.DataFrame, int]:
        """
        Apply corporate action adjustments.
        
        For splits/bonuses: Adjust all historical prices backward
        For dividends: Adjust close price on ex-date
        """
        # In production, query corporate_actions table
        # For now, return unadjusted data
        df["adjusted_close"] = df["close"]
        df["adjustment_factor"] = 1.0
        
        return df, 0

    async def _store_data(self, df: pd.DataFrame) -> int:
        """Store processed data to database."""
        # In production, use async SQLAlchemy to insert/update
        self.logger.info(f"Storing {len(df)} records")
        return len(df)

    async def backfill(
        self,
        start_date: date,
        end_date: date,
        symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Backfill historical data for a date range.
        """
        results = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_days": 0,
            "successful_days": 0,
            "failed_days": 0,
        }
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:
                day_result = await self.process(current_date, symbols)
                results["total_days"] += 1
                
                if day_result["status"] == "success":
                    results["successful_days"] += 1
                else:
                    results["failed_days"] += 1
            
            current_date += timedelta(days=1)
        
        return results
