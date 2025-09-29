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


@st.cache_data(ttl=3600)  # Cache charts for 1 hour
def create_fee_projection_chart(projections_data):
    """Create professional chart showing fee projections over time"""
    course_info = projections_data['course_info']
    fee_projections = projections_data['fee_projections']

    # Prepare data for chart
    years = list(fee_projections.keys())
    fees = list(fee_projections.values())

    # Historical vs projected
    historical_years = [y for y in years if y <= 2025]
    projected_years = [y for y in years if y > 2025]

    fig = go.Figure()

    # Historical data with professional colors
    if historical_years:
        historical_fees = [fee_projections[y] for y in historical_years]
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_fees,
            mode='lines+markers',
            name='Historical Data',
            line=dict(color='#1E40AF', width=3),  # Professional blue
            marker=dict(size=6, color='#1E40AF'),
            hovertemplate='<b>%{x}</b><br>Fee: £%{y:,.0f}<extra></extra>'
        ))

    # Projected data with professional styling
    if projected_years:
        # Connect last historical to first projected
        connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
        connect_fees = [fee_projections[y] for y in connect_years]

        fig.add_trace(go.Scatter(
            x=connect_years,
            y=connect_fees,
            mode='lines+markers',
            name='Projected',
            line=dict(color='#059669', width=3, dash='dash'),  # Professional green
            marker=dict(size=6, color='#059669'),
            hovertemplate='<b>%{x}</b><br>Projected Fee: £%{y:,.0f}<extra></extra>'
        ))

    # Professional layout styling
    fig.update_layout(
        title=dict(
            text=f"<b>{course_info['university']} - {course_info['programme']}</b><br><sub>Annual Fee Projections (CAGR: {course_info['cagr_pct']:.1f}%)</sub>",
            font=dict(size=16, color='#0F172A'),
            x=0.05
        ),
        xaxis=dict(
            title="Year",
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            titlefont=dict(color='#374151', size=14),
            tickfont=dict(color='#6B7280', size=12)
        ),
        yaxis=dict(
            title="Annual Fee (GBP)",
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            titlefont=dict(color='#374151', size=14),
            tickfont=dict(color='#6B7280', size=12),
            tickformat='£,.0f'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="system-ui, -apple-system, sans-serif", size=12),
        margin=dict(l=60, r=40, t=80, b=60),
        height=450,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            y=-0.15,
            font=dict(color='#374151', size=12)
        )
    )

    return fig


@st.cache_data(ttl=3600)  # Cache charts for 1 hour
def create_fx_projection_chart(projections_data):
    """Create professional FX projection chart"""
    fx_projections = projections_data['fx_projections']

    years = list(fx_projections.keys())
    rates = list(fx_projections.values())

    # Historical vs projected
    historical_years = [y for y in years if y <= 2025]
    projected_years = [y for y in years if y > 2025]

    fig = go.Figure()

    # Historical data with professional colors
    if historical_years:
        historical_rates = [fx_projections[y] for y in historical_years]
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=historical_rates,
            mode='lines+markers',
            name='Historical Rates',
            line=dict(color='#DC2626', width=3),  # Professional red for exchange rates
            marker=dict(size=6, color='#DC2626'),
            hovertemplate='<b>%{x}</b><br>Rate: ₹%{y:,.2f}/£<extra></extra>'
        ))

    # Projected data with professional styling
    if projected_years:
        connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
        connect_rates = [fx_projections[y] for y in connect_years]

        fig.add_trace(go.Scatter(
            x=connect_years,
            y=connect_rates,
            mode='lines+markers',
            name='Projected Rates',
            line=dict(color='#EA580C', width=3, dash='dash'),  # Professional orange
            marker=dict(size=6, color='#EA580C'),
            hovertemplate='<b>%{x}</b><br>Projected Rate: ₹%{y:,.2f}/£<extra></extra>'
        ))

    # Professional layout styling
    fig.update_layout(
        title=dict(
            text="<b>GBP/INR Exchange Rate Projections</b><br><sub>Historical CAGR: 4.18% (Conservative Estimate)</sub>",
            font=dict(size=16, color='#0F172A'),
            x=0.05
        ),
        xaxis=dict(
            title="Year",
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            titlefont=dict(color='#374151', size=14),
            tickfont=dict(color='#6B7280', size=12)
        ),
        yaxis=dict(
            title="Exchange Rate (₹ per £)",
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            titlefont=dict(color='#374151', size=14),
            tickfont=dict(color='#6B7280', size=12),
            tickformat='₹,.0f'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="system-ui, -apple-system, sans-serif", size=12),
        margin=dict(l=60, r=40, t=80, b=60),
        height=450,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            y=-0.15,
            font=dict(color='#374151', size=12)
        )
    )

    return fig


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_payg_projection(university: str, course: str, start_year: int, edu_year: int, duration: int = 3):
    """Get pay-as-you-go projection data"""
    data_processor, calculator = init_processors()
    return calculator.get_projection_details(university, course, edu_year)


@st.cache_data(ttl=1800)  # Cache for 30 minutes
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


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def create_strategy_comparison_chart(scenarios):
    """Create professional bar chart comparing strategy costs"""
    if not scenarios:
        return None

    strategy_names = [scenario.strategy_name for scenario in scenarios]
    total_costs = [scenario.total_cost_inr for scenario in scenarios]

    # Format costs in lakhs for better readability
    formatted_costs = [cost / 100000 for cost in total_costs]  # Convert to lakhs
    hover_texts = [f"<b>{name}</b><br>Cost: ₹{cost:,.0f}<br>({cost/100000:.1f}L)"
                   for name, cost in zip(strategy_names, total_costs)]

    # Professional color scheme - highlight best strategy
    colors = ['#059669' if i == 0 else '#1E40AF' if i == 1 else '#374151'
              for i in range(len(scenarios))]

    fig = go.Figure(data=[go.Bar(
        x=strategy_names,
        y=formatted_costs,
        marker_color=colors,
        hovertemplate='%{text}<extra></extra>',
        text=hover_texts,
        textposition='none'
    )])

    # Professional layout styling
    fig.update_layout(
        title=dict(
            text="<b>Strategy Cost Comparison</b><br><sub>Total Education Cost by Strategy</sub>",
            font=dict(size=16, color='#0F172A'),
            x=0.05
        ),
        xaxis=dict(
            title="Strategy",
            gridcolor='#E2E8F0',
            showgrid=False,
            linecolor='#E2E8F0',
            titlefont=dict(color='#374151', size=14),
            tickfont=dict(color='#6B7280', size=12),
            tickangle=-45
        ),
        yaxis=dict(
            title="Total Cost (Lakhs ₹)",
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            titlefont=dict(color='#374151', size=14),
            tickfont=dict(color='#6B7280', size=12),
            tickformat='₹.1f'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="system-ui, -apple-system, sans-serif", size=12),
        margin=dict(l=60, r=40, t=80, b=100),  # Extra bottom margin for rotated labels
        height=450,
        showlegend=False
    )

    # Add value labels on bars for better readability
    for i, (cost_lakhs, cost_total) in enumerate(zip(formatted_costs, total_costs)):
        fig.add_annotation(
            x=strategy_names[i],
            y=cost_lakhs + max(formatted_costs) * 0.02,  # Slightly above bar
            text=f"₹{cost_lakhs:.1f}L",
            showarrow=False,
            font=dict(color='#374151', size=12, family="system-ui"),
            xanchor='center'
        )

    return fig


@st.cache_data(ttl=7200)  # Cache for 2 hours (course info changes rarely)
def get_course_info(university: str, course: str):
    """Get course information from data processor"""
    data_processor, calculator = init_processors()
    return data_processor.get_course_info(university, course)


@st.cache_data(ttl=86400)  # Cache for 24 hours (universities change very rarely)
def get_universities():
    """Get list of available universities"""
    data_processor, calculator = init_processors()
    return data_processor.get_universities()


@st.cache_data(ttl=86400)  # Cache for 24 hours
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