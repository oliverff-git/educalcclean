"""
Unified CSS Management System for Education Savings Calculator

This module consolidates all CSS styles into a single, coherent system with:
- True responsive behavior using CSS media queries
- CSS custom properties for consistency
- Elimination of conflicting style injections
- Better performance through single DOM injection
"""

from typing import Optional, Dict, Any


class UnifiedStyleManager:
    """Manages all CSS styles for the application."""

    # Responsive breakpoints (matching mobile detector values)
    MOBILE_MAX = 768
    TABLET_MAX = 1024

    def __init__(self):
        """Initialize the style manager."""
        self._css_variables = self._get_css_variables()
        self._base_styles = self._get_base_styles()
        self._responsive_styles = self._get_responsive_styles()
        self._component_styles = self._get_component_styles()

    def _get_css_variables(self) -> str:
        """Define CSS custom properties for consistency."""
        return """
        :root {
            /* Spacing system */
            --spacing-xs: 0.25rem;
            --spacing-sm: 0.5rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 2rem;

            /* Header dimensions */
            --header-height: 2.75rem;

            /* Container padding */
            --container-padding-mobile: 0.5rem;
            --container-padding-tablet: 0.75rem;
            --container-padding-desktop: 1rem;

            /* Colors */
            --bg-light: #f0f2f6;
            --bg-lighter: #f8f9fa;
            --border-light: #e6e9ef;
            --border-lighter: #e9ecef;

            /* Typography */
            --title-margin: 0.25rem;

            /* Component dimensions */
            --chart-height-mobile: 250px;
            --chart-height-tablet: 300px;
            --chart-height-desktop: 400px;

            /* Animation */
            --transition-fast: 0.15s ease;
        }
        """

    def _get_base_styles(self) -> str:
        """Core styles that apply to all devices."""
        return """
        /* ====== STREAMLIT HEADER & CONTAINER FIXES ====== */

        /* Keep header visible but compact for native sidebar toggle */
        header[data-testid="stHeader"] {
            height: var(--header-height);
            min-height: 0;
            padding: 0;
            background: transparent;
        }

        /* Remove Streamlit's reserved top padding */
        .stApp {
            padding-top: 0 !important;
        }

        /* Remove top gap from main view container */
        [data-testid="stAppViewContainer"] > .main {
            padding-top: 0 !important;
        }

        /* Ensure titles don't re-introduce large margins */
        [data-testid="stAppViewContainer"] h1 {
            margin-top: var(--title-margin) !important;
        }

        /* ====== SIDEBAR & LAYOUT ====== */

        /* Ensure sidebar is always visible */
        section[data-testid="stSidebar"] {
            display: block !important;
        }

        /* ====== TYPOGRAPHY ====== */

        /* Consistent heading margins */
        .main h1:first-child,
        .main h2:first-child,
        .element-container:first-child h1,
        .element-container:first-child h2 {
            margin-top: 0 !important;
        }

        /* ====== PERFORMANCE OPTIMIZATIONS ====== */

        /* Smooth transitions for interactive elements */
        .streamlit-expander,
        [data-testid="metric-container"],
        .element-container {
            transition: all var(--transition-fast);
        }
        """

    def _get_responsive_styles(self) -> str:
        """Responsive styles using CSS media queries for true responsive behavior."""
        return f"""
        /* ====== MOBILE STYLES (0-{self.MOBILE_MAX}px) ====== */
        @media (max-width: {self.MOBILE_MAX}px) {{
            /* Main container */
            [data-testid="stAppViewContainer"] .block-container {{
                margin-top: 0 !important;
                padding-top: var(--container-padding-mobile) !important;
                padding-left: var(--spacing-md);
                padding-right: var(--spacing-md);
                padding-bottom: var(--spacing-md);
                max-width: 100%;
            }}

            /* Element spacing */
            .element-container {{
                margin-bottom: var(--spacing-sm);
            }}

            /* Metrics styling */
            [data-testid="metric-container"] {{
                background-color: var(--bg-light);
                border: 1px solid var(--border-light);
                padding: var(--spacing-sm);
                border-radius: 0.25rem;
                margin-bottom: var(--spacing-sm);
            }}

            /* Expanders - mobile-friendly */
            .streamlit-expander {{
                border-radius: 0.5rem;
                margin-bottom: var(--spacing-sm);
            }}

            .streamlit-expander > div > div > div {{
                padding: 0.75rem;
            }}

            /* Charts - mobile optimization */
            .js-plotly-plot {{
                width: 100% !important;
                min-height: var(--chart-height-mobile);
            }}

            /* Force single column layout */
            .row-widget.stHorizontal > div {{
                flex: 1 1 100% !important;
                margin-bottom: var(--spacing-sm);
                margin-left: 0 !important;
                margin-right: 0 !important;
            }}

            /* Mobile-specific title sizing */
            .main h1 {{
                font-size: 1.8rem;
                line-height: 1.2;
            }}

            /* Touch-friendly mobile targets (44px minimum touch target size) */
            .stSelectbox > div > div {{
                min-height: 44px;
                font-size: 16px; /* Prevents zoom on iOS */
            }}

            .stButton > button {{
                width: 100%;
                min-height: 44px;
                font-size: 16px;
                touch-action: manipulation; /* Prevents double-tap zoom */
            }}
        }}

        /* ====== TABLET STYLES ({self.MOBILE_MAX + 1}px-{self.TABLET_MAX}px) ====== */
        @media (min-width: {self.MOBILE_MAX + 1}px) and (max-width: {self.TABLET_MAX}px) {{
            /* Main container */
            [data-testid="stAppViewContainer"] .block-container {{
                margin-top: 0 !important;
                padding-top: var(--container-padding-tablet) !important;
                padding-left: var(--spacing-lg);
                padding-right: var(--spacing-lg);
                padding-bottom: var(--spacing-lg);
                max-width: 100%;
            }}

            /* Metrics styling */
            [data-testid="metric-container"] {{
                background-color: var(--bg-lighter);
                border: 1px solid var(--border-lighter);
                padding: 0.75rem;
                border-radius: 0.375rem;
            }}

            /* Charts - tablet optimization */
            .js-plotly-plot {{
                width: 100% !important;
                min-height: var(--chart-height-tablet);
            }}

            /* Two-column layout for tablets */
            .row-widget.stHorizontal > div {{
                flex: 1 1 48% !important;
                margin: 0 1% 1rem 1%;
            }}
        }}

        /* ====== DESKTOP STYLES ({self.TABLET_MAX + 1}px+) ====== */
        @media (min-width: {self.TABLET_MAX + 1}px) {{
            /* Main container */
            [data-testid="stAppViewContainer"] .block-container {{
                margin-top: 0 !important;
                padding-top: var(--container-padding-desktop) !important;
                padding-left: var(--spacing-xl);
                padding-right: var(--spacing-xl);
                padding-bottom: var(--spacing-xl);
                max-width: 100%;
            }}

            /* Charts - desktop optimization */
            .js-plotly-plot {{
                width: 100% !important;
                min-height: var(--chart-height-desktop);
            }}

            /* Multi-column layouts */
            .row-widget.stHorizontal > div {{
                margin: 0 0.5rem 1rem 0.5rem;
            }}

            /* Larger metrics on desktop */
            [data-testid="metric-container"] {{
                padding: var(--spacing-md);
                border-radius: 0.5rem;
            }}
        }}
        """

    def _get_component_styles(self) -> str:
        """Component-specific styles that work across all devices."""
        return """
        /* ====== DATA TABLES ====== */

        .dataframe {
            width: 100% !important;
        }

        .dataframe table {
            border-collapse: collapse;
            margin: 0;
        }

        .dataframe th,
        .dataframe td {
            padding: 0.5rem;
            text-align: left;
            border-bottom: 1px solid var(--border-light);
        }

        /* ====== BUTTONS & CONTROLS ====== */

        .stButton > button {
            transition: all var(--transition-fast);
        }

        .stSelectbox > div > div {
            transition: all var(--transition-fast);
        }

        /* ====== CARDS & CONTAINERS ====== */

        .metric-card {
            background: var(--bg-light);
            border: 1px solid var(--border-light);
            border-radius: 0.5rem;
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-sm);
        }

        /* ====== ACCESSIBILITY ====== */

        /* Focus indicators */
        button:focus,
        select:focus,
        input:focus {
            outline: 2px solid #0066cc;
            outline-offset: 2px;
        }

        /* Reduce motion for users who prefer it */
        @media (prefers-reduced-motion: reduce) {
            * {
                transition: none !important;
                animation: none !important;
            }
        }

        /* ====== PRINT STYLES ====== */

        @media print {
            header[data-testid="stHeader"],
            section[data-testid="stSidebar"] {
                display: none !important;
            }

            .main {
                padding: 0 !important;
                margin: 0 !important;
            }
        }
        """

    def get_complete_css(self, device_hint: Optional[str] = None) -> str:
        """
        Get the complete, unified CSS for the application.

        Args:
            device_hint: Optional device type hint for optimization (not required
                        since CSS media queries handle responsive behavior)

        Returns:
            Complete CSS string ready for injection
        """
        css_parts = [
            "/* ====== UNIFIED STYLES - EDUCATION SAVINGS CALCULATOR ====== */",
            "/* Generated by UnifiedStyleManager - Single source of truth for all styles */",
            "",
            self._css_variables,
            "",
            self._base_styles,
            "",
            self._responsive_styles,
            "",
            self._component_styles,
            "",
            "/* ====== END UNIFIED STYLES ====== */"
        ]

        return "\n".join(css_parts)


# Convenience function for easy importing
def get_unified_styles(device_hint: Optional[str] = None) -> str:
    """
    Get the complete unified CSS for the application.

    Args:
        device_hint: Optional device type hint (mobile, tablet, desktop)
                    Note: Not required since CSS media queries handle responsiveness

    Returns:
        Complete CSS string ready for st.markdown injection
    """
    manager = UnifiedStyleManager()
    return manager.get_complete_css(device_hint)