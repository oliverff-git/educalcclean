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
    st.sidebar.header(" Investment Analysis")

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
                f" 3 Years Fees ({format_amount(total_fees_inr)})": total_fees_inr,
                f" 2 Years Fees ({format_amount(total_fees_inr * 2/3)})": total_fees_inr * 2/3,
                f" 1 Year Fees ({format_amount(total_fees_inr / 3)})": total_fees_inr / 3,
                f" 1/2 Year Fees ({format_amount(total_fees_inr / 6)})": total_fees_inr / 6,
            }
        except Exception:
            # Fallback if calculation fails
            pass

    # Add fixed amount options
    investment_options.update({
        f" ₹20 Lakhs": 2000000,
        f" ₹50 Lakhs": 5000000,
        f" ₹1 Crore": 10000000,
        " Custom Amount...": "custom"
    })

    # Dropdown selection
    selected_option = st.sidebar.selectbox(
        "Investment Amount",
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
        st.sidebar.info(f" Investment: {format_amount(investment_amount)}")

    # Strategy selection
    available_strategies = {
        "GOLD_INR": " Gold (INR) - Inflation hedge, moderate volatility (±10-15% annually)",
        "FIXED_5PCT": " Fixed Deposit (5% p.a.) - Capital protected, guaranteed returns"
    }

    selected_strategies = st.sidebar.multiselect(
        " Savings Strategies",
        options=list(available_strategies.keys()),
        default=["GOLD_INR", "FIXED_5PCT"],
        format_func=lambda x: available_strategies[x],
        help="Choose between conservative fixed deposits and gold for inflation protection"
    )

    # Risk tolerance
    risk_tolerance = st.sidebar.select_slider(
        " Risk Tolerance",
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
        st.sidebar.warning(" Short investment period may limit returns")

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

    st.subheader(" Simple Comparison for Education Savings")

    # Clear comparison table for Indian parents
    st.markdown("**Your Investment:** ₹{:,.0f} ({:.1f} Lakh)".format(investment_amount, investment_amount/100000))

    # Create simple comparison
    comparison_data = []

    for scenario in scenarios:
        final_value = scenario.conversion_details.get('final_pot_inr', 0)
        profit = final_value - investment_amount
        roi_pct = (profit / investment_amount * 100) if investment_amount > 0 else 0

        # Calculate investment period and yearly rate
        investment_period = scenario.conversion_details.get('investment_period', '2024 → 2027')
        try:
            years = int(investment_period.split(' → ')[1]) - int(investment_period.split(' → ')[0])
        except:
            years = 3  # Default fallback

        yearly_rate = ((final_value / investment_amount) ** (1/years) - 1) * 100 if years > 0 and investment_amount > 0 else 0

        # Extract strategy name
        strategy_name = scenario.strategy_name.split(' (')[0].replace('Investment', '').strip()
        if 'GOLD' in strategy_name.upper():
            display_name = " Gold"
            risk_level = "Medium Risk"
            note = "Based on recent market performance - can vary significantly"
        elif 'FIXED' in strategy_name.upper() or '5%' in strategy_name:
            display_name = " Fixed Deposit"
            risk_level = "No Risk"
            note = "Guaranteed return, principal protected"
        else:
            display_name = strategy_name
            risk_level = "Unknown"
            note = ""

        comparison_data.append({
            'Strategy': display_name,
            'Final Value': f"₹{final_value/100000:.1f}L",
            'Your Profit': f"₹{profit/100000:.1f}L",
            'Total Return': f"{roi_pct:.0f}%",
            'Yearly %': f"{yearly_rate:.1f}%",
            'Years': f"{years}",
            'Risk Level': risk_level,
            'Important Note': note
        })

    # Sort by final value (best first)
    comparison_data.sort(key=lambda x: float(x['Final Value'].replace('₹', '').replace('L', '')), reverse=True)

    # Display as clean table
    for i, data in enumerate(comparison_data):
        with st.container():
            if i == 0:
                st.success(f" **Best Option: {data['Strategy']}**")
            else:
                st.info(f"**Alternative: {data['Strategy']}**")

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Final Amount", data['Final Value'])
            with col2:
                st.metric("Your Profit", data['Your Profit'])
            with col3:
                st.metric("Return", data['Total Return'])
            with col4:
                st.metric("Yearly %", data['Yearly %'])
            with col5:
                st.metric("Years", data['Years'], data['Risk Level'])

            if data['Important Note']:
                st.caption(f" {data['Important Note']}")

            st.markdown("---")

    # Important disclaimer for Indian parents
    st.markdown("---")
    st.warning("""
    ** Important for Indian Parents:**

    • **Gold**: Recent 3-year performance (24.4%) is exceptional - don't expect this to continue!
      Long-term average is 13-14% per year. Can swing from -20% to +40% in any single year.
    • **Fixed Deposit**: 5% is optimistic but achievable at top banks. Check current rates before investing.
    • **Market Reality**: Gold hit ₹102,289 per 10g in Aug 2025 - a huge jump from ₹64,070 in 2024.

     **Smart Approach**: Don't put all money in gold expecting 24% returns. Mix both for balance.
    """)


def render_roi_scenario_cards(scenarios: List):
    """Render detailed scenario cards.

    Args:
        scenarios: List of SavingsScenario objects
    """
    st.subheader(" Strategy Details")

    # Sort scenarios by final value (best first) for display
    sorted_scenarios = sorted(scenarios, key=lambda x: x.conversion_details.get('final_pot_inr', 0), reverse=True)

    for i, scenario in enumerate(sorted_scenarios):
        # Show final value and ROI in expander title
        final_value = scenario.conversion_details.get('final_pot_inr', 0)
        initial_investment = scenario.conversion_details.get('initial_investment_inr', 0)
        roi = ((final_value - initial_investment) / initial_investment * 100) if initial_investment > 0 else 0

        expander_title = f"{scenario.strategy_name.split(' (')[0]} → ₹{final_value/100000:.1f}L ({roi:.1f}% ROI)"

        with st.expander(expander_title, expanded=(i == 0)):
            # Data quality indicator at the top
            render_data_quality_indicator(scenario)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("** Investment Results**")
                final_value = scenario.conversion_details.get('final_pot_inr', 0)
                initial_investment = scenario.conversion_details.get('initial_investment_inr', 0)
                actual_profit = final_value - initial_investment

                # Clear display for Indian parents
                st.write(f"**Final Amount**: ₹{final_value/100000:.1f}L")
                st.write(f"**Your Profit**: ₹{actual_profit/100000:.1f}L")

                # ROI calculation
                roi_percent = (actual_profit / initial_investment) * 100 if initial_investment > 0 else 0
                st.write(f"**ROI**: {roi_percent:.1f}%")

                # Investment details
                if 'cagr' in scenario.conversion_details:
                    cagr = scenario.conversion_details['cagr'] * 100
                    st.write(f"**Annual Growth**: {cagr:.1f}%")

                # Show actual CAGR (not simple division)
                if 'cagr' in scenario.conversion_details:
                    cagr_yearly = scenario.conversion_details['cagr'] * 100
                    st.write(f"**Per Year (CAGR)**: {cagr_yearly:.1f}%")
                else:
                    # Fallback calculation
                    investment_period = scenario.conversion_details.get('investment_period', '2023 → 2026')
                    try:
                        years = int(investment_period.split(' → ')[1]) - int(investment_period.split(' → ')[0])
                        # Use compound annual growth rate formula
                        final_val = scenario.conversion_details.get('final_pot_inr', 0)
                        initial_val = scenario.conversion_details.get('initial_investment_inr', 0)
                        if initial_val > 0 and years > 0:
                            cagr_calc = ((final_val / initial_val) ** (1/years) - 1) * 100
                            st.write(f"**Per Year (CAGR)**: {cagr_calc:.1f}%")
                        else:
                            st.write(f"**Per Year**: {roi_percent/3:.1f}% (approx)")
                    except:
                        st.write(f"**Per Year**: {roi_percent/3:.1f}% (approx)")

            with col2:
                st.markdown("** Risk Level**")
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
                st.info(f" {performance}")

            # Clear education coverage information
            st.markdown("** Education Cost Coverage**")

            # Calculate education cost coverage
            final_value = scenario.conversion_details.get('final_pot_inr', 0)
            education_cost = scenario.savings_vs_payg_inr  # This represents the cost saved vs PAYG

            # Try to get actual education cost from breakdown
            if 'effective_cost_breakdown' in scenario.breakdown:
                breakdown = scenario.breakdown['effective_cost_breakdown']
                actual_education_cost = breakdown.get('total_education_cost', education_cost)
            else:
                # Estimate based on scenario data
                actual_education_cost = final_value - (final_value - scenario.total_cost_inr)

            if final_value >= actual_education_cost:
                surplus = final_value - actual_education_cost
                st.success(f"**Covers Full Education Cost**")
                st.success(f" Extra Money Left: ₹{surplus/100000:.1f}L")
            else:
                shortfall = actual_education_cost - final_value
                st.warning(f" **Partial Coverage Only**")
                st.warning(f"Additional Needed: ₹{shortfall/100000:.1f}L")


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
            "recommended_strategies": ["FIXED_5PCT", "GOLD_INR"],
            "max_equity_allocation": 60,
            "key_points": [
                "Balanced risk-return profile",
                "Mix of stable and growth assets",
                "Diversification across asset classes"
            ]
        },
        "Aggressive": {
            "description": "Growth-focused with higher risk tolerance",
            "recommended_strategies": ["GOLD_INR", "FIXED_5PCT"],
            "max_equity_allocation": 80,
            "key_points": [
                "Higher growth potential",
                "Equity-heavy allocation",
                "Tolerance for volatility"
            ]
        }
    }

    profile = risk_profiles.get(risk_tolerance, risk_profiles["Moderate"])

    with st.sidebar.expander(f" {risk_tolerance} Profile Guide"):
        st.write(f"**{profile['description']}**")
        st.write("**Recommended Allocation:**")

        # Show allocation guidance based on risk tolerance
        if risk_tolerance == "Conservative":
            st.write("•  Fixed Deposit: **80%** (Primary safety)")
            st.write("•  Gold: **20%** (Inflation protection)")
        elif risk_tolerance == "Moderate":
            st.write("•  Fixed Deposit: **60%** (Stability base)")
            st.write("•  Gold: **40%** (Growth potential)")
        else:  # Aggressive
            st.write("•  Gold: **60%** (Growth focus)")
            st.write("•  Fixed Deposit: **40%** (Safety anchor)")

        st.write("**Key Points:**")
        for point in profile['key_points']:
            st.write(f"• {point}")

        st.caption(" Consider your time horizon and risk comfort when choosing allocation")

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
            'EXCELLENT': '',
            'GOOD': '',
            'FAIR': '🟠',
            'POOR': '',
            'UNAVAILABLE': '⚫'
        }

        icon = color_map.get(quality, '')
        st.caption(f"{icon} Data Quality: {quality} | Confidence: {confidence}")

        if quality in ['POOR', 'UNAVAILABLE']:
            st.warning(" Limited data available for this asset. Projections may be unreliable.")

    # Asset-specific conservative messaging
    strategy_name = scenario.strategy_name.upper()
    if 'GOLD' in strategy_name:
        st.info("""
        **Gold Investment Reality Check:**

         **Historical Performance (Gullak data 1950-2025):**
        • Last 3 years: 24.4% per year (exceptional period)
        • Last 5 years: 13.5% per year
        • Last 10 years: 13.6% per year
        • Long-term (20 years): 14.35% per year

         **High Risk:** Gold can vary from -20% to +40% in any single year
         **Recent Surge:** 2025 saw major price jump - may not continue

        **Example:** ₹10L invested might become ₹7L to ₹14L after 1 year
        **Note:** Recent returns are unusually high - don't expect 24% every year!
        """)
    elif 'FIXED' in strategy_name or '5%' in strategy_name:
        st.success("""
        **Fixed Deposit Reality Check:**

        **Guaranteed Return:** Exactly 5.0% per year, every year
        **No Risk:** Your money is 100% safe
        **Predictable:** You know exactly how much you'll get
         **Requirement:** Money must be locked in (can't withdraw early)

        **Example:** ₹10L becomes exactly ₹11.6L after 3 years (guaranteed)
        """)

    # Show any validation warnings
    for warning in warnings:
        st.error(f" {warning}")
        st.info(" This may indicate a calculation error or unrealistic market data.")

    # Show validation warnings from conversion details
    if 'validation_warnings' in scenario.conversion_details:
        validation_warnings = scenario.conversion_details['validation_warnings']
        for warning in validation_warnings:
            st.error(f" Validation: {warning}")
            st.info(" Please verify this calculation - results may be unrealistic.")


def render_investment_warnings():
    """Render investment risk warnings."""
    with st.expander(" Important Investment Disclaimers"):
        st.warning("""
        **Investment Risk Warnings:**

        • **Market Risk**: All investments carry risk of loss. Past performance does not guarantee future results.
        • **Volatility**: Asset prices fluctuate. Values shown are estimates based on historical data.
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
    """Create simple ROI comparison chart showing final values.

    Args:
        scenarios: List of SavingsScenario objects

    Returns:
        Plotly figure
    """
    if not scenarios:
        return go.Figure()

    # Prepare data - show final investment values (what parents care about)
    strategy_names = [s.strategy_name.split(' (')[0] for s in scenarios]  # Remove CAGR
    final_values = [s.conversion_details.get('final_pot_inr', 0) for s in scenarios]
    colors = ['#2E8B57', '#4169E1', '#FFD700', '#8B0000'][:len(scenarios)]  # Professional colors

    # Create bar chart with clear labels
    fig = go.Figure(data=[
        go.Bar(
            x=strategy_names,
            y=final_values,
            marker_color=colors,
            text=[f"₹{x/100000:.1f}L" for x in final_values],  # Show in lakhs
            textposition='outside',
            textfont=dict(size=12, color='black'),
            hovertemplate='<b>%{x}</b><br>' +
                         'Final Value: ₹%{y:,.0f}<br>' +
                         '<extra></extra>'
        )
    ])

    fig.update_layout(
        title="Final Investment Values Comparison",
        xaxis_title="Investment Strategy",
        yaxis_title="Final Portfolio Value (₹ Lakhs)",
        height=500,
        showlegend=False,
        plot_bgcolor='white',
        font=dict(size=12),
        margin=dict(t=60, b=80, l=80, r=40)
    )

    # Format axes using update_layout (correct method)
    fig.update_layout(
        yaxis=dict(
            tickformat='.1s',
            title_font=dict(size=14),
            tickfont=dict(size=11)
        ),
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=11)
        )
    )

    return fig