"""
Professional Financial Institution Styling
Clean, minimal CSS that enhances Streamlit without breaking functionality.
"""

import streamlit as st


def apply_professional_styling():
    """Apply clean financial institution styling to Streamlit app."""

    css = """
    <style>
    /* Typography - clean hierarchy */
    .main .block-container,
    .sidebar .sidebar-content,
    div[data-testid="stMarkdown"],
    div[data-testid="stText"],
    h2, h3, h4, h5, h6,
    p, span, div, label {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
                     Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
        color: #111827 !important;
    }

    /* Main title - larger and bold */
    h1 {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
                     Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #111827 !important;
        margin-bottom: 1rem !important;
    }

    /* Bold text for emphasis only */
    h2, h3, h4, h5, h6,
    strong, b,
    .stMarkdown strong,
    .stMarkdown b {
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    /* Professional metric containers */
    div[data-testid="metric-container"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 6px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        background-color: #FAFAFA !important;
        box-shadow: none !important;
    }

    /* Metric values - bold */
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #111827 !important;
    }

    /* Clean alert/info boxes - no colored backgrounds */
    .stSuccess,
    .stInfo,
    .stWarning,
    .stError {
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        border-left: 3px solid #6B7280 !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
    }

    /* Remove any nested background colors */
    .stAlert > div,
    div[data-testid="stAlert"] > div {
        background-color: transparent !important;
    }

    /* Professional sidebar styling */
    .sidebar .sidebar-content {
        padding: 16px !important;
    }

    /* Form controls - consistent borders */
    .stSelectbox > div,
    .stSlider > div,
    .stNumberInput > div,
    .stTextInput > div {
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        background-color: #FFFFFF !important;
    }

    /* Button styling */
    .stButton > button {
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        background-color: #FFFFFF !important;
        color: #374151 !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #F9FAFB !important;
        border-color: #9CA3AF !important;
    }

    /* Expander styling - minimal and clean */
    div[data-testid="stExpander"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 6px !important;
        background-color: #FFFFFF !important;
        margin: 8px 0 !important;
    }

    /* Chart containers */
    .js-plotly-plot,
    div[data-testid="stPlotlyChart"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 6px !important;
        background-color: #FFFFFF !important;
        margin: 8px 0 !important;
    }

    /* Remove any colored highlights or decorations */
    .stMarkdown {
        color: #111827 !important;
    }

    /* Clean spacing */
    .block-container {
        padding: 2rem 1rem !important;
        max-width: 100% !important;
    }

    /* Consistent paragraph spacing */
    p {
        margin-bottom: 0.75rem !important;
    }

    /* Professional table styling */
    .stDataFrame,
    table {
        border: 1px solid #E5E7EB !important;
        border-radius: 6px !important;
        background-color: #FFFFFF !important;
    }

    /* Clean checkbox and radio styling */
    .stCheckbox,
    .stRadio {
        margin: 4px 0 !important;
    }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)