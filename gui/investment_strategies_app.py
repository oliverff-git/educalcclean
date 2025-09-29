import streamlit as st
import sys
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

from core.theme import configure_page
from roi_components import render_risk_tolerance_guide, create_simple_roi_chart
from fee_calculator import EducationSavingsCalculator
from data_processor import EducationDataProcessor

configure_page("Investment Strategies", "", "wide")

st.title("Investment Strategies")
st.markdown("**Explore investment-based approaches to education savings**")

# Initialize processors
@st.cache_resource
def init_data():
    processor = EducationDataProcessor()
    processor.load_data()
    calculator = EducationSavingsCalculator(processor)
    return processor, calculator

try:
    data_processor, calculator = init_data()

    # Create tabs for different strategies
    tab1, tab2 = st.tabs(["5% Saver Account", "Gold Investment"])

    with tab1:
        st.header("Monthly Save (5% Fixed Returns)")

        st.markdown("""
        **Fixed Deposit Strategy:**
        - **Guaranteed Return:** Exactly 5.0% per year, every year
        - **No Risk:** Your money is 100% safe
        - **Predictable:** You know exactly how much you'll get
        - **Requirement:** Money must be locked in (cannot withdraw early)
        """)

        # Simple calculator for 5% saver
        col1, col2, col3 = st.columns(3)

        with col1:
            initial_amount = st.number_input("Initial Investment (₹)", min_value=100000, max_value=50000000, value=1000000, step=100000)

        with col2:
            years = st.number_input("Investment Period (years)", min_value=1, max_value=10, value=3)

        with col3:
            annual_rate = st.slider("Annual Return (%)", min_value=3.0, max_value=8.0, value=5.0, step=0.1)

        # Calculate returns
        final_amount = initial_amount * ((1 + annual_rate/100) ** years)
        total_returns = final_amount - initial_amount

        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Amount", f"₹{final_amount/100000:.1f}L")
        with col2:
            st.metric("Total Returns", f"₹{total_returns/100000:.1f}L")
        with col3:
            st.metric("Annual Growth", f"{annual_rate:.1f}%")

        st.success(f"**Example:** ₹{initial_amount/100000:.0f}L becomes exactly ₹{final_amount/100000:.1f}L after {years} years (guaranteed)")

    with tab2:
        st.header("Gold Investment Strategy")

        st.markdown("""
        **Gold Investment Approach:**
        - **Hedge against inflation:** Gold typically maintains purchasing power
        - **Currency protection:** Gold prices in INR often rise with USD/GBP strength
        - **Liquidity:** Can be sold when needed for education expenses
        - **Volatility:** Returns can vary significantly year to year
        """)

        # Simple gold calculator
        col1, col2, col3 = st.columns(3)

        with col1:
            gold_investment = st.number_input("Gold Investment (₹)", min_value=100000, max_value=50000000, value=1000000, step=100000)

        with col2:
            gold_years = st.number_input("Holding Period (years)", min_value=1, max_value=10, value=3)

        with col3:
            gold_cagr = st.slider("Expected Gold CAGR (%)", min_value=5.0, max_value=15.0, value=8.0, step=0.5)

        # Calculate gold returns
        gold_final = gold_investment * ((1 + gold_cagr/100) ** gold_years)
        gold_returns = gold_final - gold_investment

        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Projected Value", f"₹{gold_final/100000:.1f}L")
        with col2:
            st.metric("Projected Gains", f"₹{gold_returns/100000:.1f}L")
        with col3:
            st.metric("Annual Growth", f"{gold_cagr:.1f}%")

        st.warning(f"**Risk Note:** Gold returns can be volatile. Historical CAGR ranges from 6-12% in INR terms.")

    st.divider()

    # Risk warnings
    st.subheader("Investment Considerations")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **Conservative Approach:**
        - Fixed deposits provide guaranteed returns
        - Suitable for risk-averse families
        - Returns may not beat inflation long-term
        """)

    with col2:
        st.warning("""
        **Investment Risks:**
        - Gold/equity returns are not guaranteed
        - Values can decrease in short term
        - Consider your risk tolerance carefully
        """)

    st.markdown("---")
    st.caption("**Note:** NIFTY/FTSE references removed as requested. This app focuses on simpler, more accessible investment strategies.")

except Exception as e:
    st.error(f"Error loading investment data: {e}")
    st.info("Please ensure the main education calculator data files are available.")