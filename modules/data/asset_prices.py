"""
Asset Price Data Loader for Return on Savings Module.

Simplified version for edu_fees_clean integration.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AssetPriceLoader:
    """Loader for asset price data for investment analysis."""

    def __init__(self, data_dir: Path = None):
        """Initialize asset price loader.

        Args:
            data_dir: Path to market data directory
        """
        if data_dir is None:
            # Use relative path from project root
            data_dir = Path(__file__).parent.parent.parent / "data" / "markets"

        self.data_dir = data_dir
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
        """
        if asset not in self.asset_files:
            raise ValueError(f"Unknown asset: {asset}. Available: {list(self.asset_files.keys())}")

        file_path = self.asset_files[asset]

        try:
            # Try to load from CSV file
            if file_path.exists():
                df = pd.read_csv(file_path)
                df["month"] = pd.to_datetime(df["month"])
                df = df.sort_values("month").reset_index(drop=True)
                df["asset"] = asset
                logger.info(f"Loaded {len(df)} records for {asset}")
                return df
            else:
                # Fallback to manual data
                logger.warning(f"CSV file not found for {asset}, using fallback data")
                return self._load_fallback_data(asset)

        except Exception as e:
            logger.error(f"Error loading {asset}: {e}")
            return self._load_fallback_data(asset)

    def _load_fallback_data(self, asset: str) -> pd.DataFrame:
        """Load fallback data when CSV files are unavailable."""

        # Manual fallback data (sample data for 2020-2025)
        manual_data = {
            "GOLD_INR": {
                "2020-01": 108500, "2020-02": 110200, "2020-03": 115800, "2020-04": 118200,
                "2020-05": 122500, "2020-06": 125800, "2020-07": 128400, "2020-08": 131200,
                "2020-09": 134600, "2020-10": 136800, "2020-11": 139200, "2020-12": 141800,
                "2021-01": 144200, "2021-02": 146800, "2021-03": 149500, "2021-04": 152200,
                "2021-05": 154800, "2021-06": 157600, "2021-07": 160200, "2021-08": 162900,
                "2021-09": 165400, "2021-10": 167200, "2021-11": 164800, "2021-12": 162500,
                "2022-01": 160200, "2022-02": 158600, "2022-03": 156800, "2022-04": 155200,
                "2022-05": 153800, "2022-06": 152500, "2022-07": 151200, "2022-08": 149800,
                "2022-09": 148500, "2022-10": 147200, "2022-11": 145800, "2022-12": 144500,
                "2023-01": 143200, "2023-02": 141800, "2023-03": 140500, "2023-04": 139200,
                "2023-05": 137800, "2023-06": 136500, "2023-07": 135200, "2023-08": 133800,
                "2023-09": 132500, "2023-10": 131200, "2023-11": 129800, "2023-12": 128500,
                "2024-01": 130200, "2024-02": 132800, "2024-03": 135500, "2024-04": 138200,
                "2024-05": 140800, "2024-06": 143500, "2024-07": 146200, "2024-08": 148800,
                "2024-09": 151500, "2024-10": 154200, "2024-11": 156800, "2024-12": 159500,
                "2025-01": 162200, "2025-02": 164800, "2025-03": 167500, "2025-04": 170200,
                "2025-05": 172800, "2025-06": 175500, "2025-07": 178200, "2025-08": 180800,
                "2025-09": 183500, "2025-10": 186200, "2025-11": 188800, "2025-12": 162900
            },

            "NIFTY_INR": {
                "2020-01": 12100, "2020-02": 11200, "2020-03": 8598, "2020-04": 9580,
                "2020-05": 9580, "2020-06": 10300, "2020-07": 11100, "2020-08": 11680,
                "2020-09": 11200, "2020-10": 11900, "2020-11": 12950, "2020-12": 13980,
                "2021-01": 14690, "2021-02": 14980, "2021-03": 14690, "2021-04": 14340,
                "2021-05": 15310, "2021-06": 15750, "2021-07": 15830, "2021-08": 16560,
                "2021-09": 17450, "2021-10": 17670, "2021-11": 17000, "2021-12": 17350,
                "2022-01": 17340, "2022-02": 16250, "2022-03": 17460, "2022-04": 17320,
                "2022-05": 15740, "2022-06": 15780, "2022-07": 16570, "2022-08": 17620,
                "2022-09": 17080, "2022-10": 18070, "2022-11": 18420, "2022-12": 18120,
                "2023-01": 17800, "2023-02": 17810, "2023-03": 17360, "2023-04": 18070,
                "2023-05": 18530, "2023-06": 18720, "2023-07": 19750, "2023-08": 19390,
                "2023-09": 19640, "2023-10": 19080, "2023-11": 20270, "2023-12": 21740,
                "2024-01": 21740, "2024-02": 22530, "2024-03": 22530, "2024-04": 22270,
                "2024-05": 23260, "2024-06": 23980, "2024-07": 24540, "2024-08": 25020,
                "2024-09": 25790, "2024-10": 24340, "2024-11": 23530, "2024-12": 24120,
                "2025-01": 24500, "2025-02": 24850, "2025-03": 25200, "2025-04": 25550,
                "2025-05": 25900, "2025-06": 26250, "2025-07": 26600, "2025-08": 26950,
                "2025-09": 27300, "2025-10": 27650, "2025-11": 28000, "2025-12": 27824
            },

            "FTSE_GBP": {
                "2020-01": 7420, "2020-02": 6580, "2020-03": 5577, "2020-04": 5900,
                "2020-05": 6180, "2020-06": 6240, "2020-07": 6100, "2020-08": 6030,
                "2020-09": 5900, "2020-10": 5580, "2020-11": 6370, "2020-12": 6460,
                "2021-01": 6720, "2021-02": 6480, "2021-03": 6710, "2021-04": 6970,
                "2021-05": 7030, "2021-06": 7020, "2021-07": 7010, "2021-08": 7120,
                "2021-09": 6960, "2021-10": 7240, "2021-11": 7060, "2021-12": 7380,
                "2022-01": 7450, "2022-02": 7280, "2022-03": 7520, "2022-04": 7540,
                "2022-05": 7580, "2022-06": 7170, "2022-07": 7280, "2022-08": 7420,
                "2022-09": 6890, "2022-10": 6920, "2022-11": 7540, "2022-12": 7450,
                "2023-01": 7870, "2023-02": 7910, "2023-03": 7630, "2023-04": 7850,
                "2023-05": 7850, "2023-06": 7530, "2023-07": 7680, "2023-08": 7290,
                "2023-09": 7608, "2023-10": 7283, "2023-11": 7453, "2023-12": 7733,
                "2024-01": 7608, "2024-02": 7609, "2024-03": 7953, "2024-04": 8144,
                "2024-05": 8420, "2024-06": 8252, "2024-07": 8285, "2024-08": 8370,
                "2024-09": 8282, "2024-10": 8180, "2024-11": 8070, "2024-12": 8015,
                "2025-01": 8100, "2025-02": 8185, "2025-03": 8270, "2025-04": 8355,
                "2025-05": 8440, "2025-06": 8525, "2025-07": 8610, "2025-08": 8695,
                "2025-09": 8780, "2025-10": 8565, "2025-11": 8450, "2025-12": 8634
            }
        }

        if asset not in manual_data:
            raise ValueError(f"No fallback data available for {asset}")

        # Convert to DataFrame
        asset_data = manual_data[asset]
        rows = []
        for month_str, price in asset_data.items():
            month_date = datetime.strptime(month_str, "%Y-%m").replace(day=1)
            rows.append({
                "month": month_date,
                "price_close": price,
                "asset": asset
            })

        df = pd.DataFrame(rows)
        df = df.sort_values("month").reset_index(drop=True)

        logger.info(f"Loaded {len(df)} fallback records for {asset}")
        return df

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