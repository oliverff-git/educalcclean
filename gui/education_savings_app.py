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

# Import mobile responsive components
from gui.mobile import (
    get_mobile_detector, get_responsive_manager, apply_responsive_styling,
    configure_streamlit_for_device
)
from gui.components import MobileComponentRenderer, MobileMetric
from gui.charts import MobileChartRenderer


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
    # Initialize mobile detection first
    mobile_detector = get_mobile_detector()
    device_type = mobile_detector.get_device_type()

    # Configure Streamlit for detected device
    responsive_config = configure_streamlit_for_device(device_type)
    st.set_page_config(**responsive_config)

    # Apply responsive styling
    apply_responsive_styling(device_type)

    # Initialize mobile components
    mobile_renderer = MobileComponentRenderer(device_type)
    chart_renderer = MobileChartRenderer(device_type)

    # Add mobile-specific styles
    mobile_renderer.add_mobile_styles()

    # Apply responsive styling (which includes mobile/tablet CSS)
    apply_responsive_styling(device_type)

    # Fix white space at top of page - APPLIED LAST with highest specificity
    st.markdown("""
    <style>
    /* CRITICAL: White space fix - highest priority, applied after all responsive styles */

    /* Target all possible container variations with maximum specificity */
    .stApp .main .block-container,
    .stApp section.main .block-container,
    .main .block-container,
    section.main .block-container,
    .block-container,
    div.block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* Remove any top spacing from the app container */
    .stApp {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }

    /* Remove header/toolbar spacing */
    .stApp > header,
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 0px !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Target the main content area with highest specificity */
    .stApp section.main,
    section.main,
    .main {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* Ensure first content element has minimal top spacing */
    .main > div:first-child,
    .block-container > div:first-child {
        margin-top: 0rem !important;
        padding-top: 0.25rem !important;
    }

    /* Override any framework defaults */
    * {
        margin-top: 0 !important;
    }

    /* Specific override for the title element */
    h1:first-child {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

        # Add mobile navigation if needed
        if device_type == 'mobile':
            current_section = mobile_renderer.render_mobile_navigation()
        else:
            current_section = "Analysis"

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

            # Scenarios display - mobile vs desktop
            if device_type == 'mobile':
                # For mobile, show scenarios in main area with expandable section
                def render_mobile_scenarios():
                    mobile_renderer.render_scenario_cards(scenarios)
                mobile_renderer.render_expandable_section(
                    "Saving Scenarios", render_mobile_scenarios, expanded=True
                )
            else:
                # Desktop/tablet: keep in sidebar
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

            metrics = [
                MobileMetric(
                    label=f"3-Year Programme Total ({latest_year})",
                    value=format_gbp(three_year_total),
                    help_text=f"Total cost for 3-year programme (UK fees fixed at enrollment from {latest_year})"
                ),
                MobileMetric(
                    label=f"Projected 3-Year Total ({education_year})",
                    value=format_gbp(projected_three_year_total),
                    help_text=f"Total programme cost projected using {transparency.calculation_method if transparency else 'CAGR method'}"
                ),
                MobileMetric(
                    label=cagr_label,
                    value=format_percentage(course_info['cagr_pct']),
                    help_text=cagr_help
                ),
                MobileMetric(
                    label="Data Points",
                    value=f"{course_info['data_points']} years",
                    help_text=f"Historical data: {', '.join(map(str, transparency.actual_data_years)) if transparency else 'Unknown'}"
                )
            ]

            mobile_renderer.render_metrics_section(metrics)

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

            # Mobile-optimized charts section
            def render_charts():
                # Fee projection chart
                fee_chart = chart_renderer.create_mobile_fee_projection_chart(projections_data)
                config = chart_renderer.get_chart_config()
                st.plotly_chart(fee_chart, use_container_width=True, config=config)

                # FX projection chart
                fx_chart = chart_renderer.create_mobile_fx_projection_chart(projections_data)
                st.plotly_chart(fx_chart, use_container_width=True, config=config)

            if device_type == 'mobile':
                # Stack charts vertically on mobile
                mobile_renderer.render_expandable_section(
                    "Projections", render_charts, expanded=True
                )
            else:
                # Side-by-side on larger screens
                st.subheader("📊 Projections")
                if device_type == 'desktop':
                    chart_col1, chart_col2 = st.columns(2)
                    with chart_col1:
                        fee_chart = chart_renderer.create_mobile_fee_projection_chart(projections_data)
                        config = chart_renderer.get_chart_config()
                        st.plotly_chart(fee_chart, use_container_width=True, config=config)
                    with chart_col2:
                        fx_chart = chart_renderer.create_mobile_fx_projection_chart(projections_data)
                        st.plotly_chart(fx_chart, use_container_width=True, config=config)
                else:
                    # Tablet: stack but with normal sections
                    render_charts()

            # Mobile-optimized savings comparison
            def render_savings_chart():
                savings_chart = chart_renderer.create_mobile_savings_comparison_chart(scenarios)
                if savings_chart:
                    config = chart_renderer.get_chart_config()
                    st.plotly_chart(savings_chart, use_container_width=True, config=config)

            if device_type == 'mobile':
                mobile_renderer.render_expandable_section(
                    "Strategy Comparison", render_savings_chart, expanded=False
                )
            else:
                st.subheader("💰 Strategy Comparison")
                render_savings_chart()

            # Mobile-optimized exchange rate table
            def render_fx_table():
                fx_data = []
                for year in range(conversion_year, education_year + 3):
                    rate = data_processor.project_fx_rate(year)
                    status = "Historical" if year <= 2025 else "Projected"
                    fx_data.append({
                        'Year': year,
                        'Rate (₹/£)': f"₹{rate:.2f}",
                        'Status': status
                    })

                mobile_renderer.render_data_table(
                    pd.DataFrame(fx_data),
                    max_rows=5 if device_type == 'mobile' else None
                )

                st.caption("📊 FX projections based on 8-year historical CAGR (4.18% annual depreciation, 2017-2025). Actual rates may vary due to economic conditions.")

            if device_type == 'mobile':
                mobile_renderer.render_expandable_section(
                    "Exchange Rate Forecast", render_fx_table, expanded=False
                )
            else:
                st.subheader("📈 Exchange Rate Forecast")
                render_fx_table()


    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("Make sure you're running this from the project root directory with access to the data files.")


if __name__ == "__main__":
    main()