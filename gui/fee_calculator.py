"""
Education Savings Calculator - Core calculation engine.

Implements multiple conversion strategies and savings analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
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
            strategy_name=f"Convert All in {conversion_year}",
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

        total_cost = 0
        for year_offset in range(3):  # Assuming 3-year programme
            year = education_year + year_offset
            annual_fee = self.data_processor.project_fee(university, programme, year)
            total_cost += annual_fee

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