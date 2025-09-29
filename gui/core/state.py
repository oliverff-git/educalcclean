from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import streamlit as st

@dataclass
class AppState:
    # Selection state
    university: Optional[str] = "Oxford"
    course: Optional[str] = "Philosophy Politics & Economics"
    conversion_year: int = 2025
    education_year: int = 2027

    # Calculation results (cached)
    scenarios: List = field(default_factory=list)
    roi_scenarios: List = field(default_factory=list)
    projections_data: Dict = field(default_factory=dict)

    # Singleton instances
    data_processor = None
    calculator = None

def get_state() -> AppState:
    """Get singleton app state from session state"""
    if "app_state" not in st.session_state:
        st.session_state["app_state"] = AppState()
    return st.session_state["app_state"]

def update_state(**kwargs):
    """Update app state with new values"""
    state = get_state()
    for key, value in kwargs.items():
        setattr(state, key, value)

@st.cache_resource
def init_processors():
    """Initialize data processor and calculator (singleton pattern with caching)"""
    import sys
    from pathlib import Path

    # Add parent directory to path to find gui module
    parent_dir = str(Path(__file__).parent.parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from gui.data_processor import EducationDataProcessor
    from gui.fee_calculator import EducationSavingsCalculator

    data_processor = EducationDataProcessor()
    data_processor.load_data()
    calculator = EducationSavingsCalculator(data_processor)

    return data_processor, calculator