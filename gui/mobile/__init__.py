"""
Mobile package for responsive Education Savings Calculator.
"""

from .mobile_detector import MobileDetector, get_mobile_detector, detect_device, is_mobile_device, get_responsive_config
from .responsive_config import ResponsiveConfigManager, DeviceConfig, get_responsive_manager, get_device_config, apply_responsive_styling, configure_streamlit_for_device

__all__ = [
    'MobileDetector', 'get_mobile_detector', 'detect_device', 'is_mobile_device', 'get_responsive_config',
    'ResponsiveConfigManager', 'DeviceConfig', 'get_responsive_manager', 'get_device_config',
    'apply_responsive_styling', 'configure_streamlit_for_device'
]