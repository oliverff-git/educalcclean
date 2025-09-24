"""
UK Education Savings Calculator - Streamlit Cloud Entry Point

This is the main entry point for the Streamlit Cloud deployment.
It imports and runs the full-featured GUI application.
"""

# Version for cache busting - increment to force reload
__version__ = "2.2.0"

# Import the main GUI application
from gui.education_savings_app import main
import streamlit as st

# Clear cache to ensure updated calculations are used
st.cache_data.clear()

if __name__ == "__main__":
    main()
