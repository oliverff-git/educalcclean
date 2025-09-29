"""
Data Sources module for displaying and providing downloadable access to raw data files.
Provides transparency for parents to verify calculations and data sources.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
from typing import Dict, Optional


def get_file_info(file_path: Path) -> Dict[str, str]:
    """Get file information for display purposes."""
    if not file_path.exists():
        return {
            "size": "File not found",
            "modified": "Unknown",
            "rows": "Unknown"
        }

    # File size
    size_bytes = file_path.stat().st_size
    if size_bytes < 1024:
        size_str = f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"

    # Last modified
    modified_timestamp = file_path.stat().st_mtime
    modified_date = datetime.fromtimestamp(modified_timestamp).strftime("%Y-%m-%d")

    # Row count for CSV files
    try:
        df = pd.read_csv(file_path)
        rows = f"{len(df):,} rows"
    except:
        rows = "Unknown"

    return {
        "size": size_str,
        "modified": modified_date,
        "rows": rows
    }


def create_download_button(file_path: Path, label: str, description: str, help_text: str):
    """Create a download button for a data file with metadata."""
    if not file_path.exists():
        st.error(f"Data file not found: {file_path.name}")
        return

    # Get file information
    file_info = get_file_info(file_path)

    # Read file content for download
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Create columns for layout
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{label}**")
            st.markdown(f"{description}")
            st.caption(f"📊 {file_info['rows']} • 📁 {file_info['size']} • 📅 Updated: {file_info['modified']}")

        with col2:
            st.download_button(
                label="Download CSV",
                data=file_content,
                file_name=file_path.name,
                mime="text/csv",
                help=help_text
            )

        st.divider()

    except Exception as e:
        st.error(f"Error reading file {file_path.name}: {str(e)}")


def data_sources_section():
    """Create the data sources section with downloadable CSV files."""

    # Get data directory path
    current_dir = Path(__file__).parent.parent.parent
    data_dir = current_dir / "data"

    # Data sources information
    data_sources = [
        {
            "file_path": data_dir / "fees" / "comprehensive_fees_2020_2026.csv",
            "label": "University Fees Data",
            "description": "Official tuition fees from Oxford, Cambridge, and LSE websites (2020-2026). Contains overseas student fees by programme and year.",
            "help_text": "Raw fee data scraped from official university websites. Used for CAGR calculations and projections."
        },
        {
            "file_path": data_dir / "fx" / "twelvedata" / "GBPINR_monthly_twelvedata.csv",
            "label": "GBP/INR Exchange Rates",
            "description": "Monthly GBP/INR exchange rates from TwelveData API. Historical data used for exchange rate projections and CAGR analysis.",
            "help_text": "Historical exchange rate data used to calculate 4.18% annual depreciation rate for projections."
        },
        {
            "file_path": data_dir / "savings" / "boe_official_rates_corrected.csv",
            "label": "Bank of England Interest Rates",
            "description": "Official Bank of England base rates and UK savings account interest rates. Used for opportunity cost calculations.",
            "help_text": "Interest rate data from Bank of England. Used to calculate opportunity costs of early GBP conversion strategies."
        }
    ]

    # Main data sources section
    st.markdown("### Data Sources & Verification")
    st.markdown("**For transparency and verification, download the raw data files used in all calculations:**")

    # Create expandable section
    with st.expander("📋 Download Raw Data Files", expanded=False):
        st.markdown("**All calculations in this tool are based on the following verified data sources:**")
        st.markdown("")

        # Display each data source with download button
        for source in data_sources:
            create_download_button(
                file_path=source["file_path"],
                label=source["label"],
                description=source["description"],
                help_text=source["help_text"]
            )

        # Additional information
        st.info(
            "**Calculation Transparency**: All projections use historical CAGR (Compound Annual Growth Rate) "
            "analysis. Fee growth rates are calculated per university/programme where data exists, "
            "falling back to university averages when specific programme data is limited."
        )

    # Summary footer
    st.caption("**Data Sources**: Official university websites (Oxford, Cambridge, LSE), TwelveData API for exchange rates, Bank of England official rates. All projections based on historical CAGR analysis.")


if __name__ == "__main__":
    # For testing the module
    st.title("Data Sources Test")
    data_sources_section()