import streamlit as st
import sys
from pathlib import Path
from streamlit_scroll_navigation import scroll_navbar

# Import core modules
sys.path.append(str(Path(__file__).parent))
from core.theme import configure_page
from core.state import get_state
from core.ui_components import (
    professional_page_header, professional_kpi_card, format_inr,
    success_alert, info_alert
)
from core.sections import (
    course_selector_section, projections_section,
    strategy_selector_section, summary_section
)
from core.data_sources import data_sources_section

# Configure page
configure_page("UK Education Savings Calculator", "", "wide")

# Initialize state
state = get_state()

# Scroll navigation setup
anchor_ids = ["home", "course-selector", "projections", "strategy", "summary"]
anchor_labels = ["Overview", "Course Selection", "Projections", "Strategy", "Summary"]

# Create sidebar scroll navigation
with st.sidebar:
    selected_section = scroll_navbar(
        anchor_ids,
        anchor_labels=anchor_labels,
        disable_scroll=True,  # Remove animations for instant navigation
        override_styles={
            "nav": {"background": "rgba(0,0,0,0)"},
            "ul": {"background": "rgba(0,0,0,0)", "backdrop-filter": "none"},
            "li": {"background": "rgba(0,0,0,0)"},
            "a": {"background": "rgba(0,0,0,0)"}
        }
    )

# Professional page header
professional_page_header(
    title="UK Education Savings Calculator",
    subtitle="Professional financial planning for UK university education"
)

# Overview section (Home)
st.header("Overview", anchor="home")
with st.container(border=True):
    st.markdown("### How This Calculator Helps")
    st.markdown("""
    This calculator helps Indian families plan and optimize their UK university education savings through:
    - **Course selection** and fee analysis from Oxford, Cambridge, and LSE
    - **Exchange rate projections** based on historical Bank of England data
    - **Strategy comparison** between pay-as-you-go vs early conversion approaches
    - **Comprehensive summaries** with actionable financial insights
    """)

# Current Status
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
    info_alert("**Get Started**: Complete each section below to analyze your education savings strategy.")

st.divider()

# Section 1: Course Selector
st.header("Course Selection", anchor="course-selector")
course_selector_section()

st.divider()

# Section 2: Projections
st.header("Projections", anchor="projections")
projections_section()

st.divider()

# Section 3: Strategy
st.header("Strategy", anchor="strategy")
strategy_selector_section()

st.divider()

# Section 4: Summary
st.header("Summary", anchor="summary")
summary_section()

st.divider()

# Additional Tools Section
with st.container(border=True):
    st.markdown("### Additional Tools")
    st.markdown("**Investment Strategies Analysis** - Explore investment-based savings approaches:")
    st.code("streamlit run gui/investment_strategies_app.py", language="bash")
    st.caption("Run this command in your terminal for detailed investment analysis")

st.divider()

# Data Sources Section with downloadable files
data_sources_section()