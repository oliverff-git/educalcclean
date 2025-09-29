import streamlit as st
import sys
from pathlib import Path

# Import core modules
sys.path.append(str(Path(__file__).parent))
from core.theme import configure_page
from core.state import get_state

# Configure page
configure_page("UK Education Savings Calculator", "", "wide")

# Initialize state
state = get_state()

st.title("UK Education Savings Calculator")
st.markdown("**Professional financial planning for UK university education**")

st.markdown("""
This calculator helps Indian families plan and optimize their UK university education savings through:
- **Course selection** and fee analysis
- **Exchange rate projections** based on historical data
- **Strategy comparison** between pay-as-you-go vs early conversion
- **Comprehensive summaries** with actionable insights
""")

st.divider()

st.subheader("Get Started")
st.markdown("Follow these steps to analyze your education savings strategy:")

# Navigation links
col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/1_Course_Selector.py", label="**1. Course Selector**", icon="🎓")
    st.caption("Select your university and programme")

    st.page_link("pages/3_Saver_Selector.py", label="**3. Strategy Selector**", icon="💡")
    st.caption("Compare savings strategies")

with col2:
    st.page_link("pages/2_Pay_As_You_Go_Projections.py", label="**2. Projections**", icon="📈")
    st.caption("View fee and exchange rate forecasts")

    st.page_link("pages/4_Summary.py", label="**4. Summary**", icon="📋")
    st.caption("Review your complete analysis")

st.divider()

# Current status
if state.university and state.course:
    st.success(f"**Current Selection**: {state.university} - {state.course}")

    if state.scenarios:
        best_scenario = state.scenarios[0]
        if best_scenario.savings_vs_payg_inr > 0:
            savings_lakh = best_scenario.savings_vs_payg_inr / 100000
            st.info(f"**Best Strategy**: {best_scenario.strategy_name} saves ₹{savings_lakh:.1f}L ({best_scenario.savings_percentage:.1f}%)")
else:
    st.info("**Start by selecting your university and course** in Step 1 above.")

st.divider()

st.subheader("Additional Tools")
st.markdown("**Investment Strategies** - Explore investment-based approaches:")
st.markdown("Run: `streamlit run gui/investment_strategies_app.py` for detailed investment analysis")

st.markdown("---")
st.caption("Data sources: Official university websites, Bank of England exchange rates. Projections based on historical CAGR analysis.")