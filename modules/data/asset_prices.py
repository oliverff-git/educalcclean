"""
Asset Price Data Loader for Return on Savings Module.

Simplified version for edu_fees_clean integration.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AssetPriceLoader:
    """Loader for asset price data for investment analysis."""

    def __init__(self, data_dir = None):
        """Initialize asset price loader.

        Args:
            data_dir: Path to market data directory (str or Path)
        """
        if data_dir is None:
            # Use relative path from project root
            data_dir = Path(__file__).parent.parent.parent / "data" / "markets"
        else:
            data_dir = Path(data_dir) / "markets"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Asset file mappings
        self.asset_files = {
            "GOLD_INR": self.data_dir / "gold" / "gold_inr_monthly.csv",
            "NIFTY_INR": self.data_dir / "nifty" / "nifty_inr_monthly.csv",
            "FTSE_GBP": self.data_dir / "ftse" / "ftse_gbp_monthly.csv"
        }

        # Create subdirectories
        for asset_path in self.asset_files.values():
            asset_path.parent.mkdir(parents=True, exist_ok=True)

    def load_monthly(self, asset: str) -> pd.DataFrame:
        """Load monthly asset price data.

        Args:
            asset: Asset symbol (GOLD_INR, NIFTY_INR, FTSE_GBP)

        Returns:
            DataFrame with columns: month, price_close, asset

        Raises:
            ValueError: If asset is unknown or data file not found
        """
        if asset not in self.asset_files:
            raise ValueError(f"Unknown asset: {asset}. Available: {list(self.asset_files.keys())}")

        file_path = self.asset_files[asset]

        if not file_path.exists():
            raise ValueError(
                f"Market data file not found for {asset} at: {file_path}. "
                f"Investment analysis requires actual market data files."
            )

        try:
            df = pd.read_csv(file_path)

            # Validate required columns
            required_columns = ['month', 'price_close']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns in {asset} data: {missing_columns}")

            # Process data
            df["month"] = pd.to_datetime(df["month"])
            df = df.sort_values("month").reset_index(drop=True)
            df["asset"] = asset

            # Validate data quality
            if len(df) < 12:  # Less than 1 year of data
                logger.warning(f"Limited data for {asset}: only {len(df)} months available")

            # Check for missing prices
            null_prices = df["price_close"].isnull().sum()
            if null_prices > 0:
                logger.warning(f"Found {null_prices} missing prices for {asset}")
                df = df.dropna(subset=["price_close"])

            logger.info(f"Loaded {len(df)} valid records for {asset} ({df['month'].min()} to {df['month'].max()})")
            return df

        except Exception as e:
            raise ValueError(f"Error loading market data for {asset}: {e}")

    def _load_fallback_data(self, asset: str) -> pd.DataFrame:
        """Raise error when CSV files are unavailable - no fallback data."""
        raise ValueError(
            f"No market data available for {asset}. "
            f"Please ensure CSV files are present at: {self.asset_files.get(asset, 'Unknown path')}"
        )

    def get_latest_price(self, asset: str) -> Optional[float]:
        """Get the latest price for an asset.

        Args:
            asset: Asset symbol

        Returns:
            Latest price or None if unavailable
        """
        try:
            df = self.load_monthly(asset)
            if not df.empty:
                return float(df.iloc[-1]["price_close"])
        except Exception as e:
            logger.error(f"Error getting latest price for {asset}: {e}")

        return None

    def get_price_range(self, asset: str) -> Dict[str, float]:
        """Get price range statistics for an asset.

        Args:
            asset: Asset symbol

        Returns:
            Dictionary with min, max, mean, latest prices
        """
        try:
            df = self.load_monthly(asset)
            if not df.empty:
                prices = df["price_close"]
                return {
                    "min": float(prices.min()),
                    "max": float(prices.max()),
                    "mean": float(prices.mean()),
                    "latest": float(prices.iloc[-1]),
                    "count": len(prices)
                }
        except Exception as e:
            logger.error(f"Error getting price range for {asset}: {e}")

        return {}

    def get_data_quality_info(self, asset: str) -> Dict[str, any]:
        """Get data quality information for an asset.

        Args:
            asset: Asset symbol

        Returns:
            Dictionary with data quality metrics
        """
        try:
            df = self.load_monthly(asset)
            if df.empty:
                return {
                    'quality': 'POOR',
                    'confidence': 'LOW',
                    'issues': ['No data available'],
                    'data_points': 0,
                    'date_range': None
                }

            # Calculate quality metrics
            date_range = (df['month'].min(), df['month'].max())
            data_points = len(df)
            months_span = (date_range[1] - date_range[0]).days / 30.44  # Average days per month

            # Check for data gaps
            expected_months = int(months_span) + 1
            missing_months = max(0, expected_months - data_points)

            # Check data recency
            latest_date = df['month'].max()
            days_old = (pd.Timestamp.now() - latest_date).days

            issues = []
            if data_points < 24:  # Less than 2 years
                issues.append(f'Limited historical data ({data_points} months)')

            if missing_months > 3:
                issues.append(f'Data gaps detected (~{missing_months} missing months)')

            if days_old > 90:  # Data older than 3 months
                issues.append(f'Data may be outdated (last update: {latest_date.strftime("%Y-%m")})')

            # Determine overall quality
            if len(issues) == 0 and data_points >= 36:  # 3+ years, no issues
                quality = 'EXCELLENT'
                confidence = 'HIGH'
            elif len(issues) <= 1 and data_points >= 24:  # 2+ years, minor issues
                quality = 'GOOD'
                confidence = 'HIGH'
            elif data_points >= 12:  # 1+ year
                quality = 'FAIR'
                confidence = 'MEDIUM'
            else:
                quality = 'POOR'
                confidence = 'LOW'

            return {
                'quality': quality,
                'confidence': confidence,
                'issues': issues,
                'data_points': data_points,
                'date_range': date_range,
                'latest_data': latest_date,
                'days_old': days_old
            }

        except Exception as e:
            return {
                'quality': 'UNAVAILABLE',
                'confidence': 'NONE',
                'issues': [f'Data loading error: {str(e)}'],
                'data_points': 0,
                'date_range': None
            }