import streamlit as st
import sys
from pathlib import Path

# Import core modules with correct path
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from gui.core.theme import configure_page
from gui.core.state import get_state, update_state, init_processors
from gui.core.ui import kpi_row
from gui.core.compute import get_universities, get_courses, get_course_info

configure_page("Course Selector")
st.header("Course Selector")

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
        help="Choose from Oxford, Cambridge, or LSE"
    )

    # Course selection
    if university:
        courses = get_courses(university)
        course = st.selectbox(
            "Select Course/Programme",
            courses,
            index=courses.index(state.course) if state.course in courses else 0,
            help="Choose a specific programme"
        )

        if course:
            # Get course information
            course_info = get_course_info(university, course)
            latest_year = course_info.get('latest_actual_year', 'Unknown')
            latest_fee = course_info.get('latest_fee', 0)
            three_year_total = latest_fee * 3

            # Display current fees
            kpi_row([
                (f"Current Annual Fee ({latest_year})", f"£{latest_fee:,.0f}", "Official course page"),
                (f"3-Year Programme Total ({latest_year})", f"£{three_year_total:,.0f}", "Total cost for 3-year programme"),
                ("Course CAGR", f"{course_info.get('cagr_pct', 0):.1f}%", "Historical fee growth rate"),
                ("Data Points", f"{course_info.get('data_points', 0)} years", "Years of historical data available"),
            ])

            # Data quality information
            transparency = course_info.get('transparency')
            if transparency:
                st.info(f"**Data Quality:** {transparency.data_quality.value.title()} | **Confidence:** {transparency.confidence_level.value.title()}")

            # Update state
            update_state(university=university, course=course)

            st.divider()

            # Navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Next → Projections", use_container_width=True, type="primary"):
                    st.switch_page("pages/2_Pay_As_You_Go_Projections.py")

            st.caption("Navigate to the next page to see projections and continue your analysis.")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please check that the data files are available and try refreshing the page.")