"""
Savings Return Calculator for Return on Savings Module.

Simplified version for edu_fees_clean integration.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

try:
    from numba import jit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    # Define a no-op decorator if numba is not available
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


@dataclass
class SavingsGrowthResult:
    """Result of investment growth calculation."""
    asset: str
    start_month: pd.Timestamp
    end_month: pd.Timestamp
    curve: pd.DataFrame  # Monthly growth progression
    final_value_native: float
    cagr: float
    total_return: float  # Percentage return
    volatility: float    # Annualized volatility
    max_drawdown: float  # Maximum peak-to-trough loss
    currency: str        # INR, GBP, USD
    initial_value: float
    max_value: float
    min_value: float
    data_quality: Dict   # Data quality metrics


@jit(nopython=True) if HAS_NUMBA else lambda x: x
def _calculate_cagr_fast(start_value: float, end_value: float, years: float) -> float:
    """Fast CAGR calculation with Numba optimization."""
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return 0.0
    return (end_value / start_value) ** (1.0 / years) - 1.0


def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
    """Calculate Compound Annual Growth Rate."""
    try:
        return _calculate_cagr_fast(start_value, end_value, years)
    except Exception:
        # Fallback for edge cases
        if start_value <= 0 or end_value <= 0 or years <= 0:
            return 0.0
        return (end_value / start_value) ** (1.0 / years) - 1.0


def grow_lump_sum(monthly_prices: pd.DataFrame, start: pd.Timestamp,
                  end: pd.Timestamp, lump_sum: float, currency: str = "INR") -> SavingsGrowthResult:
    """Calculate growth of lump sum investment based on asset prices.

    Args:
        monthly_prices: DataFrame with columns [month, price_close]
        start: Investment start date
        end: Investment end date
        lump_sum: Initial investment amount

    Returns:
        SavingsGrowthResult with complete growth analysis
    """
    # Filter data for date range
    px = monthly_prices[
        (monthly_prices["month"] >= start) &
        (monthly_prices["month"] <= end)
    ].copy()

    if px.empty:
        raise ValueError(f"No price data available for period {start} to {end}")

    px = px.sort_values("month").reset_index(drop=True)

    # Calculate relative performance
    base_price = px.iloc[0]["price_close"]
    px["relative_performance"] = px["price_close"] / base_price
    px["value_native"] = lump_sum * px["relative_performance"]

    # Calculate metrics
    years = (px["month"].iloc[-1] - px["month"].iloc[0]).days / 365.25
    final_value = px["value_native"].iloc[-1]

    # CAGR calculation
    cagr = calculate_cagr(lump_sum, final_value, years) if years > 0 else 0.0

    # Total return
    total_return = (final_value - lump_sum) / lump_sum if lump_sum > 0 else 0.0

    # Volatility (annualized)
    if len(px) > 1:
        monthly_returns = px["relative_performance"].pct_change().dropna()
        volatility = monthly_returns.std() * np.sqrt(12) if len(monthly_returns) > 0 else 0.0
    else:
        volatility = 0.0

    # Max drawdown
    rolling_max = px["value_native"].expanding().max()
    drawdown = (px["value_native"] - rolling_max) / rolling_max
    max_drawdown = drawdown.min() if len(drawdown) > 0 else 0.0

    # Min/max values
    max_value = px["value_native"].max()
    min_value = px["value_native"].min()

    # Basic data quality assessment
    data_quality = {
        'data_points': len(px),
        'date_range': (px["month"].iloc[0], px["month"].iloc[-1]),
        'years_of_data': years,
        'quality': 'GOOD' if len(px) >= 24 else 'FAIR' if len(px) >= 12 else 'POOR',
        'confidence': 'HIGH' if years >= 2 else 'MEDIUM' if years >= 1 else 'LOW'
    }

    return SavingsGrowthResult(
        asset=monthly_prices.get("asset", ["Unknown"])[0] if "asset" in monthly_prices.columns else "Unknown",
        start_month=px["month"].iloc[0],
        end_month=px["month"].iloc[-1],
        curve=px[["month", "value_native"]].copy(),
        final_value_native=final_value,
        cagr=cagr,
        total_return=total_return,
        volatility=volatility,
        max_drawdown=max_drawdown,
        currency=currency,
        initial_value=lump_sum,
        max_value=max_value,
        min_value=min_value,
        data_quality=data_quality
    )


def grow_fixed_rate(start: pd.Timestamp, end: pd.Timestamp,
                   lump_sum: float, annual_rate: float) -> SavingsGrowthResult:
    """Calculate growth with fixed annual rate (e.g., bank savings).

    Args:
        start: Investment start date
        end: Investment end date
        lump_sum: Initial investment amount
        annual_rate: Annual interest rate (e.g., 0.05 for 5%)

    Returns:
        SavingsGrowthResult with fixed rate growth
    """
    # Generate monthly periods
    months = pd.period_range(start=start, end=end, freq="M").to_timestamp()

    if len(months) == 0:
        raise ValueError("Invalid date range")

    # Monthly compounding rate
    monthly_rate = (1 + annual_rate) ** (1/12) - 1

    # Calculate monthly growth
    curve_data = []
    current_value = lump_sum

    for month in months:
        current_value *= (1 + monthly_rate)
        curve_data.append({
            "month": month,
            "value_native": current_value
        })

    curve_df = pd.DataFrame(curve_data)

    # Calculate metrics
    years = (months[-1] - months[0]).days / 365.25
    final_value = current_value
    cagr = calculate_cagr(lump_sum, final_value, years) if years > 0 else 0.0
    total_return = (final_value - lump_sum) / lump_sum if lump_sum > 0 else 0.0

    # Fixed rate has perfect data quality
    data_quality = {
        'data_points': len(months),
        'date_range': (months[0], months[-1]),
        'years_of_data': years,
        'quality': 'EXCELLENT',  # Fixed rate is deterministic
        'confidence': 'HIGH'
    }

    return SavingsGrowthResult(
        asset="FIXED_RATE",
        start_month=months[0],
        end_month=months[-1],
        curve=curve_df,
        final_value_native=final_value,
        cagr=cagr,
        total_return=total_return,
        volatility=0.0,  # Fixed rate has no volatility
        max_drawdown=0.0,  # No drawdown for fixed rate
        currency="INR",
        initial_value=lump_sum,
        max_value=final_value,
        min_value=lump_sum,
        data_quality=data_quality
    )


def calculate_effective_cost(projected_fee_inr: float, final_pot_inr: float) -> float:
    """Calculate effective cost after investment growth.

    Args:
        projected_fee_inr: Total projected education cost in INR
        final_pot_inr: Final investment value in INR

    Returns:
        Effective cost (never negative)
    """
    effective_cost = projected_fee_inr - min(projected_fee_inr, final_pot_inr)
    return max(0, effective_cost)


def compare_savings_vs_payg(payg_total_inr: float, effective_cost_inr: float) -> Dict[str, float]:
    """Compare investment strategy vs pay-as-you-go.

    Args:
        payg_total_inr: Total cost with pay-as-you-go
        effective_cost_inr: Effective cost after investment

    Returns:
        Dictionary with savings metrics
    """
    savings_inr = payg_total_inr - effective_cost_inr
    savings_percentage = (savings_inr / payg_total_inr * 100) if payg_total_inr > 0 else 0

    return {
        "savings_inr": savings_inr,
        "savings_percentage": savings_percentage,
        "payg_total_inr": payg_total_inr,
        "effective_cost_inr": effective_cost_inr
    }


class ROICalculator:
    """Simple ROI calculator for investment scenarios."""

    def __init__(self):
        """Initialize ROI calculator."""
        # Import asset loader
        try:
            from modules.data.asset_prices import AssetPriceLoader
            self.asset_loader = AssetPriceLoader()
        except ImportError:
            logger.warning("AssetPriceLoader not available")
            self.asset_loader = None

    def calculate_asset_growth(self, asset: str, start_date: str, end_date: str,
                             amount: float) -> SavingsGrowthResult:
        """Calculate growth for a specific asset.

        Args:
            asset: Asset symbol (GOLD_INR, NIFTY_INR, FTSE_GBP)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            amount: Investment amount

        Returns:
            SavingsGrowthResult with growth analysis
        """
        if self.asset_loader is None:
            raise ValueError("Asset loader not available")

        # Convert dates
        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)

        # Load asset data
        asset_data = self.asset_loader.load_monthly(asset)

        # Calculate growth
        if asset == "FIXED_5PCT":
            return grow_fixed_rate(start, end, amount, 0.05)
        else:
            # Determine currency based on asset
            currency = "GBP" if asset == "FTSE_GBP" else "INR"
            return grow_lump_sum(asset_data, start, end, amount, currency)

    def calculate_multiple_scenarios(self, start_date: str, end_date: str,
                                   amount: float, assets: List[str]) -> Dict[str, SavingsGrowthResult]:
        """Calculate growth for multiple assets.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            amount: Investment amount
            assets: List of asset symbols

        Returns:
            Dictionary mapping asset to SavingsGrowthResult

        Raises:
            ValueError: If any asset calculation fails
        """
        results = {}
        errors = []

        for asset in assets:
            try:
                results[asset] = self.calculate_asset_growth(asset, start_date, end_date, amount)
            except Exception as e:
                error_msg = f"Failed to calculate {asset}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        if errors and not results:
            # All calculations failed
            raise ValueError(f"Investment calculations failed for all assets: {'; '.join(errors)}")
        elif errors:
            # Some calculations failed - log warnings but continue with successful ones
            logger.warning(f"Some investment calculations failed: {'; '.join(errors)}")

        return results