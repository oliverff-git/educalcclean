"""
Responsive Configuration System
Manages responsive layouts and styling for different device types.
"""

import streamlit as st
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ResponsiveBreakpoints:
    """Responsive breakpoints configuration."""
    mobile_max: int = 768
    tablet_max: int = 1024
    desktop_min: int = 1025


@dataclass
class DeviceConfig:
    """Configuration for specific device type."""
    # Layout settings
    layout: str = 'centered'  # 'wide', 'centered'
    sidebar_state: str = 'expanded'  # 'expanded', 'collapsed'
    columns_max: int = 4

    # Chart settings
    chart_height: int = 400
    chart_margin: Dict[str, int] = None

    # Typography
    font_scale: float = 1.0
    title_size: str = 'h1'  # 'h1', 'h2', 'h3'

    # Component settings
    show_advanced_metrics: bool = True
    use_compact_tables: bool = False
    metric_columns: int = 4

    # Mobile-specific
    use_accordions: bool = False
    stack_vertically: bool = False
    hide_sidebar_by_default: bool = False

    def __post_init__(self):
        if self.chart_margin is None:
            self.chart_margin = {'l': 50, 'r': 50, 't': 80, 'b': 50}


class ResponsiveConfigManager:
    """Manages responsive configurations for different device types."""

    def __init__(self):
        """Initialize responsive config manager."""
        self.breakpoints = ResponsiveBreakpoints()
        self._configs = self._create_device_configs()

    def _create_device_configs(self) -> Dict[str, DeviceConfig]:
        """Create configurations for each device type."""
        return {
            'mobile': DeviceConfig(
                layout='centered',
                sidebar_state='collapsed',
                columns_max=1,
                chart_height=250,
                chart_margin={'l': 20, 'r': 20, 't': 40, 'b': 40},
                font_scale=0.85,
                title_size='h2',
                show_advanced_metrics=False,
                use_compact_tables=True,
                metric_columns=1,
                use_accordions=True,
                stack_vertically=True,
                hide_sidebar_by_default=True
            ),
            'tablet': DeviceConfig(
                layout='centered',
                sidebar_state='collapsed',
                columns_max=2,
                chart_height=300,
                chart_margin={'l': 30, 'r': 30, 't': 60, 'b': 40},
                font_scale=0.9,
                title_size='h2',
                show_advanced_metrics=True,
                use_compact_tables=True,
                metric_columns=2,
                use_accordions=False,
                stack_vertically=False,
                hide_sidebar_by_default=False
            ),
            'desktop': DeviceConfig(
                layout='wide',
                sidebar_state='expanded',
                columns_max=4,
                chart_height=400,
                chart_margin={'l': 50, 'r': 50, 't': 80, 'b': 50},
                font_scale=1.0,
                title_size='h1',
                show_advanced_metrics=True,
                use_compact_tables=False,
                metric_columns=4,
                use_accordions=False,
                stack_vertically=False,
                hide_sidebar_by_default=False
            )
        }

    def get_config(self, device_type: str) -> DeviceConfig:
        """Get configuration for device type."""
        return self._configs.get(device_type, self._configs['desktop'])

    def get_responsive_columns(self, device_type: str, desired_columns: int) -> int:
        """Get appropriate number of columns for device."""
        config = self.get_config(device_type)
        return min(desired_columns, config.columns_max)

    def get_chart_config(self, device_type: str) -> Dict[str, Any]:
        """Get chart configuration for device."""
        config = self.get_config(device_type)

        return {
            'height': config.chart_height,
            'margin': config.chart_margin,
            'responsive': True,
            'config': {
                'displayModeBar': device_type == 'desktop',
                'scrollZoom': device_type != 'mobile',
                'doubleClick': 'reset' if device_type == 'desktop' else 'reset+autosize',
                'showTips': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': [
                    'pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'toggleSpikelines'
                ] if device_type == 'mobile' else []
            }
        }

    def get_streamlit_config(self, device_type: str) -> Dict[str, Any]:
        """Get Streamlit page configuration for device."""
        config = self.get_config(device_type)

        return {
            'page_title': "Education Savings Calculator",
            'page_icon': "",
            'layout': config.layout,
            'initial_sidebar_state': config.sidebar_state
        }

    def apply_mobile_css(self, device_type: str) -> None:
        """Apply mobile-specific CSS styling."""
        # CSS is now handled by unified styles system
        # This method now only handles non-CSS responsive behavior
        pass

    def get_metric_layout(self, device_type: str, total_metrics: int) -> Dict[str, Any]:
        """Get optimal metric layout for device."""
        config = self.get_config(device_type)

        if device_type == 'mobile':
            # Stack all metrics vertically on mobile
            return {
                'columns': 1,
                'layout': 'vertical',
                'spacing': 'small'
            }
        elif device_type == 'tablet':
            # 2x2 grid for tablets
            columns = min(2, total_metrics)
            return {
                'columns': columns,
                'layout': 'grid',
                'spacing': 'medium'
            }
        else:
            # Full horizontal layout for desktop
            columns = min(config.metric_columns, total_metrics)
            return {
                'columns': columns,
                'layout': 'horizontal',
                'spacing': 'large'
            }

    def should_use_expander(self, device_type: str, section: str) -> bool:
        """Determine if section should use expander on device."""
        config = self.get_config(device_type)

        if not config.use_accordions:
            return False

        # Always use expanders for mobile
        if device_type == 'mobile':
            return True

        # Specific sections that benefit from expanders
        expander_sections = ['data_sources', 'advanced_settings', 'help']
        return section in expander_sections

    def get_sidebar_config(self, device_type: str) -> Dict[str, Any]:
        """Get sidebar configuration for device."""
        config = self.get_config(device_type)

        return {
            'initial_state': config.sidebar_state,
            'hide_by_default': config.hide_sidebar_by_default,
            'use_compact_mode': device_type in ['mobile', 'tablet'],
            'show_tooltips': device_type != 'mobile'
        }


# Global instance
_responsive_manager = None

def get_responsive_manager() -> ResponsiveConfigManager:
    """Get singleton responsive manager instance."""
    global _responsive_manager
    if _responsive_manager is None:
        _responsive_manager = ResponsiveConfigManager()
    return _responsive_manager


def get_device_config(device_type: str) -> DeviceConfig:
    """Quick function to get device configuration."""
    manager = get_responsive_manager()
    return manager.get_config(device_type)


def apply_responsive_styling(device_type: str) -> None:
    """Apply responsive styling for device type."""
    manager = get_responsive_manager()
    manager.apply_mobile_css(device_type)


def configure_streamlit_for_device(device_type: str) -> Dict[str, Any]:
    """Get Streamlit configuration for device."""
    manager = get_responsive_manager()
    return manager.get_streamlit_config(device_type)