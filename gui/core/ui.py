import streamlit as st
from typing import List, Tuple

def kpi_row(items: List[Tuple[str, str, str]]):
    """Render a row of st.metric KPIs using native Streamlit components
    items: List of (label, value, help_text) tuples
    """
    if not items:
        return

    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        with col:
            st.metric(label, value, help=help_text)

def success_alert(text: str):
    """Display success message using native Streamlit"""
    st.success(text)

def info_card(title: str, content: str):
    """Display info card using native Streamlit"""
    st.info(f"**{title}**\n\n{content}")

def inline_svg_arrow(size: int = 18) -> str:
    """Return inline SVG arrow to replace Material Icons"""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none"
         xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;">
      <path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """

def format_inr(amount: float) -> str:
    """Format INR amounts in lakhs/crores"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"

def format_gbp(amount: float) -> str:
    """Format GBP amounts"""
    return f"£{amount:,.0f}"

def format_percentage(pct: float) -> str:
    """Format percentage"""
    return f"{pct:.1f}%"