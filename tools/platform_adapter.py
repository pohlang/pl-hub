"""
PLHub Platform Adapter
Provides platform-specific UI adaptations, native-look components,
and platform-aware behaviors for cross-platform applications.

Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import platform
import json
from pathlib import Path


class Platform(Enum):
    """Supported platforms"""
    IOS = "ios"
    ANDROID = "android"
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    WEB = "web"


class NavigationStyle(Enum):
    """Platform-specific navigation styles"""
    IOS_NAVIGATION = "ios_navigation"
    ANDROID_NAVIGATION = "android_navigation"
    DESKTOP_MENU = "desktop_menu"
    WEB_HEADER = "web_header"


class PlatformConvention:
    """Platform UI conventions and patterns"""
    
    # Button positions
    BUTTON_POSITIONS = {
        Platform.IOS: "right",          # Action buttons on right
        Platform.ANDROID: "right",      # FAB and actions on right
        Platform.WINDOWS: "right",      # OK/Apply on right
        Platform.MACOS: "right",        # Primary action on right
        Platform.WEB: "right"           # Submit on right
    }
    
    # Confirmation button order
    CONFIRMATION_ORDER = {
        Platform.IOS: ["Cancel", "Confirm"],
        Platform.ANDROID: ["Cancel", "Confirm"],
        Platform.WINDOWS: ["Confirm", "Cancel"],
        Platform.MACOS: ["Cancel", "Confirm"],
        Platform.WEB: ["Cancel", "Confirm"]
    }
    
    # Navigation patterns
    NAVIGATION_PATTERNS = {
        Platform.IOS: "hierarchical",       # Back button + title
        Platform.ANDROID: "drawer",         # Hamburger menu
        Platform.WINDOWS: "ribbon",         # Ribbon or menu bar
        Platform.MACOS: "sidebar",          # Sidebar navigation
        Platform.WEB: "header"              # Top navigation bar
    }
    
    # System fonts
    SYSTEM_FONTS = {
        Platform.IOS: "-apple-system, BlinkMacSystemFont, 'SF Pro'",
        Platform.ANDROID: "Roboto, 'Noto Sans'",
        Platform.WINDOWS: "'Segoe UI', Tahoma, sans-serif",
        Platform.MACOS: "-apple-system, BlinkMacSystemFont, 'SF Pro'",
        Platform.LINUX: "Ubuntu, 'Liberation Sans', sans-serif",
        Platform.WEB: "system-ui, -apple-system, sans-serif"
    }
    
    # Default spacing units
    SPACING_UNITS = {
        Platform.IOS: 8,
        Platform.ANDROID: 8,
        Platform.WINDOWS: 4,
        Platform.MACOS: 8,
        Platform.LINUX: 4,
        Platform.WEB: 8
    }
    
    # Animation durations (ms)
    ANIMATION_DURATIONS = {
        Platform.IOS: {
            "quick": 200,
            "normal": 300,
            "slow": 500
        },
        Platform.ANDROID: {
            "quick": 150,
            "normal": 250,
            "slow": 400
        },
        Platform.WINDOWS: {
            "quick": 167,
            "normal": 300,
            "slow": 500
        },
        Platform.MACOS: {
            "quick": 200,
            "normal": 300,
            "slow": 500
        },
        Platform.WEB: {
            "quick": 150,
            "normal": 300,
            "slow": 500
        }
    }


@dataclass
class PlatformTheme:
    """Platform-specific theme configuration"""
    platform: Platform
    primary_color: str
    accent_color: str
    background_color: str
    surface_color: str
    text_color: str
    border_color: str
    shadow: str
    border_radius: str
    font_family: str
    
    @classmethod
    def get_default(cls, platform: Platform) -> 'PlatformTheme':
        """Get default theme for platform"""
        if platform == Platform.IOS:
            return cls(
                platform=platform,
                primary_color="#007AFF",
                accent_color="#5AC8FA",
                background_color="#F2F2F7",
                surface_color="#FFFFFF",
                text_color="#000000",
                border_color="#C6C6C8",
                shadow="0px 1px 3px rgba(0, 0, 0, 0.12)",
                border_radius="10px",
                font_family=PlatformConvention.SYSTEM_FONTS[Platform.IOS]
            )
        elif platform == Platform.ANDROID:
            return cls(
                platform=platform,
                primary_color="#6200EE",
                accent_color="#03DAC6",
                background_color="#FFFFFF",
                surface_color="#FFFFFF",
                text_color="#000000",
                border_color="#E0E0E0",
                shadow="0px 2px 4px rgba(0, 0, 0, 0.14)",
                border_radius="4px",
                font_family=PlatformConvention.SYSTEM_FONTS[Platform.ANDROID]
            )
        elif platform == Platform.WINDOWS:
            return cls(
                platform=platform,
                primary_color="#0078D4",
                accent_color="#00A4EF",
                background_color="#F3F3F3",
                surface_color="#FFFFFF",
                text_color="#000000",
                border_color="#CCCCCC",
                shadow="0px 1.6px 3.6px rgba(0, 0, 0, 0.13)",
                border_radius="2px",
                font_family=PlatformConvention.SYSTEM_FONTS[Platform.WINDOWS]
            )
        elif platform == Platform.MACOS:
            return cls(
                platform=platform,
                primary_color="#007AFF",
                accent_color="#5AC8FA",
                background_color="#F5F5F5",
                surface_color="#FFFFFF",
                text_color="#000000",
                border_color="#D1D1D6",
                shadow="0px 1px 3px rgba(0, 0, 0, 0.12)",
                border_radius="6px",
                font_family=PlatformConvention.SYSTEM_FONTS[Platform.MACOS]
            )
        else:  # WEB/LINUX
            return cls(
                platform=platform,
                primary_color="#3B82F6",
                accent_color="#10B981",
                background_color="#F9FAFB",
                surface_color="#FFFFFF",
                text_color="#111827",
                border_color="#E5E7EB",
                shadow="0px 1px 3px rgba(0, 0, 0, 0.1)",
                border_radius="8px",
                font_family=PlatformConvention.SYSTEM_FONTS[Platform.WEB]
            )


@dataclass
class HapticFeedback:
    """Haptic feedback configuration"""
    type: str  # 'impact', 'notification', 'selection'
    intensity: str = 'medium'  # 'light', 'medium', 'heavy'
    
    @staticmethod
    def impact(intensity: str = 'medium') -> 'HapticFeedback':
        """Impact haptic (collision, tap)"""
        return HapticFeedback('impact', intensity)
    
    @staticmethod
    def notification(type: str = 'success') -> 'HapticFeedback':
        """Notification haptic (success, warning, error)"""
        return HapticFeedback('notification', type)
    
    @staticmethod
    def selection() -> 'HapticFeedback':
        """Selection haptic (picker, wheel)"""
        return HapticFeedback('selection')


@dataclass
class GestureConfig:
    """Platform-specific gesture configuration"""
    swipe_threshold: int  # Pixels
    long_press_duration: int  # Milliseconds
    double_tap_delay: int  # Milliseconds
    pinch_threshold: float  # Scale delta
    
    @classmethod
    def get_default(cls, platform: Platform) -> 'GestureConfig':
        """Get default gesture config for platform"""
        if platform in [Platform.IOS, Platform.ANDROID]:
            return cls(
                swipe_threshold=50,
                long_press_duration=500,
                double_tap_delay=300,
                pinch_threshold=0.1
            )
        else:
            return cls(
                swipe_threshold=80,
                long_press_duration=600,
                double_tap_delay=400,
                pinch_threshold=0.15
            )


class PlatformAdapter:
    """Adapts UI components to platform-specific conventions"""
    
    def __init__(self, platform: Optional[Platform] = None):
        self.platform = platform or self._detect_platform()
        self.theme = PlatformTheme.get_default(self.platform)
        self.gesture_config = GestureConfig.get_default(self.platform)
        self.haptics_enabled = self.platform in [Platform.IOS, Platform.ANDROID]
    
    def _detect_platform(self) -> Platform:
        """Auto-detect current platform"""
        system = platform.system().lower()
        
        if system == 'darwin':
            # Check if iOS (in production, would check device)
            return Platform.MACOS
        elif system == 'windows':
            return Platform.WINDOWS
        elif system == 'linux':
            # Check if Android (in production, would check device)
            return Platform.LINUX
        else:
            return Platform.WEB
    
    def adapt_button(self, label: str, style: str = 'primary') -> Dict:
        """Adapt button to platform conventions"""
        base = {
            'label': label,
            'font_family': self.theme.font_family
        }
        
        if self.platform == Platform.IOS:
            return {
                **base,
                'background': 'transparent' if style == 'secondary' else self.theme.primary_color,
                'text_color': self.theme.primary_color if style == 'secondary' else '#FFFFFF',
                'border_radius': '10px',
                'padding': '12px 24px',
                'font_weight': '600',
                'border': 'none'
            }
        elif self.platform == Platform.ANDROID:
            return {
                **base,
                'background': self.theme.primary_color if style == 'primary' else 'transparent',
                'text_color': '#FFFFFF' if style == 'primary' else self.theme.primary_color,
                'border_radius': '4px',
                'padding': '10px 24px',
                'font_weight': '500',
                'elevation': '2' if style == 'primary' else '0',
                'text_transform': 'uppercase'
            }
        elif self.platform == Platform.WINDOWS:
            return {
                **base,
                'background': self.theme.primary_color if style == 'primary' else self.theme.surface_color,
                'text_color': '#FFFFFF' if style == 'primary' else self.theme.text_color,
                'border_radius': '2px',
                'padding': '8px 16px',
                'font_weight': '400',
                'border': f'1px solid {self.theme.border_color}'
            }
        else:  # macOS/Web
            return {
                **base,
                'background': self.theme.primary_color if style == 'primary' else 'transparent',
                'text_color': '#FFFFFF' if style == 'primary' else self.theme.primary_color,
                'border_radius': '8px',
                'padding': '10px 20px',
                'font_weight': '500',
                'border': f'1px solid {self.theme.primary_color if style == "secondary" else "transparent"}'
            }
    
    def adapt_dialog(self, title: str, message: str, actions: List[str]) -> Dict:
        """Adapt dialog to platform conventions"""
        button_order = PlatformConvention.CONFIRMATION_ORDER[self.platform]
        
        # Reorder actions based on platform
        ordered_actions = []
        for btn in button_order:
            if btn in actions:
                ordered_actions.append(btn)
        # Add any remaining actions
        for action in actions:
            if action not in ordered_actions:
                ordered_actions.append(action)
        
        if self.platform == Platform.IOS:
            return {
                'type': 'action_sheet' if len(actions) > 2 else 'alert',
                'title': title,
                'message': message,
                'actions': ordered_actions,
                'blur_background': True,
                'border_radius': '14px'
            }
        elif self.platform == Platform.ANDROID:
            return {
                'type': 'dialog',
                'title': title,
                'message': message,
                'actions': ordered_actions,
                'elevation': 24,
                'border_radius': '4px'
            }
        elif self.platform == Platform.WINDOWS:
            return {
                'type': 'message_box',
                'title': title,
                'message': message,
                'actions': ordered_actions,
                'icon': 'info',
                'border_radius': '0px'
            }
        else:  # macOS/Web
            return {
                'type': 'modal',
                'title': title,
                'message': message,
                'actions': ordered_actions,
                'border_radius': '12px'
            }
    
    def adapt_navigation(self, title: str, has_back: bool = False) -> Dict:
        """Adapt navigation bar to platform"""
        if self.platform == Platform.IOS:
            return {
                'type': 'navigation_bar',
                'title': title,
                'title_position': 'center',
                'has_back_button': has_back,
                'back_button_style': 'chevron_with_label',
                'blur_effect': True,
                'height': '44px'
            }
        elif self.platform == Platform.ANDROID:
            return {
                'type': 'app_bar',
                'title': title,
                'title_position': 'left',
                'has_back_button': has_back,
                'back_button_style': 'arrow',
                'elevation': 4,
                'height': '56px'
            }
        elif self.platform == Platform.WINDOWS:
            return {
                'type': 'title_bar',
                'title': title,
                'title_position': 'left',
                'has_back_button': has_back,
                'back_button_style': 'arrow',
                'height': '32px'
            }
        else:  # macOS/Web
            return {
                'type': 'header',
                'title': title,
                'title_position': 'center',
                'has_back_button': has_back,
                'back_button_style': 'chevron',
                'height': '52px'
            }
    
    def adapt_list_item(self, title: str, subtitle: Optional[str] = None, 
                       icon: Optional[str] = None, has_disclosure: bool = False) -> Dict:
        """Adapt list item to platform"""
        base = {
            'title': title,
            'subtitle': subtitle,
            'icon': icon,
            'has_disclosure': has_disclosure,
            'font_family': self.theme.font_family
        }
        
        if self.platform == Platform.IOS:
            return {
                **base,
                'padding': '12px 16px',
                'separator_style': 'inset',
                'disclosure_icon': 'chevron_right',
                'icon_size': '29px'
            }
        elif self.platform == Platform.ANDROID:
            return {
                **base,
                'padding': '16px',
                'separator_style': 'full',
                'disclosure_icon': 'chevron_right',
                'icon_size': '24px',
                'ripple_effect': True
            }
        elif self.platform == Platform.WINDOWS:
            return {
                **base,
                'padding': '8px 12px',
                'separator_style': 'full',
                'disclosure_icon': 'chevron_right',
                'icon_size': '16px'
            }
        else:  # macOS/Web
            return {
                **base,
                'padding': '12px 16px',
                'separator_style': 'full',
                'disclosure_icon': 'chevron_right',
                'icon_size': '20px'
            }
    
    def get_animation_duration(self, speed: str = 'normal') -> int:
        """Get platform-appropriate animation duration"""
        durations = PlatformConvention.ANIMATION_DURATIONS[self.platform]
        return durations.get(speed, durations['normal'])
    
    def trigger_haptic(self, haptic: HapticFeedback):
        """Trigger haptic feedback (if supported)"""
        if not self.haptics_enabled:
            return
        
        # In production, would call native haptic API
        print(f"Haptic: {haptic.type} - {haptic.intensity}")
    
    def get_system_font(self) -> str:
        """Get platform system font"""
        return PlatformConvention.SYSTEM_FONTS[self.platform]
    
    def get_spacing_unit(self) -> int:
        """Get platform spacing unit"""
        return PlatformConvention.SPACING_UNITS[self.platform]
    
    def supports_feature(self, feature: str) -> bool:
        """Check if platform supports feature"""
        features = {
            'haptics': [Platform.IOS, Platform.ANDROID],
            'blur_effects': [Platform.IOS, Platform.MACOS, Platform.WEB],
            'elevation_shadows': [Platform.ANDROID, Platform.WEB],
            'system_gestures': [Platform.IOS, Platform.ANDROID],
            'dark_mode': [Platform.IOS, Platform.ANDROID, Platform.MACOS, Platform.WINDOWS, Platform.WEB],
            'notifications': [Platform.IOS, Platform.ANDROID, Platform.WINDOWS, Platform.MACOS, Platform.WEB],
            'file_picker': [Platform.WINDOWS, Platform.MACOS, Platform.LINUX, Platform.WEB]
        }
        
        return self.platform in features.get(feature, [])


class NativeComponentWrapper:
    """Wraps components with platform-specific native behaviors"""
    
    def __init__(self, adapter: PlatformAdapter):
        self.adapter = adapter
    
    def create_button(self, label: str, on_click: Callable, style: str = 'primary') -> Dict:
        """Create platform-adapted button"""
        button_style = self.adapter.adapt_button(label, style)
        
        def wrapped_click():
            # Trigger haptic feedback
            if self.adapter.haptics_enabled:
                self.adapter.trigger_haptic(HapticFeedback.impact('light'))
            
            # Call original handler
            on_click()
        
        return {
            'component': 'button',
            'style': button_style,
            'on_click': wrapped_click
        }
    
    def create_dialog(self, title: str, message: str, 
                     on_confirm: Callable, on_cancel: Optional[Callable] = None) -> Dict:
        """Create platform-adapted dialog"""
        actions = ['Confirm']
        if on_cancel:
            actions.insert(0, 'Cancel')
        
        dialog_config = self.adapter.adapt_dialog(title, message, actions)
        
        return {
            'component': 'dialog',
            'config': dialog_config,
            'handlers': {
                'Confirm': on_confirm,
                'Cancel': on_cancel
            }
        }
    
    def create_list(self, items: List[Dict], on_item_click: Callable) -> Dict:
        """Create platform-adapted list"""
        adapted_items = []
        
        for item in items:
            adapted_item = self.adapter.adapt_list_item(
                title=item.get('title', ''),
                subtitle=item.get('subtitle'),
                icon=item.get('icon'),
                has_disclosure=item.get('has_disclosure', False)
            )
            adapted_items.append(adapted_item)
        
        def wrapped_click(index: int):
            # Trigger haptic on mobile
            if self.adapter.platform in [Platform.IOS, Platform.ANDROID]:
                self.adapter.trigger_haptic(HapticFeedback.selection())
            
            on_item_click(index)
        
        return {
            'component': 'list',
            'items': adapted_items,
            'on_item_click': wrapped_click
        }
    
    def create_navigation_bar(self, title: str, on_back: Optional[Callable] = None) -> Dict:
        """Create platform-adapted navigation bar"""
        nav_config = self.adapter.adapt_navigation(title, has_back=on_back is not None)
        
        def wrapped_back():
            if self.adapter.haptics_enabled:
                self.adapter.trigger_haptic(HapticFeedback.impact('light'))
            
            if on_back:
                on_back()
        
        return {
            'component': 'navigation',
            'config': nav_config,
            'on_back': wrapped_back if on_back else None
        }


class PlatformLayoutManager:
    """Manages platform-specific layouts"""
    
    def __init__(self, adapter: PlatformAdapter):
        self.adapter = adapter
    
    def get_safe_area_insets(self) -> Dict[str, int]:
        """Get platform safe area insets"""
        if self.adapter.platform == Platform.IOS:
            # iPhone with notch
            return {
                'top': 47,
                'bottom': 34,
                'left': 0,
                'right': 0
            }
        elif self.adapter.platform == Platform.ANDROID:
            # Status bar + navigation bar
            return {
                'top': 24,
                'bottom': 48,
                'left': 0,
                'right': 0
            }
        else:
            return {
                'top': 0,
                'bottom': 0,
                'left': 0,
                'right': 0
            }
    
    def apply_safe_area(self, layout: Dict) -> Dict:
        """Apply safe area insets to layout"""
        insets = self.get_safe_area_insets()
        
        layout['padding'] = layout.get('padding', {})
        layout['padding']['top'] = layout['padding'].get('top', 0) + insets['top']
        layout['padding']['bottom'] = layout['padding'].get('bottom', 0) + insets['bottom']
        layout['padding']['left'] = layout['padding'].get('left', 0) + insets['left']
        layout['padding']['right'] = layout['padding'].get('right', 0) + insets['right']
        
        return layout
    
    def get_platform_layout(self, layout_type: str) -> Dict:
        """Get platform-specific layout configuration"""
        layouts = {
            'form': self._get_form_layout(),
            'list': self._get_list_layout(),
            'grid': self._get_grid_layout(),
            'detail': self._get_detail_layout()
        }
        
        return layouts.get(layout_type, {})
    
    def _get_form_layout(self) -> Dict:
        """Platform-specific form layout"""
        if self.adapter.platform == Platform.IOS:
            return {
                'spacing': 16,
                'input_height': 44,
                'label_style': 'above',
                'group_style': 'grouped'
            }
        elif self.adapter.platform == Platform.ANDROID:
            return {
                'spacing': 16,
                'input_height': 56,
                'label_style': 'floating',
                'group_style': 'outlined'
            }
        else:
            return {
                'spacing': 12,
                'input_height': 40,
                'label_style': 'above',
                'group_style': 'standard'
            }
    
    def _get_list_layout(self) -> Dict:
        """Platform-specific list layout"""
        if self.adapter.platform == Platform.IOS:
            return {
                'item_height': 44,
                'section_header_height': 28,
                'separator_inset': 16
            }
        elif self.adapter.platform == Platform.ANDROID:
            return {
                'item_height': 72,
                'section_header_height': 48,
                'separator_inset': 0
            }
        else:
            return {
                'item_height': 48,
                'section_header_height': 32,
                'separator_inset': 0
            }
    
    def _get_grid_layout(self) -> Dict:
        """Platform-specific grid layout"""
        spacing = self.adapter.get_spacing_unit()
        
        return {
            'column_count': 2 if self.adapter.platform in [Platform.IOS, Platform.ANDROID] else 3,
            'item_spacing': spacing * 2,
            'section_spacing': spacing * 4
        }
    
    def _get_detail_layout(self) -> Dict:
        """Platform-specific detail view layout"""
        if self.adapter.platform == Platform.IOS:
            return {
                'header_height': 300,
                'content_padding': 20,
                'section_spacing': 32
            }
        elif self.adapter.platform == Platform.ANDROID:
            return {
                'header_height': 256,
                'content_padding': 16,
                'section_spacing': 24
            }
        else:
            return {
                'header_height': 240,
                'content_padding': 24,
                'section_spacing': 32
            }


# Export main classes
__all__ = [
    'Platform',
    'PlatformAdapter',
    'NativeComponentWrapper',
    'PlatformLayoutManager',
    'HapticFeedback',
    'GestureConfig',
    'PlatformTheme',
    'PlatformConvention'
]


# Example usage
if __name__ == '__main__':
    # Create adapter for current platform
    adapter = PlatformAdapter()
    
    print(f"Platform: {adapter.platform.value}")
    print(f"System font: {adapter.get_system_font()}")
    print(f"Spacing unit: {adapter.get_spacing_unit()}px")
    
    # Adapt components
    button = adapter.adapt_button("Submit", "primary")
    print(f"\nButton style: {button}")
    
    dialog = adapter.adapt_dialog("Confirm", "Are you sure?", ["Cancel", "OK"])
    print(f"\nDialog config: {dialog}")
    
    # Check features
    print(f"\nSupports haptics: {adapter.supports_feature('haptics')}")
    print(f"Supports blur: {adapter.supports_feature('blur_effects')}")
