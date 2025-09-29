import streamlit as st

def configure_page(title: str = "UK Education Savings", icon: str = "", layout: str = "wide"):
    """Configure Streamlit page with consistent settings"""
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout
    )