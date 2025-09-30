"""
Investment Calculator Wrapper for Education Savings App.

This module provides a clean interface to the existing backend systems,
connecting the investment app to fee_calculator.py and data_processor.py
without modifying the core backend files.

Authors: Agent 2 - Data Integration & ROI Calculations
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import existing backend modules (DO NOT MODIFY THESE)
from gui.fee_calculator import EducationSavingsCalculator, SavingsScenario
from gui.data_processor import EducationDataProcessor


@dataclass
class InvestmentResult:
    """Wrapper for investment calculation results."""
    strategy_name: str
    total_cost_inr: float
    total_cost_gbp: float
    savings_vs_payg_inr: float
    savings_percentage: float
    investment_details: Dict
    risk_level: str
    performance_summary: str
    validation_warnings: List[str] = None


class InvestmentCalculator:
    """
    Wrapper class that connects investment UI to existing backend systems.

    This class provides a clean interface without modifying the core
    fee_calculator.py and data_processor.py files.
    """

    def __init__(self):
        """Initialize calculator with backend components."""
        try:
            # Initialize backend components
            self.data_processor = EducationDataProcessor()
            self.data_processor.load_data()
            self.savings_calculator = EducationSavingsCalculator(self.data_processor)

            logger.info("Investment calculator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize investment calculator: {e}")
            raise

    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_available_universities(_self) -> List[str]:
        """
        Get list of available universities from data processor.

        Returns:
            List of university names
        """
        try:
            return _self.data_processor.get_universities()
        except Exception as e:
            logger.error(f"Failed to get universities: {e}")
            return []

    @st.cache_data(ttl=3600)
    def get_available_courses(_self, university: str) -> List[str]:
        """
        Get list of available courses for a specific university.

        Args:
            university: University name

        Returns:
            List of course names
        """
        try:
            return _self.data_processor.get_courses(university)
        except Exception as e:
            logger.error(f"Failed to get courses for {university}: {e}")
            return []

    def validate_investment_inputs(
        self,
        university: str,
        course: str,
        start_year: int,
        education_year: int,
        amount: float,
        strategies: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate investment calculation inputs.

        Args:
            university: University name
            course: Course name
            start_year: Investment start year
            education_year: Education start year
            amount: Investment amount in INR
            strategies: List of investment strategies

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Validate university and course
        if not university or university not in self.get_available_universities():
            errors.append(f"Invalid university: {university}")

        if not course:
            errors.append("Course is required")
        elif university and course not in self.get_available_courses(university):
            errors.append(f"Invalid course '{course}' for {university}")

        # Validate date ranges
        if start_year >= education_year:
            errors.append("Investment start year must be before education year")

        if start_year < 2020 or start_year > 2030:
            errors.append("Investment start year must be between 2020 and 2030")

        if education_year < 2025 or education_year > 2035:
            errors.append("Education year must be between 2025 and 2035")

        # Validate investment amount
        if amount <= 0:
            errors.append("Investment amount must be positive")

        if amount < 100000:  # ₹1 lakh minimum
            errors.append("Investment amount should be at least ₹1,00,000")

        if amount > 50000000:  # ₹5 crore maximum (reasonable upper limit)
            errors.append("Investment amount should not exceed ₹5,00,00,000")

        # Validate strategies
        valid_strategies = ["GOLD_INR", "FIXED_5PCT", "NIFTY_INR", "FTSE_GBP"]
        if not strategies:
            errors.append("At least one investment strategy must be selected")
        else:
            invalid_strategies = [s for s in strategies if s not in valid_strategies]
            if invalid_strategies:
                errors.append(f"Invalid strategies: {', '.join(invalid_strategies)}")

        return len(errors) == 0, errors

    def calculate_investment_scenarios(
        self,
        university: str,
        course: str,
        start_year: int,
        education_year: int,
        amount: float,
        strategies: List[str] = None
    ) -> List[InvestmentResult]:
        """
        Calculate investment scenarios using existing backend.

        Args:
            university: University name
            course: Course/programme name
            start_year: Investment start year
            education_year: Education start year
            amount: Investment amount in INR
            strategies: List of investment strategies (default: ["GOLD_INR", "FIXED_5PCT"])

        Returns:
            List of InvestmentResult objects sorted by savings amount

        Raises:
            ValueError: If inputs are invalid or calculation fails
        """
        # Set default strategies if not provided
        if strategies is None:
            strategies = ["GOLD_INR", "FIXED_5PCT"]

        # Validate inputs
        is_valid, errors = self.validate_investment_inputs(
            university, course, start_year, education_year, amount, strategies
        )

        if not is_valid:
            raise ValueError(f"Invalid inputs: {'; '.join(errors)}")

        try:
            # Call existing backend method
            scenarios = self.savings_calculator.calculate_all_roi_scenarios(
                university=university,
                programme=course,
                conversion_year=start_year,
                education_year=education_year,
                initial_amount_inr=amount,
                selected_strategies=strategies
            )

            # Convert to our wrapper format
            results = []
            for scenario in scenarios:
                # Extract validation warnings if available
                warnings = []
                if hasattr(scenario, 'conversion_details') and scenario.conversion_details:
                    warnings = scenario.conversion_details.get('validation_warnings', [])

                # Extract investment details
                investment_details = {
                    'initial_investment': amount,
                    'final_value': scenario.conversion_details.get('final_pot_inr', 0) if scenario.conversion_details else 0,
                    'cagr': scenario.conversion_details.get('cagr', 0) if scenario.conversion_details else 0,
                    'total_return': scenario.conversion_details.get('total_return', 0) if scenario.conversion_details else 0,
                    'volatility': scenario.conversion_details.get('volatility', 0) if scenario.conversion_details else 0,
                    'investment_period': f"{start_year} → {education_year}",
                    'asset_type': scenario.conversion_details.get('asset_type', 'Unknown') if scenario.conversion_details else 'Unknown'
                }

                # Get risk level from breakdown
                risk_level = "Medium"
                performance_summary = "No performance data available"

                if hasattr(scenario, 'breakdown') and scenario.breakdown:
                    risk_level = scenario.breakdown.get('risk_level', 'Medium')
                    performance_summary = scenario.breakdown.get('performance_summary', 'No performance data available')

                result = InvestmentResult(
                    strategy_name=scenario.strategy_name,
                    total_cost_inr=scenario.total_cost_inr,
                    total_cost_gbp=scenario.total_cost_gbp,
                    savings_vs_payg_inr=scenario.savings_vs_payg_inr,
                    savings_percentage=scenario.savings_percentage,
                    investment_details=investment_details,
                    risk_level=risk_level,
                    performance_summary=performance_summary,
                    validation_warnings=warnings
                )

                results.append(result)

            # Results are already sorted by savings amount in the backend
            logger.info(f"Successfully calculated {len(results)} investment scenarios")
            return results

        except Exception as e:
            error_msg = f"Investment calculation failed: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def get_course_info(_self, university: str, course: str) -> Dict:
        """
        Get comprehensive course information from data processor.

        Args:
            university: University name
            course: Course name

        Returns:
            Dictionary with course information including fees and projections
        """
        try:
            return _self.data_processor.get_course_info(university, course)
        except Exception as e:
            logger.error(f"Failed to get course info for {university} {course}: {e}")
            return {}

    def get_total_programme_cost(self, university: str, course: str, education_year: int) -> float:
        """
        Get total 3-year programme cost in GBP.

        Args:
            university: University name
            course: Course name
            education_year: Year when education starts

        Returns:
            Total programme cost in GBP
        """
        try:
            return self.savings_calculator.calculate_total_programme_cost(
                university, course, education_year
            )
        except Exception as e:
            logger.error(f"Failed to calculate programme cost: {e}")
            return 0.0

    def get_pay_as_you_go_cost(self, university: str, course: str, education_year: int) -> Dict[str, float]:
        """
        Get pay-as-you-go baseline costs.

        Args:
            university: University name
            course: Course name
            education_year: Year when education starts

        Returns:
            Dictionary with GBP and INR costs
        """
        try:
            total_gbp = self.get_total_programme_cost(university, course, education_year)
            fx_rate = self.data_processor.get_september_fx_rate(education_year)
            total_inr = total_gbp * fx_rate

            return {
                'total_gbp': total_gbp,
                'total_inr': total_inr,
                'exchange_rate': fx_rate,
                'education_year': education_year
            }
        except Exception as e:
            logger.error(f"Failed to calculate pay-as-you-go cost: {e}")
            return {'total_gbp': 0, 'total_inr': 0, 'exchange_rate': 0, 'education_year': education_year}

    def format_investment_amount(self, amount: float) -> str:
        """
        Format investment amount for display.

        Args:
            amount: Amount in INR

        Returns:
            Formatted string (e.g., "₹10.0L", "₹1.5Cr")
        """
        try:
            if amount >= 10000000:  # 1 crore or more
                return f"₹{amount/10000000:.1f}Cr"
            elif amount >= 100000:  # 1 lakh or more
                return f"₹{amount/100000:.1f}L"
            elif amount >= 1000:    # 1 thousand or more
                return f"₹{amount/1000:.1f}K"
            else:
                return f"₹{amount:,.0f}"
        except Exception:
            return f"₹{amount:,.0f}"

    def format_savings_amount(self, amount: float) -> str:
        """
        Format savings amount with appropriate sign and color coding.

        Args:
            amount: Savings amount in INR (positive = savings, negative = loss)

        Returns:
            Formatted string with sign
        """
        try:
            formatted = self.format_investment_amount(abs(amount))
            if amount > 0:
                return f"+{formatted}"
            elif amount < 0:
                return f"-{formatted}"
            else:
                return formatted
        except Exception:
            return f"₹{amount:,.0f}"

    def get_investment_summary(self, results: List[InvestmentResult]) -> Dict[str, Any]:
        """
        Generate summary statistics for investment results.

        Args:
            results: List of InvestmentResult objects

        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {}

        try:
            # Find best and worst strategies
            best_result = max(results, key=lambda x: x.savings_vs_payg_inr)
            worst_result = min(results, key=lambda x: x.savings_vs_payg_inr)

            # Count profitable strategies
            profitable_count = len([r for r in results if r.savings_vs_payg_inr > 0])

            # Calculate averages
            avg_savings = np.mean([r.savings_vs_payg_inr for r in results])
            avg_savings_pct = np.mean([r.savings_percentage for r in results])

            return {
                'total_strategies': len(results),
                'profitable_strategies': profitable_count,
                'best_strategy': {
                    'name': best_result.strategy_name,
                    'savings_inr': best_result.savings_vs_payg_inr,
                    'savings_percentage': best_result.savings_percentage
                },
                'worst_strategy': {
                    'name': worst_result.strategy_name,
                    'savings_inr': worst_result.savings_vs_payg_inr,
                    'savings_percentage': worst_result.savings_percentage
                },
                'average_savings_inr': avg_savings,
                'average_savings_percentage': avg_savings_pct,
                'has_warnings': any(r.validation_warnings for r in results)
            }
        except Exception as e:
            logger.error(f"Failed to generate investment summary: {e}")
            return {}

    def get_default_scenario(self) -> Dict[str, Any]:
        """
        Get default investment scenario: Oxford PPE 2025-2027, ₹10L investment.

        Returns:
            Dictionary with default parameters
        """
        return {
            'university': 'Oxford',
            'course': 'Philosophy Politics & Economics',
            'start_year': 2025,
            'education_year': 2027,
            'amount': 1000000,  # ₹10 lakhs
            'strategies': ['GOLD_INR', 'FIXED_5PCT']
        }

    def test_backend_connection(self) -> Dict[str, bool]:
        """
        Test connection to backend systems.

        Returns:
            Dictionary with connection status for each component
        """
        status = {
            'data_processor': False,
            'savings_calculator': False,
            'universities_loaded': False,
            'fee_calculation': False
        }

        try:
            # Test data processor
            if self.data_processor and hasattr(self.data_processor, 'fees_df'):
                status['data_processor'] = self.data_processor.fees_df is not None

            # Test savings calculator
            if self.savings_calculator:
                status['savings_calculator'] = True

            # Test university data
            universities = self.get_available_universities()
            status['universities_loaded'] = len(universities) > 0

            # Test fee calculation with default data
            if universities:
                test_uni = universities[0]
                courses = self.get_available_courses(test_uni)
                if courses:
                    test_course = courses[0]
                    test_cost = self.get_total_programme_cost(test_uni, test_course, 2027)
                    status['fee_calculation'] = test_cost > 0

            logger.info(f"Backend connection test results: {status}")

        except Exception as e:
            logger.error(f"Backend connection test failed: {e}")

        return status


# Convenience functions for common operations
def create_investment_calculator() -> InvestmentCalculator:
    """
    Create and initialize investment calculator.

    Returns:
        Initialized InvestmentCalculator instance

    Raises:
        ValueError: If initialization fails
    """
    try:
        return InvestmentCalculator()
    except Exception as e:
        raise ValueError(f"Failed to create investment calculator: {e}")


@st.cache_data(ttl=3600)
def get_universities() -> List[str]:
    """
    Cached function to get available universities.

    Returns:
        List of university names
    """
    try:
        calc = create_investment_calculator()
        return calc.get_available_universities()
    except Exception as e:
        logger.error(f"Failed to get universities: {e}")
        return []


@st.cache_data(ttl=3600)
def get_courses(university: str) -> List[str]:
    """
    Cached function to get courses for a university.

    Args:
        university: University name

    Returns:
        List of course names
    """
    try:
        calc = create_investment_calculator()
        return calc.get_available_courses(university)
    except Exception as e:
        logger.error(f"Failed to get courses for {university}: {e}")
        return []


def calculate_investment_roi(
    university: str,
    course: str,
    start_year: int,
    education_year: int,
    amount: float,
    strategies: List[str] = None
) -> List[InvestmentResult]:
    """
    Convenience function for calculating investment ROI.

    Args:
        university: University name
        course: Course name
        start_year: Investment start year
        education_year: Education start year
        amount: Investment amount in INR
        strategies: Investment strategies (default: Gold and 5% Fixed)

    Returns:
        List of InvestmentResult objects

    Raises:
        ValueError: If calculation fails
    """
    calc = create_investment_calculator()
    return calc.calculate_investment_scenarios(
        university, course, start_year, education_year, amount, strategies
    )