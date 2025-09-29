"""
Style Injector - Professional CSS styling for Streamlit app
Provides consistent card layouts and typography without breaking existing functionality.
"""

import streamlit as st


def inject_styles():
    """Inject professional CSS styles into the Streamlit app."""

    css = """
    <style>
    /* System-ui font stack for better cross-platform consistency */
    .main .block-container,
    .sidebar .sidebar-content,
    div[data-testid="stMarkdown"],
    div[data-testid="stText"],
    h1, h2, h3, h4, h5, h6,
    p, span, div, label {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
                     Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
    }

    /* Typography hierarchy using only bold/regular weights */
    h1, h2, h3, h4, h5, h6,
    strong, b,
    .stMarkdown strong,
    .stMarkdown b {
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    /* Card container styling */
    .card {
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        background-color: #ffffff !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06) !important;
    }

    /* Apply card styling to key Streamlit components */
    div[data-testid="metric-container"],
    div[data-testid="expander"],
    .stSelectbox > div,
    .stSlider > div,
    .stNumberInput > div,
    div[data-testid="stAlert"] {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        background-color: #ffffff;
    }

    /* Subtle hover effects for interactive elements */
    div[data-testid="metric-container"]:hover,
    div[data-testid="expander"]:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: box-shadow 0.2s ease-in-out;
    }

    /* Clean up metric container styling */
    div[data-testid="metric-container"] > div {
        background: transparent !important;
        border: none !important;
    }

    /* Consistent button styling */
    .stButton > button {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
                     Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button:hover {
        background-color: #f8fafc !important;
        border-color: #9ca3af !important;
    }

    /* Sidebar spacing improvements */
    .sidebar .sidebar-content {
        padding-top: 16px !important;
    }

    /* Chart container styling */
    .js-plotly-plot {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        margin: 8px 0;
        overflow: hidden;
    }

    /* Clean up default Streamlit spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Success/Warning/Error messages with consistent styling */
    .stAlert {
        border-radius: 8px !important;
        border-left: 4px solid !important;
    }

    .stSuccess {
        border-left-color: #10b981 !important;
        background-color: #f0fdf4 !important;
    }

    .stWarning {
        border-left-color: #f59e0b !important;
        background-color: #fffbeb !important;
    }

    .stError {
        border-left-color: #ef4444 !important;
        background-color: #fef2f2 !important;
    }

    .stInfo {
        border-left-color: #3b82f6 !important;
        background-color: #eff6ff !important;
    }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)