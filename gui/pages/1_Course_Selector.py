import streamlit as st
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
    navigation_buttons, info_alert, format_gbp
)
from gui.core.compute import get_universities, get_courses, get_course_info

configure_page("Course Selector")

# Professional page header with breadcrumb
professional_page_header(
    title="Course Selector",
    subtitle="Select your target university and academic programme",
    breadcrumb_steps=["Home", "Course Selection", "Projections", "Strategy", "Summary"],
    current_step=1
)

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

            st.subheader("Course Fee Information")

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

            # Professional navigation
            navigation_buttons(
                next_page="pages/2_Pay_As_You_Go_Projections.py",
                next_label="Next → Projections"
            )

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please check that the data files are available and try refreshing the page.")