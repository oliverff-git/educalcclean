"""
Education Savings Calculator - Core calculation engine.

Implements multiple conversion strategies and savings analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)
from dataclasses import dataclass
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


@dataclass
class SavingsScenario:
    """Results of a savings calculation scenario."""
    strategy_name: str
    total_cost_inr: float
    total_cost_gbp: float
    savings_vs_payg_inr: float
    savings_percentage: float
    exchange_rate_used: float
    conversion_details: Dict
    breakdown: Dict


class EducationSavingsCalculator:
    """Core calculator for education savings strategies."""

    def __init__(self, data_processor):
        """Initialize with data processor."""
        self.data_processor = data_processor
        self.fx_cagr = 0.0418  # Historical GBP/INR CAGR (2017-2025 conservative)

    def calculate_early_conversion_scenario(
        self,
        university: str,
        programme: str,
        conversion_year: int,
        education_year: int,
        total_gbp_needed: float
    ) -> SavingsScenario:
        """Calculate early conversion scenario."""

        # Get exchange rates
        conversion_fx_rate = self.data_processor.get_september_fx_rate(conversion_year)
        education_fx_rate = self.data_processor.get_september_fx_rate(education_year)

        # Calculate costs
        initial_inr_cost = total_gbp_needed * conversion_fx_rate

        # Calculate UK earnings between conversion and education
        years_invested = education_year - conversion_year
        uk_earnings_gbp = 0
        avg_interest_rate = 0

        if years_invested > 0:
            # Calculate using actual BoE rates for each year
            total_interest_rate = 0
            for year in range(conversion_year, education_year):
                year_rate = self.data_processor.get_uk_interest_rate(year)
                total_interest_rate += year_rate

            avg_interest_rate = total_interest_rate / years_invested
            uk_earnings_gbp = total_gbp_needed * avg_interest_rate * years_invested

        # Total cost accounting for UK earnings
        effective_gbp_cost = total_gbp_needed - uk_earnings_gbp
        total_cost_inr = max(initial_inr_cost, effective_gbp_cost * conversion_fx_rate)

        # Calculate savings vs pay-as-you-go
        payg_cost_inr = total_gbp_needed * education_fx_rate
        savings_inr = payg_cost_inr - total_cost_inr
        savings_pct = (savings_inr / payg_cost_inr) * 100 if payg_cost_inr > 0 else 0

        return SavingsScenario(
            strategy_name=f"Up Front 100% {conversion_year}",
            total_cost_inr=total_cost_inr,
            total_cost_gbp=total_gbp_needed,
            savings_vs_payg_inr=savings_inr,
            savings_percentage=savings_pct,
            exchange_rate_used=conversion_fx_rate,
            conversion_details={
                'conversion_year': conversion_year,
                'conversion_rate': conversion_fx_rate,
                'education_year': education_year,
                'education_rate': education_fx_rate,
                'years_invested': years_invested
            },
            breakdown={
                'initial_inr_cost': initial_inr_cost,
                'uk_earnings': {
                    'total_interest_gbp': uk_earnings_gbp,
                    'avg_interest_rate': avg_interest_rate,
                    'years': years_invested
                },
                'payg_comparison': {
                    'payg_cost_inr': payg_cost_inr,
                    'payg_rate': education_fx_rate
                }
            }
        )

    def calculate_staggered_conversion_scenario(
        self,
        university: str,
        programme: str,
        conversion_year: int,
        education_year: int,
        total_gbp_needed: float
    ) -> SavingsScenario:
        """Calculate staggered conversion scenario (convert 1/3 each year)."""

        years_to_education = education_year - conversion_year
        if years_to_education <= 0:
            # Fallback to early conversion if no time gap
            return self.calculate_early_conversion_scenario(
                university, programme, conversion_year, education_year, total_gbp_needed
            )

        annual_gbp_amount = total_gbp_needed / max(years_to_education, 1)
        total_inr_cost = 0
        conversion_details = {}

        # Convert portion each year
        for year_offset in range(years_to_education):
            conversion_year_i = conversion_year + year_offset
            fx_rate_i = self.data_processor.get_september_fx_rate(conversion_year_i)
            inr_cost_i = annual_gbp_amount * fx_rate_i
            total_inr_cost += inr_cost_i

            conversion_details[f'year_{conversion_year_i}'] = {
                'gbp_amount': annual_gbp_amount,
                'fx_rate': fx_rate_i,
                'inr_cost': inr_cost_i
            }

        # Calculate savings vs pay-as-you-go
        education_fx_rate = self.data_processor.get_september_fx_rate(education_year)
        payg_cost_inr = total_gbp_needed * education_fx_rate
        savings_inr = payg_cost_inr - total_inr_cost
        savings_pct = (savings_inr / payg_cost_inr) * 100 if payg_cost_inr > 0 else 0

        # Average exchange rate used
        avg_fx_rate = total_inr_cost / total_gbp_needed

        return SavingsScenario(
            strategy_name=f"Staggered from {conversion_year}",
            total_cost_inr=total_inr_cost,
            total_cost_gbp=total_gbp_needed,
            savings_vs_payg_inr=savings_inr,
            savings_percentage=savings_pct,
            exchange_rate_used=avg_fx_rate,
            conversion_details=conversion_details,
            breakdown={
                'annual_conversions': conversion_details,
                'years_of_conversion': years_to_education,
                'payg_comparison': {
                    'payg_cost_inr': payg_cost_inr,
                    'payg_rate': education_fx_rate
                }
            }
        )

    def calculate_payg_scenario(
        self,
        university: str,
        programme: str,
        education_year: int,
        total_gbp_needed: float
    ) -> SavingsScenario:
        """Calculate pay-as-you-go scenario (baseline)."""

        education_fx_rate = self.data_processor.get_september_fx_rate(education_year)
        total_cost_inr = total_gbp_needed * education_fx_rate

        return SavingsScenario(
            strategy_name="Pay-As-You-Go (Baseline)",
            total_cost_inr=total_cost_inr,
            total_cost_gbp=total_gbp_needed,
            savings_vs_payg_inr=0,  # Baseline has no savings
            savings_percentage=0,
            exchange_rate_used=education_fx_rate,
            conversion_details={
                'education_year': education_year,
                'education_rate': education_fx_rate
            },
            breakdown={
                'immediate_conversion': {
                    'gbp_amount': total_gbp_needed,
                    'fx_rate': education_fx_rate,
                    'inr_cost': total_cost_inr
                }
            }
        )

    def calculate_total_programme_cost(self, university: str, programme: str, education_year: int) -> float:
        """Calculate total programme cost for 3 years."""

        # UK fees are fixed at enrollment for entire programme duration
        first_year_fee = self.data_processor.project_fee(university, programme, education_year)
        total_cost = first_year_fee * 3  # Same fee for all 3 years

        return total_cost

    def compare_all_strategies(
        self,
        university: str,
        programme: str,
        conversion_year: int,
        education_year: int
    ) -> List[SavingsScenario]:
        """Compare all conversion strategies and return sorted by savings."""

        # Calculate total programme cost
        total_gbp_needed = self.calculate_total_programme_cost(university, programme, education_year)

        scenarios = []

        # Early conversion scenarios (different start years)
        for start_year in range(conversion_year, education_year):
            scenario = self.calculate_early_conversion_scenario(
                university, programme, start_year, education_year, total_gbp_needed
            )
            scenarios.append(scenario)

        # Staggered conversion
        if education_year - conversion_year > 1:
            staggered_scenario = self.calculate_staggered_conversion_scenario(
                university, programme, conversion_year, education_year, total_gbp_needed
            )
            scenarios.append(staggered_scenario)

        # Pay-as-you-go baseline
        payg_scenario = self.calculate_payg_scenario(
            university, programme, education_year, total_gbp_needed
        )
        scenarios.append(payg_scenario)

        # Sort by savings (descending)
        scenarios.sort(key=lambda x: x.savings_vs_payg_inr, reverse=True)

        return scenarios

    def get_projection_details(self, university: str, programme: str, education_year: int) -> Dict:
        """Get detailed projection information for charts."""

        # Fee projections
        fee_projections = {}
        course_info = self.data_processor.get_course_info(university, programme)

        # Historical fees
        for year, fee in course_info['historical_fees'].items():
            fee_projections[year] = fee

        # Future projections
        for year in range(2025, education_year + 4):
            if year not in fee_projections:
                projected_fee = self.data_processor.project_fee(university, programme, year)
                fee_projections[year] = projected_fee

        # FX projections
        fx_projections = {}
        for year in range(2020, education_year + 4):
            if year <= 2025:
                # Historical/current rates
                fx_rate = self.data_processor.get_september_fx_rate(year)
            else:
                # Projected rates
                fx_rate = self.data_processor.project_fx_rate(year)
            fx_projections[year] = fx_rate

        return {
            'course_info': course_info,
            'fee_projections': fee_projections,
            'fx_projections': fx_projections,
            'total_programme_cost': self.calculate_total_programme_cost(university, programme, education_year)
        }

    # ========== ROI ANALYSIS METHODS ==========

    def calculate_roi_scenario(
        self,
        asset_type: str,
        university: str,
        programme: str,
        conversion_year: int,
        education_year: int,
        initial_amount_inr: float
    ) -> SavingsScenario:
        """Calculate ROI-based investment scenario.

        Args:
            asset_type: Investment type (GOLD_INR, NIFTY_INR, FTSE_GBP, FIXED_5PCT)
            university: University name
            programme: Programme name
            conversion_year: Year to start investing
            education_year: Year education starts
            initial_amount_inr: Initial investment amount in INR

        Returns:
            SavingsScenario with investment analysis
        """
        try:
            # Import ROI calculator
            from modules.metrics.savings_return import ROICalculator, calculate_effective_cost

            # Initialize calculator
            roi_calc = ROICalculator()

            # Calculate total programme cost
            total_gbp_needed = self.calculate_total_programme_cost(university, programme, education_year)

            # Get pay-as-you-go baseline
            education_fx_rate = self.data_processor.get_september_fx_rate(education_year)
            payg_cost_inr = total_gbp_needed * education_fx_rate

            # Calculate investment growth
            start_date = f"{conversion_year}-01-01"
            end_date = f"{education_year}-01-01"

            if asset_type == "FIXED_5PCT":
                # Fixed rate calculation
                from modules.metrics.savings_return import grow_fixed_rate
                import pandas as pd
                growth_result = grow_fixed_rate(
                    pd.Timestamp(start_date),
                    pd.Timestamp(end_date),
                    initial_amount_inr,
                    0.05
                )
            elif asset_type == "FTSE_GBP":
                # FTSE requires currency conversion BEFORE calculation
                conversion_fx_rate = self.data_processor.get_september_fx_rate(conversion_year)
                initial_amount_gbp = initial_amount_inr / conversion_fx_rate

                # Calculate growth in GBP
                growth_result = roi_calc.calculate_asset_growth(
                    asset_type, start_date, end_date, initial_amount_gbp
                )
                # growth_result.final_value_native is now in GBP
            else:
                # Asset-based growth (INR assets)
                growth_result = roi_calc.calculate_asset_growth(
                    asset_type, start_date, end_date, initial_amount_inr
                )

            # Handle final pot conversion properly
            final_pot_inr = growth_result.final_value_native
            if asset_type == "FTSE_GBP":
                # Convert GBP result to INR using education year rate
                final_pot_inr = growth_result.final_value_native * education_fx_rate

            # Calculate effective cost after investment
            effective_cost_inr = calculate_effective_cost(payg_cost_inr, final_pot_inr)

            # Calculate savings
            savings_inr = payg_cost_inr - effective_cost_inr
            savings_pct = (savings_inr / payg_cost_inr) * 100 if payg_cost_inr > 0 else 0

            # Add validation for unrealistic results
            investment_years = education_year - conversion_year
            annual_growth_rate = growth_result.cagr * 100
            total_return = growth_result.total_return * 100

            validation_warnings = []

            # Enhanced sanity checks for realistic investment returns

            # Check if this is a future projection (education year > 2025)
            is_future_projection = education_year > 2025

            # Check for unrealistic annual growth rates
            if annual_growth_rate > 25:  # >25% annual is extremely optimistic
                validation_warnings.append(f"Extremely high annual growth: {annual_growth_rate:.1f}%")
            elif annual_growth_rate > 15:  # >15% annual is optimistic
                if is_future_projection:
                    validation_warnings.append(f"High projected growth: {annual_growth_rate:.1f}% - conservative estimate used")
                else:
                    validation_warnings.append(f"High annual growth: {annual_growth_rate:.1f}% - verify assumptions")
            elif annual_growth_rate < -50:
                validation_warnings.append(f"Extreme annual loss: {annual_growth_rate:.1f}%")

            # Add projection disclaimer for future years
            if is_future_projection:
                validation_warnings.append(f"Future projections use conservative estimates - actual returns may vary")

            # Check for unrealistic total returns based on investment period
            max_reasonable_return = investment_years * 20  # Max 20% per year is aggressive but possible
            if total_return > max_reasonable_return:
                validation_warnings.append(f"Total return {total_return:.1f}% very high for {investment_years} years")
            elif total_return > 500:
                validation_warnings.append(f"Unrealistic total return: {total_return:.1f}%")
            elif total_return < -90:
                validation_warnings.append(f"Unrealistic total loss: {total_return:.1f}%")

            # Check for ROI sanity (profit-based)
            actual_profit = final_pot_inr - initial_amount_inr
            actual_roi = (actual_profit / initial_amount_inr) * 100 if initial_amount_inr > 0 else 0

            # For 3-year investments, ROI >60% is very optimistic
            if investment_years <= 3 and actual_roi > 60:
                validation_warnings.append(f"ROI {actual_roi:.1f}% very high for {investment_years}-year investment")
            elif investment_years <= 5 and actual_roi > 100:
                validation_warnings.append(f"ROI {actual_roi:.1f}% extremely high for {investment_years}-year investment")

            # Check for impossibly high final values
            multiplier = final_pot_inr / initial_amount_inr if initial_amount_inr > 0 else 0
            if multiplier > 5:  # 5x growth is very aggressive
                validation_warnings.append(f"Investment grew {multiplier:.1f}x in {investment_years} years - verify calculation")

            # Log warnings but don't fail calculation
            if validation_warnings:
                logger.warning(f"Investment validation warnings for {asset_type}: {'; '.join(validation_warnings)}")

            # Strategy name with performance
            strategy_name = f"{asset_type.replace('_', ' ')} Investment ({growth_result.cagr*100:.1f}% CAGR)"

            return SavingsScenario(
                strategy_name=strategy_name,
                total_cost_inr=effective_cost_inr,
                total_cost_gbp=effective_cost_inr / education_fx_rate,
                savings_vs_payg_inr=savings_inr,
                savings_percentage=savings_pct,
                exchange_rate_used=education_fx_rate,
                conversion_details={
                    'asset_type': asset_type,
                    'initial_investment_inr': initial_amount_inr,
                    'final_pot_value': growth_result.final_value_native,
                    'final_pot_inr': final_pot_inr,
                    'cagr': growth_result.cagr,
                    'total_return': growth_result.total_return,
                    'volatility': growth_result.volatility,
                    'max_drawdown': growth_result.max_drawdown,
                    'investment_period': f"{conversion_year} → {education_year}",
                    'growth_curve': growth_result.curve.to_dict('records') if hasattr(growth_result.curve, 'to_dict') else [],
                    'data_quality': growth_result.data_quality,
                    # Currency conversion info for FTSE
                    'currency_conversion': {
                        'initial_fx_rate': self.data_processor.get_september_fx_rate(conversion_year) if asset_type == "FTSE_GBP" else None,
                        'final_fx_rate': education_fx_rate if asset_type == "FTSE_GBP" else None,
                        'initial_amount_native': initial_amount_inr / self.data_processor.get_september_fx_rate(conversion_year) if asset_type == "FTSE_GBP" else initial_amount_inr,
                        'native_currency': 'GBP' if asset_type == "FTSE_GBP" else 'INR'
                    },
                    'validation_warnings': validation_warnings
                },
                breakdown={
                    'investment_type': 'Market-based ROI' if asset_type != 'FIXED_5PCT' else 'Fixed rate savings',
                    'risk_level': self._get_risk_level(asset_type, growth_result.volatility),
                    'performance_summary': f"{growth_result.total_return:.1f}% total return over {education_year - conversion_year} years",
                    'effective_cost_breakdown': {
                        'total_education_cost': payg_cost_inr,
                        'investment_proceeds': final_pot_inr,
                        'net_cost_after_investment': effective_cost_inr,
                        'surplus_if_any': max(0, final_pot_inr - payg_cost_inr)
                    }
                }
            )

        except Exception as e:
            # Don't silently fall back - raise the error with context
            error_msg = (
                f"Investment analysis failed for {asset_type}: {str(e)}. "
                f"This may be due to missing market data files or calculation errors."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

    def calculate_all_roi_scenarios(
        self,
        university: str,
        programme: str,
        conversion_year: int,
        education_year: int,
        initial_amount_inr: float,
        selected_strategies: List[str] = None
    ) -> List[SavingsScenario]:
        """Calculate all available ROI scenarios.

        Args:
            university: University name
            programme: Programme name
            conversion_year: Investment start year
            education_year: Education start year
            initial_amount_inr: Initial investment amount
            selected_strategies: List of strategies to calculate (optional)

        Returns:
            List of SavingsScenario results sorted by savings amount
        """
        if selected_strategies is None:
            selected_strategies = ["GOLD_INR", "FIXED_5PCT"]

        scenarios = []

        for asset_type in selected_strategies:
            scenario = self.calculate_roi_scenario(
                asset_type, university, programme, conversion_year, education_year, initial_amount_inr
            )
            scenarios.append(scenario)

        # Sort by savings amount (descending)
        scenarios.sort(key=lambda x: x.savings_vs_payg_inr, reverse=True)

        return scenarios

    def _get_risk_level(self, asset_type: str, volatility: float) -> str:
        """Determine risk level based on asset type and volatility.

        Args:
            asset_type: Type of asset
            volatility: Annualized volatility

        Returns:
            Risk level string
        """
        if asset_type == "FIXED_5PCT":
            return "Low (Capital protected)"
        elif asset_type == "GOLD_INR":
            return "Low-Medium (Inflation hedge)"
        elif asset_type == "FTSE_GBP":
            return "Medium (International equity + currency risk)"
        elif asset_type == "NIFTY_INR":
            if volatility < 0.15:
                return "Medium (Domestic equity)"
            else:
                return "Medium-High (Domestic equity, volatile period)"
        else:
            return "Medium"

    def get_roi_investment_summary(
        self,
        scenarios: List[SavingsScenario]
    ) -> Dict:
        """Get summary of ROI investment scenarios.

        Args:
            scenarios: List of calculated scenarios

        Returns:
            Dictionary with investment summary
        """
        if not scenarios:
            return {}

        best_scenario = max(scenarios, key=lambda x: x.savings_vs_payg_inr)
        worst_scenario = min(scenarios, key=lambda x: x.savings_vs_payg_inr)

        total_strategies = len(scenarios)
        profitable_strategies = len([s for s in scenarios if s.savings_vs_payg_inr > 0])

        return {
            'total_strategies_analyzed': total_strategies,
            'profitable_strategies': profitable_strategies,
            'best_strategy': {
                'name': best_scenario.strategy_name,
                'savings': best_scenario.savings_vs_payg_inr,
                'savings_percentage': best_scenario.savings_percentage
            },
            'worst_strategy': {
                'name': worst_scenario.strategy_name,
                'savings': worst_scenario.savings_vs_payg_inr,
                'savings_percentage': worst_scenario.savings_percentage
            },
            'average_savings': np.mean([s.savings_vs_payg_inr for s in scenarios]),
            'strategies_with_positive_savings': profitable_strategies,
            'recommendation': self._get_investment_recommendation(scenarios)
        }

    def _get_investment_recommendation(self, scenarios: List[SavingsScenario]) -> str:
        """Generate investment recommendation based on scenario analysis."""
        if not scenarios:
            return "No scenarios available for analysis"

        profitable = [s for s in scenarios if s.savings_vs_payg_inr > 0]

        if len(profitable) == 0:
            return "Consider traditional conversion strategies as investment options show limited benefit"
        elif len(profitable) == len(scenarios):
            best = max(scenarios, key=lambda x: x.savings_vs_payg_inr)
            return f"All strategies show positive returns. Best option: {best.strategy_name}"
        else:
            best = max(profitable, key=lambda x: x.savings_vs_payg_inr)
            return f"Mixed results. Consider {best.strategy_name} for optimal returns with appropriate risk management"