"""
Education Savings Calculator - Interactive Streamlit Application

This application helps Indian families calculate potential savings from early
currency conversion strategies for UK university education.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from gui.data_processor import EducationDataProcessor
from gui.fee_calculator import EducationSavingsCalculator
from gui.data_quality_utils import (
    get_data_quality_badge, get_confidence_indicator,
    get_projection_disclaimer, get_calculation_explanation,
    DataQuality, ConfidenceLevel
)



def format_inr(amount):
    """Format INR amounts in lakhs/crores."""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


def format_gbp(amount):
    """Format GBP amounts."""
    return f"£{amount:,.0f}"


def format_percentage(pct):
    """Format percentage."""
    return f"{pct:.1f}%"


# Legacy chart functions kept for backward compatibility
# Mobile-optimized versions are used in main app








def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Education Savings Calculator",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎓 UK Education Savings Calculator")
    st.markdown("**Calculate potential savings from early INR→GBP conversion strategies**")

    # Initialize data processor
    @st.cache_data
    def load_data():
        processor = EducationDataProcessor()
        processor.load_data()
        return processor

    try:
        with st.spinner("Loading education data..."):
            data_processor = load_data()

        calculator = EducationSavingsCalculator(data_processor)


        # Sidebar for inputs
        st.sidebar.header("📋 Selection Parameters")

        # University selection
        universities = data_processor.get_universities()
        selected_university = st.sidebar.selectbox(
            "🏫 Select University",
            universities,
            help="Choose from Oxford, Cambridge, or LSE"
        )

        # Course selection
        if selected_university:
            courses = data_processor.get_courses(selected_university)
            selected_course = st.sidebar.selectbox(
                "📚 Select Course/Programme",
                courses,
                help="Choose a specific programme"
            )

            # Date selections
            st.sidebar.header("📅 Timeline")

            conversion_year = st.sidebar.selectbox(
                "💰 Savings Start Year",
                [2023, 2024, 2025, 2026],
                index=0,
                help="When to convert INR to GBP"
            )

            education_year = st.sidebar.selectbox(
                "🎓 Education Start Year",
                list(range(2026, 2031)),
                index=0,
                help="When your child starts university"
            )

            if education_year <= conversion_year:
                st.sidebar.error("⚠️ Education start year must be after conversion year")
                return

            # Calculate scenarios first for sidebar display
            scenarios = calculator.compare_all_strategies(
                selected_university, selected_course, conversion_year, education_year
            )

            # Sidebar scenarios
            st.sidebar.header("💼 Saving Scenarios")
            for i, scenario in enumerate(scenarios):
                with st.sidebar.expander(f"{i+1}. {scenario.strategy_name}", expanded=(i==0)):
                    st.metric("Total Cost", format_inr(scenario.total_cost_inr))

                    if scenario.savings_vs_payg_inr > 0:
                        st.metric(
                            "Savings",
                            format_inr(scenario.savings_vs_payg_inr),
                            delta=format_percentage(scenario.savings_percentage)
                        )
                    else:
                        st.info("Baseline comparison")

                    if scenario.exchange_rate_used > 0:
                        st.metric("Exchange Rate", f"₹{scenario.exchange_rate_used:.2f}/£")

                    # Additional breakdown
                    breakdown = scenario.breakdown
                    if 'uk_earnings' in breakdown and breakdown['uk_earnings']['total_interest_gbp'] > 0:
                        uk_earnings = breakdown['uk_earnings']
                        st.caption(f"UK Interest: £{uk_earnings['total_interest_gbp']:.0f} ({uk_earnings['avg_interest_rate']*100:.1f}% avg BoE rate)")

            # Data Sources & Terms in Sidebar
            st.sidebar.header("📄 Data Sources & Terms")
            transparency = data_processor.get_course_info(selected_university, selected_course).get('transparency')

            if transparency:
                with st.sidebar.expander("📊 How Numbers Are Calculated", expanded=False):
                    explanation = get_calculation_explanation(transparency)
                    st.markdown(explanation)

                with st.sidebar.expander("✅ Parent Verification Guide", expanded=False):
                    st.markdown(transparency.source_verification)

                with st.sidebar.expander("📈 Exchange Rate Verification", expanded=False):
                    st.markdown("**📈 Exchange Rate Verification:**")
                    st.markdown("- Visit Bank of England website (www.bankofengland.co.uk)")
                    st.markdown("- Search for 'Exchange rates' → Historical data")
                    st.markdown("- Alternative: xe.com for current/historical rates")

            # Main content area (full width)
            # Remove two-column layout for cleaner interface
            st.header(f"📊 Analysis: {selected_university} - {selected_course}")

            # Get course information
            course_info = data_processor.get_course_info(selected_university, selected_course)

            # Display course metrics with transparency
            st.subheader("📈 Course Fee Analysis")

            # Get transparency info
            transparency = course_info.get('transparency')

            # Data quality badge
            if transparency:
                badge_emoji, badge_color = get_data_quality_badge(transparency.data_quality)
                confidence_emoji, confidence_desc = get_confidence_indicator(transparency.confidence_level)

                st.markdown(f"""
                <div style="background-color: {badge_color}20; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                    {badge_emoji} <strong>Data Quality:</strong> {transparency.data_quality.value.title()}
                    &nbsp;&nbsp;{confidence_emoji} <strong>Confidence:</strong> {transparency.confidence_level.value.title()}
                </div>
                """, unsafe_allow_html=True)

            # Create mobile-optimized metrics
            latest_year = course_info.get('latest_actual_year', 'Unknown')
            three_year_total = course_info['latest_fee'] * 3
            projected_annual_fee = data_processor.project_fee(selected_university, selected_course, education_year)
            projected_three_year_total = projected_annual_fee * 3
            cagr_label = "Course CAGR" if not course_info.get('is_using_university_average', False) else "University Avg CAGR"
            cagr_help = ("Calculated from course-specific data" if not course_info.get('is_using_university_average', False)
                        else f"Using {selected_university} average due to limited course data")

            # Display metrics using standard Streamlit columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    f"3-Year Programme Total ({latest_year})",
                    format_gbp(three_year_total),
                    help=f"Total cost for 3-year programme (UK fees fixed at enrollment from {latest_year})"
                )

            with col2:
                st.metric(
                    f"Projected 3-Year Total ({education_year})",
                    format_gbp(projected_three_year_total),
                    help=f"Total programme cost projected using {transparency.calculation_method if transparency else 'CAGR method'}"
                )

            with col3:
                st.metric(
                    cagr_label,
                    format_percentage(course_info['cagr_pct']),
                    help=cagr_help
                )

            with col4:
                st.metric(
                    "Data Points",
                    f"{course_info['data_points']} years",
                    help=f"Historical data: {', '.join(map(str, transparency.actual_data_years)) if transparency else 'Unknown'}"
                )

            # Add transparency disclaimer
            if transparency:
                disclaimer = get_projection_disclaimer(transparency)
                if transparency.confidence_level == ConfidenceLevel.LOW:
                    st.warning(disclaimer)
                else:
                    st.info(disclaimer)

            # Display best strategy (scenarios already calculated for sidebar)
            if scenarios:
                best_scenario = scenarios[0]
                st.success(
                    f"💡 **Best Strategy**: {best_scenario.strategy_name} "
                    f"saves **{format_inr(best_scenario.savings_vs_payg_inr)}** "
                    f"({format_percentage(best_scenario.savings_percentage)})"
                )

            # Get projection details for charts
            projections_data = calculator.get_projection_details(
                selected_university, selected_course, education_year
            )

            # Charts section
            st.subheader("📊 Projections")

            # Create charts using correct data structure
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                # Fee projection chart
                if projections_data and 'fee_projections' in projections_data:
                    fee_projections = projections_data['fee_projections']
                    if fee_projections:
                        years = sorted(fee_projections.keys())
                        fees = [fee_projections[year] for year in years]

                        fee_fig = go.Figure()
                        fee_fig.add_trace(go.Scatter(
                            x=years,
                            y=fees,
                            mode='lines+markers',
                            name='Projected Fees',
                            line=dict(color='#1f77b4')
                        ))
                        fee_fig.update_layout(
                            title="Fee Projections",
                            xaxis_title="Year",
                            yaxis_title="Annual Fee (GBP)",
                            height=400
                        )
                        st.plotly_chart(fee_fig, use_container_width=True)

            with chart_col2:
                # FX projection chart
                if projections_data and 'fx_projections' in projections_data:
                    fx_projections = projections_data['fx_projections']
                    if fx_projections:
                        years = sorted(fx_projections.keys())
                        rates = [fx_projections[year] for year in years]

                        fx_fig = go.Figure()
                        fx_fig.add_trace(go.Scatter(
                            x=years,
                            y=rates,
                            mode='lines+markers',
                            name='Exchange Rate',
                            line=dict(color='#ff7f0e')
                        ))
                        fx_fig.update_layout(
                            title="Exchange Rate Projections",
                            xaxis_title="Year",
                            yaxis_title="INR per GBP",
                            height=400
                        )
                        st.plotly_chart(fx_fig, use_container_width=True)

            # Strategy comparison
            st.subheader("💰 Strategy Comparison")
            if scenarios:
                # Create simple bar chart
                strategy_names = [scenario.strategy_name for scenario in scenarios]
                total_costs = [scenario.total_cost_inr for scenario in scenarios]

                savings_fig = go.Figure(data=[go.Bar(
                    x=strategy_names,
                    y=total_costs,
                    marker_color=['#2E8B57' if i == 0 else '#4682B4' for i in range(len(scenarios))]
                )])

                savings_fig.update_layout(
                    title="Total Cost Comparison (INR)",
                    xaxis_title="Strategy",
                    yaxis_title="Total Cost (INR)",
                    height=400
                )
                st.plotly_chart(savings_fig, use_container_width=True)

            # Exchange rate forecast
            st.subheader("📈 Exchange Rate Forecast")

            fx_data = []
            for year in range(conversion_year, education_year + 3):
                rate = data_processor.project_fx_rate(year)
                status = "Historical" if year <= 2025 else "Projected"
                fx_data.append({
                    'Year': year,
                    'Rate (₹/£)': f"₹{rate:.2f}",
                    'Status': status
                })

            st.dataframe(pd.DataFrame(fx_data), use_container_width=True)
            st.caption("📊 FX projections based on 8-year historical CAGR (4.18% annual depreciation, 2017-2025). Actual rates may vary due to economic conditions.")


    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("Make sure you're running this from the project root directory with access to the data files.")


if __name__ == "__main__":
    main()