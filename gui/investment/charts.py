"""
Investment Strategies App Chart Components
Placeholder for professional visualizations following Streamlit Design Bible
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional


# ===== PROFESSIONAL CHART LAYOUT CONFIGURATION =====

def get_professional_chart_layout(title: Optional[str] = None) -> Dict:
    """
    Standard professional chart layout for investment app
    Follows Streamlit Design Bible styling
    """
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': dict(family="system-ui, -apple-system, sans-serif", size=14),
        'margin': dict(l=20, r=20, t=40 if title else 20, b=60),
        'title': dict(
            text=title,
            font=dict(size=18, color='#0F172A'),
            x=0.05
        ) if title else None,
        'xaxis': dict(
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            tickcolor='#6B7280',
            title=dict(font=dict(color='#374151'))
        ),
        'yaxis': dict(
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            tickcolor='#6B7280',
            title=dict(font=dict(color='#374151')),
            tickformat='₹,.0f'
        ),
        'legend': dict(
            orientation="h",
            y=-0.15,
            font=dict(color='#374151')
        ),
        'showlegend': True
    }


# ===== INVESTMENT GROWTH CHARTS =====

def create_investment_growth_chart(projection_data: List[Dict]) -> go.Figure:
    """
    Create professional line chart showing investment growth over time

    Args:
        projection_data: List of yearly projection dictionaries

    Returns:
        Plotly figure object
    """
    if not projection_data:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No projection data available.<br>Please calculate projections first.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color='#6B7280')
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400
        )
        return fig

    # Extract data for plotting
    years = [item['year'] for item in projection_data]
    amounts = [item['amount'] for item in projection_data]

    # Create line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=amounts,
        mode='lines+markers',
        line=dict(color='#1E40AF', width=3),
        marker=dict(color='#1E40AF', size=8),
        name='Investment Value',
        hovertemplate='<b>Year %{x}</b><br>Value: ₹%{y:,.0f}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(**get_professional_chart_layout("Investment Growth Projection"))
    fig.update_xaxes(title="Year")
    fig.update_yaxes(title="Investment Value (₹)")

    return fig


def create_annual_growth_chart(projection_data: List[Dict]) -> go.Figure:
    """
    Create bar chart showing annual growth amounts

    Args:
        projection_data: List of yearly projection dictionaries

    Returns:
        Plotly figure object
    """
    if not projection_data or len(projection_data) <= 1:
        fig = go.Figure()
        fig.add_annotation(
            text="No growth data available.<br>Need at least 2 years of projections.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color='#6B7280')
        )
        return fig

    # Skip first year (no growth)
    growth_data = projection_data[1:]
    years = [item['year'] for item in growth_data]
    growth_amounts = [item['annual_growth'] for item in growth_data]

    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=growth_amounts,
        marker_color='#059669',
        name='Annual Growth',
        hovertemplate='<b>Year %{x}</b><br>Growth: ₹%{y:,.0f}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(**get_professional_chart_layout("Annual Growth Breakdown"))
    fig.update_xaxes(title="Year")
    fig.update_yaxes(title="Annual Growth (₹)")

    return fig


# ===== STRATEGY COMPARISON CHARTS =====

def create_strategy_comparison_chart(initial_investment: int, years: int) -> go.Figure:
    """
    Create comparison chart between Gold and 5% Saver strategies

    Args:
        initial_investment: Initial investment amount
        years: Number of years to project

    Returns:
        Plotly figure object
    """
    if years <= 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Invalid projection period.<br>Years must be greater than 0.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color='#6B7280')
        )
        return fig

    # Generate projections for both strategies
    gold_return = 0.11
    saver_return = 0.05

    year_range = list(range(years + 1))
    gold_values = [initial_investment * ((1 + gold_return) ** year) for year in year_range]
    saver_values = [initial_investment * ((1 + saver_return) ** year) for year in year_range]

    # Create comparison chart
    fig = go.Figure()

    # Gold strategy line
    fig.add_trace(go.Scatter(
        x=year_range,
        y=gold_values,
        mode='lines+markers',
        line=dict(color='#F59E0B', width=3),
        marker=dict(color='#F59E0B', size=6),
        name='Gold Investment (11%)',
        hovertemplate='<b>Year %{x}</b><br>Gold Value: ₹%{y:,.0f}<extra></extra>'
    ))

    # Saver strategy line
    fig.add_trace(go.Scatter(
        x=year_range,
        y=saver_values,
        mode='lines+markers',
        line=dict(color='#10B981', width=3),
        marker=dict(color='#10B981', size=6),
        name='5% Fixed Saver',
        hovertemplate='<b>Year %{x}</b><br>Saver Value: ₹%{y:,.0f}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(**get_professional_chart_layout("Strategy Comparison"))
    fig.update_xaxes(title="Years")
    fig.update_yaxes(title="Investment Value (₹)")

    return fig


# ===== RISK-RETURN VISUALIZATION =====

def create_risk_return_scatter() -> go.Figure:
    """
    Create scatter plot showing risk vs return for different investment strategies
    """
    strategies = {
        'Gold': {'return': 11, 'risk': 15, 'color': '#F59E0B'},
        '5% Saver': {'return': 5, 'risk': 0, 'color': '#10B981'},
        'Equity Mutual Funds': {'return': 12, 'risk': 20, 'color': '#3B82F6'},
        'Fixed Deposits': {'return': 6, 'risk': 0, 'color': '#6B7280'},
        'Real Estate': {'return': 8, 'risk': 12, 'color': '#8B5CF6'}
    }

    fig = go.Figure()

    for name, data in strategies.items():
        marker_size = 20 if name in ['Gold', '5% Saver'] else 15
        marker_symbol = 'star' if name in ['Gold', '5% Saver'] else 'circle'

        fig.add_trace(go.Scatter(
            x=[data['risk']],
            y=[data['return']],
            mode='markers',
            marker=dict(
                color=data['color'],
                size=marker_size,
                symbol=marker_symbol,
                line=dict(width=2, color='white')
            ),
            name=name,
            hovertemplate=f'<b>{name}</b><br>Expected Return: %{{y}}%<br>Risk Level: %{{x}}%<extra></extra>'
        ))

    # Update layout
    fig.update_layout(**get_professional_chart_layout("Risk vs Return Analysis"))
    fig.update_xaxes(title="Risk Level (%)")
    fig.update_yaxes(title="Expected Annual Return (%)")

    return fig


# ===== CHART DISPLAY FUNCTIONS =====

def display_investment_charts(projection_data: List[Dict]) -> None:
    """
    Display all investment-related charts in tabs

    Args:
        projection_data: List of yearly projection dictionaries
    """
    if not projection_data:
        st.warning("No projection data available. Please calculate projections first.")
        return

    tab1, tab2, tab3 = st.tabs(["📈 Growth Projection", "📊 Annual Growth", "⚖️ Strategy Comparison"])

    with tab1:
        st.subheader("Investment Growth Over Time")
        growth_chart = create_investment_growth_chart(projection_data)
        st.plotly_chart(growth_chart, use_container_width=True)

    with tab2:
        st.subheader("Year-over-Year Growth")
        annual_chart = create_annual_growth_chart(projection_data)
        st.plotly_chart(annual_chart, use_container_width=True)

    with tab3:
        st.subheader("Gold vs 5% Saver Comparison")
        # Calculate years from projection data
        years = len(projection_data) - 1 if projection_data else 5
        initial_investment = projection_data[0]['amount'] if projection_data else 1000000

        comparison_chart = create_strategy_comparison_chart(initial_investment, years)
        st.plotly_chart(comparison_chart, use_container_width=True)


def display_risk_analysis() -> None:
    """
    Display risk analysis chart
    """
    st.subheader("Risk vs Return Analysis")
    st.caption("Compare different investment options based on expected returns and risk levels")

    risk_chart = create_risk_return_scatter()
    st.plotly_chart(risk_chart, use_container_width=True)

    # Add explanation
    st.info(
        "**How to read this chart**: "
        "The further right a strategy appears, the higher its risk. "
        "The higher up it appears, the greater its expected return. "
        "Gold and 5% Saver (highlighted) represent our main strategies."
    )