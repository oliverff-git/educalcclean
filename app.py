"""
Simple Education Savings Calculator for Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Education Savings Calculator",
    page_icon="🎓",
    layout="wide"
)

# Title
st.title("🎓 UK Education Savings Calculator")
st.markdown("**Calculate potential savings from early INR→GBP conversion strategies**")

# Load sample data (simplified for demo)
@st.cache_data
def load_sample_data():
    # Sample fee data for demonstration
    fees_data = {
        'Oxford': {
            'Computer Science': {'2020': 35080, '2021': 37850, '2022': 39800, '2023': 42600, '2024': 46500},
            'Economics': {'2020': 32500, '2021': 35200, '2022': 37100, '2023': 39800, '2024': 43200}
        },
        'Cambridge': {
            'Engineering': {'2020': 34300, '2021': 37100, '2022': 38900, '2023': 41700, '2024': 45400},
            'Medicine': {'2020': 58800, '2021': 63500, '2022': 66700, '2023': 71500, '2024': 78000}
        },
        'LSE': {
            'Economics': {'2020': 25200, '2021': 27300, '2022': 28700, '2023': 30800, '2024': 33500},
            'Finance': {'2020': 28900, '2021': 31200, '2022': 32800, '2023': 35200, '2024': 38300}
        }
    }

    # Sample exchange rates
    fx_rates = {
        2020: 95.12,
        2021: 98.45,
        2022: 102.30,
        2023: 106.85,
        2024: 111.20,
        2025: 115.80,
        2026: 120.65
    }

    return fees_data, fx_rates

def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate"""
    if years <= 0 or start_value <= 0:
        return 0
    return (end_value / start_value) ** (1 / years) - 1

def calculate_savings_scenarios(university, course, conversion_year, education_year, fees_data, fx_rates):
    """Calculate different conversion scenarios"""

    course_fees = fees_data[university][course]
    years = list(course_fees.keys())
    fees = list(course_fees.values())

    # Calculate fee CAGR
    fee_cagr = calculate_cagr(fees[0], fees[-1], len(fees) - 1)

    # Project fee for education year
    base_fee = fees[-1]  # Latest available fee
    base_year = int(years[-1])
    years_ahead = education_year - base_year
    projected_fee = base_fee * (1 + fee_cagr) ** years_ahead

    # FX rates
    conversion_fx = fx_rates[conversion_year]
    education_fx = fx_rates[education_year]

    # Scenario 1: Convert early
    early_conversion_cost_inr = projected_fee * conversion_fx

    # Scenario 2: Convert at education time
    late_conversion_cost_inr = projected_fee * education_fx

    # Savings
    savings_inr = late_conversion_cost_inr - early_conversion_cost_inr
    savings_pct = (savings_inr / late_conversion_cost_inr) * 100

    return {
        'projected_fee_gbp': projected_fee,
        'fee_cagr': fee_cagr * 100,
        'early_cost_inr': early_conversion_cost_inr,
        'late_cost_inr': late_conversion_cost_inr,
        'savings_inr': savings_inr,
        'savings_pct': savings_pct,
        'conversion_fx': conversion_fx,
        'education_fx': education_fx
    }

def format_inr(amount):
    """Format INR amounts in lakhs/crores"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"

# Load data
fees_data, fx_rates = load_sample_data()

# Sidebar controls
st.sidebar.header("📋 Selection Parameters")

university = st.sidebar.selectbox(
    "🏫 Select University",
    list(fees_data.keys())
)

course = st.sidebar.selectbox(
    "📚 Select Course",
    list(fees_data[university].keys())
)

conversion_year = st.sidebar.selectbox(
    "💰 Savings Start Year",
    [2022, 2023, 2024, 2025],
    index=1
)

education_year = st.sidebar.selectbox(
    "🎓 Education Start Year",
    [2025, 2026, 2027, 2028],
    index=1
)

if education_year <= conversion_year:
    st.sidebar.error("⚠️ Education start year must be after conversion year")
    st.stop()

# Calculate scenarios
results = calculate_savings_scenarios(
    university, course, conversion_year, education_year,
    fees_data, fx_rates
)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"📊 Analysis: {university} - {course}")

    # Metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            f"Projected Fee ({education_year})",
            f"£{results['projected_fee_gbp']:,.0f}"
        )

    with metric_col2:
        st.metric(
            "Fee Growth (CAGR)",
            f"{results['fee_cagr']:.1f}%"
        )

    with metric_col3:
        st.metric(
            "Potential Savings",
            format_inr(results['savings_inr']),
            f"{results['savings_pct']:.1f}%"
        )

    # Show savings result
    if results['savings_inr'] > 0:
        st.success(
            f"💡 **Converting early saves {format_inr(results['savings_inr'])} "
            f"({results['savings_pct']:.1f}%)**"
        )

    # Chart showing fee progression
    course_fees = fees_data[university][course]
    years = [int(y) for y in course_fees.keys()]
    fees = list(course_fees.values())

    # Add projected point
    years.append(education_year)
    fees.append(results['projected_fee_gbp'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years[:-1],
        y=fees[:-1],
        mode='lines+markers',
        name='Historical',
        line=dict(color='#1f77b4', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=[years[-2], years[-1]],
        y=[fees[-2], fees[-1]],
        mode='lines+markers',
        name='Projected',
        line=dict(color='#ff7f0e', width=3, dash='dash')
    ))

    fig.update_layout(
        title=f"{university} - {course} Fee Projections",
        xaxis_title="Year",
        yaxis_title="Annual Fee (GBP)",
        height=400
    )
    fig.update_yaxes(tickformat='£,.0f')

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("💰 Cost Breakdown")

    # Early conversion scenario
    with st.expander("🟢 Early Conversion Strategy", expanded=True):
        st.metric("Conversion Year", conversion_year)
        st.metric("Exchange Rate", f"₹{results['conversion_fx']:.2f}/£")
        st.metric("Total Cost", format_inr(results['early_cost_inr']))

    # Late conversion scenario
    with st.expander("🔴 Pay-As-You-Go Strategy"):
        st.metric("Conversion Year", education_year)
        st.metric("Exchange Rate", f"₹{results['education_fx']:.2f}/£")
        st.metric("Total Cost", format_inr(results['late_cost_inr']))

    # Exchange rate table
    st.subheader("📈 Exchange Rate Forecast")
    fx_data = []
    for year in range(conversion_year, education_year + 2):
        if year in fx_rates:
            status = "Historical" if year <= 2024 else "Projected"
            fx_data.append({
                'Year': year,
                'Rate (₹/£)': f"₹{fx_rates[year]:.2f}",
                'Status': status
            })

    st.dataframe(pd.DataFrame(fx_data), hide_index=True)

# Disclaimer
st.info(
    "📊 **Disclaimer**: This calculator provides estimates based on historical trends. "
    "Actual fees and exchange rates may vary. Please verify current rates and fees "
    "with official university sources."
)

# Footer
st.markdown("---")
st.markdown(
    "**🎓 UK Education Savings Calculator** | "
    "Helping Indian families plan their UK education finances"
)