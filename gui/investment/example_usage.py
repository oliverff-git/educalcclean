#!/usr/bin/env python3
"""
Example usage of the Investment Calculator wrapper.

This demonstrates how to use the investment calculations integration
to connect to the existing backend systems.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from gui.investment.calculations import (
    InvestmentCalculator,
    create_investment_calculator,
    calculate_investment_roi
)


def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===\n")

    # Create calculator
    calc = create_investment_calculator()

    # Get available data
    universities = calc.get_available_universities()
    print(f"Available universities: {universities}")

    # Get courses for Oxford
    oxford_courses = calc.get_available_courses("Oxford")
    print(f"Oxford courses (first 5): {oxford_courses[:5]}")

    # Calculate investment scenarios for default parameters
    default = calc.get_default_scenario()
    print(f"\nDefault scenario: {default}")

    results = calc.calculate_investment_scenarios(
        university=default['university'],
        course=default['course'],
        start_year=default['start_year'],
        education_year=default['education_year'],
        amount=default['amount'],
        strategies=default['strategies']
    )

    print(f"\nResults ({len(results)} scenarios):")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.strategy_name}")
        print(f"   Savings: {calc.format_savings_amount(result.savings_vs_payg_inr)}")
        print(f"   Risk: {result.risk_level}")


def example_custom_calculation():
    """Custom calculation example."""
    print("\n=== Custom Calculation Example ===\n")

    # Use convenience function
    results = calculate_investment_roi(
        university="Cambridge",
        course="Computer Science",
        start_year=2024,
        education_year=2026,
        amount=1500000,  # ₹15 lakhs
        strategies=["GOLD_INR", "FIXED_5PCT"]
    )

    calc = create_investment_calculator()

    print("Cambridge Computer Science (2024→2026, ₹15L investment):")
    for result in results:
        print(f"\n• {result.strategy_name}")
        print(f"  Total cost: {calc.format_investment_amount(result.total_cost_inr)}")
        print(f"  Savings: {calc.format_savings_amount(result.savings_vs_payg_inr)} ({result.savings_percentage:.1f}%)")
        print(f"  Performance: {result.performance_summary}")

    # Get summary
    summary = calc.get_investment_summary(results)
    print(f"\nSummary:")
    print(f"  Best: {summary['best_strategy']['name']}")
    print(f"  Profitable: {summary['profitable_strategies']}/{summary['total_strategies']}")


def example_course_analysis():
    """Course information analysis example."""
    print("\n=== Course Analysis Example ===\n")

    calc = create_investment_calculator()

    # Analyze Oxford PPE
    course_info = calc.get_course_info("Oxford", "Philosophy Politics & Economics")
    print("Oxford PPE Analysis:")
    print(f"  Latest fee: £{course_info.get('latest_fee', 0):,.0f}")
    print(f"  Fee CAGR: {course_info.get('cagr_pct', 0):.2f}%")
    print(f"  Data points: {course_info.get('data_points', 0)}")

    # Get programme costs
    total_gbp = calc.get_total_programme_cost("Oxford", "Philosophy Politics & Economics", 2027)
    payg_costs = calc.get_pay_as_you_go_cost("Oxford", "Philosophy Politics & Economics", 2027)

    print(f"\n2027 Programme Costs:")
    print(f"  Total 3-year cost: £{total_gbp:,.0f}")
    print(f"  Pay-as-you-go cost: {calc.format_investment_amount(payg_costs['total_inr'])}")
    print(f"  Exchange rate used: {payg_costs['exchange_rate']:.2f}")


def example_validation():
    """Input validation example."""
    print("\n=== Validation Example ===\n")

    calc = create_investment_calculator()

    # Test valid inputs
    is_valid, errors = calc.validate_investment_inputs(
        university="Oxford",
        course="Mathematics",
        start_year=2025,
        education_year=2027,
        amount=1000000,
        strategies=["GOLD_INR"]
    )
    print(f"Valid inputs: {is_valid}")

    # Test invalid inputs
    is_valid, errors = calc.validate_investment_inputs(
        university="Invalid University",
        course="Invalid Course",
        start_year=2028,  # After education year
        education_year=2027,
        amount=-1000,     # Negative
        strategies=["INVALID"]
    )
    print(f"Invalid inputs: {is_valid}")
    print(f"Errors: {errors}")


def main():
    """Run all examples."""
    print("Investment Calculator Usage Examples")
    print("=" * 50)

    try:
        example_basic_usage()
        example_custom_calculation()
        example_course_analysis()
        example_validation()

        print("\n" + "=" * 50)
        print("✓ All examples completed successfully!")

    except Exception as e:
        print(f"❌ Example failed: {e}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)