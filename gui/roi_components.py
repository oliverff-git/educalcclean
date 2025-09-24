"""
ROI Components for Return on Savings Module.

UI components for investment analysis interface.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Optional
import numpy as np


def render_roi_sidebar(conversion_year: int, education_year: int, university: str = None, programme: str = None, calculator = None) -> Dict:
    """Render ROI analysis sidebar components.

    Args:
        conversion_year: Year to start investing
        education_year: Year education starts
        university: University name for fee calculation
        programme: Programme name for fee calculation
        calculator: EducationSavingsCalculator instance

    Returns:
        Dictionary with ROI configuration
    """
    st.sidebar.header("💰 Investment Analysis")

    # Enable ROI analysis
    enable_roi = st.sidebar.checkbox(
        "Enable Investment Strategies",
        value=False,
        help="Analyze investment-based funding strategies"
    )

    if not enable_roi:
        return {"enabled": False}

    # Helper function to format amounts
    def format_amount(amt):
        if amt >= 10000000:  # 1 crore
            return f"₹{amt/10000000:.2f}Cr"
        elif amt >= 100000:  # 1 lakh
            return f"₹{amt/100000:.1f}L"
        else:
            return f"₹{amt:,.0f}"

    # Calculate investment options based on course fees
    investment_options = {}

    if calculator and university and programme:
        try:
            # Calculate total programme fees
            total_fees_gbp = calculator.calculate_total_programme_cost(university, programme, education_year)
            current_fx_rate = calculator.data_processor.get_september_fx_rate(conversion_year)
            total_fees_inr = total_fees_gbp * current_fx_rate

            # Create year-based options
            investment_options = {
                f"📅 3 Years Fees ({format_amount(total_fees_inr)})": total_fees_inr,
                f"📅 2 Years Fees ({format_amount(total_fees_inr * 2/3)})": total_fees_inr * 2/3,
                f"📅 1 Year Fees ({format_amount(total_fees_inr / 3)})": total_fees_inr / 3,
                f"📅 1/2 Year Fees ({format_amount(total_fees_inr / 6)})": total_fees_inr / 6,
            }
        except Exception:
            # Fallback if calculation fails
            pass

    # Add fixed amount options
    investment_options.update({
        f"💰 ₹20 Lakhs": 2000000,
        f"💰 ₹50 Lakhs": 5000000,
        f"💰 ₹1 Crore": 10000000,
        "💡 Custom Amount...": "custom"
    })

    # Dropdown selection
    selected_option = st.sidebar.selectbox(
        "💵 Investment Amount",
        options=list(investment_options.keys()),
        index=0,  # Default to first option
        help="Select investment amount based on programme fees or fixed amounts"
    )

    # Get the investment amount
    if investment_options[selected_option] == "custom":
        investment_amount = st.sidebar.number_input(
            "Enter Custom Amount (₹)",
            min_value=500000,
            max_value=50000000,
            value=2000000,
            step=100000,
            help="Custom investment amount in INR"
        )
    else:
        investment_amount = investment_options[selected_option]
        st.sidebar.info(f"💰 Investment: {format_amount(investment_amount)}")

    # Strategy selection
    available_strategies = {
        "GOLD_INR": "🟡 Gold Investment - Safe, beats inflation",
        "NIFTY_INR": "🔴 Indian Stock Market (NIFTY) - Higher growth potential",
        "FTSE_GBP": "🔴 UK Stock Market (FTSE) - International exposure",
        "FIXED_5PCT": "🟢 Fixed Deposit 5% - Guaranteed returns"
    }

    selected_strategies = st.sidebar.multiselect(
        "📈 Investment Strategies",
        options=list(available_strategies.keys()),
        default=["GOLD_INR", "NIFTY_INR", "FIXED_5PCT"],
        format_func=lambda x: available_strategies[x],
        help="Select investment strategies to analyze"
    )

    # Risk tolerance
    risk_tolerance = st.sidebar.select_slider(
        "⚖️ Risk Tolerance",
        options=["Conservative", "Moderate", "Aggressive"],
        value="Moderate",
        help="Your comfort level with investment risk"
    )

    # Investment period validation
    investment_years = education_year - conversion_year
    if investment_years <= 0:
        st.sidebar.error("Education year must be after conversion year")
        return {"enabled": False}

    if investment_years < 2:
        st.sidebar.warning("⚠️ Short investment period may limit returns")

    return {
        "enabled": True,
        "investment_amount": investment_amount,
        "selected_strategies": selected_strategies,
        "risk_tolerance": risk_tolerance,
        "investment_years": investment_years
    }


def render_roi_scenarios_summary(scenarios: List, investment_amount: float):
    """Render summary of ROI scenarios.

    Args:
        scenarios: List of SavingsScenario objects
        investment_amount: Initial investment amount
    """
    if not scenarios:
        st.warning("No investment scenarios available")
        return

    st.subheader("💼 Investment Strategy Results")

    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)

    # Best strategy
    best_scenario = max(scenarios, key=lambda x: x.savings_vs_payg_inr)
    with col1:
        st.metric(
            "🏆 Best Option",
            best_scenario.strategy_name.split(' (')[0],  # Remove CAGR from display
            f"₹{best_scenario.savings_vs_payg_inr:,.0f} saved"
        )

    # Average savings
    avg_savings = np.mean([s.savings_vs_payg_inr for s in scenarios])
    with col2:
        st.metric(
            "📊 Average Savings",
            f"₹{avg_savings:,.0f}",
            f"{len([s for s in scenarios if s.savings_vs_payg_inr > 0])}/{len(scenarios)} profitable"
        )

    # Investment growth
    best_growth = best_scenario.conversion_details.get('total_return', 0) * 100
    with col3:
        st.metric(
            "📈 Total Growth",
            f"{best_growth:.1f}%",
            f"Over {best_scenario.conversion_details.get('investment_period', 'N/A')}"
        )

    # Return on Investment (ROI) - more meaningful than cost reduction
    roi = (best_scenario.savings_vs_payg_inr / investment_amount) * 100 if investment_amount > 0 else 0

    # Cap ROI display at reasonable levels
    if roi > 500:
        roi_display = "500%+"
        roi_desc = "⚠️ verify calculations"
    elif roi < -100:
        roi_display = "-100%"
        roi_desc = "⚠️ significant loss"
    else:
        roi_display = f"{roi:.1f}%"
        roi_desc = "profit on investment"

    with col4:
        st.metric(
            "📈 Return on Investment",
            roi_display,
            roi_desc
        )


def render_roi_scenario_cards(scenarios: List):
    """Render detailed scenario cards.

    Args:
        scenarios: List of SavingsScenario objects
    """
    st.subheader("📋 Strategy Details")

    for i, scenario in enumerate(scenarios):
        with st.expander(f"💎 {scenario.strategy_name}", expanded=(i == 0)):
            # Data quality indicator at the top
            render_data_quality_indicator(scenario)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**💰 Investment Results**")
                st.write(f"Total Cost: ₹{scenario.total_cost_inr:,.0f}")
                st.write(f"Money Saved: ₹{scenario.savings_vs_payg_inr:,.0f}")
                st.write(f"Savings Rate: {scenario.savings_percentage:.1f}%")

                # Investment details
                if 'cagr' in scenario.conversion_details:
                    cagr = scenario.conversion_details['cagr'] * 100
                    st.write(f"Annual Growth: {cagr:.1f}%")

                if 'total_return' in scenario.conversion_details:
                    total_return = scenario.conversion_details['total_return'] * 100
                    st.write(f"Total Profit: {total_return:.1f}%")

            with col2:
                st.markdown("**⚖️ Risk Level**")
                risk_level = scenario.breakdown.get('risk_level', 'Unknown')
                st.write(f"Investment Type: {risk_level}")

                if 'volatility' in scenario.conversion_details:
                    volatility = scenario.conversion_details['volatility'] * 100
                    # Simplify volatility explanation
                    if volatility < 5:
                        risk_desc = "Very Safe"
                    elif volatility < 15:
                        risk_desc = "Moderate Risk"
                    else:
                        risk_desc = "Higher Risk"
                    st.write(f"Risk Level: {risk_desc} ({volatility:.1f}%)")

                if 'max_drawdown' in scenario.conversion_details:
                    max_drawdown = abs(scenario.conversion_details['max_drawdown']) * 100
                    st.write(f"Worst Case Loss: {max_drawdown:.1f}%")

            # Performance summary
            performance = scenario.breakdown.get('performance_summary', '')
            if performance:
                st.info(f"📊 {performance}")

            # Investment breakdown
            if 'effective_cost_breakdown' in scenario.breakdown:
                breakdown = scenario.breakdown['effective_cost_breakdown']
                st.markdown("**💼 Cost Breakdown**")

                investment_proceeds = breakdown.get('investment_proceeds', 0)
                total_cost = breakdown.get('total_education_cost', 0)
                surplus = breakdown.get('surplus_if_any', 0)

                if surplus > 0:
                    st.success(f"💰 Surplus after covering education: ₹{surplus:,.0f}")
                else:
                    remaining_cost = total_cost - investment_proceeds
                    if remaining_cost > 0:
                        st.info(f"💳 Remaining cost to cover: ₹{remaining_cost:,.0f}")


def render_risk_tolerance_guide(risk_tolerance: str) -> Dict:
    """Render risk tolerance guidance.

    Args:
        risk_tolerance: Selected risk tolerance level

    Returns:
        Dictionary with risk-based recommendations
    """
    risk_profiles = {
        "Conservative": {
            "description": "Capital preservation with modest growth",
            "recommended_strategies": ["FIXED_5PCT", "GOLD_INR"],
            "max_equity_allocation": 30,
            "key_points": [
                "Focus on capital protection",
                "Lower volatility strategies",
                "Steady, predictable returns"
            ]
        },
        "Moderate": {
            "description": "Balanced approach with moderate risk",
            "recommended_strategies": ["GOLD_INR", "NIFTY_INR", "FIXED_5PCT"],
            "max_equity_allocation": 60,
            "key_points": [
                "Balanced risk-return profile",
                "Mix of stable and growth assets",
                "Diversification across asset classes"
            ]
        },
        "Aggressive": {
            "description": "Growth-focused with higher risk tolerance",
            "recommended_strategies": ["NIFTY_INR", "FTSE_GBP", "GOLD_INR"],
            "max_equity_allocation": 80,
            "key_points": [
                "Higher growth potential",
                "Equity-heavy allocation",
                "Tolerance for volatility"
            ]
        }
    }

    profile = risk_profiles.get(risk_tolerance, risk_profiles["Moderate"])

    with st.sidebar.expander(f"ℹ️ {risk_tolerance} Profile Guide"):
        st.write(f"**{profile['description']}**")
        st.write("**Recommended Strategies:**")
        for strategy in profile['recommended_strategies']:
            st.write(f"• {strategy.replace('_', ' ')}")
        st.write("**Key Points:**")
        for point in profile['key_points']:
            st.write(f"• {point}")

    return profile


def format_roi_metrics(amount: float, is_currency: bool = True) -> str:
    """Format ROI metrics for display.

    Args:
        amount: Amount to format
        is_currency: Whether to format as currency

    Returns:
        Formatted string
    """
    if is_currency:
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.0f}"
    else:
        return f"{amount:.1f}%"


def render_data_quality_indicator(scenario):
    """Render data quality indicator for a scenario.

    Args:
        scenario: SavingsScenario with conversion_details containing data quality info
    """
    # Check for unrealistic values first
    warnings = []

    if 'cagr' in scenario.conversion_details:
        cagr_pct = scenario.conversion_details['cagr'] * 100
        if cagr_pct < -50 or cagr_pct > 50:
            warnings.append(f"Unrealistic annual growth: {cagr_pct:.1f}%")

    if 'total_return' in scenario.conversion_details:
        total_return_pct = scenario.conversion_details['total_return'] * 100
        if total_return_pct < -90 or total_return_pct > 1000:
            warnings.append(f"Unrealistic total return: {total_return_pct:.1f}%")

    # Show data quality info
    if 'data_quality' in scenario.conversion_details:
        quality_info = scenario.conversion_details['data_quality']
        quality = quality_info.get('quality', 'UNKNOWN')
        confidence = quality_info.get('confidence', 'LOW')

        # Color coding
        color_map = {
            'EXCELLENT': '🟢',
            'GOOD': '🟡',
            'FAIR': '🟠',
            'POOR': '🔴',
            'UNAVAILABLE': '⚫'
        }

        icon = color_map.get(quality, '❓')
        st.caption(f"{icon} Data Quality: {quality} | Confidence: {confidence}")

        if quality in ['POOR', 'UNAVAILABLE']:
            st.warning("⚠️ Limited data available for this asset. Projections may be unreliable.")

    # Show any validation warnings
    for warning in warnings:
        st.error(f"⚠️ {warning}")
        st.info("💡 This may indicate a calculation error or unrealistic market data.")


def render_investment_warnings():
    """Render investment risk warnings."""
    with st.expander("⚠️ Important Investment Disclaimers"):
        st.warning("""
        **Investment Risk Warnings:**

        • **Market Risk**: All investments carry risk of loss. Past performance does not guarantee future results.
        • **Volatility**: Asset prices fluctuate. Values shown are estimates based on historical data.
        • **Currency Risk**: FTSE investments involve GBP/INR conversion risk.
        • **Education Planning**: This tool is for planning purposes only. Consult financial advisors for investment decisions.
        • **Data Limitations**: Projections are based on historical trends and may not reflect future market conditions.
        • **Data Requirements**: Investment analysis requires actual market data files - estimates may be used when data is unavailable.

        **Recommendations:**
        • Diversify across multiple asset classes
        • Consider your risk tolerance and investment timeline
        • Review and adjust strategy regularly
        • Seek professional financial advice for significant investments
        • Verify data quality indicators before making decisions
        """)


def create_simple_roi_chart(scenarios: List) -> go.Figure:
    """Create simple ROI comparison chart.

    Args:
        scenarios: List of SavingsScenario objects

    Returns:
        Plotly figure
    """
    if not scenarios:
        return go.Figure()

    # Prepare data
    strategy_names = [s.strategy_name.split(' (')[0] for s in scenarios]  # Remove CAGR
    savings_amounts = [s.savings_vs_payg_inr for s in scenarios]
    colors = ['green' if x > 0 else 'red' for x in savings_amounts]

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=strategy_names,
            y=savings_amounts,
            marker_color=colors,
            text=[f"₹{x:,.0f}" for x in savings_amounts],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title="Investment Strategy Comparison",
        xaxis_title="Strategy",
        yaxis_title="Savings vs Pay-as-you-go (₹)",
        height=400,
        showlegend=False
    )

    return fig