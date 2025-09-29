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
from gui.roi_components import (
    render_roi_sidebar, render_roi_scenarios_summary,
    render_roi_scenario_cards, render_investment_warnings,
    create_simple_roi_chart
)
from gui.components.second_child import (
    SecondChildAdapter, render_second_child_sidebar,
    render_second_child_results
)
from gui.components.style_injector import inject_styles



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


# Legacy chart functions kept for backward compatibility
# Mobile-optimized versions are used in main app








def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Education Savings Calculator",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply professional styling
    inject_styles()

    st.title("UK Education Savings Calculator")
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
        st.sidebar.header(" Selection Parameters")

        # University selection
        universities = data_processor.get_universities()
        selected_university = st.sidebar.selectbox(
            " Select University",
            universities,
            help="Choose from Oxford, Cambridge, or LSE"
        )

        # Course selection
        if selected_university:
            courses = data_processor.get_courses(selected_university)
            selected_course = st.sidebar.selectbox(
                " Select Course/Programme",
                courses,
                help="Choose a specific programme"
            )

            # Date selections
            st.sidebar.header(" Timeline")

            conversion_year = st.sidebar.selectbox(
                " Savings Start Year",
                [2023, 2024, 2025, 2026],
                index=0,
                help="When to convert INR to GBP"
            )

            education_year = st.sidebar.selectbox(
                " Education Start Year",
                list(range(2026, 2031)),
                index=0,
                help="When your child starts university"
            )

            if education_year <= conversion_year:
                st.sidebar.error(" Education start year must be after conversion year")
                return

            # ROI Analysis Configuration
            roi_config = render_roi_sidebar(
                conversion_year,
                education_year,
                selected_university,
                selected_course,
                calculator
            )

            # 2nd Child Savers Configuration
            st.session_state.selected_university = selected_university
            st.session_state.selected_programme = selected_course
            second_child_config = render_second_child_sidebar(calculator, data_processor)

            # Calculate scenarios first for sidebar display
            scenarios = calculator.compare_all_strategies(
                selected_university, selected_course, conversion_year, education_year
            )

            # Calculate ROI scenarios if enabled
            roi_scenarios = []
            roi_error_message = None
            if roi_config.get("enabled", False):
                try:
                    roi_scenarios = calculator.calculate_all_roi_scenarios(
                        selected_university,
                        selected_course,
                        conversion_year,
                        education_year,
                        roi_config["investment_amount"],
                        roi_config["selected_strategies"]
                    )
                except Exception as e:
                    roi_error_message = str(e)
                    st.sidebar.error(f" Investment analysis unavailable: {roi_error_message}")
                    st.sidebar.info(" This usually means market data files are missing. Investment analysis requires actual historical market data.")
                    roi_scenarios = []

            # Calculate 2nd Child scenarios if enabled
            second_child_scenario = None
            second_child_metrics = None
            second_child_error = None
            if second_child_config.get("enabled", False):
                try:
                    adapter = SecondChildAdapter(calculator, data_processor)
                    second_child_scenario, second_child_metrics = adapter.calculate_savings_for_inr_amount(
                        inr_amount=second_child_config["amount_inr"],
                        conversion_year=second_child_config["conversion_year"],
                        education_year=second_child_config["education_year"],
                        university=second_child_config.get("university"),
                        programme=second_child_config.get("programme")
                    )
                except Exception as e:
                    second_child_error = str(e)
                    st.sidebar.error(f" 2nd Child calculation error: {second_child_error}")

            # Sidebar scenarios
            st.sidebar.header(" Saving Scenarios")
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
            st.sidebar.header(" Data Sources & Terms")
            transparency = data_processor.get_course_info(selected_university, selected_course).get('transparency')

            if transparency:
                with st.sidebar.expander(" How Numbers Are Calculated", expanded=False):
                    explanation = get_calculation_explanation(transparency)
                    st.markdown(explanation)

                with st.sidebar.expander("✅ Parent Verification Guide", expanded=False):
                    st.markdown(transparency.source_verification)

                with st.sidebar.expander(" Exchange Rate Verification", expanded=False):
                    st.markdown("** Exchange Rate Verification:**")
                    st.markdown("- Visit Bank of England website (www.bankofengland.co.uk)")
                    st.markdown("- Search for 'Exchange rates' → Historical data")
                    st.markdown("- Alternative: xe.com for current/historical rates")

            # Main content area (full width)
            # Remove two-column layout for cleaner interface
            st.header(f" Analysis: {selected_university} - {selected_course}")

            # Get course information
            course_info = data_processor.get_course_info(selected_university, selected_course)

            # Display course metrics with transparency
            st.subheader(" Course Fee Analysis")

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
                    f" **Best Strategy**: {best_scenario.strategy_name} "
                    f"saves **{format_inr(best_scenario.savings_vs_payg_inr)}** "
                    f"({format_percentage(best_scenario.savings_percentage)})"
                )

            # Get projection details for charts
            projections_data = calculator.get_projection_details(
                selected_university, selected_course, education_year
            )

            # Charts section
            st.subheader(" Projections")

            # Create charts using working repository's exact functions
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                # Fee projection chart with historical/projected distinction
                fee_chart = create_fee_projection_chart(projections_data)
                st.plotly_chart(fee_chart, use_container_width=True)

            with chart_col2:
                # FX projection chart with historical/projected distinction
                fx_chart = create_fx_projection_chart(projections_data)
                st.plotly_chart(fx_chart, use_container_width=True)

            # Strategy comparison
            st.subheader(" Strategy Comparison")
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
            st.subheader(" Exchange Rate Forecast")

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
            st.caption(" FX projections based on 8-year historical CAGR (4.18% annual depreciation, 2017-2025). Actual rates may vary due to economic conditions.")

            # ROI Analysis Section
            if roi_config.get("enabled", False) and roi_scenarios:
                st.markdown("---")
                st.header(" Investment Strategy Analysis")

                # ROI scenarios summary
                render_roi_scenarios_summary(roi_scenarios, roi_config["investment_amount"])

                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs([" Overview", " Detailed Analysis", " Risk Information"])

                with tab1:
                    # Simple comparison chart
                    if roi_scenarios:
                        chart = create_simple_roi_chart(roi_scenarios)
                        st.plotly_chart(chart, use_container_width=True)

                        # Simple comparison between currency strategies and savings strategies
                        st.subheader(" Should You Invest or Just Convert Currency?")

                        # Get the best traditional strategy (usually early conversion)
                        best_traditional = min(scenarios, key=lambda x: x.total_cost_inr)
                        # Get the best investment strategy
                        best_roi = max(roi_scenarios, key=lambda x: x.savings_vs_payg_inr)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.info("**🏦 Currency Exchange Only**")
                            st.write(f"Strategy: {best_traditional.strategy_name}")
                            st.write(f"You save: {format_inr(best_traditional.savings_vs_payg_inr)}")
                            st.write("✅ Simple and safe")

                        with col2:
                            st.success("** Investment + Currency Exchange**")
                            strategy_name = best_roi.strategy_name.split(' (')[0].replace('Investment', '').strip()
                            if 'GOLD' in strategy_name.upper():
                                display_name = "Gold Investment"
                            elif 'FIXED' in strategy_name.upper():
                                display_name = "Fixed Deposit"
                            else:
                                display_name = strategy_name
                            st.write(f"Strategy: {display_name}")
                            st.write(f"You save: {format_inr(best_roi.savings_vs_payg_inr)}")
                            difference = best_roi.savings_vs_payg_inr - best_traditional.savings_vs_payg_inr
                            if difference > 0:
                                st.write(f"💚 Extra benefit: {format_inr(difference)}")
                            else:
                                st.write(" May not be better than simple conversion")

                        st.caption(" Compare both options and choose what makes you comfortable")

                with tab2:
                    # Detailed scenario cards
                    render_roi_scenario_cards(roi_scenarios)

                with tab3:
                    # Investment warnings and risk information
                    render_investment_warnings()

                    # Risk tolerance summary
                    risk_tolerance = roi_config.get("risk_tolerance", "Moderate")
                    st.info(f" Your risk tolerance: **{risk_tolerance}**. This affects strategy recommendations and expected returns.")

            elif roi_config.get("enabled", False):
                st.markdown("---")
                st.header(" Investment Strategy Analysis")

                if roi_error_message:
                    st.error(f" Investment analysis unavailable: {roi_error_message}")

                    with st.expander(" Why is investment analysis unavailable?"):
                        st.markdown("""
                        **Common reasons for investment analysis errors:**

                        • **Missing market data files**: Investment calculations require historical price data for Gold investments
                        • **Invalid date range**: Requested investment period may not have available data
                        • **Asset data quality issues**: Market data files may be corrupted or have missing values

                        **To resolve this:**
                        1. Ensure market data CSV files are present in the `data/markets/` directory
                        2. Verify the files have the required columns (`month`, `price_close`)
                        3. Check that data covers your selected investment period
                        4. Try using different assets or shorter investment periods

                        **Note**: Traditional currency conversion strategies are still available and don't require market data.
                        """)
                else:
                    st.warning(" Investment analysis enabled but no scenarios calculated. Please check your selections.")

            # 2nd Child Savers Results
            if second_child_config.get("enabled", False):
                if second_child_scenario and second_child_metrics and not second_child_error:
                    render_second_child_results(second_child_scenario, second_child_metrics, second_child_config)
                elif second_child_error:
                    st.markdown("---")
                    st.subheader(" 2nd Child Savings Analysis")
                    st.error(f" Unable to calculate 2nd child savings: {second_child_error}")
                    st.info(" Please check your inputs and ensure all required data is available.")
                else:
                    st.markdown("---")
                    st.subheader(" 2nd Child Savings Analysis")
                    st.warning(" 2nd Child analysis enabled but no calculations available. Please check your configuration.")


    except Exception as e:
        st.error(f" Error loading data: {str(e)}")
        st.info("Make sure you're running this from the project root directory with access to the data files.")


if __name__ == "__main__":
    main()