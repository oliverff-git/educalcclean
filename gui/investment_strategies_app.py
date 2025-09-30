"""
Investment Strategies App - Professional Single-Page Application with Smooth Scrolling

This is the main investment strategies application that integrates all components
created by Agents 1 and 2, providing a smooth scrolling experience with real-time
dynamic updates.

Architecture:
- Agent 1: UI components (components.py, state.py, charts.py)
- Agent 2: Data integration (calculations.py)
- Agent 3: Main app integration with smooth scrolling

Features:
- Smooth scrolling navigation between sections
- Real-time calculations without page reload
- Professional fintech design
- Default state: Oxford PPE 2025-2027, ₹10L investment
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add paths for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

# Core imports
from core.theme import configure_page

# Agent 1 imports - UI Components
from investment.components import (
    investment_header,
    course_selector_section,
    investment_options_section,
    investment_kpi_card,
    show_investment_projections,
    investment_summary_row,
    strategy_comparison_table,
    investment_action_buttons
)

from investment.state import (
    get_investment_state,
    update_investment_state,
    reset_investment_state,
    init_investment_defaults,
    sync_state_from_ui,
    calculate_investment_projections,
    get_investment_summary,
    is_calculation_valid,
    format_investment_amount
)

from investment.charts import (
    display_investment_charts,
    display_risk_analysis,
    create_strategy_comparison_chart,
    create_investment_growth_chart
)

# Agent 2 imports - Data Integration
from investment.calculations import (
    InvestmentCalculator,
    create_investment_calculator,
    calculate_investment_roi
)

# Data sources for CSV downloads
from core.data_sources import data_sources_section

# Smooth scrolling navigation
try:
    from streamlit_scroll_navigation import scroll_navbar
    SCROLL_NAVIGATION_AVAILABLE = True
except ImportError:
    SCROLL_NAVIGATION_AVAILABLE = False
    st.warning("Smooth scrolling navigation not available. Install streamlit-scroll-navigation for enhanced experience.")


# ===== PAGE CONFIGURATION =====

def setup_page():
    """Setup page configuration with professional theme"""
    configure_page(
        title="Investment Strategies Calculator",
        icon="📊",
        layout="wide"
    )


# ===== SMOOTH SCROLLING NAVIGATION =====

def setup_scroll_navigation():
    """Setup smooth scrolling navigation if available"""
    if not SCROLL_NAVIGATION_AVAILABLE:
        return None

    anchor_ids = ["overview", "selection", "investment", "results", "risk"]
    anchor_labels = ["Overview", "Course & Timeline", "Investment Strategy", "Results & Charts", "Risk Analysis"]

    # Create sidebar scroll navigation with proper API
    with st.sidebar:
        return scroll_navbar(
            anchor_ids,
            anchor_labels=anchor_labels,
            disable_scroll=True,  # Remove animations for instant navigation
            override_styles={
                "nav": {"background": "#1E40AF"},
                "ul": {"background": "#1E40AF", "backdrop-filter": "none"},
                "li": {"background": "rgba(0,0,0,0)"},
                "a": {"color": "#FFFFFF", "background": "rgba(0,0,0,0)"},
                "a:hover": {"background": "rgba(245,158,11,0.2)"}
            }
        )


# ===== SECTION IMPLEMENTATIONS =====

def section_overview():
    """Section 1: Hero/Overview"""
    st.markdown('<div id="overview"></div>', unsafe_allow_html=True)

    # Professional header
    investment_header()

    # Key metrics dashboard
    st.markdown("### Investment Dashboard")

    state = get_investment_state()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        investment_kpi_card(
            "Default Investment",
            format_investment_amount(state.investment_amount)
        )

    with col2:
        investment_kpi_card(
            "Selected Strategy",
            state.selected_strategy.title()
        )

    with col3:
        investment_kpi_card(
            "Expected Return",
            f"{state.expected_return*100:.1f}%"
        )

    with col4:
        years_to_goal = state.start_year - datetime.now().year
        investment_kpi_card(
            "Years to Goal",
            f"{max(0, years_to_goal)} years"
        )

    # Quick overview cards
    st.markdown("### Strategy Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **🥇 Gold Investment Strategy**
        - Historical return: 10-12% annually
        - Hedge against inflation
        - Medium-high risk profile
        - Physical asset backing
        """)

    with col2:
        st.success("""
        **🏦 5% Fixed Saver Strategy**
        - Guaranteed return: 5% annually
        - Low risk investment
        - Capital protection
        - Stable growth pattern
        """)


def section_course_selection():
    """Section 2: Course & Timeline Selection"""
    st.markdown('<div id="selection"></div>', unsafe_allow_html=True)

    st.markdown("## Course & Timeline Selection")
    st.markdown("Select your target university, course, and timeline for education funding.")

    # Get course selection from components
    course_details = course_selector_section()

    # Update state with selections
    sync_state_from_ui()

    # Display selection summary
    state = get_investment_state()
    summary = get_investment_summary()

    if summary['projections_ready']:
        st.success(f"✅ Configuration ready: {summary['course']} starting {summary['years_to_goal']} years from now")
    else:
        st.warning("⚠️ Please ensure course start year is in the future for valid projections")


def section_investment_strategy():
    """Section 3: Investment Strategy Options"""
    st.markdown('<div id="investment"></div>', unsafe_allow_html=True)

    st.markdown("## Investment Strategy")
    st.markdown("Choose your investment approach and configure funding amount.")

    # Get investment options from components
    investment_details = investment_options_section()

    # Update state with selections
    sync_state_from_ui()

    # Display current configuration summary
    state = get_investment_state()

    st.markdown("### Current Configuration")

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            investment_kpi_card(
                "Investment Amount",
                format_investment_amount(state.investment_amount)
            )

        with col2:
            investment_kpi_card(
                "Strategy",
                state.selected_strategy.title(),
                f"{state.risk_level} Risk"
            )

        with col3:
            investment_kpi_card(
                "Expected Return",
                f"{state.expected_return*100:.1f}%",
                "per year"
            )


def section_results_and_charts():
    """Section 4: Results & Charts"""
    st.markdown('<div id="results"></div>', unsafe_allow_html=True)

    st.markdown("## Results & Projections")

    state = get_investment_state()

    # Action buttons for calculations
    actions = investment_action_buttons()

    if actions['reset']:
        reset_investment_state()
        st.rerun()

    if actions['calculate'] or not state.projections_calculated:
        if is_calculation_valid():
            with st.spinner("Calculating investment projections..."):
                calculate_investment_projections()
                st.success("Projections calculated successfully!")
                st.rerun()
        else:
            st.error("Please configure valid course and investment settings before calculating.")

    # Display results if available
    if state.projections_calculated and is_calculation_valid():

        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            investment_kpi_card(
                "Projected Value",
                format_investment_amount(state.final_amount),
                f"+{state.total_return_percentage:.1f}%"
            )

        with col2:
            investment_kpi_card(
                "Total Growth",
                format_investment_amount(state.total_growth)
            )

        with col3:
            years_to_goal = state.start_year - datetime.now().year
            investment_kpi_card(
                "CAGR",
                f"{state.expected_return*100:.1f}%",
                f"over {years_to_goal} years"
            )

        # Charts and visualizations
        st.markdown("### Investment Growth Analysis")

        if state.projection_data:
            display_investment_charts(state.projection_data)

        # Detailed projections table
        st.markdown("### Year-by-Year Projections")

        if state.projection_data:
            import pandas as pd

            # Create DataFrame for display
            df_data = []
            for item in state.projection_data:
                df_data.append({
                    "Year": item['year'],
                    "Investment Value": item['amount'],
                    "Annual Growth": item['annual_growth'],
                    "Return %": f"{item['return_percentage']:.1f}%" if item['return_percentage'] > 0 else "Initial"
                })

            df = pd.DataFrame(df_data)

            st.dataframe(
                df,
                column_config={
                    "Year": st.column_config.NumberColumn("Year", format="%d"),
                    "Investment Value": st.column_config.NumberColumn("Investment Value", format="₹%d"),
                    "Annual Growth": st.column_config.NumberColumn("Annual Growth", format="₹%d"),
                    "Return %": "Annual Return"
                },
                hide_index=True,
                use_container_width=True
            )

    # Strategy comparison
    if actions['compare'] or state.show_comparison:
        st.markdown("### Strategy Comparison")
        strategy_comparison_table()

        # Visual comparison chart
        years_to_goal = max(1, state.start_year - datetime.now().year)
        comparison_chart = create_strategy_comparison_chart(
            state.investment_amount,
            years_to_goal
        )
        st.plotly_chart(comparison_chart, use_container_width=True)


def section_risk_analysis():
    """Section 5: Risk Information"""
    st.markdown('<div id="risk"></div>', unsafe_allow_html=True)

    st.markdown("## Risk Analysis & Information")

    # Risk analysis charts
    display_risk_analysis()

    # Risk education
    st.markdown("### Investment Risk Guidelines")

    col1, col2 = st.columns(2)

    with col1:
        st.warning("""
        **⚠️ Important Risk Considerations**

        - **Gold Investment**: Returns can be volatile year-to-year
        - **Market Risk**: Past performance doesn't guarantee future results
        - **Currency Risk**: UK education costs are in GBP, subject to exchange rate fluctuations
        - **Timing Risk**: Market conditions at education start date may impact final value
        """)

    with col2:
        st.info("""
        **💡 Risk Management Tips**

        - **Diversification**: Consider splitting between strategies
        - **Time Horizon**: Longer investment periods typically reduce risk
        - **Regular Review**: Monitor and adjust strategy as needed
        - **Professional Advice**: Consult financial advisors for personalized guidance
        """)

    # Disclaimers
    st.markdown("### Important Disclaimers")

    st.caption("""
    **Investment Disclaimer**: This calculator provides estimates based on historical data and assumptions.
    Actual returns may vary significantly. All investments carry risk of loss. This is not financial advice.
    Consult qualified financial professionals before making investment decisions.

    **Education Cost Disclaimer**: UK university fees and living costs may change. Exchange rates fluctuate.
    Additional costs (visa, travel, etc.) not included in projections.
    """)


def section_data_sources():
    """Section 6: Data Sources & Verification"""
    st.markdown('<div id="data"></div>', unsafe_allow_html=True)

    st.markdown("## Data Sources & Verification")
    st.markdown("**For complete transparency, download the raw data files used in calculations:**")

    # Call the data sources section
    data_sources_section()


# ===== MAIN APPLICATION =====

def main():
    """Main application function"""

    # Setup page configuration
    setup_page()

    # Initialize state with defaults
    init_investment_defaults()

    # Setup smooth scrolling navigation
    selected_section = setup_scroll_navigation()

    # Main content container
    with st.container():

        # Section 1: Overview
        section_overview()
        st.divider()

        # Section 2: Course Selection
        section_course_selection()
        st.divider()

        # Section 3: Investment Strategy
        section_investment_strategy()
        st.divider()

        # Section 4: Results & Charts
        section_results_and_charts()
        st.divider()

        # Section 5: Risk Analysis
        section_risk_analysis()
        st.divider()

        # Section 6: Data Sources
        section_data_sources()

    # Footer
    st.markdown("---")
    st.caption("Investment Strategies Calculator - Professional Education Funding Analysis")
    st.caption("Built with Streamlit • Data from UK Universities • Investment projections are estimates")


# ===== APP ENTRY POINT =====

if __name__ == "__main__":
    main()