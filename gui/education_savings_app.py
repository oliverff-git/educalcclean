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


def create_fee_projection_chart(projections_data):
    """Create chart showing fee projections over time."""
    course_info = projections_data['course_info']
    fee_projections = projections_data['fee_projections']

    # Prepare data for chart
    years = list(fee_projections.keys())
    fees = list(fee_projections.values())

    # Historical vs projected
    historical_years = [y for y in years if y <= 2025]
    projected_years = [y for y in years if y > 2025]

    fig = go.Figure()

    # Historical data
    if historical_years:
        historical_fees = [fee_projections[y] for y in historical_years]
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_fees,
            mode='lines+markers',
            name='Historical',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))

    # Projected data
    if projected_years:
        # Connect last historical to first projected
        connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
        connect_fees = [fee_projections[y] for y in connect_years]

        fig.add_trace(go.Scatter(
            x=connect_years,
            y=connect_fees,
            mode='lines+markers',
            name='Projected',
            line=dict(color='#ff7f0e', width=3, dash='dash'),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=f"{course_info['university']} - {course_info['programme']}<br>Fee Projections (CAGR: {course_info['cagr_pct']:.2f}%)",
        xaxis_title="Year",
        yaxis_title="Annual Fee (GBP)",
        height=400,
        hovermode='x unified'
    )

    fig.update_yaxes(tickformat='£,.0f')

    return fig


def create_fx_projection_chart(projections_data):
    """Create chart showing exchange rate projections."""
    fx_projections = projections_data['fx_projections']

    years = list(fx_projections.keys())
    rates = list(fx_projections.values())

    # Historical vs projected
    historical_years = [y for y in years if y <= 2025]
    projected_years = [y for y in years if y > 2025]

    fig = go.Figure()

    # Historical data
    if historical_years:
        historical_rates = [fx_projections[y] for y in historical_years]
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_rates,
            mode='lines+markers',
            name='Historical',
            line=dict(color='#2ca02c', width=3),
            marker=dict(size=8)
        ))

    # Projected data
    if projected_years:
        connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
        connect_rates = [fx_projections[y] for y in connect_years]

        fig.add_trace(go.Scatter(
            x=connect_years,
            y=connect_rates,
            mode='lines+markers',
            name='Projected',
            line=dict(color='#d62728', width=3, dash='dash'),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title="GBP/INR Exchange Rate Projections<br>(Historical CAGR: 4.18% - Conservative)",
        xaxis_title="Year",
        yaxis_title="INR per GBP",
        height=400,
        hovermode='x unified'
    )

    fig.update_yaxes(tickformat='₹,.0f')

    return fig


def create_savings_comparison_chart(scenarios):
    """Create bar chart comparing savings across strategies."""
    if not scenarios:
        return None

    # Prepare data
    strategy_names = [s.strategy_name for s in scenarios]
    costs_inr = [s.total_cost_inr for s in scenarios]
    savings_inr = [s.savings_vs_payg_inr for s in scenarios]
    savings_pct = [s.savings_percentage for s in scenarios]

    # Create colors (green for savings, red for baseline)
    colors = ['#2ca02c' if s > 0 else '#d62728' for s in savings_inr]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Total Cost (INR)', 'Savings vs Pay-As-You-Go'),
        vertical_spacing=0.15
    )

    # Cost comparison
    fig.add_trace(
        go.Bar(
            x=strategy_names,
            y=costs_inr,
            name='Total Cost',
            marker_color='#1f77b4',
            text=[format_inr(c) for c in costs_inr],
            textposition='auto'
        ),
        row=1, col=1
    )

    # Savings comparison
    fig.add_trace(
        go.Bar(
            x=strategy_names,
            y=savings_inr,
            name='Savings',
            marker_color=colors,
            text=[f"{format_inr(s)}<br>({format_percentage(p)})" for s, p in zip(savings_inr, savings_pct)],
            textposition='auto'
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Savings Strategy Comparison"
    )

    # Update y-axis formats
    fig.update_yaxes(tickformat='₹,.0f', row=1, col=1)
    fig.update_yaxes(tickformat='₹,.0f', row=2, col=1)

    # Use shorter strategy names to avoid overlap
    fig.update_xaxes(
        tickangle=45,
        tickfont=dict(size=9),
        tickmode='array',
        tickvals=list(range(len(strategy_names))),
        ticktext=[name.replace(' from ', '<br>from ').replace(' in ', '<br>in ') for name in strategy_names]
    )
    fig.update_layout(
        margin=dict(b=120),  # Increased bottom margin
        height=700  # Taller chart to accommodate labels
    )

    return fig


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

            # Scenario Details in Sidebar
            st.sidebar.header("💼 Scenario Details")
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

            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                # Show 3-year programme total (UK fees are fixed at enrollment)
                latest_year = course_info.get('latest_actual_year', 'Unknown')
                three_year_total = course_info['latest_fee'] * 3
                st.metric(
                    f"3-Year Programme Total ({latest_year})",
                    format_gbp(three_year_total),
                    help=f"Total cost for 3-year programme (UK fees fixed at enrollment from {latest_year})"
                )

            with metric_col2:
                projected_annual_fee = data_processor.project_fee(selected_university, selected_course, education_year)
                projected_three_year_total = projected_annual_fee * 3
                st.metric(
                    f"Projected 3-Year Total ({education_year})",
                    format_gbp(projected_three_year_total),
                    help=f"Total programme cost projected using {transparency.calculation_method if transparency else 'CAGR method'}"
                )

            with metric_col3:
                # Show whether it's course-specific or university average
                cagr_label = "Course CAGR" if not course_info.get('is_using_university_average', False) else "University Avg CAGR"
                cagr_help = ("Calculated from course-specific data" if not course_info.get('is_using_university_average', False)
                            else f"Using {selected_university} average due to limited course data")

                st.metric(
                    cagr_label,
                    format_percentage(course_info['cagr_pct']),
                    help=cagr_help
                )

            with metric_col4:
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

            # Charts
            st.subheader("📊 Projections")

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                fee_chart = create_fee_projection_chart(projections_data)
                st.plotly_chart(fee_chart, use_container_width=True)

            with chart_col2:
                fx_chart = create_fx_projection_chart(projections_data)
                st.plotly_chart(fx_chart, use_container_width=True)

            # Savings comparison
            st.subheader("💰 Strategy Comparison")
            savings_chart = create_savings_comparison_chart(scenarios)
            if savings_chart:
                st.plotly_chart(savings_chart, use_container_width=True)

            # Exchange rate forecast table
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

            st.dataframe(pd.DataFrame(fx_data), hide_index=True)

            # Add FX disclaimer
            st.caption("📊 FX projections based on 8-year historical CAGR (4.18% annual depreciation, 2017-2025). Actual rates may vary due to economic conditions.")


    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("Make sure you're running this from the project root directory with access to the data files.")


if __name__ == "__main__":
    main()