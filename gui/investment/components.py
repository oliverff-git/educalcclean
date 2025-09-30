"""
Investment Strategies App UI Components
Professional investment-focused components following Streamlit Design Bible
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== INVESTMENT-SPECIFIC KPI COMPONENTS =====

def investment_kpi_card(label: str, value: str, delta: Optional[str] = None) -> None:
    """
    Professional investment KPI card using native Streamlit container

    Args:
        label: KPI label (will be displayed in uppercase)
        value: Main value to display (formatted investment amount/percentage)
        delta: Optional delta change indicator for returns/growth
    """
    with st.container(border=True):
        st.caption(label.upper())
        if delta:
            st.metric(
                label="",
                value=value,
                delta=delta
            )
        else:
            st.markdown(f"### {value}")


# ===== INVESTMENT COURSE SELECTOR SECTION =====

def course_selector_section() -> Dict[str, Any]:
    """
    Dynamic course selection UI for investment planning using real backend data
    Returns selected course details as dictionary
    """
    st.markdown("### Course Selection")

    with st.container(border=True):
        # Import calculations module for real data
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent))
            from calculations import create_investment_calculator

            calc = create_investment_calculator()
            available_universities = calc.get_available_universities()
        except Exception:
            # Fallback to static data if backend unavailable
            available_universities = ["Oxford", "Cambridge", "LSE"]

        # University selection
        col1, col2 = st.columns(2)

        with col1:
            university = st.selectbox(
                "University",
                options=available_universities,
                index=0,
                key="investment_university"
            )

        with col2:
            # Get real course options from backend
            try:
                course_options = calc.get_available_courses(university)
                # Set default to PPE if available, otherwise first option
                default_index = 0
                if "Philosophy Politics & Economics" in course_options:
                    default_index = course_options.index("Philosophy Politics & Economics")
            except Exception:
                # Fallback course options
                course_options = ["Philosophy Politics & Economics", "Computer Science", "Economics"]
                default_index = 0

            course = st.selectbox(
                "Course",
                options=course_options,
                index=default_index,
                key="investment_course"
            )

        # Duration selection
        col3, col4 = st.columns(2)

        with col3:
            start_year = st.selectbox(
                "Start Year",
                options=[2025, 2026, 2027, 2028, 2029],
                index=0,
                key="investment_start_year"
            )

        with col4:
            duration = st.selectbox(
                "Duration (Years)",
                options=[3, 4, 5],
                index=0,
                key="investment_duration"
            )
            end_year = start_year + duration

    # Display selection summary
    st.info(f"**Selected**: {course} at {university} ({start_year}-{end_year})")

    return {
        "university": university,
        "course": course,
        "start_year": start_year,
        "end_year": end_year,
        "duration": duration
    }


# ===== INVESTMENT OPTIONS SECTION =====

def investment_options_section() -> Dict[str, Any]:
    """
    Gold vs 5% Saver investment selection UI
    Returns selected investment strategy details
    """
    st.markdown("### Investment Strategy")

    with st.container(border=True):
        # Investment amount calculation based on tuition or custom
        st.markdown("**Investment Amount Calculation**")

        # Get current session state values
        current_university = st.session_state.get("investment_university", "Oxford")
        current_course = st.session_state.get("investment_course", "Philosophy Politics & Economics (PPE)")

        # Investment amount strategy selection
        amount_strategy = st.radio(
            "Base your investment on:",
            options=["1 Year Tuition", "2 Years Tuition", "3 Years Tuition", "Custom Amount"],
            index=0,
            key="investment_amount_strategy"
        )

        # Calculate investment amount based on selection
        investment_amount = 1000000  # Default fallback

        if amount_strategy != "Custom Amount":
            # Try to fetch real tuition fee
            try:
                # Import data processor to get real fees
                sys.path.append(str(Path(__file__).parent.parent))
                from gui.data_processor import EducationDataProcessor

                data_processor = EducationDataProcessor()
                data_processor.load_data()

                # Get latest tuition fee in GBP
                annual_fee_gbp = data_processor.get_latest_fee(current_university, current_course)

                # Convert to INR (using current exchange rate ~105)
                exchange_rate = 105.0
                annual_fee_inr = annual_fee_gbp * exchange_rate

                # Calculate based on selected years
                years_map = {"1 Year Tuition": 1, "2 Years Tuition": 2, "3 Years Tuition": 3}
                years = years_map[amount_strategy]
                investment_amount = int(annual_fee_inr * years)

                # Display tuition breakdown
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Annual Tuition**: £{annual_fee_gbp:,.0f}")
                    st.caption(f"Exchange Rate: ₹{exchange_rate}/£")
                with col2:
                    st.success(f"**{years} Year(s) Total**: ₹{investment_amount:,.0f}")
                    st.caption(f"Annual: ₹{annual_fee_inr:,.0f}")

            except Exception as e:
                # Fallback to default calculation
                default_fees = {"Oxford": 39000, "Cambridge": 37000, "LSE": 35000}
                annual_fee_gbp = default_fees.get(current_university, 38000)
                exchange_rate = 105.0
                annual_fee_inr = annual_fee_gbp * exchange_rate
                years_map = {"1 Year Tuition": 1, "2 Years Tuition": 2, "3 Years Tuition": 3}
                years = years_map[amount_strategy]
                investment_amount = int(annual_fee_inr * years)

                st.warning("Using estimated tuition fees (real data unavailable)")
                st.info(f"**Estimated {years} Year(s) Tuition**: ₹{investment_amount:,.0f}")

        else:
            # Custom amount input
            investment_amount = st.number_input(
                "Custom Investment Amount (₹)",
                min_value=100000,
                max_value=50000000,
                value=st.session_state.get("custom_investment_amount", 1000000),
                step=100000,
                format="%d",
                key="custom_investment_amount"
            )

        # Store the calculated amount in session state
        st.session_state["calculated_investment_amount"] = investment_amount

        # Display formatted final amount
        if investment_amount >= 10000000:  # 1 crore
            formatted_amount = f"₹{investment_amount/10000000:.1f}Cr"
        elif investment_amount >= 100000:  # 1 lakh
            formatted_amount = f"₹{investment_amount/100000:.1f}L"
        else:
            formatted_amount = f"₹{investment_amount:,}"

        st.markdown(f"**Final Investment Amount**: {formatted_amount}")

        st.divider()

        # Investment strategy selection
        st.markdown("**Choose Your Investment Strategy:**")

        col1, col2 = st.columns(2)

        with col1:
            gold_selected = st.button(
                "Gold Investment",
                use_container_width=True,
                type="primary" if st.session_state.get("selected_strategy") == "gold" else "secondary",
                key="select_gold"
            )
            if gold_selected:
                st.session_state["selected_strategy"] = "gold"

            if st.session_state.get("selected_strategy") == "gold":
                st.success("Historical avg return: 10-12% annually")
                st.caption("• Hedge against inflation\n• Physical asset backing\n• Long-term wealth preservation")

        with col2:
            saver_selected = st.button(
                "5% Fixed Saver",
                use_container_width=True,
                type="primary" if st.session_state.get("selected_strategy") == "saver" else "secondary",
                key="select_saver"
            )
            if saver_selected:
                st.session_state["selected_strategy"] = "saver"

            if st.session_state.get("selected_strategy") == "saver":
                st.success("Guaranteed return: 5% annually")
                st.caption("• Fixed guaranteed returns\n• Low risk investment\n• Stable growth pattern")

    # Get selected strategy or default
    selected_strategy = st.session_state.get("selected_strategy", "gold")

    return {
        "investment_amount": st.session_state.get("calculated_investment_amount", investment_amount),
        "strategy": selected_strategy,
        "expected_return": 0.11 if selected_strategy == "gold" else 0.05,
        "risk_level": "Medium-High" if selected_strategy == "gold" else "Low"
    }


# ===== INVESTMENT HEADER =====

def investment_header() -> None:
    """
    Professional page header for investment strategies app
    """
    # Page title and subtitle
    st.title("Investment Strategies Calculator")
    st.markdown("**Professional education funding through strategic investments**")

    # Breadcrumb navigation
    breadcrumb = "Home > Investment Planning > Strategy Selection"
    st.caption(breadcrumb)

    st.divider()

    # Key features highlight
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 Real-Time Analysis**")
        st.caption("Live calculations based on current market data")

    with col2:
        st.markdown("**🎯 Goal-Oriented**")
        st.caption("Tailored projections for education funding")

    with col3:
        st.markdown("**📈 Growth Tracking**")
        st.caption("Monitor investment performance over time")


# ===== INVESTMENT SUMMARY COMPONENTS =====

def investment_summary_row(course_details: Dict, investment_details: Dict) -> None:
    """
    Display a summary row of key investment information
    """
    st.markdown("### Investment Summary")

    # Create KPI cards for key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        investment_kpi_card(
            "Initial Investment",
            f"₹{investment_details['investment_amount']:,}"
        )

    with col2:
        investment_kpi_card(
            "Strategy",
            investment_details['strategy'].title()
        )

    with col3:
        investment_kpi_card(
            "Expected Return",
            f"{investment_details['expected_return']*100:.1f}%"
        )

    with col4:
        years_to_goal = course_details['start_year'] - datetime.now().year
        investment_kpi_card(
            "Years to Goal",
            f"{years_to_goal} years"
        )


# ===== PROJECTION DISPLAY COMPONENTS =====

def show_investment_projections(course_details: Dict, investment_details: Dict) -> None:
    """
    Calculate and display investment projections
    """
    st.markdown("### Investment Projections")

    # Calculate projections
    initial_amount = investment_details['investment_amount']
    annual_return = investment_details['expected_return']
    years_to_goal = course_details['start_year'] - datetime.now().year

    if years_to_goal <= 0:
        st.warning("Course start year should be in the future for meaningful projections.")
        return

    # Compound growth calculation
    final_amount = initial_amount * ((1 + annual_return) ** years_to_goal)
    total_growth = final_amount - initial_amount

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            investment_kpi_card(
                "Projected Value at Course Start",
                f"₹{final_amount:,.0f}",
                f"+₹{total_growth:,.0f}"
            )

        with col2:
            total_return_percentage = ((final_amount - initial_amount) / initial_amount) * 100
            investment_kpi_card(
                "Total Return",
                f"{total_return_percentage:.1f}%",
                f"{annual_return*100:.1f}% annually"
            )

    # Show yearly breakdown
    st.markdown("#### Year-by-Year Growth")

    # Create projection table
    projection_data = []
    current_amount = initial_amount

    for year in range(years_to_goal + 1):
        target_year = datetime.now().year + year
        if year == 0:
            growth = 0
        else:
            growth = current_amount * annual_return
            current_amount += growth

        projection_data.append({
            "Year": target_year,
            "Amount (₹)": int(current_amount),
            "Annual Growth (₹)": int(growth),
            "Return %": f"{annual_return*100:.1f}%" if year > 0 else "Initial"
        })

    df = pd.DataFrame(projection_data)

    # Display with professional formatting
    st.dataframe(
        df,
        column_config={
            "Year": st.column_config.NumberColumn(
                "Year",
                format="%d"
            ),
            "Amount (₹)": st.column_config.NumberColumn(
                "Investment Value",
                format="₹%d"
            ),
            "Annual Growth (₹)": st.column_config.NumberColumn(
                "Annual Growth",
                format="₹%d"
            ),
            "Return %": "Annual Return"
        },
        hide_index=True,
        use_container_width=True
    )


# ===== ACTION BUTTONS =====

def investment_action_buttons() -> Dict[str, bool]:
    """
    Professional action buttons for investment calculations
    Returns dictionary of button states
    """
    st.divider()

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        calculate_clicked = st.button(
            "📊 Calculate Projections",
            type="primary",
            use_container_width=True,
            key="calculate_projections"
        )

    with col2:
        compare_clicked = st.button(
            "⚖️ Compare Strategies",
            use_container_width=True,
            key="compare_strategies"
        )

    with col3:
        reset_clicked = st.button(
            "🔄 Reset All",
            use_container_width=True,
            key="reset_all"
        )

    return {
        "calculate": calculate_clicked,
        "compare": compare_clicked,
        "reset": reset_clicked
    }


# ===== STRATEGY COMPARISON COMPONENT =====

def strategy_comparison_table() -> None:
    """
    Display side-by-side comparison of Gold vs 5% Saver strategies
    """
    st.markdown("### Strategy Comparison")

    comparison_data = pd.DataFrame({
        "Feature": [
            "Expected Annual Return",
            "Risk Level",
            "Volatility",
            "Inflation Protection",
            "Liquidity",
            "Minimum Investment",
            "Tax Implications"
        ],
        "Gold Investment": [
            "10-12%",
            "Medium-High",
            "Moderate to High",
            "Excellent",
            "Good",
            "₹1,00,000+",
            "Long-term capital gains"
        ],
        "5% Fixed Saver": [
            "5%",
            "Low",
            "None",
            "Limited",
            "Excellent",
            "₹10,000+",
            "Interest taxable as income"
        ]
    })

    st.dataframe(
        comparison_data,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Feature": st.column_config.TextColumn(
                "Feature",
                width="medium"
            ),
            "Gold Investment": st.column_config.TextColumn(
                "🥇 Gold Investment",
                width="medium"
            ),
            "5% Fixed Saver": st.column_config.TextColumn(
                "🏦 5% Fixed Saver",
                width="medium"
            )
        }
    )

    # Add recommendation box
    st.info(
        "**Recommendation**: Gold investment typically offers higher long-term returns but comes with increased volatility. "
        "Fixed saver provides guaranteed returns with complete capital protection."
    )