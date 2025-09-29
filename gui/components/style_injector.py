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
    h2, h3, h4, h5, h6,
    p, span, div, label {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
                     Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
    }

    /* Main title - larger font size */
    h1 {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
                     Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        line-height: 1.4 !important;
        margin-bottom: 1rem !important;
    }

    /* Typography hierarchy using only bold/regular weights */
    h2, h3, h4, h5, h6,
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
    .stNumberInput > div {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        background-color: #ffffff;
    }

    /* Professional metric container styling */
    div[data-testid="metric-container"] {
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 20px !important;
        margin: 12px 0 !important;
        background-color: #ffffff !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.08) !important;
    }

    /* Metric values - make bold */
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        font-weight: 700 !important;
        font-size: 16px !important;
        color: #1f2937 !important;
    }

    /* Alert styling - clean borders only */
    div[data-testid="stAlert"] {
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        background-color: #ffffff !important;
        border-left: 4px solid #3b82f6 !important;
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

    /* Success/Warning/Error messages - clean professional styling */
    .stSuccess {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-left: 4px solid #10b981 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
    }

    .stWarning {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-left: 4px solid #f59e0b !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
    }

    .stError {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
    }

    .stInfo {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
    }

    /* Remove any residual colored backgrounds */
    div[data-testid="stAlert"] > div {
        background-color: transparent !important;
    }

    /* Fix Material Icon fallback text issues */
    /* Hide keyboard_arrow text fallbacks and replace with Unicode arrows */
    .streamlit-expanderHeader::before {
        content: "▶ " !important;
        font-size: 12px !important;
        color: #6b7280 !important;
        margin-right: 8px !important;
    }

    /* Hide the Material Icon fallback text */
    .streamlit-expanderHeader span[title*="keyboard"],
    span:contains("keyboard_arrow_right"),
    span:contains("keyboard_arrow_down"),
    span:contains("keyboard_double_arrow_right") {
        display: none !important;
    }

    /* Alternative approach - replace text content directly */
    div[data-testid="stExpander"] summary {
        position: relative;
    }

    div[data-testid="stExpander"] summary::before {
        content: "→ ";
        position: absolute;
        left: 0;
        color: #6b7280;
        font-size: 14px;
    }

    /* Hide any text that contains keyboard references */
    *:contains("keyboard_arrow_right"),
    *:contains("keyboard_arrow_down"),
    *:contains("keyboard_double_arrow_right") {
        font-size: 0 !important;
    }

    /* Clean replacement for expander arrows */
    div[data-testid="stExpander"] > div > summary > div > p {
        position: relative;
        padding-left: 20px;
    }

    div[data-testid="stExpander"] > div > summary > div > p::before {
        content: "▶";
        position: absolute;
        left: 0;
        color: #6b7280;
        font-size: 12px;
        top: 2px;
    }

    /* When expanded, change arrow direction */
    div[data-testid="stExpander"][open] > div > summary > div > p::before {
        content: "▼";
    }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)