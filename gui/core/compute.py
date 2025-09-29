"""
Compute layer for the multipage refactor.
Contains chart functions and wrapper functions for clean interfaces between pages and calculators.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .state import get_state, init_processors
from .ui import format_inr, format_gbp, format_percentage


def create_fee_projection_chart(projections_data):
    """Create chart showing fee projections over time - extracted from education_savings_app.py"""
    course_info = projections_data['course_info']
    fee_projections = projections_data['fee_projections']

    # Prepare data for chart
    years = list(fee_projections.keys())
    fees = list(fee_projections.values())

    # Historical vs projected
    historical_years = [y for y in years if y <= 2025]
    projected_years = [y for y in years if y > 2025]

    fig = go.Figure()

    # Historical data
    if historical_years:
        historical_fees = [fee_projections[y] for y in historical_years]
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_fees,
            mode='lines+markers',
            name='Historical',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))

    # Projected data
    if projected_years:
        # Connect last historical to first projected
        connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
        connect_fees = [fee_projections[y] for y in connect_years]

        fig.add_trace(go.Scatter(
            x=connect_years,
            y=connect_fees,
            mode='lines+markers',
            name='Projected',
            line=dict(color='#ff7f0e', width=3, dash='dash'),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=f"{course_info['university']} - {course_info['programme']}<br>Fee Projections (CAGR: {course_info['cagr_pct']:.2f}%)",
        xaxis_title="Year",
        yaxis_title="Annual Fee (GBP)",
        height=400,
        hovermode='x unified'
    )

    fig.update_yaxes(tickformat='£,.0f')

    return fig


def create_fx_projection_chart(projections_data):
    """Create FX projection chart - extracted from education_savings_app.py"""
    fx_projections = projections_data['fx_projections']

    years = list(fx_projections.keys())
    rates = list(fx_projections.values())

    # Historical vs projected
    historical_years = [y for y in years if y <= 2025]
    projected_years = [y for y in years if y > 2025]

    fig = go.Figure()

    # Historical data
    if historical_years:
        historical_rates = [fx_projections[y] for y in historical_years]
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_rates,
            mode='lines+markers',
            name='Historical',
            line=dict(color='#2ca02c', width=3),
            marker=dict(size=8)
        ))

    # Projected data
    if projected_years:
        connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
        connect_rates = [fx_projections[y] for y in connect_years]

        fig.add_trace(go.Scatter(
            x=connect_years,
            y=connect_rates,
            mode='lines+markers',
            name='Projected',
            line=dict(color='#d62728', width=3, dash='dash'),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title="GBP/INR Exchange Rate Projections<br>(Historical CAGR: 4.18% - Conservative)",
        xaxis_title="Year",
        yaxis_title="INR per GBP",
        height=400,
        hovermode='x unified'
    )

    fig.update_yaxes(tickformat='₹,.0f')

    return fig


def get_payg_projection(university: str, course: str, start_year: int, edu_year: int, duration: int = 3):
    """Get pay-as-you-go projection data"""
    data_processor, calculator = init_processors()
    return calculator.get_projection_details(university, course, edu_year)


def compare_strategies(university: str, course: str, conversion_year: int, education_year: int):
    """Compare all savings strategies"""
    data_processor, calculator = init_processors()
    return calculator.compare_all_strategies(university, course, conversion_year, education_year)


def get_roi_scenarios(university: str, course: str, conversion_year: int, education_year: int,
                     investment_amount: float, strategies: List[str]):
    """Get ROI investment scenarios"""
    data_processor, calculator = init_processors()
    return calculator.calculate_all_roi_scenarios(
        university, course, conversion_year, education_year, investment_amount, strategies
    )


def create_strategy_comparison_chart(scenarios):
    """Create bar chart comparing strategy costs"""
    if not scenarios:
        return None

    strategy_names = [scenario.strategy_name for scenario in scenarios]
    total_costs = [scenario.total_cost_inr for scenario in scenarios]

    fig = go.Figure(data=[go.Bar(
        x=strategy_names,
        y=total_costs,
        marker_color=['#2E8B57' if i == 0 else '#4682B4' for i in range(len(scenarios))]
    )])

    fig.update_layout(
        title="Total Cost Comparison (INR)",
        xaxis_title="Strategy",
        yaxis_title="Total Cost (INR)",
        height=400
    )

    return fig


def get_course_info(university: str, course: str):
    """Get course information from data processor"""
    data_processor, calculator = init_processors()
    return data_processor.get_course_info(university, course)


def get_universities():
    """Get list of available universities"""
    data_processor, calculator = init_processors()
    return data_processor.get_universities()


def get_courses(university: str):
    """Get courses for a specific university"""
    data_processor, calculator = init_processors()
    return data_processor.get_courses(university)


def project_fee(university: str, course: str, year: int):
    """Project fee for a specific year"""
    data_processor, calculator = init_processors()
    return data_processor.project_fee(university, course, year)


def project_fx_rate(year: int):
    """Project exchange rate for a specific year"""
    data_processor, calculator = init_processors()
    return data_processor.project_fx_rate(year)