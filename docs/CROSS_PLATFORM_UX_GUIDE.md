# PLHub Cross-Platform UX Guide

## Overview

PLHub's Platform Adapter provides native-looking components and platform-specific behaviors for iOS, Android, Windows, macOS, Linux, and Web platforms.

**Key Features**:
- ✅ Auto platform detection
- ✅ Native component styling
- ✅ Platform conventions (button order, navigation style)
- ✅ Haptic feedback (mobile)
- ✅ Native gestures
- ✅ Safe area handling
- ✅ Platform-specific layouts

---

## Quick Start

### Basic Usage

```python
from tools.platform_adapter import PlatformAdapter, NativeComponentWrapper

# Auto-detect platform
adapter = PlatformAdapter()

# Create native-looking button
button = adapter.adapt_button("Submit", style="primary")

# Create native dialog
dialog = adapter.adapt_dialog(
    title="Confirm Action",
    message="Are you sure?",
    actions=["Cancel", "OK"]
)
```

### With PohLang

```poh
Start Program

# Import platform adapter
Import "plhub/platform"

# Auto-adapt components
Create button "Submit" with:
  - style: "primary"
  - auto_adapt: true

# Platform will automatically apply native styling

End Program
```

---

## Platform Detection

### Auto Detection

```python
from tools.platform_adapter import PlatformAdapter, Platform

# Automatically detect platform
adapter = PlatformAdapter()

print(f"Platform: {adapter.platform.value}")
# iOS, android, windows, macos, linux, or web
```

### Manual Platform

```python
# Override platform (for testing)
adapter = PlatformAdapter(platform=Platform.IOS)
adapter = PlatformAdapter(platform=Platform.ANDROID)
adapter = PlatformAdapter(platform=Platform.WINDOWS)
```

### Platform Information

```python
# Get system font
font = adapter.get_system_font()
# iOS: -apple-system, BlinkMacSystemFont, 'SF Pro'
# Android: Roboto, 'Noto Sans'
# Windows: 'Segoe UI', Tahoma, sans-serif

# Get spacing unit
spacing = adapter.get_spacing_unit()
# iOS/Android: 8px
# Windows/Linux: 4px

# Check feature support
has_haptics = adapter.supports_feature('haptics')
has_blur = adapter.supports_feature('blur_effects')
has_dark_mode = adapter.supports_feature('dark_mode')
```

---

## Native Components

### Buttons

```python
# Primary button
primary = adapter.adapt_button("Submit", style="primary")

# Secondary button
secondary = adapter.adapt_button("Cancel", style="secondary")
```

**iOS Style**:
```python
{
    'background': '#007AFF',
    'text_color': '#FFFFFF',
    'border_radius': '10px',
    'padding': '12px 24px',
    'font_weight': '600',
    'border': 'none'
}
```

**Android Style**:
```python
{
    'background': '#6200EE',
    'text_color': '#FFFFFF',
    'border_radius': '4px',
    'padding': '10px 24px',
    'font_weight': '500',
    'elevation': '2',
    'text_transform': 'uppercase'  # Material Design
}
```

**Windows Style**:
```python
{
    'background': '#0078D4',
    'text_color': '#FFFFFF',
    'border_radius': '2px',
    'padding': '8px 16px',
    'font_weight': '400',
    'border': '1px solid #CCCCCC'
}
```

### Dialogs

```python
dialog = adapter.adapt_dialog(
    title="Delete Item",
    message="This action cannot be undone",
    actions=["Cancel", "Delete"]
)
```

**iOS**: Action Sheet or Alert
```python
{
    'type': 'action_sheet',
    'title': 'Delete Item',
    'message': 'This action cannot be undone',
    'actions': ['Cancel', 'Delete'],  # Cancel first (iOS convention)
    'blur_background': True,
    'border_radius': '14px'
}
```

**Android**: Material Dialog
```python
{
    'type': 'dialog',
    'actions': ['Cancel', 'Delete'],
    'elevation': 24,
    'border_radius': '4px'
}
```

**Windows**: MessageBox
```python
{
    'type': 'message_box',
    'actions': ['Delete', 'Cancel'],  # OK/Delete first (Windows convention)
    'icon': 'info',
    'border_radius': '0px'
}
```

### Navigation Bars

```python
nav = adapter.adapt_navigation(
    title="Settings",
    has_back=True
)
```

**iOS Navigation Bar**:
```python
{
    'type': 'navigation_bar',
    'title_position': 'center',
    'back_button_style': 'chevron_with_label',  # < Back
    'blur_effect': True,
    'height': '44px'
}
```

**Android App Bar**:
```python
{
    'type': 'app_bar',
    'title_position': 'left',
    'back_button_style': 'arrow',  # ← only
    'elevation': 4,
    'height': '56px'
}
```

**Windows Title Bar**:
```python
{
    'type': 'title_bar',
    'title_position': 'left',
    'height': '32px'
}
```

### List Items

```python
item = adapter.adapt_list_item(
    title="Profile",
    subtitle="View your profile",
    icon="person",
    has_disclosure=True
)
```

**iOS List Item**:
```python
{
    'padding': '12px 16px',
    'separator_style': 'inset',  # Inset from left
    'disclosure_icon': 'chevron_right',
    'icon_size': '29px'
}
```

**Android List Item**:
```python
{
    'padding': '16px',
    'separator_style': 'full',
    'disclosure_icon': 'chevron_right',
    'icon_size': '24px',
    'ripple_effect': True  # Material ripple
}
```

---

## Platform Conventions

### Button Positions

| Platform | Primary Action |
|----------|----------------|
| iOS | Right |
| Android | Right (FAB) |
| Windows | Right |
| macOS | Right |
| Web | Right |

### Dialog Button Order

| Platform | Button Order |
|----------|--------------|
| iOS | [Cancel, OK] |
| Android | [Cancel, OK] |
| Windows | [OK, Cancel] |
| macOS | [Cancel, OK] |
| Web | [Cancel, OK] |

```python
# Automatically reordered per platform
actions = ["Cancel", "Confirm"]
dialog = adapter.adapt_dialog("Title", "Message", actions)

# iOS/Android: ["Cancel", "Confirm"]
# Windows: ["Confirm", "Cancel"]
```

### Navigation Patterns

| Platform | Pattern |
|----------|---------|
| iOS | Hierarchical (Back button + title) |
| Android | Drawer (Hamburger menu) |
| Windows | Ribbon/Menu bar |
| macOS | Sidebar |
| Web | Top navigation bar |

```python
pattern = PlatformConvention.NAVIGATION_PATTERNS[adapter.platform]
# iOS: "hierarchical"
# Android: "drawer"
# Windows: "ribbon"
```

---

## Haptic Feedback

### Mobile Haptics

```python
from tools.platform_adapter import HapticFeedback

# Impact haptic (button tap, collision)
adapter.trigger_haptic(HapticFeedback.impact('light'))
adapter.trigger_haptic(HapticFeedback.impact('medium'))
adapter.trigger_haptic(HapticFeedback.impact('heavy'))

# Notification haptic
adapter.trigger_haptic(HapticFeedback.notification('success'))
adapter.trigger_haptic(HapticFeedback.notification('warning'))
adapter.trigger_haptic(HapticFeedback.notification('error'))

# Selection haptic (picker, wheel)
adapter.trigger_haptic(HapticFeedback.selection())
```

### When to Use Haptics

| Action | Haptic Type |
|--------|-------------|
| Button tap | Impact (light) |
| Delete action | Impact (medium) |
| Error | Notification (error) |
| Success | Notification (success) |
| List selection | Selection |
| Swipe action | Impact (light) |

### Platform Support

```python
if adapter.haptics_enabled:
    # iOS and Android support haptics
    adapter.trigger_haptic(HapticFeedback.impact())
```

---

## Native Component Wrapper

### Creating Native Buttons

```python
from tools.platform_adapter import NativeComponentWrapper

wrapper = NativeComponentWrapper(adapter)

# Button with automatic haptic feedback
button = wrapper.create_button(
    label="Save",
    on_click=lambda: print("Saved!"),
    style="primary"
)

# Automatically triggers haptic on click (mobile)
```

### Creating Native Dialogs

```python
dialog = wrapper.create_dialog(
    title="Confirm Delete",
    message="This cannot be undone",
    on_confirm=lambda: delete_item(),
    on_cancel=lambda: print("Cancelled")
)
```

### Creating Native Lists

```python
items = [
    {'title': 'Profile', 'subtitle': 'View profile', 'has_disclosure': True},
    {'title': 'Settings', 'subtitle': 'App settings', 'has_disclosure': True},
    {'title': 'Logout', 'subtitle': None, 'has_disclosure': False}
]

list_view = wrapper.create_list(
    items=items,
    on_item_click=lambda index: print(f"Clicked item {index}")
)

# Automatically triggers selection haptic (mobile)
```

### Creating Navigation

```python
nav = wrapper.create_navigation_bar(
    title="Settings",
    on_back=lambda: navigate_back()
)

# Automatically triggers haptic on back button (mobile)
```

---

## Platform-Specific Layouts

### Safe Area Insets

```python
from tools.platform_adapter import PlatformLayoutManager

layout_mgr = PlatformLayoutManager(adapter)

# Get safe area insets
insets = layout_mgr.get_safe_area_insets()

# iOS (iPhone with notch):
# {'top': 47, 'bottom': 34, 'left': 0, 'right': 0}

# Android:
# {'top': 24, 'bottom': 48, 'left': 0, 'right': 0}

# Desktop:
# {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
```

### Apply Safe Area

```python
layout = {
    'padding': {'top': 0, 'bottom': 0, 'left': 16, 'right': 16}
}

# Apply safe area insets
safe_layout = layout_mgr.apply_safe_area(layout)

# Result (iOS):
# {
#     'padding': {
#         'top': 47,    # Original 0 + inset 47
#         'bottom': 34, # Original 0 + inset 34
#         'left': 16,
#         'right': 16
#     }
# }
```

### Platform Layouts

```python
# Form layout
form = layout_mgr.get_platform_layout('form')

# iOS:
# {'spacing': 16, 'input_height': 44, 'label_style': 'above', 'group_style': 'grouped'}

# Android:
# {'spacing': 16, 'input_height': 56, 'label_style': 'floating', 'group_style': 'outlined'}

# List layout
list_layout = layout_mgr.get_platform_layout('list')

# iOS:
# {'item_height': 44, 'section_header_height': 28, 'separator_inset': 16}

# Android:
# {'item_height': 72, 'section_header_height': 48, 'separator_inset': 0}

# Grid layout
grid = layout_mgr.get_platform_layout('grid')

# Mobile: 2 columns
# Desktop: 3 columns
```

---

## Animation Durations

### Platform-Specific Timing

```python
# Get platform-appropriate duration
quick = adapter.get_animation_duration('quick')
normal = adapter.get_animation_duration('normal')
slow = adapter.get_animation_duration('slow')
```

| Platform | Quick | Normal | Slow |
|----------|-------|--------|------|
| iOS | 200ms | 300ms | 500ms |
| Android | 150ms | 250ms | 400ms |
| Windows | 167ms | 300ms | 500ms |
| macOS | 200ms | 300ms | 500ms |
| Web | 150ms | 300ms | 500ms |

### Usage

```python
from tools.animation_framework import TransitionAnimation

# Use platform duration
duration = adapter.get_animation_duration('normal')

animation = TransitionAnimation(
    property="opacity",
    from_value=0,
    to_value=1,
    duration=duration  # Platform-appropriate
)
```

---

## Gesture Configuration

### Platform Gestures

```python
gestures = adapter.gesture_config

# Swipe threshold (pixels)
swipe_threshold = gestures.swipe_threshold  # 50px (mobile), 80px (desktop)

# Long press duration (milliseconds)
long_press = gestures.long_press_duration  # 500ms (mobile), 600ms (desktop)

# Double tap delay
double_tap = gestures.double_tap_delay  # 300ms (mobile), 400ms (desktop)

# Pinch threshold
pinch = gestures.pinch_threshold  # 0.1 (mobile), 0.15 (desktop)
```

### System Gestures

```python
if adapter.supports_feature('system_gestures'):
    # iOS: Swipe from edge to go back
    # Android: Swipe from edge for drawer
    enable_system_gestures()
```

---

## Platform Themes

### Default Themes

```python
theme = adapter.theme

# Colors
primary_color = theme.primary_color      # #007AFF (iOS), #6200EE (Android)
accent_color = theme.accent_color        # #5AC8FA (iOS), #03DAC6 (Android)
background_color = theme.background_color # Platform default
surface_color = theme.surface_color       # Card/surface color
text_color = theme.text_color            # Default text

# Styling
border_radius = theme.border_radius      # 10px (iOS), 4px (Android), 2px (Windows)
shadow = theme.shadow                    # Platform shadow
border_color = theme.border_color        # Border/divider
font_family = theme.font_family          # System font
```

### Theme per Platform

| Platform | Primary | Accent | Radius |
|----------|---------|--------|--------|
| iOS | #007AFF | #5AC8FA | 10px |
| Android | #6200EE | #03DAC6 | 4px |
| Windows | #0078D4 | #00A4EF | 2px |
| macOS | #007AFF | #5AC8FA | 6px |
| Web | #3B82F6 | #10B981 | 8px |

---

## Feature Support

### Check Features

```python
# Haptic feedback
has_haptics = adapter.supports_feature('haptics')
# iOS, Android: True

# Blur effects
has_blur = adapter.supports_feature('blur_effects')
# iOS, macOS, Web: True

# Elevation shadows
has_elevation = adapter.supports_feature('elevation_shadows')
# Android, Web: True

# System gestures
has_gestures = adapter.supports_feature('system_gestures')
# iOS, Android: True

# Dark mode
has_dark_mode = adapter.supports_feature('dark_mode')
# All platforms: True

# Native notifications
has_notifications = adapter.supports_feature('notifications')
# All platforms: True

# File picker
has_file_picker = adapter.supports_feature('file_picker')
# Desktop, Web: True
```

### Conditional Features

```python
if adapter.supports_feature('blur_effects'):
    # Use blur backdrop
    apply_blur_effect()
else:
    # Fallback to solid background
    apply_solid_background()

if adapter.supports_feature('haptics'):
    adapter.trigger_haptic(HapticFeedback.impact())
```

---

## Complete Example

### Cross-Platform App

```python
from tools.platform_adapter import (
    PlatformAdapter,
    NativeComponentWrapper,
    PlatformLayoutManager,
    HapticFeedback
)

# Initialize
adapter = PlatformAdapter()
wrapper = NativeComponentWrapper(adapter)
layout_mgr = PlatformLayoutManager(adapter)

print(f"Running on {adapter.platform.value}")

# Create native navigation
nav = wrapper.create_navigation_bar(
    title="My App",
    on_back=lambda: print("Back pressed")
)

# Create native list
items = [
    {'title': 'Item 1', 'subtitle': 'Description', 'has_disclosure': True},
    {'title': 'Item 2', 'subtitle': 'Description', 'has_disclosure': True},
    {'title': 'Item 3', 'subtitle': 'Description', 'has_disclosure': True}
]

list_view = wrapper.create_list(
    items=items,
    on_item_click=lambda idx: show_detail(idx)
)

# Create native button
def handle_submit():
    # Show native dialog
    dialog = wrapper.create_dialog(
        title="Confirm",
        message="Submit data?",
        on_confirm=lambda: submit_data(),
        on_cancel=lambda: print("Cancelled")
    )
    show_dialog(dialog)

button = wrapper.create_button(
    label="Submit",
    on_click=handle_submit,
    style="primary"
)

# Apply safe area
layout = layout_mgr.apply_safe_area({
    'padding': {'top': 0, 'bottom': 0, 'left': 16, 'right': 16}
})

# Use platform animation duration
duration = adapter.get_animation_duration('normal')

# Result: Native-looking app on all platforms!
```

---

## PohLang Integration

### Auto-Adapting Components

```poh
Start Program

# Auto-detect platform
Detect platform

# Create button (auto-adapts)
Create button "Submit" with:
  - auto_adapt: true
  - style: "primary"

# Create dialog (auto-adapts button order)
Create dialog with:
  - title: "Confirm"
  - message: "Are you sure?"
  - actions: ["Cancel", "OK"]
  - auto_adapt: true

# Create list (auto-adapts styling)
Create list with:
  - items: [...data...]
  - auto_adapt: true

# Apply safe area automatically
Enable safe_area_insets

Print "Running on" platform_name

End Program
```

### Platform-Specific Code

```poh
Start Program

Detect platform

If platform is "ios":
  Use ios_navigation_style
  Enable blur_effects
  Enable haptic_feedback
Else If platform is "android":
  Use material_design
  Enable ripple_effects
  Enable haptic_feedback
Else If platform is "windows":
  Use fluent_design
  Use title_bar_navigation
Else:
  Use default_theme

End Program
```

---

## Best Practices

### 1. Always Auto-Adapt

```python
# Good: Use adapter
button = adapter.adapt_button("Submit", "primary")

# Avoid: Hardcoded styles
button = {'background': '#007AFF', 'padding': '12px 24px'}
```

### 2. Respect Platform Conventions

```python
# Good: Platform-specific button order
dialog = adapter.adapt_dialog(title, message, ["Cancel", "OK"])

# Avoid: Hardcoded order
actions = ["OK", "Cancel"]  # Breaks iOS/Android conventions
```

### 3. Use Haptics Appropriately

```python
# Good: Subtle, meaningful feedback
adapter.trigger_haptic(HapticFeedback.impact('light'))

# Avoid: Excessive haptics
for item in items:
    adapter.trigger_haptic(HapticFeedback.impact('heavy'))  # Too much!
```

### 4. Handle Safe Areas

```python
# Good: Apply safe area
layout = layout_mgr.apply_safe_area(layout)

# Avoid: Fixed positioning without safe area
layout = {'position': 'fixed', 'top': '0px'}  # Overlaps notch
```

### 5. Check Feature Support

```python
# Good: Check before using
if adapter.supports_feature('haptics'):
    adapter.trigger_haptic(HapticFeedback.impact())

# Avoid: Assume support
adapter.trigger_haptic(HapticFeedback.impact())  # Fails on desktop
```

---

## Platform Differences Summary

| Feature | iOS | Android | Windows | macOS | Web |
|---------|-----|---------|---------|-------|-----|
| **Button Radius** | 10px | 4px | 2px | 6px | 8px |
| **Navigation Height** | 44px | 56px | 32px | 52px | 64px |
| **List Item Height** | 44px | 72px | 48px | 48px | 56px |
| **Haptics** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Blur Effects** | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Elevation** | ❌ | ✅ | ✅ | ❌ | ✅ |
| **System Gestures** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Safe Area Insets** | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## See Also

- [Design System](./DESIGN_SYSTEM_GUIDE.md)
- [Animation Framework](./ANIMATION_FRAMEWORK_GUIDE.md)
- [Component Library](./COMPONENT_LIBRARY_GUIDE.md)

---

**PLHub Platform Adapter** - True native experience on every platform.
