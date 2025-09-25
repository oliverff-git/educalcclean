"""
ROI Charts Module for Return on Savings Feature.

Advanced chart components for investment analysis.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def create_investment_growth_chart(scenarios: List) -> go.Figure:
    """Create investment growth curve chart.

    Args:
        scenarios: List of SavingsScenario objects with growth curves

    Returns:
        Plotly figure showing growth over time
    """
    fig = go.Figure()

    colors = ['#2E8B57', '#FFD700']  # Green for Fixed, Gold for Gold

    for i, scenario in enumerate(scenarios):
        # Extract growth curve data
        if 'growth_curve' in scenario.conversion_details:
            curve_data = scenario.conversion_details['growth_curve']
            if curve_data:
                df = pd.DataFrame(curve_data)
                strategy_name = scenario.strategy_name.split(' (')[0]
                color = colors[i % len(colors)]

                fig.add_trace(go.Scatter(
                    x=df['month'],
                    y=df['value_native'],
                    mode='lines+markers',
                    name=strategy_name,
                    line=dict(color=color, width=3),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{strategy_name}</b><br>' +
                                  'Date: %{x}<br>' +
                                  'Value: ₹%{y:,.0f}<extra></extra>'
                ))

    fig.update_layout(
        title="Investment Growth Over Time",
        xaxis_title="Date",
        yaxis_title="Investment Value (₹)",
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_risk_return_scatter(scenarios: List) -> go.Figure:
    """Create risk vs return scatter plot.

    Args:
        scenarios: List of SavingsScenario objects

    Returns:
        Plotly figure showing risk-return relationship
    """
    if not scenarios:
        return go.Figure()

    # Extract data
    returns = []
    risks = []
    names = []
    savings = []

    for scenario in scenarios:
        if 'cagr' in scenario.conversion_details:
            returns.append(scenario.conversion_details['cagr'] * 100)
            risks.append(scenario.conversion_details.get('volatility', 0) * 100)
            names.append(scenario.strategy_name.split(' (')[0])
            savings.append(scenario.savings_vs_payg_inr)

    if not returns:
        return go.Figure()

    # Create scatter plot
    fig = go.Figure()

    # Color by savings amount
    fig.add_trace(go.Scatter(
        x=risks,
        y=returns,
        mode='markers+text',
        text=names,
        textposition="middle right",
        marker=dict(
            size=[abs(s)/100000 + 10 for s in savings],  # Size by savings
            color=savings,
            colorscale='RdYlGn',
            colorbar=dict(title="Savings vs PAYG (₹)"),
            line=dict(width=2, color='black')
        ),
        hovertemplate='<b>%{text}</b><br>' +
                      'Return: %{y:.1f}%<br>' +
                      'Risk: %{x:.1f}%<br>' +
                      'Savings: ₹%{marker.color:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title="Risk vs Return Analysis",
        xaxis_title="Risk (Volatility %)",
        yaxis_title="Expected Return (CAGR %)",
        height=500,
        showlegend=False
    )

    # Add quadrant lines
    max_risk = max(risks) if risks else 20
    max_return = max(returns) if returns else 15

    # Add quadrant labels
    fig.add_annotation(
        x=max_risk * 0.8, y=max_return * 0.8,
        text="High Risk<br>High Return",
        showarrow=False, font=dict(size=10, color="gray")
    )
    fig.add_annotation(
        x=max_risk * 0.2, y=max_return * 0.8,
        text="Low Risk<br>High Return",
        showarrow=False, font=dict(size=10, color="gray")
    )

    return fig


def create_cost_waterfall_chart(baseline_cost: float, scenarios: List) -> go.Figure:
    """Create waterfall chart showing cost reduction.

    Args:
        baseline_cost: Pay-as-you-go baseline cost
        scenarios: List of SavingsScenario objects

    Returns:
        Plotly figure showing cost waterfall
    """
    if not scenarios:
        return go.Figure()

    # Use best scenario for waterfall
    best_scenario = max(scenarios, key=lambda x: x.savings_vs_payg_inr)

    # Waterfall data
    categories = ['Pay-as-you-go\nBaseline', 'Investment\nProceeds', 'Final\nCost']
    values = [
        baseline_cost,
        -best_scenario.savings_vs_payg_inr,
        best_scenario.total_cost_inr
    ]

    # Colors: baseline (blue), savings (green), final (orange)
    colors = ['blue', 'green', 'orange']

    fig = go.Figure(go.Waterfall(
        name="Cost Analysis",
        orientation="v",
        measure=["absolute", "relative", "total"],
        x=categories,
        textposition="outside",
        text=[f"₹{v:,.0f}" for v in values],
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "green"}},
        decreasing={"marker": {"color": "red"}},
        totals={"marker": {"color": "blue"}}
    ))

    fig.update_layout(
        title=f"Cost Reduction Analysis - {best_scenario.strategy_name.split(' (')[0]}",
        yaxis_title="Cost (₹)",
        height=400,
        showlegend=False
    )

    return fig


def create_allocation_pie_chart(risk_tolerance: str, scenarios: List) -> go.Figure:
    """Create portfolio allocation pie chart based on risk tolerance.

    Args:
        risk_tolerance: User's risk tolerance (Conservative/Moderate/Aggressive)
        scenarios: List of available scenarios

    Returns:
        Plotly figure showing recommended allocation
    """
    # Define allocations based on risk tolerance
    allocations = {
        "Conservative": {
            "FIXED_5PCT": 80,
            "GOLD_INR": 20
        },
        "Moderate": {
            "FIXED_5PCT": 60,
            "GOLD_INR": 40
        },
        "Aggressive": {
            "FIXED_5PCT": 40,
            "GOLD_INR": 60
        }
    }

    allocation = allocations.get(risk_tolerance, allocations["Moderate"])

    # Filter by available scenarios
    available_assets = [s.conversion_details.get('asset_type', '') for s in scenarios]
    filtered_allocation = {k: v for k, v in allocation.items() if k in available_assets and v > 0}

    if not filtered_allocation:
        return go.Figure()

    # Create pie chart
    labels = [asset.replace('_', ' ') for asset in filtered_allocation.keys()]
    values = list(filtered_allocation.values())

    # Colors for different asset types
    color_map = {
        'FIXED 5PCT': '#2E8B57',    # Green
        'GOLD INR': '#FFD700'       # Gold
    }
    colors = [color_map.get(label, '#808080') for label in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker=dict(colors=colors, line=dict(color='#000000', width=2)),
        textinfo='label+percent',
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>' +
                      'Allocation: %{percent}<br>' +
                      'Amount: %{value}%<extra></extra>'
    )])

    fig.update_layout(
        title=f"Recommended Portfolio Allocation - {risk_tolerance} Risk",
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )

    return fig


def create_performance_comparison_matrix(scenarios: List) -> go.Figure:
    """Create performance comparison matrix heatmap.

    Args:
        scenarios: List of SavingsScenario objects

    Returns:
        Plotly figure showing performance matrix
    """
    if not scenarios:
        return go.Figure()

    # Extract metrics
    metrics = ['CAGR (%)', 'Total Return (%)', 'Volatility (%)', 'Max Drawdown (%)']
    strategy_names = [s.strategy_name.split(' (')[0] for s in scenarios]

    matrix_data = []
    for scenario in scenarios:
        row = [
            scenario.conversion_details.get('cagr', 0) * 100,
            scenario.conversion_details.get('total_return', 0) * 100,
            scenario.conversion_details.get('volatility', 0) * 100,
            abs(scenario.conversion_details.get('max_drawdown', 0)) * 100
        ]
        matrix_data.append(row)

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix_data,
        x=metrics,
        y=strategy_names,
        colorscale='RdYlGn',
        text=[[f'{val:.1f}%' for val in row] for row in matrix_data],
        texttemplate='%{text}',
        textfont={"size": 12},
        hovertemplate='<b>%{y}</b><br>' +
                      '%{x}: %{z:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title="Performance Metrics Comparison",
        height=300 + len(scenarios) * 40,
        xaxis_title="Metrics",
        yaxis_title="Investment Strategy"
    )

    return fig


def create_savings_timeline_chart(scenarios: List, education_year: int) -> go.Figure:
    """Create timeline chart showing savings progression.

    Args:
        scenarios: List of SavingsScenario objects
        education_year: Year when education starts

    Returns:
        Plotly figure showing savings timeline
    """
    if not scenarios:
        return go.Figure()

    fig = go.Figure()

    # Best scenario for timeline
    best_scenario = max(scenarios, key=lambda x: x.savings_vs_payg_inr)

    # Create timeline data (simplified)
    years = list(range(education_year - 4, education_year + 1))
    savings_progression = []

    initial_investment = best_scenario.conversion_details.get('initial_investment_inr', 5000000)
    final_value = best_scenario.conversion_details.get('final_pot_inr', initial_investment)

    # Linear progression (simplified)
    for i, year in enumerate(years):
        progress = i / (len(years) - 1)
        value = initial_investment + (final_value - initial_investment) * progress
        savings_progression.append(value)

    fig.add_trace(go.Scatter(
        x=years,
        y=savings_progression,
        mode='lines+markers',
        name='Investment Value',
        line=dict(color='green', width=4),
        marker=dict(size=10),
        fill='tonexty',
        hovertemplate='Year: %{x}<br>Value: ₹%{y:,.0f}<extra></extra>'
    ))

    # Add education start marker
    fig.add_vline(
        x=education_year,
        line_dash="dash",
        line_color="red",
        annotation_text="Education Starts"
    )

    fig.update_layout(
        title="Investment Growth Timeline",
        xaxis_title="Year",
        yaxis_title="Investment Value (₹)",
        height=400,
        showlegend=False
    )

    return fig