from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import streamlit as st

@dataclass
class AppState:
    # Selection state
    university: Optional[str] = None
    course: Optional[str] = None
    conversion_year: int = 2023
    education_year: int = 2026

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

def init_processors():
    """Initialize data processor and calculator (singleton pattern)"""
    state = get_state()
    if state.data_processor is None:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))

        from gui.data_processor import EducationDataProcessor
        from gui.fee_calculator import EducationSavingsCalculator

        state.data_processor = EducationDataProcessor()
        state.data_processor.load_data()
        state.calculator = EducationSavingsCalculator(state.data_processor)

    return state.data_processor, state.calculator