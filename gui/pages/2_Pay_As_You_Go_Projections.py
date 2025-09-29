import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Import core modules
sys.path.append(str(Path(__file__).parent.parent))
from core.theme import configure_page
from core.state import get_state, update_state, init_processors
from core.ui import kpi_row
from core.compute import get_payg_projection, create_fee_projection_chart, create_fx_projection_chart, project_fx_rate

configure_page("Pay-As-You-Go Projections")
st.header("Pay-As-You-Go Projections")

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

        if edu_start <= start_year:
            st.error("Education start year must be after savings start year")
        else:
            # Get projection data
            projections_data = get_payg_projection(state.university, state.course, start_year, edu_start, duration)

            if projections_data:
                # Calculate key metrics
                projected_annual_fee = data_processor.project_fee(state.university, state.course, edu_start)
                projected_total = projected_annual_fee * duration
                latest_fee = course_info.get('latest_fee', 0)
                current_total = latest_fee * duration

                # Display KPIs
                kpi_row([
                    (f"{duration}-Year Programme Total (Current)", f"£{current_total:,.0f}", f"Based on {course_info.get('latest_actual_year', 'current')} fees"),
                    (f"Projected {duration}-Year Total ({edu_start})", f"£{projected_total:,.0f}", "Projected using historical CAGR"),
                    ("Course CAGR", f"{cagr:.1f}%", "Annual fee growth rate"),
                    ("Data Points", f"{course_info.get('data_points', 0)} years", "Historical data available"),
                ])

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

            else:
                st.error("Unable to generate projections. Please check your selections.")

    except Exception as e:
        st.error(f"Error generating projections: {e}")
        st.info("Please ensure all data is properly loaded and try again.")