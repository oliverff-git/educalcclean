"""
2nd Child Savers Module - Education Planning for Younger Children

This module provides functionality to plan education savings for a second/younger child
using arbitrary INR amounts and leveraging the existing calculator engine.
"""

import streamlit as st
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import pandas as pd

from gui.fee_calculator import EducationSavingsCalculator, SavingsScenario
from gui.data_processor import EducationDataProcessor


class SecondChildAdapter:
    """
    Adapter class that wraps the existing EducationSavingsCalculator to handle
    arbitrary INR amounts for second child education planning.
    """

    def __init__(self, calculator: EducationSavingsCalculator, data_processor: EducationDataProcessor):
        self.calculator = calculator
        self.data_processor = data_processor

    def calculate_savings_for_inr_amount(
        self,
        inr_amount: float,
        conversion_year: int,
        education_year: int,
        university: Optional[str] = None,
        programme: Optional[str] = None
    ) -> Tuple[SavingsScenario, Dict]:
        """
        Calculate savings scenario for arbitrary INR amount.

        Args:
            inr_amount: Amount in INR to invest
            conversion_year: Year to convert INR to GBP
            education_year: Year when education starts
            university: Optional university name (for metadata)
            programme: Optional programme name (for coverage calculation)

        Returns:
            Tuple of (SavingsScenario, enhanced_metrics_dict)
        """
        if inr_amount <= 0:
            raise ValueError("INR amount must be positive")

        if education_year <= conversion_year:
            raise ValueError("Education year must be after conversion year")

        # Get FX rate for conversion year
        fx_rate_conversion = self.data_processor.get_september_fx_rate(conversion_year)
        gbp_amount = inr_amount / fx_rate_conversion

        # Use existing calculator with arbitrary amount
        scenario = self.calculator.calculate_early_conversion_scenario(
            university=university or "2nd Child",
            programme=programme or "Future Education",
            conversion_year=conversion_year,
            education_year=education_year,
            total_gbp_needed=gbp_amount
        )

        # Calculate pay-as-you-go for comparison (what you'd pay if waiting)
        payg_scenario = self.calculator.calculate_payg_scenario(
            university=university or "2nd Child",
            programme=programme or "Future Education",
            education_year=education_year,
            total_gbp_needed=gbp_amount
        )

        # Calculate coverage if programme provided
        coverage_percentage = None
        if programme and university:
            try:
                coverage_percentage = self._calculate_programme_coverage(
                    gbp_amount, university, programme, education_year
                )
            except:
                coverage_percentage = None

        # Enhanced metrics for Indian parent clarity
        metrics = {
            "input_inr": inr_amount,
            "gbp_equivalent": gbp_amount,
            "savings_inr": scenario.savings_vs_payg_inr,
            "savings_percentage": scenario.savings_percentage,
            "fx_at_conversion": scenario.exchange_rate_used,
            "fx_at_education": payg_scenario.exchange_rate_used,
            "fx_benefit_per_pound": payg_scenario.exchange_rate_used - scenario.exchange_rate_used,
            "total_fx_benefit": (payg_scenario.exchange_rate_used - scenario.exchange_rate_used) * gbp_amount,
            "coverage_vs_programme": coverage_percentage,
            "payg_total_inr": payg_scenario.total_cost_inr,
            "early_conversion_inr": scenario.total_cost_inr,
            "data_quality": "EXCELLENT" if education_year <= 2026 else "PROJECTED"
        }

        return scenario, metrics

    def _calculate_programme_coverage(
        self,
        gbp_amount: float,
        university: str,
        programme: str,
        education_year: int
    ) -> float:
        """Calculate what percentage of programme fees the GBP amount covers."""
        try:
            # Get course info and project fee to education year
            course_info = self.data_processor.get_course_info(university, programme)
            if not course_info:
                return None

            # Project the fee to education year
            projected_fee_gbp = self.data_processor.project_fee(
                course_info['fee_2023_gbp'],
                2023,
                education_year,
                course_info['cagr_2020_2023']
            )

            # Assume 3-year programme for total cost
            total_programme_cost = projected_fee_gbp * 3

            coverage = (gbp_amount / total_programme_cost) * 100
            return min(coverage, 100.0)  # Cap at 100%

        except Exception:
            return None


def format_inr(amount: float) -> str:
    """Format INR amount in Indian number system (Lakh/Crore)."""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.1f}Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.1f}L"
    else:
        return f"₹{amount:,.0f}"


def render_second_child_sidebar(
    calculator: EducationSavingsCalculator,
    data_processor: EducationDataProcessor
) -> Dict:
    """
    Render sidebar UI for 2nd child configuration.

    Returns:
        Configuration dictionary with user inputs
    """
    st.sidebar.markdown("---")
    st.sidebar.header("👶 2nd Child Planner")

    enabled = st.sidebar.checkbox(
        "Enable 2nd Child Savings",
        value=False,
        help="Plan education savings for a younger child with any INR amount"
    )

    if not enabled:
        return {"enabled": False}

    with st.sidebar.expander("👶 2nd Child Configuration", expanded=True):
        # Course selection option
        use_same = st.checkbox(
            "📚 Use same university/course as 1st child",
            value=True,
            help="Reuse the selected university and programme from above"
        )

        if not use_same:
            # Get available universities and programmes
            universities = data_processor.get_universities()
            selected_uni = st.selectbox(
                "🏫 University",
                options=universities,
                help="Select university for coverage calculation"
            )

            programmes = data_processor.get_courses(selected_uni)
            selected_prog = st.selectbox(
                "📚 Programme",
                options=programmes,
                help="Select programme for fee coverage analysis"
            )

            university = selected_uni
            programme = selected_prog
        else:
            # Get from main app session state
            university = st.session_state.get("selected_university", "Generic")
            programme = st.session_state.get("selected_programme", "Generic")

        # Timeline selection
        current_year = 2024
        conversion_year = st.selectbox(
            "📅 Start Saving Year",
            options=list(range(current_year, current_year + 4)),
            index=0,
            help="Year when you convert INR to GBP and invest"
        )

        education_year = st.selectbox(
            "🎓 Education Start Year",
            options=list(range(conversion_year + 1, current_year + 8)),
            index=2,  # Default to 3 years later
            help="When the child starts university"
        )

        # Amount input with live formatting
        amount_inr = st.number_input(
            "💰 Investment Amount (₹)",
            min_value=100000,
            max_value=100000000,
            value=2000000,  # Default 20 lakh
            step=100000,
            format="%d",
            help="Any INR amount you want to save for the child"
        )

        # Live formatting display
        st.caption(f"💵 **{format_inr(amount_inr)}**")

        # Show basic calculation preview
        try:
            fx_rate = data_processor.get_september_fx_rate(conversion_year)
            gbp_equiv = amount_inr / fx_rate
            st.caption(f"🏦 ≈ £{gbp_equiv:,.0f} @ ₹{fx_rate:.2f}/£")
        except:
            st.caption("Exchange rate data loading...")

    return {
        "enabled": True,
        "amount_inr": amount_inr,
        "conversion_year": conversion_year,
        "education_year": education_year,
        "university": university,
        "programme": programme,
        "use_same_course": use_same
    }


def render_second_child_results(
    scenario: SavingsScenario,
    metrics: Dict,
    config: Dict
):
    """
    Render main panel display for 2nd child results.

    Args:
        scenario: SavingsScenario from calculator
        metrics: Enhanced metrics dictionary
        config: Configuration from sidebar
    """
    st.markdown("---")
    st.subheader("👶 2nd Child Education Savings Analysis")

    # Key metrics in responsive columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💵 Your Investment",
            format_inr(metrics["input_inr"]),
            help="Amount you invest today in INR"
        )

    with col2:
        savings_color = "normal" if metrics["savings_inr"] > 0 else "inverse"
        st.metric(
            "💰 Total Savings",
            format_inr(metrics["savings_inr"]),
            f"{metrics['savings_percentage']:.1f}%",
            delta_color=savings_color,
            help="How much you save by converting early vs waiting"
        )

    with col3:
        fx_benefit_color = "normal" if metrics["fx_benefit_per_pound"] > 0 else "inverse"
        st.metric(
            "📈 FX Advantage",
            f"₹{metrics['fx_benefit_per_pound']:.2f}/£",
            format_inr(metrics["total_fx_benefit"]),
            delta_color=fx_benefit_color,
            help="Exchange rate benefit from early conversion"
        )

    with col4:
        if metrics.get("coverage_vs_programme"):
            coverage_color = "normal" if metrics["coverage_vs_programme"] >= 80 else "inverse"
            st.metric(
                "📚 Programme Coverage",
                f"{metrics['coverage_vs_programme']:.0f}%",
                delta_color=coverage_color,
                help="% of 3-year programme fees covered"
            )
        else:
            st.metric(
                "📊 Planning Horizon",
                f"{config['education_year'] - config['conversion_year']} years",
                help="Years between investment and education start"
            )

    # Comparison visualization
    with st.expander("📊 Early vs Late Conversion Comparison", expanded=True):
        fig = create_second_child_comparison_chart(scenario, metrics, config)
        st.plotly_chart(fig, use_container_width=True)

    # Detailed breakdown
    with st.expander("📋 Calculation Breakdown"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Early Conversion (Your Plan)**")
            st.write(f"• Investment: {format_inr(metrics['input_inr'])}")
            st.write(f"• Converts to: £{metrics['gbp_equivalent']:,.0f}")
            st.write(f"• FX Rate: ₹{metrics['fx_at_conversion']:.2f}/£")
            st.write(f"• Total Cost: {format_inr(scenario.total_cost_inr)}")

        with col2:
            st.markdown("**Pay-as-You-Go (Wait & Pay)**")
            st.write(f"• Same GBP Amount: £{metrics['gbp_equivalent']:,.0f}")
            st.write(f"• Future FX Rate: ₹{metrics['fx_at_education']:.2f}/£")
            st.write(f"• Total Cost: {format_inr(metrics['payg_total_inr'])}")
            st.write(f"• **Extra Cost: {format_inr(metrics['payg_total_inr'] - scenario.total_cost_inr)}**")

    # Data quality and disclaimers
    st.info(f"📊 Data Quality: **{metrics['data_quality']}** | " +
            f"Exchange rates {('historical' if config['education_year'] <= 2026 else 'projected')} | " +
            "Future projections are estimates")


def create_second_child_comparison_chart(
    scenario: SavingsScenario,
    metrics: Dict,
    config: Dict
) -> go.Figure:
    """
    Create comparison chart showing early vs late conversion costs.

    Returns:
        Plotly figure
    """
    strategies = ['Early Conversion<br>(Your Plan)', 'Pay-as-You-Go<br>(Wait & Pay)']
    costs_inr = [scenario.total_cost_inr, metrics['payg_total_inr']]
    colors = ['#2E8B57', '#CD5C5C']  # Green for good, Red for expensive

    fig = go.Figure(data=[
        go.Bar(
            x=strategies,
            y=costs_inr,
            text=[format_inr(cost) for cost in costs_inr],
            textposition='auto',
            marker_color=colors,
            hovertemplate='<b>%{x}</b><br>Total Cost: ₹%{y:,.0f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title=f"2nd Child: {format_inr(metrics['input_inr'])} Investment Comparison",
        xaxis_title="Strategy",
        yaxis_title="Total Cost (₹)",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Add savings annotation
    if metrics["savings_inr"] > 0:
        fig.add_annotation(
            x=0.5,
            y=max(costs_inr) * 0.9,
            text=f"<b>You Save: {format_inr(metrics['savings_inr'])}</b><br>({metrics['savings_percentage']:.1f}%)",
            showarrow=False,
            font=dict(size=14, color="green"),
            bgcolor="lightgreen",
            bordercolor="green",
            borderwidth=1
        )

    return fig