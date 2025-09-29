import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Import core modules
sys.path.append(str(Path(__file__).parent.parent))
from core.theme import configure_page
from core.state import get_state
from core.ui import kpi_row, format_inr, format_percentage
from core.compute import project_fx_rate

configure_page("Summary")
st.header("Summary")

state = get_state()

if not state.university or not state.course or not state.scenarios:
    st.warning("Please complete the previous steps to see your summary.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Course Selector"):
            st.switch_page("pages/1_Course_Selector.py")
    with col2:
        if st.button("Projections"):
            st.switch_page("pages/2_Pay_As_You_Go_Projections.py")
    with col3:
        if st.button("Strategy Selector"):
            st.switch_page("pages/3_Saver_Selector.py")
else:
    try:
        # Get best scenario
        best_scenario = state.scenarios[0] if state.scenarios else None
        selected_strategy = getattr(state, 'selected_strategy', 'Pay As You Go')

        if best_scenario:
            st.subheader("Your Education Savings Plan")

            # Main KPIs
            kpi_row([
                ("University", state.university, "Selected institution"),
                ("Course", state.course, "Selected programme"),
                ("Education Start", str(state.education_year), "When studies begin"),
                ("Strategy", selected_strategy, "Your chosen approach"),
            ])

            st.divider()

            # Financial summary
            st.subheader("Financial Summary")

            kpi_row([
                ("Best Strategy", best_scenario.strategy_name, "Most cost-effective approach"),
                ("Total Cost (INR)", format_inr(best_scenario.total_cost_inr), "Total education cost in Indian Rupees"),
                ("Savings vs PAYG", format_inr(best_scenario.savings_vs_payg_inr) if best_scenario.savings_vs_payg_inr > 0 else "Baseline", "Amount saved compared to pay-as-you-go"),
                ("Savings Percentage", format_percentage(best_scenario.savings_percentage) if best_scenario.savings_percentage > 0 else "0%", "Percentage saved"),
            ])

            # Key insights
            st.subheader("Key Insights")

            if best_scenario.savings_vs_payg_inr > 0:
                st.success(
                    f"**Optimal Strategy**: {best_scenario.strategy_name} can save you "
                    f"**{format_inr(best_scenario.savings_vs_payg_inr)}** "
                    f"({format_percentage(best_scenario.savings_percentage)}) compared to paying as you go."
                )
            else:
                st.info("**Pay-as-you-go** appears to be the most cost-effective strategy for your timeline.")

            # Exchange rate forecast
            st.subheader("Exchange Rate Forecast")

            fx_data = []
            for year in range(state.conversion_year, state.education_year + 3):
                rate = project_fx_rate(year)
                status = "Historical" if year <= 2025 else "Projected"
                fx_data.append({
                    'Year': year,
                    'Rate (₹/£)': f"₹{rate:.2f}",
                    'Status': status,
                    'Impact': 'Lower rates favor early conversion' if rate < 100 else 'Higher rates favor late payment'
                })

            st.dataframe(pd.DataFrame(fx_data), use_container_width=True)
            st.caption("Exchange rate projections based on historical trends. Actual rates may vary due to economic conditions.")

            # Next steps
            st.subheader("Recommended Next Steps")

            recommendations = [
                "**Verify university fees** - Check official university websites for the most current fee information",
                "**Monitor exchange rates** - Keep track of GBP/INR exchange rates leading up to your conversion",
                "**Consider risk tolerance** - Early conversion reduces exchange rate risk but requires upfront capital",
                "**Review regularly** - Update your analysis as new fee data becomes available"
            ]

            for rec in recommendations:
                st.markdown(f"• {rec}")

            # Data transparency
            st.subheader("Data Sources")
            st.info(
                "**Projections based on**: Historical university fee data (2020-2026) and Bank of England exchange rates (2017-2025). "
                "All calculations use compound annual growth rates (CAGR) derived from official sources."
            )

        else:
            st.error("No strategy analysis available. Please complete the strategy selection first.")

    except Exception as e:
        st.error(f"Error generating summary: {e}")
        st.info("Please ensure all previous steps are completed correctly.")