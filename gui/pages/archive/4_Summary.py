import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Import core modules with correct path
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from gui.core.theme import configure_page
from gui.core.state import get_state
from gui.core.ui_components import (
    professional_page_header, professional_kpi_card, professional_dataframe,
    navigation_buttons, format_inr, format_percentage, format_exchange_rate
)
from gui.core.compute import project_fx_rate

configure_page("Summary")

# Professional page header with breadcrumb
professional_page_header(
    title="Analysis Summary",
    subtitle="Complete overview of your education savings strategy",
    breadcrumb_steps=["Home", "Course Selection", "Projections", "Strategy", "Summary"],
    current_step=4
)

state = get_state()

if not state.university or not state.course or not state.scenarios:
    st.warning("Please complete the previous steps to see your summary.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Course Selector", use_container_width=True):
            st.switch_page("pages/1_Course_Selector.py")
    with col2:
        if st.button("Projections", use_container_width=True):
            st.switch_page("pages/2_Pay_As_You_Go_Projections.py")
    with col3:
        if st.button("Strategy Selector", use_container_width=True):
            st.switch_page("pages/3_Saver_Selector.py")
else:
    try:
        # Get best scenario
        best_scenario = state.scenarios[0] if state.scenarios else None
        selected_strategy = getattr(state, 'selected_strategy', 'Pay As You Go')

        if best_scenario:
            st.subheader("Your Education Savings Plan")

            # Main overview KPIs
            st.subheader("Your Education Plan")
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    professional_kpi_card(
                        "University",
                        state.university,
                        help_text="Selected institution"
                    )
                with col2:
                    professional_kpi_card(
                        "Course",
                        state.course,
                        help_text="Selected programme"
                    )
                with col3:
                    professional_kpi_card(
                        "Education Start",
                        str(state.education_year),
                        help_text="When studies begin"
                    )
                with col4:
                    professional_kpi_card(
                        "Chosen Strategy",
                        selected_strategy,
                        help_text="Your selected approach"
                    )

            st.divider()

            # Financial summary
            st.subheader("Financial Summary")

            # Financial summary KPIs
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    professional_kpi_card(
                        "Best Strategy",
                        best_scenario.strategy_name,
                        help_text="Most cost-effective approach",
                        highlight=True
                    )
                with col2:
                    professional_kpi_card(
                        "Total Cost",
                        format_inr(best_scenario.total_cost_inr),
                        help_text="Total education cost in Indian Rupees"
                    )
                with col3:
                    professional_kpi_card(
                        "Total Savings",
                        format_inr(best_scenario.savings_vs_payg_inr) if best_scenario.savings_vs_payg_inr > 0 else "Baseline",
                        help_text="Amount saved compared to pay-as-you-go"
                    )
                with col4:
                    professional_kpi_card(
                        "Savings Percentage",
                        format_percentage(best_scenario.savings_percentage) if best_scenario.savings_percentage > 0 else "0%",
                        help_text="Percentage reduction in cost"
                    )

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

            fx_df = pd.DataFrame(fx_data)
            professional_dataframe(fx_df)
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

            # Professional navigation
            navigation_buttons(
                back_page="pages/3_Saver_Selector.py",
                back_label="← Back to Strategy"
            )

            # Start over option
            st.divider()
            if st.button("Start New Analysis", use_container_width=True):
                # Clear session state and go to home
                for key in list(st.session_state.keys()):
                    if key.startswith('app_state') or key in ['university', 'course', 'scenarios']:
                        del st.session_state[key]
                st.switch_page("gui/education_savings_app.py")

        else:
            st.error("No strategy analysis available. Please complete the strategy selection first.")

    except Exception as e:
        st.error(f"Error generating summary: {e}")
        st.info("Please ensure all previous steps are completed correctly.")