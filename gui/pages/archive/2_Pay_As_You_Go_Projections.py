import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Import core modules with correct path
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from gui.core.theme import configure_page
from gui.core.state import get_state, update_state, init_processors
from gui.core.ui_components import (
    professional_page_header, professional_kpi_card, kpi_row,
    navigation_buttons, professional_dataframe, format_gbp, format_inr, format_percentage
)
from gui.core.compute import get_payg_projection, create_fee_projection_chart, create_fx_projection_chart, project_fx_rate

configure_page("Pay-As-You-Go Projections")

# Professional page header with breadcrumb
professional_page_header(
    title="Pay-As-You-Go Projections",
    subtitle="Fee and exchange rate forecasts for your education timeline",
    breadcrumb_steps=["Home", "Course Selection", "Projections", "Strategy", "Summary"],
    current_step=2
)

state = get_state()

if not state.university or not state.course:
    st.warning("Please select a university and course on the Course Selector page first.")
    if st.button("Go to Course Selector"):
        st.switch_page("pages/1_Course_Selector.py")
else:
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
                step=1
            )

        with col2:
            edu_start = st.number_input(
                "Education Start Year",
                min_value=start_year,
                max_value=start_year+10,
                value=state.education_year,
                step=1
            )

        with col3:
            duration = st.selectbox("Programme Length (years)", [1,2,3,4], index=2)

        with col4:
            course_info = data_processor.get_course_info(state.university, state.course)
            default_cagr = course_info.get('cagr_pct', 5.0)
            cagr = st.slider("Fee CAGR (%)", 0.0, 15.0, default_cagr, 0.1)

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
                st.subheader("Programme Cost Analysis")
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
                st.subheader("Projections")
                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    fee_chart = create_fee_projection_chart(projections_data)
                    st.plotly_chart(fee_chart, use_container_width=True, theme="streamlit")

                with chart_col2:
                    fx_chart = create_fx_projection_chart(projections_data)
                    st.plotly_chart(fx_chart, use_container_width=True, theme="streamlit")

                # Exchange rate forecast table
                st.subheader("Exchange Rate Forecast")
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

                st.divider()

                # Professional navigation
                navigation_buttons(
                    back_page="pages/1_Course_Selector.py",
                    next_page="pages/3_Saver_Selector.py",
                    back_label="← Back to Course",
                    next_label="Next → Strategy"
                )

            else:
                st.error("Unable to generate projections. Please check your selections.")

    except Exception as e:
        st.error(f"Error generating projections: {e}")
        st.info("Please ensure all data is properly loaded and try again.")