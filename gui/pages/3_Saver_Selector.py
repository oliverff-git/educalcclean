import streamlit as st
import sys
from pathlib import Path

# Import core modules with correct path
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from gui.core.theme import configure_page
from gui.core.state import get_state, update_state, init_processors
from gui.core.ui import kpi_row, success_alert, format_inr, format_percentage
from gui.core.compute import compare_strategies, create_strategy_comparison_chart

configure_page("Saver Selector")
st.header("Saver Selector")

state = get_state()

if not state.university or not state.course:
    st.warning("Please select a university and course first, then set up projections.")
    if st.button("Go to Course Selector"):
        st.switch_page("pages/1_Course_Selector.py")
elif not state.conversion_year or not state.education_year:
    st.warning("Please set up your timeline and projections first.")
    if st.button("Go to Projections"):
        st.switch_page("pages/2_Pay_As_You_Go_Projections.py")
else:
    try:
        data_processor, calculator = init_processors()

        # Strategy selection
        st.subheader("Choose Your Savings Strategy")

        strategies = [
            "Pay As You Go",
            "Early Conversion (2023)",
            "Early Conversion (2024)",
            "Early Conversion (2025)"
        ]

        selected_strategy = st.radio(
            "Select Strategy",
            strategies,
            index=0,
            horizontal=True,
            help="Choose between paying at education time vs converting currency early"
        )

        # Get strategy comparison
        scenarios = compare_strategies(
            state.university,
            state.course,
            state.conversion_year,
            state.education_year
        )

        if scenarios:
            # Display comparison chart
            st.subheader("Strategy Comparison")
            comparison_chart = create_strategy_comparison_chart(scenarios)
            if comparison_chart:
                st.plotly_chart(comparison_chart, use_container_width=True, theme="streamlit")

            # Find best scenario
            best_scenario = scenarios[0]  # Scenarios are sorted by savings

            # Display best strategy
            if best_scenario.savings_vs_payg_inr > 0:
                success_alert(
                    f"**Best Strategy**: {best_scenario.strategy_name} "
                    f"saves **{format_inr(best_scenario.savings_vs_payg_inr)}** "
                    f"({format_percentage(best_scenario.savings_percentage)})"
                )

            # Strategy comparison table
            st.subheader("Detailed Comparison")

            comparison_data = []
            for scenario in scenarios:
                comparison_data.append({
                    'Strategy': scenario.strategy_name,
                    'Total Cost (INR)': format_inr(scenario.total_cost_inr),
                    'Savings vs PAYG': format_inr(scenario.savings_vs_payg_inr) if scenario.savings_vs_payg_inr > 0 else "Baseline",
                    'Savings %': format_percentage(scenario.savings_percentage) if scenario.savings_percentage > 0 else "0%",
                    'Exchange Rate': f"₹{scenario.exchange_rate_used:.2f}/£" if scenario.exchange_rate_used > 0 else "Variable"
                })

            st.dataframe(comparison_data, use_container_width=True)

            # Strategy details
            for i, scenario in enumerate(scenarios):
                with st.expander(f"{scenario.strategy_name} - Details", expanded=(i==0)):

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Cost", format_inr(scenario.total_cost_inr))
                    with col2:
                        if scenario.savings_vs_payg_inr > 0:
                            st.metric("Savings", format_inr(scenario.savings_vs_payg_inr),
                                     delta=format_percentage(scenario.savings_percentage))
                        else:
                            st.info("Baseline comparison")
                    with col3:
                        if scenario.exchange_rate_used > 0:
                            st.metric("Exchange Rate", f"₹{scenario.exchange_rate_used:.2f}/£")

                    # Additional breakdown if available
                    breakdown = scenario.breakdown
                    if 'uk_earnings' in breakdown and breakdown['uk_earnings']['total_interest_gbp'] > 0:
                        uk_earnings = breakdown['uk_earnings']
                        st.caption(f"UK Interest: £{uk_earnings['total_interest_gbp']:.0f} ({uk_earnings['avg_interest_rate']*100:.1f}% avg BoE rate)")

            # Update state with scenarios and selected strategy
            update_state(scenarios=scenarios, selected_strategy=selected_strategy)

            st.divider()

            # Navigation
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("← Back to Projections", use_container_width=True):
                    st.switch_page("pages/2_Pay_As_You_Go_Projections.py")
            with col3:
                if st.button("Next → Summary", use_container_width=True, type="primary"):
                    st.switch_page("pages/4_Summary.py")

        else:
            st.error("Unable to calculate strategy comparison. Please check your inputs.")

    except Exception as e:
        st.error(f"Error calculating strategies: {e}")
        st.info("Please ensure all previous steps are completed and try again.")