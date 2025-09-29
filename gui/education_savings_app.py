import streamlit as st
import sys
from pathlib import Path

# Import core modules
sys.path.append(str(Path(__file__).parent))
from core.theme import configure_page
from core.state import get_state
from core.ui_components import (
    professional_page_header, professional_kpi_card, format_inr,
    success_alert, info_alert, navigation_buttons
)

# Configure page
configure_page("UK Education Savings Calculator", "", "wide")

# Initialize state
state = get_state()

# Professional page header
professional_page_header(
    title="UK Education Savings Calculator",
    subtitle="Professional financial planning for UK university education"
)

# Overview section
with st.container(border=True):
    st.markdown("### How This Calculator Helps")
    st.markdown("""
    This calculator helps Indian families plan and optimize their UK university education savings through:
    - **Course selection** and fee analysis from Oxford, Cambridge, and LSE
    - **Exchange rate projections** based on historical Bank of England data
    - **Strategy comparison** between pay-as-you-go vs early conversion approaches
    - **Comprehensive summaries** with actionable financial insights
    """)

st.divider()

st.subheader("Get Started")
st.markdown("Follow these steps to analyze your education savings strategy:")

# Navigation instructions
col1, col2 = st.columns(2)

with col1:
    st.markdown("**1. Course Selector**")
    st.caption("Select your university and programme")
    st.markdown("*Navigate to 'Course Selector' page using the sidebar*")

    st.markdown("**3. Strategy Selector**")
    st.caption("Compare savings strategies")
    st.markdown("*Navigate to 'Saver Selector' page using the sidebar*")

with col2:
    st.markdown("**2. Projections**")
    st.caption("View fee and exchange rate forecasts")
    st.markdown("*Navigate to 'Pay As You Go Projections' page using the sidebar*")

    st.markdown("**4. Summary**")
    st.caption("Review your complete analysis")
    st.markdown("*Navigate to 'Summary' page using the sidebar*")

st.divider()

# Current Status
st.subheader("Current Status")
if state.university and state.course:
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            professional_kpi_card("Selected University", state.university)
        with col2:
            professional_kpi_card("Selected Course", state.course)

        if hasattr(state, 'scenarios') and state.scenarios:
            best_scenario = state.scenarios[0]
            if best_scenario.savings_vs_payg_inr > 0:
                st.divider()
                col1, col2, col3 = st.columns(3)
                with col1:
                    professional_kpi_card(
                        "Best Strategy",
                        best_scenario.strategy_name,
                        help_text="Most cost-effective approach"
                    )
                with col2:
                    professional_kpi_card(
                        "Total Savings",
                        format_inr(best_scenario.savings_vs_payg_inr),
                        help_text="Savings vs pay-as-you-go"
                    )
                with col3:
                    professional_kpi_card(
                        "Savings Percentage",
                        f"{best_scenario.savings_percentage:.1f}%",
                        help_text="Percentage saved"
                    )
else:
    info_alert("**Get Started**: Select your university and course using the sidebar navigation to begin your analysis.")

st.divider()

# Additional Tools Section
with st.container(border=True):
    st.markdown("### Additional Tools")
    st.markdown("**Investment Strategies Analysis** - Explore investment-based savings approaches:")
    st.code("streamlit run gui/investment_strategies_app.py", language="bash")
    st.caption("Run this command in your terminal for detailed investment analysis")

st.divider()

# Data Sources Footer
st.caption("**Data Sources**: Official university websites (Oxford, Cambridge, LSE), Bank of England exchange rates. All projections based on historical CAGR analysis.")