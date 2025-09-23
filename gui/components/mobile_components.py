"""
Mobile-Optimized UI Components
Provides mobile-friendly versions of UI components for the Education Savings Calculator.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class MobileMetric:
    """Mobile-optimized metric display."""
    label: str
    value: str
    delta: Optional[str] = None
    help_text: Optional[str] = None
    highlight: bool = False


class MobileComponentRenderer:
    """Renders mobile-optimized components."""

    def __init__(self, device_type: str):
        """Initialize with device type."""
        self.device_type = device_type
        self.is_mobile = device_type == 'mobile'
        self.is_tablet = device_type == 'tablet'

    def render_metrics_section(self, metrics: List[MobileMetric], title: str = None) -> None:
        """Render metrics optimized for mobile."""
        if title:
            if self.is_mobile:
                st.subheader(title)
            else:
                st.header(title)

        if self.is_mobile:
            # Stack all metrics vertically on mobile
            for metric in metrics:
                self._render_single_metric_mobile(metric)
        elif self.is_tablet:
            # 2-column grid for tablets
            cols = st.columns(2)
            for i, metric in enumerate(metrics):
                with cols[i % 2]:
                    self._render_single_metric_tablet(metric)
        else:
            # Standard horizontal layout for desktop
            cols = st.columns(len(metrics))
            for i, metric in enumerate(metrics):
                with cols[i]:
                    st.metric(
                        metric.label,
                        metric.value,
                        delta=metric.delta,
                        help=metric.help_text
                    )

    def _render_single_metric_mobile(self, metric: MobileMetric) -> None:
        """Render single metric for mobile."""
        # Use card-style container for mobile metrics
        if metric.highlight:
            bg_color = "#e8f5e8"
            border_color = "#4caf50"
        else:
            bg_color = "#f8f9fa"
            border_color = "#dee2e6"

        metric_html = f"""
        <div style="
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 14px; color: #6c757d; margin-bottom: 4px;">
                {metric.label}
            </div>
            <div style="font-size: 24px; font-weight: bold; color: #212529;">
                {metric.value}
            </div>
            {f'<div style="font-size: 14px; color: #28a745; margin-top: 4px;">{metric.delta}</div>' if metric.delta else ''}
        </div>
        """
        st.markdown(metric_html, unsafe_allow_html=True)

        if metric.help_text:
            with st.expander("ℹ️ Details", expanded=False):
                st.caption(metric.help_text)

    def _render_single_metric_tablet(self, metric: MobileMetric) -> None:
        """Render single metric for tablet."""
        st.metric(
            metric.label,
            metric.value,
            delta=metric.delta,
            help=metric.help_text
        )

    def render_expandable_section(self, title: str, content_func, expanded: bool = False, icon: str = "📊") -> None:
        """Render expandable section optimized for mobile."""
        if self.is_mobile:
            # Always use expanders on mobile
            with st.expander(f"{icon} {title}", expanded=expanded):
                content_func()
        else:
            # Use regular sections on larger screens
            st.subheader(f"{icon} {title}")
            content_func()

    def render_mobile_chart(self, fig, title: str = None, description: str = None) -> None:
        """Render chart optimized for mobile viewing."""
        if title:
            if self.is_mobile:
                st.markdown(f"**{title}**")
            else:
                st.subheader(title)

        if description and not self.is_mobile:
            st.caption(description)

        # Mobile-specific chart configuration
        if self.is_mobile:
            # Compact layout for mobile
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=30, b=20),
                font=dict(size=10),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                )
            )

            # Simplify mobile charts
            fig.update_xaxes(tickangle=45, tickfont=dict(size=8))
            fig.update_yaxes(tickfont=dict(size=8))

        elif self.is_tablet:
            fig.update_layout(
                height=300,
                margin=dict(l=30, r=30, t=40, b=30),
                font=dict(size=11)
            )

        # Disable some interactions for touch devices
        config = {
            'displayModeBar': not self.is_mobile,
            'scrollZoom': not self.is_mobile,
            'doubleClick': 'reset+autosize',
            'displaylogo': False,
            'responsive': True
        }

        if self.is_mobile:
            config['modeBarButtonsToRemove'] = [
                'pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'toggleSpikelines'
            ]

        st.plotly_chart(fig, use_container_width=True, config=config)

        if description and self.is_mobile:
            st.caption(description)

    def render_data_table(self, df: pd.DataFrame, title: str = None, max_rows: int = None) -> None:
        """Render data table optimized for mobile."""
        if title:
            if self.is_mobile:
                st.markdown(f"**{title}**")
            else:
                st.subheader(title)

        if self.is_mobile:
            # Limit rows on mobile for performance
            display_df = df.head(max_rows or 5) if max_rows else df

            # Make table more mobile-friendly
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                height=min(250, len(display_df) * 35 + 50)
            )

            if max_rows and len(df) > max_rows:
                with st.expander(f"Show all {len(df)} rows"):
                    st.dataframe(df, hide_index=True, use_container_width=True)

        else:
            st.dataframe(df, hide_index=True, use_container_width=True)

    def render_scenario_cards(self, scenarios: List[Any]) -> None:
        """Render scenario comparison as cards for mobile."""
        if not scenarios:
            st.warning("No scenarios available")
            return

        if self.is_mobile:
            # Card layout for mobile
            for i, scenario in enumerate(scenarios):
                is_best = i == 0
                self._render_scenario_card_mobile(scenario, is_best, i + 1)
        else:
            # Standard sidebar layout for larger screens
            for i, scenario in enumerate(scenarios):
                with st.expander(f"{i+1}. {scenario.strategy_name}", expanded=(i==0)):
                    self._render_scenario_details(scenario)

    def _render_scenario_card_mobile(self, scenario: Any, is_best: bool, rank: int) -> None:
        """Render individual scenario card for mobile."""
        # Card styling
        if is_best:
            bg_color = "#e8f5e8"
            border_color = "#4caf50"
            badge = "🏆 BEST"
        else:
            bg_color = "#f8f9fa"
            border_color = "#dee2e6"
            badge = f"#{rank}"

        card_html = f"""
        <div style="
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: 12px;
            padding: 16px;
            margin: 12px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: bold; color: #212529;">{scenario.strategy_name}</span>
                <span style="background-color: {border_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">
                    {badge}
                </span>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        # Metrics in card
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Cost", self._format_inr(scenario.total_cost_inr))
        with col2:
            if scenario.savings_vs_payg_inr > 0:
                st.metric(
                    "Savings",
                    self._format_inr(scenario.savings_vs_payg_inr),
                    delta=f"{scenario.savings_percentage:.1f}%"
                )
            else:
                st.metric("Type", "Baseline")

        # Additional details in expander
        with st.expander("💡 Details", expanded=False):
            self._render_scenario_details(scenario)

    def _render_scenario_details(self, scenario: Any) -> None:
        """Render detailed scenario information."""
        if scenario.exchange_rate_used > 0:
            st.metric("Exchange Rate", f"₹{scenario.exchange_rate_used:.2f}/£")

        # Breakdown details
        breakdown = scenario.breakdown
        if 'uk_earnings' in breakdown and breakdown['uk_earnings']['total_interest_gbp'] > 0:
            uk_earnings = breakdown['uk_earnings']
            st.caption(
                f"UK Interest: £{uk_earnings['total_interest_gbp']:.0f} "
                f"({uk_earnings['avg_interest_rate']*100:.1f}% avg BoE rate)"
            )

    def _format_inr(self, amount: float) -> str:
        """Format INR amounts in lakhs/crores."""
        if amount >= 10000000:  # 1 crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.0f}"

    def render_mobile_navigation(self) -> str:
        """Render mobile navigation menu."""
        if self.is_mobile:
            st.sidebar.markdown("### 📱 Quick Navigation")

            nav_options = [
                "📊 Analysis",
                "💰 Scenarios",
                "📈 Projections",
                "📋 Exchange Rates",
                "ℹ️ Help"
            ]

            selected = st.sidebar.selectbox(
                "Go to section:",
                nav_options,
                index=0,
                key="mobile_nav"
            )

            return selected.split(" ", 1)[1]  # Return section name without emoji

        return "Analysis"  # Default for non-mobile

    def add_mobile_styles(self) -> None:
        """Add mobile-specific CSS styles."""
        if self.is_mobile:
            mobile_css = """
            <style>
            /* Mobile-optimized styles */
            .main .block-container {
                padding-top: 0.5rem;
                padding-bottom: 1rem;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
                max-width: 100%;
            }

            /* Larger touch targets */
            .stSelectbox > div > div {
                min-height: 44px;
            }

            .stButton > button {
                width: 100%;
                min-height: 44px;
                font-size: 16px;
            }

            /* Better mobile metrics */
            [data-testid="metric-container"] {
                margin-bottom: 1rem;
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            /* Responsive charts */
            .js-plotly-plot {
                width: 100% !important;
            }

            /* Mobile-friendly expanders */
            .streamlit-expander {
                margin-bottom: 0.5rem;
            }

            .streamlit-expander > div > div > div {
                padding: 0.75rem;
            }

            /* Hide sidebar on mobile by default */
            @media (max-width: 768px) {
                .css-1d391kg {
                    display: none;
                }
            }
            </style>
            """
            st.markdown(mobile_css, unsafe_allow_html=True)