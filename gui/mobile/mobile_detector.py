"""
Mobile Detection System for Education Savings Calculator
Provides device detection and responsive configuration.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Tuple, Optional
import re


class MobileDetector:
    """Detects device type and provides responsive configuration."""

    # Breakpoints (in pixels)
    MOBILE_MAX = 768
    TABLET_MAX = 1024

    # User agent patterns for mobile detection
    MOBILE_PATTERNS = [
        r'Mobile|Android|iPhone|iPad|iPod|BlackBerry|Opera Mini|IEMobile',
        r'webOS|Windows Phone|Kindle|Silk|Mobile Safari'
    ]

    def __init__(self):
        """Initialize mobile detector."""
        self._device_info = None

    def get_viewport_size(self) -> Tuple[int, int]:
        """Get viewport dimensions using JavaScript."""
        viewport_js = """
        <script>
        function getViewportSize() {
            const width = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
            const height = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);

            // Store in session storage for Streamlit access
            window.parent.postMessage({
                type: 'viewport_size',
                width: width,
                height: height
            }, '*');

            return {width: width, height: height};
        }

        // Get initial size
        const size = getViewportSize();

        // Listen for resize events
        window.addEventListener('resize', getViewportSize);

        // Also check for orientation change on mobile
        window.addEventListener('orientationchange', function() {
            setTimeout(getViewportSize, 100);
        });
        </script>
        """

        # Inject JavaScript
        components.html(viewport_js, height=0)

        # Get from session state or use defaults
        width = st.session_state.get('viewport_width', 1024)
        height = st.session_state.get('viewport_height', 768)

        return width, height

    def detect_user_agent(self) -> str:
        """Detect device type from user agent (fallback method)."""
        # Try to get user agent from Streamlit context
        try:
            # This is a workaround - Streamlit doesn't directly expose user agent
            # We'll use JavaScript to detect and store it
            user_agent_js = """
            <script>
            const userAgent = navigator.userAgent;
            const isMobile = /Mobile|Android|iPhone|iPad|iPod|BlackBerry|Opera Mini|IEMobile|webOS|Windows Phone|Kindle|Silk|Mobile Safari/i.test(userAgent);
            const isTablet = /iPad|Android.*Tablet|Windows.*Touch/i.test(userAgent) && !/Mobile/i.test(userAgent);

            let deviceType = 'desktop';
            if (isMobile && !isTablet) {
                deviceType = 'mobile';
            } else if (isTablet || isMobile) {
                deviceType = 'tablet';
            }

            // Send to parent
            window.parent.postMessage({
                type: 'user_agent_detection',
                userAgent: userAgent,
                deviceType: deviceType,
                isMobile: isMobile,
                isTablet: isTablet
            }, '*');
            </script>
            """

            components.html(user_agent_js, height=0)

            # Return stored value or default
            return st.session_state.get('detected_device_type', 'desktop')

        except Exception:
            return 'desktop'

    def get_device_type(self) -> str:
        """
        Determine device type based on viewport and user agent.
        Returns: 'mobile', 'tablet', or 'desktop'
        """
        # Get viewport dimensions
        width, height = self.get_viewport_size()

        # Primary detection via viewport width
        if width < self.MOBILE_MAX:
            device_type = 'mobile'
        elif width < self.TABLET_MAX:
            device_type = 'tablet'
        else:
            device_type = 'desktop'

        # Secondary validation via user agent
        ua_device_type = self.detect_user_agent()

        # If user agent strongly suggests mobile but viewport says tablet, trust user agent
        if ua_device_type == 'mobile' and device_type == 'tablet':
            device_type = 'mobile'

        # Store in session state
        st.session_state['device_type'] = device_type
        st.session_state['viewport_width'] = width
        st.session_state['viewport_height'] = height

        return device_type

    def is_mobile(self) -> bool:
        """Check if current device is mobile."""
        return self.get_device_type() == 'mobile'

    def is_tablet(self) -> bool:
        """Check if current device is tablet."""
        return self.get_device_type() == 'tablet'

    def is_desktop(self) -> bool:
        """Check if current device is desktop."""
        return self.get_device_type() == 'desktop'

    def get_device_info(self) -> Dict:
        """Get comprehensive device information."""
        device_type = self.get_device_type()
        width, height = self.get_viewport_size()

        return {
            'device_type': device_type,
            'viewport_width': width,
            'viewport_height': height,
            'is_mobile': device_type == 'mobile',
            'is_tablet': device_type == 'tablet',
            'is_desktop': device_type == 'desktop',
            'is_touch_device': device_type in ['mobile', 'tablet'],
            'orientation': 'portrait' if height > width else 'landscape'
        }

    @staticmethod
    def setup_viewport_listener():
        """Setup JavaScript listener for viewport changes."""
        listener_js = """
        <script>
        // Listen for messages from iframe
        window.addEventListener('message', function(event) {
            if (event.data.type === 'viewport_size') {
                // Update Streamlit session state (this requires custom component)
                console.log('Viewport size:', event.data.width, 'x', event.data.height);
            } else if (event.data.type === 'user_agent_detection') {
                console.log('Device detection:', event.data.deviceType);
            }
        });

        // Force detection on load
        setTimeout(function() {
            const width = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
            const height = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
            console.log('Initial viewport:', width, 'x', height);
        }, 100);
        </script>
        """

        components.html(listener_js, height=0)


# Global detector instance
_mobile_detector = None

def get_mobile_detector() -> MobileDetector:
    """Get singleton mobile detector instance."""
    global _mobile_detector
    if _mobile_detector is None:
        _mobile_detector = MobileDetector()
    return _mobile_detector


def detect_device() -> str:
    """Quick function to detect device type."""
    detector = get_mobile_detector()
    return detector.get_device_type()


def is_mobile_device() -> bool:
    """Quick function to check if mobile."""
    return detect_device() == 'mobile'


def get_responsive_config() -> Dict:
    """Get responsive configuration for current device."""
    detector = get_mobile_detector()
    device_info = detector.get_device_info()

    # Base configuration
    config = {
        'device_info': device_info,
        'sidebar_state': 'expanded' if device_info['is_desktop'] else 'collapsed',
        'layout': 'wide' if device_info['is_desktop'] else 'centered',
        'chart_height': 400 if device_info['is_desktop'] else 300,
        'columns_count': 4 if device_info['is_desktop'] else (2 if device_info['is_tablet'] else 1),
        'show_advanced_metrics': device_info['is_desktop'],
        'use_compact_mode': device_info['is_mobile'],
        'font_scale': 1.0 if device_info['is_desktop'] else (0.9 if device_info['is_tablet'] else 0.8)
    }

    return config