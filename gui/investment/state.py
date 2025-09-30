"""
Investment Strategies App State Management
Completely isolated from education_savings_app.py session state
"""

import streamlit as st
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime


@dataclass
class InvestmentAppState:
    """
    Investment app state isolated from education savings app
    Default state: Oxford PPE 2025-2027, ₹10L investment
    """
    # Course selection state
    university: str = "Oxford"
    course: str = "Philosophy Politics & Economics (PPE)"
    start_year: int = 2026
    end_year: int = 2028
    duration: int = 3

    # Investment selection state
    investment_amount: int = 1000000  # ₹10L default
    selected_strategy: str = "gold"  # Default to gold investment
    expected_return: float = 0.11  # 11% for gold
    risk_level: str = "Medium-High"

    # Calculation results (cached)
    projections_calculated: bool = False
    projection_data: List[Dict] = field(default_factory=list)
    final_amount: float = 0.0
    total_growth: float = 0.0
    total_return_percentage: float = 0.0

    # UI state
    show_comparison: bool = False
    calculation_loading: bool = False


def get_investment_state() -> InvestmentAppState:
    """
    Get singleton investment app state from session state
    Completely separate from education app state
    """
    if "investment_app_state" not in st.session_state:
        st.session_state["investment_app_state"] = InvestmentAppState()
    return st.session_state["investment_app_state"]


def update_investment_state(**kwargs) -> None:
    """
    Update investment app state with new values
    """
    state = get_investment_state()
    for key, value in kwargs.items():
        if hasattr(state, key):
            setattr(state, key, value)


def reset_investment_state() -> None:
    """
    Reset investment app state to defaults
    """
    if "investment_app_state" in st.session_state:
        del st.session_state["investment_app_state"]

    # Clear related session state keys
    keys_to_clear = [
        "investment_university",
        "investment_course",
        "investment_start_year",
        "investment_duration",
        "investment_amount",
        "selected_strategy",
        "select_gold",
        "select_saver",
        "calculate_projections",
        "compare_strategies",
        "reset_all"
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def init_investment_defaults() -> None:
    """
    Initialize default session state values for investment app
    """
    state = get_investment_state()

    # Initialize session state keys if not present
    default_values = {
        "investment_university": state.university,
        "investment_course": state.course,
        "investment_start_year": state.start_year,
        "investment_duration": state.duration,
        "investment_amount": state.investment_amount,
        "selected_strategy": state.selected_strategy
    }

    for key, default_value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def sync_state_from_ui() -> None:
    """
    Sync investment app state from UI session state values
    """
    state = get_investment_state()

    # Sync course selection
    if "investment_university" in st.session_state:
        state.university = st.session_state["investment_university"]
    if "investment_course" in st.session_state:
        state.course = st.session_state["investment_course"]
    if "investment_start_year" in st.session_state:
        state.start_year = st.session_state["investment_start_year"]
    if "investment_duration" in st.session_state:
        state.duration = st.session_state["investment_duration"]
        state.end_year = state.start_year + state.duration

    # Sync investment selection
    if "investment_amount" in st.session_state:
        state.investment_amount = st.session_state["investment_amount"]
    if "selected_strategy" in st.session_state:
        state.selected_strategy = st.session_state["selected_strategy"]
        # Update expected return based on strategy
        if state.selected_strategy == "gold":
            state.expected_return = 0.11  # 11% for gold
            state.risk_level = "Medium-High"
        else:  # saver
            state.expected_return = 0.05  # 5% for saver
            state.risk_level = "Low"


def calculate_investment_projections() -> None:
    """
    Calculate investment projections and store in state
    """
    state = get_investment_state()
    sync_state_from_ui()

    # Calculate years to goal
    current_year = datetime.now().year
    years_to_goal = state.start_year - current_year

    if years_to_goal <= 0:
        state.projections_calculated = False
        return

    # Calculate compound growth
    initial_amount = state.investment_amount
    annual_return = state.expected_return

    state.final_amount = initial_amount * ((1 + annual_return) ** years_to_goal)
    state.total_growth = state.final_amount - initial_amount
    state.total_return_percentage = ((state.final_amount - initial_amount) / initial_amount) * 100

    # Generate year-by-year projections
    projection_data = []
    current_amount = initial_amount

    for year in range(years_to_goal + 1):
        target_year = current_year + year
        if year == 0:
            growth = 0
        else:
            growth = current_amount * annual_return
            current_amount += growth

        projection_data.append({
            "year": target_year,
            "amount": int(current_amount),
            "annual_growth": int(growth),
            "return_percentage": annual_return * 100 if year > 0 else 0
        })

    state.projection_data = projection_data
    state.projections_calculated = True


def get_strategy_comparison_data() -> Dict[str, Dict]:
    """
    Get comparison data for Gold vs 5% Saver strategies
    """
    return {
        "gold": {
            "name": "Gold Investment",
            "expected_return": 0.11,
            "return_range": "10-12%",
            "risk_level": "Medium-High",
            "volatility": "Moderate to High",
            "inflation_protection": "Excellent",
            "liquidity": "Good",
            "min_investment": "₹1,00,000+",
            "tax_implications": "Long-term capital gains"
        },
        "saver": {
            "name": "5% Fixed Saver",
            "expected_return": 0.05,
            "return_range": "5%",
            "risk_level": "Low",
            "volatility": "None",
            "inflation_protection": "Limited",
            "liquidity": "Excellent",
            "min_investment": "₹10,000+",
            "tax_implications": "Interest taxable as income"
        }
    }


def format_investment_amount(amount: int) -> str:
    """
    Format investment amount in Indian currency notation
    """
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.1f}Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.1f}L"
    else:
        return f"₹{amount:,}"


def get_course_options() -> Dict[str, List[str]]:
    """
    Get course options mapped by university
    """
    return {
        "Oxford": ["Philosophy Politics & Economics (PPE)", "Computer Science", "Engineering Science", "Medicine"],
        "Cambridge": ["Natural Sciences", "Computer Science", "Engineering", "Economics"],
        "LSE": ["Economics", "Management", "International Relations", "Finance"],
        "Imperial College": ["Computing", "Engineering", "Medicine", "Business School"],
        "UCL": ["Computer Science", "Engineering", "Medicine", "Economics"]
    }


def is_calculation_valid() -> bool:
    """
    Check if current state allows for valid calculations
    """
    state = get_investment_state()
    current_year = datetime.now().year
    years_to_goal = state.start_year - current_year

    return (
        years_to_goal > 0 and
        state.investment_amount > 0 and
        state.selected_strategy in ["gold", "saver"]
    )


def get_investment_summary() -> Dict[str, Any]:
    """
    Get formatted summary of current investment configuration
    """
    state = get_investment_state()
    current_year = datetime.now().year
    years_to_goal = state.start_year - current_year

    return {
        "course": f"{state.course} at {state.university}",
        "duration": f"{state.start_year}-{state.end_year} ({state.duration} years)",
        "years_to_goal": years_to_goal,
        "investment_amount": format_investment_amount(state.investment_amount),
        "strategy": state.selected_strategy.title(),
        "expected_return": f"{state.expected_return*100:.1f}%",
        "risk_level": state.risk_level,
        "projections_ready": state.projections_calculated and is_calculation_valid()
    }