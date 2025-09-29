"""
Converted page sections for the single-page scrollable app.
Each function represents a section that was previously a separate page.
"""

import streamlit as st
import pandas as pd
from .state import get_state, update_state, init_processors
from .ui_components import (
    professional_page_header, professional_kpi_card, kpi_row,
    professional_dataframe, info_alert, success_alert, format_gbp, format_inr,
    format_percentage, format_exchange_rate
)
from .compute import (
    get_universities, get_courses, get_course_info, get_payg_projection,
    create_fee_projection_chart, create_fx_projection_chart, compare_strategies,
    create_strategy_comparison_chart, project_fx_rate
)


def course_selector_section():
    """Course Selector section - previously page 1"""

    # Section header
    st.subheader("1. Course Selection")
    st.caption("Select your target university and academic programme")

    # Initialize processors
    try:
        data_processor, calculator = init_processors()
        state = get_state()

        # University selection
        universities = get_universities()
        university = st.selectbox(
            "Select University",
            universities,
            index=universities.index(state.university) if state.university in universities else 0,
            help="Choose from Oxford, Cambridge, or LSE",
            key="university_selector"
        )

        # Course selection
        if university:
            courses = get_courses(university)
            course = st.selectbox(
                "Select Course/Programme",
                courses,
                index=courses.index(state.course) if state.course in courses else 0,
                help="Choose a specific programme",
                key="course_selector"
            )

            if course:
                # Get course information
                course_info = get_course_info(university, course)
                latest_year = course_info.get('latest_actual_year', 'Unknown')
                latest_fee = course_info.get('latest_fee', 0)
                three_year_total = latest_fee * 3

                st.markdown("**Course Fee Information**")

                # Display current fees using professional KPI cards
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        professional_kpi_card(
                            f"Annual Fee ({latest_year})",
                            format_gbp(latest_fee),
                            help_text="Current annual tuition fee from official course page"
                        )

                    with col2:
                        professional_kpi_card(
                            f"3-Year Total ({latest_year})",
                            format_gbp(three_year_total),
                            help_text="Total cost for standard 3-year programme"
                        )

                    with col3:
                        professional_kpi_card(
                            "Annual Growth Rate",
                            f"{course_info.get('cagr_pct', 0):.1f}%",
                            help_text="Historical fee compound annual growth rate"
                        )

                    with col4:
                        professional_kpi_card(
                            "Data Coverage",
                            f"{course_info.get('data_points', 0)} years",
                            help_text="Years of historical data available for analysis"
                        )

                # Data quality information
                transparency = course_info.get('transparency')
                if transparency:
                    st.info(f"**Data Quality:** {transparency.data_quality.value.title()} | **Confidence:** {transparency.confidence_level.value.title()}")

                # Update state
                update_state(university=university, course=course)

    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check that the data files are available and try refreshing the page.")


def projections_section():
    """Pay-As-You-Go Projections section - previously page 2"""

    st.subheader("2. Fee & Exchange Rate Projections")
    st.caption("Fee and exchange rate forecasts for your education timeline")

    state = get_state()

    if not state.university or not state.course:
        st.warning("Please select a university and course in the Course Selection section above.")
        return

    try:
        data_processor, calculator = init_processors()

        # Timeline inputs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            start_year = st.number_input(
                "Savings Start Year",
                min_value=2015,
                max_value=2035,
                value=state.conversion_year,
                step=1,
                key="savings_start_year"
            )

        with col2:
            edu_start = st.number_input(
                "Education Start Year",
                min_value=start_year,
                max_value=start_year+10,
                value=state.education_year,
                step=1,
                key="education_start_year"
            )

        with col3:
            duration = st.selectbox(
                "Programme Length (years)",
                [1,2,3,4],
                index=2,
                key="programme_duration"
            )

        with col4:
            course_info = data_processor.get_course_info(state.university, state.course)
            default_cagr = course_info.get('cagr_pct', 5.0)
            cagr = st.slider(
                "Fee CAGR (%)",
                0.0, 15.0,
                default_cagr,
                0.1,
                key="fee_cagr"
            )

        # Input validation with helpful feedback
        if edu_start <= start_year:
            st.error("⚠️ **Invalid Timeline**: Education start year must be after savings start year")
            st.info("💡 **Suggestion**: Set education start year to at least " + str(start_year + 1))
        elif (edu_start - start_year) > 10:
            st.warning("⚠️ **Long Timeline**: Very long savings period detected (" + str(edu_start - start_year) + " years)")
            st.info("💡 **Note**: Projections become less reliable over extended periods")
        else:
            # Get projection data with loading indicator
            with st.spinner("Generating projections..."):
                projections_data = get_payg_projection(state.university, state.course, start_year, edu_start, duration)

            if projections_data:
                # Calculate key metrics
                projected_annual_fee = data_processor.project_fee(state.university, state.course, edu_start)
                projected_total = projected_annual_fee * duration
                latest_fee = course_info.get('latest_fee', 0)
                current_total = latest_fee * duration

                # Display KPIs using professional cards
                st.markdown("**Programme Cost Analysis**")
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        professional_kpi_card(
                            f"{duration}-Year Total (Current)",
                            format_gbp(current_total),
                            help_text=f"Based on {course_info.get('latest_actual_year', 'current')} fees"
                        )
                    with col2:
                        professional_kpi_card(
                            f"Projected Total ({edu_start})",
                            format_gbp(projected_total),
                            help_text="Projected using historical CAGR"
                        )
                    with col3:
                        professional_kpi_card(
                            "Annual Growth Rate",
                            f"{cagr:.1f}%",
                            help_text="Course fee compound annual growth rate"
                        )
                    with col4:
                        professional_kpi_card(
                            "Data Coverage",
                            f"{course_info.get('data_points', 0)} years",
                            help_text="Years of historical data available"
                        )

                # Charts
                st.markdown("**Projections**")
                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    fee_chart = create_fee_projection_chart(projections_data)
                    st.plotly_chart(fee_chart, use_container_width=True)

                with chart_col2:
                    fx_chart = create_fx_projection_chart(projections_data)
                    st.plotly_chart(fx_chart, use_container_width=True)

                # Exchange rate forecast table
                st.markdown("**Exchange Rate Forecast**")
                fx_data = []
                for year in range(start_year, edu_start + duration):
                    rate = project_fx_rate(year)
                    status = "Historical" if year <= 2025 else "Projected"
                    fx_data.append({
                        'Year': year,
                        'Rate (₹/£)': f"₹{rate:.2f}",
                        'Status': status
                    })

                st.dataframe(pd.DataFrame(fx_data), use_container_width=True)
                st.caption("FX projections based on 8-year historical CAGR (4.18% annual depreciation, 2017-2025). Actual rates may vary due to economic conditions.")

                # Update state
                update_state(
                    conversion_year=start_year,
                    education_year=edu_start,
                    projections_data=projections_data
                )

            else:
                st.error("Unable to generate projections. Please check your selections.")

    except Exception as e:
        st.error(f"Error generating projections: {e}")
        st.info("Please ensure all data is properly loaded and try again.")


def strategy_selector_section():
    """Strategy Selector section - previously page 3"""

    st.subheader("3. Strategy Comparison")
    st.caption("Compare different savings strategies to optimize your costs")

    state = get_state()

    if not state.university or not state.course:
        st.warning("Please complete the Course Selection section above first.")
        return
    elif not state.conversion_year or not state.education_year:
        st.warning("Please complete the Projections section above first.")
        return

    try:
        data_processor, calculator = init_processors()

        # Strategy selection
        st.markdown("**Choose Your Savings Strategy**")

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
            help="Choose between paying at education time vs converting currency early",
            key="strategy_selection"
        )

        # Get strategy comparison with loading indicator
        with st.spinner("Analyzing savings strategies..."):
            scenarios = compare_strategies(
                state.university,
                state.course,
                state.conversion_year,
                state.education_year
            )

        if scenarios:
            # Display comparison chart
            st.markdown("**Strategy Comparison**")
            comparison_chart = create_strategy_comparison_chart(scenarios)
            if comparison_chart:
                st.plotly_chart(comparison_chart, use_container_width=True)

            # Find best scenario
            best_scenario = scenarios[0]  # Scenarios are sorted by savings

            # Display best strategy using professional KPI
            if best_scenario.savings_vs_payg_inr > 0:
                st.markdown("**Recommended Strategy**")
                with st.container(border=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        professional_kpi_card(
                            "Best Strategy",
                            best_scenario.strategy_name,
                            help_text="Most cost-effective approach",
                            highlight=True
                        )
                    with col2:
                        professional_kpi_card(
                            "Total Savings",
                            format_inr(best_scenario.savings_vs_payg_inr),
                            help_text="Amount saved vs pay-as-you-go"
                        )
                    with col3:
                        professional_kpi_card(
                            "Savings Percentage",
                            format_percentage(best_scenario.savings_percentage),
                            help_text="Percentage reduction in total cost"
                        )

            # Strategy comparison table
            st.markdown("**Detailed Comparison**")

            comparison_data = []
            for scenario in scenarios:
                comparison_data.append({
                    'Strategy': scenario.strategy_name,
                    'Total Cost (INR)': format_inr(scenario.total_cost_inr),
                    'Savings vs PAYG': format_inr(scenario.savings_vs_payg_inr) if scenario.savings_vs_payg_inr > 0 else "Baseline",
                    'Savings %': format_percentage(scenario.savings_percentage) if scenario.savings_percentage > 0 else "0%",
                    'Exchange Rate': f"₹{scenario.exchange_rate_used:.2f}/£" if scenario.exchange_rate_used > 0 else "Variable"
                })

            # Use professional dataframe with proper column configuration
            comparison_df = pd.DataFrame(comparison_data)
            professional_dataframe(comparison_df)

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

        else:
            st.error("Unable to calculate strategy comparison. Please check your inputs.")

    except Exception as e:
        st.error(f"Error calculating strategies: {e}")
        st.info("Please ensure all previous steps are completed and try again.")


def summary_section():
    """Summary section - previously page 4"""

    st.subheader("4. Analysis Summary")
    st.caption("Complete overview of your education savings strategy")

    state = get_state()

    if not state.university or not state.course or not state.scenarios:
        st.warning("Please complete all previous sections to see your summary.")
        return

    try:
        # Get best scenario
        best_scenario = state.scenarios[0] if state.scenarios else None
        selected_strategy = getattr(state, 'selected_strategy', 'Pay As You Go')

        if best_scenario:
            st.markdown("**Your Education Savings Plan**")

            # Main overview KPIs
            st.markdown("**Your Education Plan**")
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
            st.markdown("**Financial Summary**")

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
            st.markdown("**Key Insights**")

            if best_scenario.savings_vs_payg_inr > 0:
                st.success(
                    f"**Optimal Strategy**: {best_scenario.strategy_name} can save you "
                    f"**{format_inr(best_scenario.savings_vs_payg_inr)}** "
                    f"({format_percentage(best_scenario.savings_percentage)}) compared to paying as you go."
                )
            else:
                st.info("**Pay-as-you-go** appears to be the most cost-effective strategy for your timeline.")

            # Exchange rate forecast
            st.markdown("**Exchange Rate Forecast**")

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
            st.markdown("**Recommended Next Steps**")

            recommendations = [
                "**Verify university fees** - Check official university websites for the most current fee information",
                "**Monitor exchange rates** - Keep track of GBP/INR exchange rates leading up to your conversion",
                "**Consider risk tolerance** - Early conversion reduces exchange rate risk but requires upfront capital",
                "**Review regularly** - Update your analysis as new fee data becomes available"
            ]

            for rec in recommendations:
                st.markdown(f"• {rec}")

            # Data transparency
            st.markdown("**Data Sources**")
            st.info(
                "**Projections based on**: Historical university fee data (2020-2026) and Bank of England exchange rates (2017-2025). "
                "All calculations use compound annual growth rates (CAGR) derived from official sources."
            )

            # Start over option
            st.divider()
            if st.button("Start New Analysis", use_container_width=True):
                # Clear session state and reload page
                for key in list(st.session_state.keys()):
                    if key.startswith('app_state') or key in ['university', 'course', 'scenarios']:
                        del st.session_state[key]
                st.rerun()

        else:
            st.error("No strategy analysis available. Please complete the strategy selection first.")

    except Exception as e:
        st.error(f"Error generating summary: {e}")
        st.info("Please ensure all previous steps are completed correctly.")