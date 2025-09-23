"""
Mobile-Optimized Chart Rendering
Provides touch-friendly charts optimized for mobile and tablet viewing.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any


class MobileChartRenderer:
    """Renders charts optimized for mobile devices."""

    def __init__(self, device_type: str):
        """Initialize with device type."""
        self.device_type = device_type
        self.is_mobile = device_type == 'mobile'
        self.is_tablet = device_type == 'tablet'

    def create_mobile_fee_projection_chart(self, projections_data: Dict) -> go.Figure:
        """Create mobile-optimized fee projection chart."""
        course_info = projections_data['course_info']
        fee_projections = projections_data['fee_projections']

        # Prepare data
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
                line=dict(color='#1f77b4', width=2 if self.is_mobile else 3),
                marker=dict(size=6 if self.is_mobile else 8),
                hovertemplate='<b>%{x}</b><br>Fee: £%{y:,.0f}<extra></extra>'
            ))

        # Projected data
        if projected_years:
            connect_years = [historical_years[-1]] + projected_years if historical_years else projected_years
            connect_fees = [fee_projections[y] for y in connect_years]

            fig.add_trace(go.Scatter(
                x=connect_years,
                y=connect_fees,
                mode='lines+markers',
                name='Projected',
                line=dict(color='#ff7f0e', width=2 if self.is_mobile else 3, dash='dash'),
                marker=dict(size=6 if self.is_mobile else 8),
                hovertemplate='<b>%{x}</b><br>Fee: £%{y:,.0f}<extra></extra>'
            ))

        # Mobile-specific layout
        title_text = f"{course_info['university']} - {course_info['programme']}"
        if self.is_mobile:
            # Shorter title for mobile
            title_text = f"{course_info['university']}<br>Fee Projections"
            subtitle = f"CAGR: {course_info['cagr_pct']:.1f}%"
        else:
            title_text += f"<br>Fee Projections (CAGR: {course_info['cagr_pct']:.2f}%)"
            subtitle = None

        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=14 if self.is_mobile else 16),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="Year",
            yaxis_title="Annual Fee (GBP)",
            height=250 if self.is_mobile else (300 if self.is_tablet else 400),
            margin=dict(
                l=20 if self.is_mobile else 40,
                r=20 if self.is_mobile else 40,
                t=60 if self.is_mobile else 80,
                b=40 if self.is_mobile else 50
            ),
            hovermode='x unified',
            font=dict(size=10 if self.is_mobile else 12),
            legend=dict(
                orientation="h" if self.is_mobile else "v",
                yanchor="bottom" if self.is_mobile else "top",
                y=-0.3 if self.is_mobile else 1,
                xanchor="center" if self.is_mobile else "left",
                x=0.5 if self.is_mobile else 1.02
            )
        )

        # Mobile-friendly axis formatting
        fig.update_xaxes(
            tickangle=45 if self.is_mobile else 0,
            tickfont=dict(size=8 if self.is_mobile else 10)
        )
        fig.update_yaxes(
            tickformat='£,.0f',
            tickfont=dict(size=8 if self.is_mobile else 10)
        )

        if subtitle and self.is_mobile:
            fig.add_annotation(
                text=subtitle,
                xref="paper", yref="paper",
                x=0.5, y=1.05,
                xanchor="center", yanchor="bottom",
                font=dict(size=10, color="gray"),
                showarrow=False
            )

        return fig

    def create_mobile_fx_projection_chart(self, projections_data: Dict) -> go.Figure:
        """Create mobile-optimized exchange rate chart."""
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
                line=dict(color='#2ca02c', width=2 if self.is_mobile else 3),
                marker=dict(size=6 if self.is_mobile else 8),
                hovertemplate='<b>%{x}</b><br>Rate: ₹%{y:.2f}<extra></extra>'
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
                line=dict(color='#d62728', width=2 if self.is_mobile else 3, dash='dash'),
                marker=dict(size=6 if self.is_mobile else 8),
                hovertemplate='<b>%{x}</b><br>Rate: ₹%{y:.2f}<extra></extra>'
            ))

        # Mobile-optimized layout
        title_text = "GBP/INR Exchange Rate"
        if self.is_mobile:
            title_text += "<br>Projections"
            subtitle = "Historical CAGR: 4.18%"
        else:
            title_text += " Projections<br>(Historical CAGR: 4.18% - Conservative)"
            subtitle = None

        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=14 if self.is_mobile else 16),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="Year",
            yaxis_title="INR per GBP",
            height=250 if self.is_mobile else (300 if self.is_tablet else 400),
            margin=dict(
                l=20 if self.is_mobile else 40,
                r=20 if self.is_mobile else 40,
                t=60 if self.is_mobile else 80,
                b=40 if self.is_mobile else 50
            ),
            hovermode='x unified',
            font=dict(size=10 if self.is_mobile else 12),
            legend=dict(
                orientation="h" if self.is_mobile else "v",
                yanchor="bottom" if self.is_mobile else "top",
                y=-0.3 if self.is_mobile else 1,
                xanchor="center" if self.is_mobile else "left",
                x=0.5 if self.is_mobile else 1.02
            )
        )

        # Mobile-friendly axis formatting
        fig.update_xaxes(
            tickangle=45 if self.is_mobile else 0,
            tickfont=dict(size=8 if self.is_mobile else 10)
        )
        fig.update_yaxes(
            tickformat='₹,.0f',
            tickfont=dict(size=8 if self.is_mobile else 10)
        )

        if subtitle and self.is_mobile:
            fig.add_annotation(
                text=subtitle,
                xref="paper", yref="paper",
                x=0.5, y=1.05,
                xanchor="center", yanchor="bottom",
                font=dict(size=10, color="gray"),
                showarrow=False
            )

        return fig

    def create_mobile_savings_comparison_chart(self, scenarios: List) -> go.Figure:
        """Create mobile-optimized savings comparison chart."""
        if not scenarios:
            return None

        # Prepare data
        strategy_names = [s.strategy_name for s in scenarios]
        costs_inr = [s.total_cost_inr for s in scenarios]
        savings_inr = [s.savings_vs_payg_inr for s in scenarios]
        savings_pct = [s.savings_percentage for s in scenarios]

        # Shorten strategy names for mobile
        if self.is_mobile:
            short_names = []
            for name in strategy_names:
                if "Up Front 100%" in name:
                    year = name.split()[-1]
                    short_names.append(f"100% {year}")
                elif "Staggered" in name:
                    year = name.split()[-1]
                    short_names.append(f"Staggered {year}")
                elif "Pay-As-You-Go" in name:
                    short_names.append("Pay-As-Go")
                else:
                    short_names.append(name[:12] + "..." if len(name) > 12 else name)
            display_names = short_names
        else:
            display_names = strategy_names

        # Create colors
        colors = ['#2ca02c' if s > 0 else '#d62728' for s in savings_inr]

        if self.is_mobile:
            # Single chart for mobile - focus on savings
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=display_names,
                y=savings_inr,
                name='Savings vs Pay-As-You-Go',
                marker_color=colors,
                text=[f"₹{s/100000:.1f}L<br>({p:.1f}%)" if s >= 100000 else f"₹{s:,.0f}<br>({p:.1f}%)"
                      for s, p in zip(savings_inr, savings_pct)],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Savings: ₹%{y:,.0f}<extra></extra>'
            ))

            fig.update_layout(
                title=dict(
                    text="Savings Comparison",
                    font=dict(size=14),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title="Strategy",
                yaxis_title="Savings (INR)",
                height=300,
                margin=dict(l=20, r=20, t=50, b=60),
                showlegend=False,
                font=dict(size=10)
            )

            fig.update_xaxes(
                tickangle=45,
                tickfont=dict(size=8)
            )
            fig.update_yaxes(
                tickformat='₹,.0f',
                tickfont=dict(size=8)
            )

        else:
            # Two-chart layout for tablet/desktop
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Total Cost (INR)', 'Savings vs Pay-As-You-Go'),
                vertical_spacing=0.15
            )

            # Cost comparison
            fig.add_trace(
                go.Bar(
                    x=display_names,
                    y=costs_inr,
                    name='Total Cost',
                    marker_color='#1f77b4',
                    text=[f"₹{c/100000:.1f}L" if c >= 100000 else f"₹{c:,.0f}" for c in costs_inr],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Cost: ₹%{y:,.0f}<extra></extra>'
                ),
                row=1, col=1
            )

            # Savings comparison
            fig.add_trace(
                go.Bar(
                    x=display_names,
                    y=savings_inr,
                    name='Savings',
                    marker_color=colors,
                    text=[f"₹{s/100000:.1f}L<br>({p:.1f}%)" if s >= 100000 else f"₹{s:,.0f}<br>({p:.1f}%)"
                          for s, p in zip(savings_inr, savings_pct)],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Savings: ₹%{y:,.0f}<extra></extra>'
                ),
                row=2, col=1
            )

            height = 300 if self.is_tablet else 600
            fig.update_layout(
                height=height,
                showlegend=False,
                title_text="Savings Strategy Comparison",
                font=dict(size=10 if self.is_tablet else 12)
            )

            # Update y-axis formats
            fig.update_yaxes(tickformat='₹,.0f', row=1, col=1)
            fig.update_yaxes(tickformat='₹,.0f', row=2, col=1)

            # Update x-axis
            fig.update_xaxes(
                tickangle=45 if self.is_tablet else 0,
                tickfont=dict(size=8 if self.is_tablet else 10)
            )

        return fig

    def get_chart_config(self) -> Dict[str, Any]:
        """Get chart configuration for device type."""
        config = {
            'displaylogo': False,
            'responsive': True,
            'doubleClick': 'reset+autosize'
        }

        if self.is_mobile:
            config.update({
                'displayModeBar': False,
                'scrollZoom': False,
                'modeBarButtonsToRemove': [
                    'pan2d', 'select2d', 'lasso2d', 'resetScale2d',
                    'toggleSpikelines', 'hoverCompareCartesian'
                ]
            })
        elif self.is_tablet:
            config.update({
                'displayModeBar': True,
                'scrollZoom': False,
                'modeBarButtonsToRemove': [
                    'pan2d', 'select2d', 'lasso2d'
                ]
            })
        else:
            config.update({
                'displayModeBar': True,
                'scrollZoom': True
            })

        return config