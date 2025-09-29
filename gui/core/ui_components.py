"""
Professional UI Components for Financial Education Calculator
Based on Streamlit Design Bible - Reusable, native components only
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# ===== PROFESSIONAL KPI COMPONENTS =====

def professional_kpi_card(label: str, value: str, delta: Optional[str] = None,
                         help_text: Optional[str] = None, highlight: bool = False) -> None:
    """
    Professional KPI card using native Streamlit container with border

    Args:
        label: KPI label (will be displayed in uppercase)
        value: Main value to display
        delta: Optional delta change indicator
        help_text: Optional help text for tooltip
        highlight: Whether to use primary color styling
    """
    with st.container(border=True):
        if highlight:
            st.markdown(f"**{label.upper()}**")
        else:
            st.caption(label.upper())

        if delta:
            st.metric(
                label="",
                value=value,
                delta=delta,
                help=help_text
            )
        else:
            st.markdown(f"### {value}")
            if help_text:
                st.caption(help_text)

def kpi_row(kpis: List[tuple]) -> None:
    """
    Display a row of KPI cards

    Args:
        kpis: List of tuples (label, value, help_text) or (label, value, delta, help_text)
    """
    cols = st.columns(len(kpis))
    for i, kpi in enumerate(kpis):
        with cols[i]:
            if len(kpi) == 3:
                professional_kpi_card(kpi[0], kpi[1], help_text=kpi[2])
            elif len(kpi) == 4:
                professional_kpi_card(kpi[0], kpi[1], kpi[2], kpi[3])


def selected_strategy_card(strategy_name: str) -> None:
    """
    Display a highlighted card showing the user's selected strategy

    Args:
        strategy_name: The name of the selected strategy
    """
    st.markdown(f"**CHOSEN STRATEGY**: {strategy_name}")
    st.caption("This is your selected approach for comparison and summary")

# ===== PROFESSIONAL DATA COMPONENTS =====

def professional_dataframe(data: pd.DataFrame,
                          column_config: Optional[Dict] = None,
                          key: Optional[str] = None) -> None:
    """
    Professional dataframe with consistent styling and configuration

    Args:
        data: DataFrame to display
        column_config: Optional column configuration
        key: Optional key for the dataframe widget
    """
    default_config = {}

    # Auto-configure common column types
    for col in data.columns:
        if data[col].dtype in ['float64', 'int64']:
            if any(keyword in col.lower() for keyword in ['amount', 'cost', 'fee', 'price', 'inr', 'gbp']):
                if 'inr' in col.lower() or '₹' in str(data[col].iloc[0] if len(data) > 0 else ''):
                    default_config[col] = st.column_config.NumberColumn(
                        col,
                        format="₹%.0f",
                        help=f"Amount in Indian Rupees"
                    )
                elif 'gbp' in col.lower() or '£' in str(data[col].iloc[0] if len(data) > 0 else ''):
                    default_config[col] = st.column_config.NumberColumn(
                        col,
                        format="£%.0f",
                        help=f"Amount in British Pounds"
                    )
            elif any(keyword in col.lower() for keyword in ['rate', 'percentage', '%']):
                default_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f%%",
                    help=f"Percentage value"
                )
        elif 'year' in col.lower():
            default_config[col] = st.column_config.NumberColumn(
                col,
                format="%d",
                help=f"Year value"
            )

    # Merge with user-provided config
    if column_config:
        default_config.update(column_config)

    st.dataframe(
        data,
        column_config=default_config,
        hide_index=True,
        use_container_width=True,
        key=key
    )

# ===== PROFESSIONAL CHART COMPONENTS =====

def create_professional_chart_layout(title: Optional[str] = None) -> Dict:
    """
    Standard professional chart layout configuration
    """
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': dict(family="system-ui, -apple-system, sans-serif", size=14),
        'margin': dict(l=20, r=20, t=40 if title else 20, b=20),
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
            titlefont=dict(color='#374151')
        ),
        'yaxis': dict(
            gridcolor='#E2E8F0',
            showgrid=True,
            linecolor='#E2E8F0',
            tickcolor='#6B7280',
            titlefont=dict(color='#374151')
        ),
        'legend': dict(
            orientation="h",
            y=-0.15,
            font=dict(color='#374151')
        )
    }

def professional_line_chart(data: pd.DataFrame, x: str, y: str,
                           title: Optional[str] = None,
                           color: str = '#1E40AF') -> go.Figure:
    """
    Create a professional line chart
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data[x],
        y=data[y],
        mode='lines+markers',
        line=dict(color=color, width=3),
        marker=dict(color=color, size=6),
        name=y
    ))

    fig.update_layout(**create_professional_chart_layout(title))
    return fig

def professional_bar_chart(data: pd.DataFrame, x: str, y: str,
                          title: Optional[str] = None,
                          color: str = '#1E40AF') -> go.Figure:
    """
    Create a professional bar chart
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data[x],
        y=data[y],
        marker_color=color,
        name=y
    ))

    fig.update_layout(**create_professional_chart_layout(title))
    return fig

# ===== NAVIGATION COMPONENTS =====

def breadcrumb_navigation(steps: List[str], current_step: int) -> None:
    """
    Professional breadcrumb navigation

    Args:
        steps: List of step names
        current_step: Current step index (0-based)
    """
    breadcrumb = " > ".join([
        f"**{step}**" if i == current_step else step
        for i, step in enumerate(steps)
    ])
    st.caption(breadcrumb)

def navigation_buttons(back_page: Optional[str] = None,
                      next_page: Optional[str] = None,
                      back_label: str = "← Back",
                      next_label: str = "Next →") -> None:
    """
    Professional navigation buttons with consistent styling

    Args:
        back_page: Page to navigate back to
        next_page: Page to navigate forward to
        back_label: Label for back button
        next_label: Label for next button
    """
    st.divider()

    if back_page and next_page:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(back_label, use_container_width=True):
                st.switch_page(back_page)
        with col3:
            if st.button(next_label, use_container_width=True, type="primary"):
                st.switch_page(next_page)
    elif back_page:
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button(back_label, use_container_width=True):
                st.switch_page(back_page)
    elif next_page:
        col1, col2 = st.columns([2, 1])
        with col2:
            if st.button(next_label, use_container_width=True, type="primary"):
                st.switch_page(next_page)

# ===== PAGE LAYOUT COMPONENTS =====

def professional_page_header(title: str, subtitle: Optional[str] = None,
                            breadcrumb_steps: Optional[List[str]] = None,
                            current_step: Optional[int] = None) -> None:
    """
    Professional page header with title, subtitle, and breadcrumb
    """
    if breadcrumb_steps and current_step is not None:
        breadcrumb_navigation(breadcrumb_steps, current_step)

    st.title(title)

    if subtitle:
        st.markdown(f"**{subtitle}**")

    st.divider()

def success_alert(message: str) -> None:
    """Professional success alert"""
    st.success(message)

def info_alert(message: str) -> None:
    """Professional info alert"""
    st.info(message)

def warning_alert(message: str) -> None:
    """Professional warning alert"""
    st.warning(message)

def error_alert(message: str) -> None:
    """Professional error alert"""
    st.error(message)

# ===== FORMATTING UTILITIES =====

def format_inr(amount: float) -> str:
    """Format amount in Indian Rupees"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.1f}Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.1f}L"
    else:
        return f"₹{amount:,.0f}"

def format_gbp(amount: float) -> str:
    """Format amount in British Pounds"""
    return f"£{amount:,.0f}"

def format_percentage(value: float) -> str:
    """Format percentage value"""
    return f"{value:.1f}%"

def format_exchange_rate(rate: float) -> str:
    """Format exchange rate"""
    return f"₹{rate:.2f}/£"

# ===== SMART BUTTON COMPONENTS =====

def smart_button(label: str, key: str, callback_func=None,
                disabled: bool = False, type: str = "secondary",
                loading_message: str = "Processing...") -> bool:
    """
    Smart button with loading state and session management

    Args:
        label: Button label
        key: Unique key for session state
        callback_func: Function to call on click
        disabled: Whether button is disabled
        type: Button type ("primary" or "secondary")
        loading_message: Message to show during loading

    Returns:
        bool: True if button was clicked
    """
    loading_key = f"{key}_loading"

    # Initialize session state
    if loading_key not in st.session_state:
        st.session_state[loading_key] = False

    def on_click():
        st.session_state[loading_key] = True
        if callback_func:
            with st.spinner(loading_message):
                callback_func()
        st.session_state[loading_key] = False

    return st.button(
        label,
        key=key,
        disabled=disabled or st.session_state[loading_key],
        type=type,
        use_container_width=True,
        on_click=on_click
    )

# ===== LOADING AND STATUS COMPONENTS =====

def show_loading_state(message: str = "Loading..."):
    """Show professional loading state"""
    return st.spinner(message)

def show_progress_bar(progress: float, message: str = "Processing"):
    """Show professional progress bar"""
    progress_bar = st.progress(0)
    status_text = st.empty()

    progress_bar.progress(progress)
    status_text.text(f'{message}: {int(progress * 100)}%')

    return progress_bar, status_text

# ===== INPUT VALIDATION HELPERS =====

def validate_required_fields(fields: Dict[str, Any]) -> List[str]:
    """
    Validate required fields and return list of missing field names

    Args:
        fields: Dict of field_name: value pairs

    Returns:
        List of missing field names
    """
    missing = []
    for field_name, value in fields.items():
        if value is None or value == "" or (isinstance(value, str) and not value.strip()):
            missing.append(field_name)
    return missing

def show_validation_errors(missing_fields: List[str]) -> None:
    """Display validation errors professionally"""
    if missing_fields:
        error_message = f"Please complete the following required fields: {', '.join(missing_fields)}"
        error_alert(error_message)