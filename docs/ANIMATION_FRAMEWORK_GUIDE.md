# PLHub Animation Framework Guide

## Overview

PLHub's Animation Framework provides a comprehensive system for creating smooth, performant animations with CSS-like transitions, keyframe animations, physics-based springs, and gesture-driven interactions.

**Key Features**:
- ✅ 25+ easing functions
- ✅ Transition animations (fade, slide, scale, rotate)
- ✅ Keyframe animations with timelines
- ✅ Spring physics animations
- ✅ Gesture-driven animations
- ✅ Animation groups and sequencing
- ✅ Staggered animations
- ✅ Animation presets

---

## Quick Start

### Simple Fade In

```python
from tools.animation_framework import AnimationPresets, AnimationManager

# Create animation manager
manager = AnimationManager()

# Register fade-in animation
fade_in = AnimationPresets.fade_in(duration=300)
manager.register('fade-in', fade_in)

# Play animation
manager.play('fade-in')
```

### With PohLang

```poh
Start Program

# Import animation
Import "plhub/animation"

# Create fade-in animation
Create animation "fade_in" with:
  - type: "fade"
  - direction: "in"
  - duration: 300
  - easing: "ease-out"

# Play animation on element
Animate element "welcome_message" with "fade_in"

End Program
```

---

## Easing Functions

### Standard Easing

**Linear**: No acceleration
```python
EasingFunction.LINEAR
```

**Ease In/Out**: Smooth start/end
```python
EasingFunction.EASE_IN      # Slow start
EasingFunction.EASE_OUT     # Slow end
EasingFunction.EASE_IN_OUT  # Slow start and end
```

### Quadratic (Gentle)

```python
EasingFunction.EASE_IN_QUAD
EasingFunction.EASE_OUT_QUAD
EasingFunction.EASE_IN_OUT_QUAD
```

### Cubic (Moderate)

```python
EasingFunction.EASE_IN_CUBIC
EasingFunction.EASE_OUT_CUBIC
EasingFunction.EASE_IN_OUT_CUBIC
```

### Quartic (Strong)

```python
EasingFunction.EASE_IN_QUART
EasingFunction.EASE_OUT_QUART
EasingFunction.EASE_IN_OUT_QUART
```

### Exponential (Very Strong)

```python
EasingFunction.EASE_IN_EXPO
EasingFunction.EASE_OUT_EXPO
EasingFunction.EASE_IN_OUT_EXPO
```

### Back (Overshoot)

```python
EasingFunction.EASE_IN_BACK      # Pulls back before starting
EasingFunction.EASE_OUT_BACK     # Overshoots then settles
EasingFunction.EASE_IN_OUT_BACK  # Both
```

### Elastic (Spring-like)

```python
EasingFunction.EASE_IN_ELASTIC
EasingFunction.EASE_OUT_ELASTIC
EasingFunction.EASE_IN_OUT_ELASTIC
```

### Bounce

```python
EasingFunction.EASE_IN_BOUNCE
EasingFunction.EASE_OUT_BOUNCE
EasingFunction.EASE_IN_OUT_BOUNCE
```

### Visualization

```
LINEAR:        ────────────
EASE_IN:       ________──────
EASE_OUT:      ──────________
EASE_IN_OUT:   ____────____
BACK:          ↶───────────↷
ELASTIC:       ╱╲╱╲╱────────
BOUNCE:        ────────╱\╱\╱
```

---

## Transition Animations

### Basic Transitions

```python
from tools.animation_framework import TransitionAnimation, EasingFunction

# Fade
fade = TransitionAnimation(
    property="opacity",
    from_value=0,
    to_value=1,
    duration=300,
    easing=EasingFunction.EASE_OUT
)

# Scale
scale = TransitionAnimation(
    property="scale",
    from_value=0,
    to_value=1,
    duration=400,
    easing=EasingFunction.EASE_OUT_BACK
)

# Position
slide = TransitionAnimation(
    property="translateX",
    from_value=-100,
    to_value=0,
    duration=500,
    easing=EasingFunction.EASE_OUT_CUBIC
)
```

### With Callbacks

```python
def on_start():
    print("Animation started")

def on_update(value):
    print(f"Current value: {value}")

def on_complete():
    print("Animation complete")

animation = TransitionAnimation(
    property="opacity",
    from_value=0,
    to_value=1,
    duration=300,
    on_start=on_start,
    on_update=on_update,
    on_complete=on_complete
)
```

---

## Keyframe Animations

### Creating Keyframes

```python
from tools.animation_framework import KeyframeAnimation, Keyframe

# Pulse animation
pulse = KeyframeAnimation(
    property="scale",
    keyframes=[
        Keyframe(0.0, 1.0),                          # Start
        Keyframe(0.5, 1.2, EasingFunction.EASE_OUT), # Mid
        Keyframe(1.0, 1.0)                           # End
    ],
    duration=600,
    iterations=-1  # Infinite
)

# Complex animation
complex_anim = KeyframeAnimation(
    property="transform",
    keyframes=[
        Keyframe(0.0, {'x': 0, 'y': 0, 'scale': 1}),
        Keyframe(0.3, {'x': 50, 'y': -20, 'scale': 1.2}),
        Keyframe(0.6, {'x': 100, 'y': 0, 'scale': 1}),
        Keyframe(1.0, {'x': 0, 'y': 0, 'scale': 1})
    ],
    duration=2000
)
```

### Keyframe Offsets

Offsets are normalized (0.0 to 1.0):
- `0.0` = Start (0%)
- `0.5` = Midpoint (50%)
- `1.0` = End (100%)

```python
keyframes = [
    Keyframe(0.0, 0),      # 0% - Start
    Keyframe(0.25, 50),    # 25% - Quarter way
    Keyframe(0.5, 100),    # 50% - Halfway
    Keyframe(0.75, 50),    # 75% - Three quarters
    Keyframe(1.0, 0)       # 100% - End
]
```

---

## Spring Physics Animations

### Basic Spring

```python
from tools.animation_framework import SpringAnimation, SpringConfig

# Default spring (bouncy)
spring = SpringAnimation(
    property="translateY",
    from_value=0,
    to_value=100,
    config=SpringConfig(
        stiffness=170,  # How stiff the spring is
        damping=26,     # How much resistance
        mass=1          # Mass of object
    )
)
```

### Spring Presets

**Gentle Spring**:
```python
config = SpringConfig(stiffness=120, damping=14)
```

**Bouncy Spring**:
```python
config = SpringConfig(stiffness=300, damping=10)
```

**Slow Spring**:
```python
config = SpringConfig(stiffness=80, damping=20)
```

**Stiff Spring** (no overshoot):
```python
config = SpringConfig(stiffness=500, damping=50)
```

### Spring Parameters

- **Stiffness** (50-500): How quickly spring pulls back
  - Low = slow, gentle
  - High = fast, snappy

- **Damping** (5-50): Resistance/friction
  - Low = more oscillation/bounce
  - High = less bounce, settles quickly

- **Mass** (0.5-2): Weight of object
  - Low = lighter, faster
  - High = heavier, slower

---

## Animation Presets

### Entrance Animations

```python
from tools.animation_framework import AnimationPresets

# Fade in
fade_in = AnimationPresets.fade_in(duration=300)

# Slide in from left
slide_in_left = AnimationPresets.slide_in(
    direction=AnimationDirection.LEFT,
    duration=400
)

# Scale in
scale_in = AnimationPresets.scale_in(duration=300)

# Bounce in
bounce_in = AnimationPresets.bounce_in(duration=600)

# Rotate in
rotate_in = AnimationPresets.rotate_in(duration=400)
```

### Exit Animations

```python
# Fade out
fade_out = AnimationPresets.fade_out(duration=300)

# Slide out to right
slide_out = AnimationPresets.slide_in(
    direction=AnimationDirection.RIGHT,
    duration=400
)
```

### Attention Seekers

```python
# Pulse (scale up/down repeatedly)
pulse = AnimationPresets.pulse(duration=1000, iterations=-1)

# Shake (horizontal movement)
shake = AnimationPresets.shake(duration=500)

# Wobble (rotation)
wobble = AnimationPresets.wobble(duration=800)
```

---

## Animation Groups

### Parallel Animations

Multiple animations play at the same time:

```python
from tools.animation_framework import AnimationGroup

fade = AnimationPresets.fade_in(duration=300)
slide = AnimationPresets.slide_in(duration=300)
scale = AnimationPresets.scale_in(duration=300)

group = AnimationGroup(
    [fade, slide, scale],
    mode="parallel"
)

# All three animations play simultaneously
```

### Sequential Animations

Animations play one after another:

```python
group = AnimationGroup(
    [fade, slide, scale],
    mode="sequence"
)

# fade → slide → scale (in order)
```

---

## Staggered Animations

Animate multiple items with a delay between each:

```python
from tools.animation_framework import StaggeredAnimation

# Create factory function
def create_fade_in(index):
    return AnimationPresets.fade_in(duration=300)

# Stagger 5 items with 100ms delay
staggered = StaggeredAnimation(
    animation_factory=create_fade_in,
    item_count=5,
    stagger_delay=100
)

# Items animate: 0ms, 100ms, 200ms, 300ms, 400ms
```

### Real-World Example

```python
# Animate list items
items = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']

def create_item_animation(index):
    return KeyframeAnimation(
        property="transform",
        keyframes=[
            Keyframe(0.0, {'opacity': 0, 'translateY': -20}),
            Keyframe(1.0, {'opacity': 1, 'translateY': 0})
        ],
        duration=400,
        easing=EasingFunction.EASE_OUT
    )

staggered = StaggeredAnimation(
    animation_factory=create_item_animation,
    item_count=len(items),
    stagger_delay=80
)
```

---

## Gesture-Driven Animations

### Drag Animation

```python
from tools.animation_framework import GestureAnimation

gesture = GestureAnimation(animation_type="drag")

# On touch/mouse down
gesture.on_start(x=100, y=100)

# On move
gesture.on_move(x=150, y=120)

# On touch/mouse up
momentum_anim = gesture.on_end()

# momentum_anim is a SpringAnimation for deceleration
if momentum_anim:
    manager.register('momentum', momentum_anim)
    manager.play('momentum')
```

### Swipe Animation

```python
gesture = GestureAnimation(animation_type="swipe")

# Track gesture
gesture.on_start(x=0, y=100)
gesture.on_move(x=200, y=100)  # Swiped 200px right

# Get delta
dx, dy = gesture.get_delta()
print(f"Swiped {dx}px horizontally")

# End gesture
gesture.on_end()
```

---

## Animation Manager

### Managing Multiple Animations

```python
from tools.animation_framework import AnimationManager

manager = AnimationManager()

# Register animations
manager.register('fade-in', AnimationPresets.fade_in())
manager.register('slide-up', AnimationPresets.slide_in())
manager.register('pulse', AnimationPresets.pulse())

# Play animations
manager.play('fade-in')
manager.play('pulse')

# Control playback
manager.pause('pulse')
manager.resume('pulse')
manager.stop('pulse')

# Update loop (call repeatedly, e.g., 60 FPS)
while True:
    manager.update(delta_time=0.016)  # 16ms = ~60 FPS
```

### Export/Import Configurations

```python
from pathlib import Path

# Export animations to JSON
manager.export_config(Path('animations.json'))

# Import from JSON
manager.import_config(Path('animations.json'))
```

---

## Advanced Usage

### Custom Easing with Cubic Bezier

```python
from tools.animation_framework import Easing

# CSS cubic-bezier(0.42, 0, 0.58, 1)
def custom_easing(t):
    return Easing.cubic_bezier(t, 0.42, 0, 0.58, 1)

animation = TransitionAnimation(
    property="opacity",
    from_value=0,
    to_value=1,
    duration=300,
    easing=custom_easing
)
```

### Interpolation

```python
from tools.animation_framework import lerp, clamp

# Linear interpolation
value = lerp(start=0, end=100, t=0.5)  # 50

# Clamp values
clamped = clamp(value=150, min_val=0, max_val=100)  # 100
```

### Animation Chaining

```python
def chain_animations():
    fade_in = AnimationPresets.fade_in(duration=300)
    scale_up = AnimationPresets.scale_in(duration=200)
    
    fade_in.on_complete = lambda: manager.play('scale-up')
    
    manager.register('fade-in', fade_in)
    manager.register('scale-up', scale_up)
    manager.play('fade-in')
```

---

## Performance Optimization

### Best Practices

1. **Use transform properties**:
   ```python
   # Good (GPU accelerated)
   TransitionAnimation(property="translateX", ...)
   TransitionAnimation(property="scale", ...)
   
   # Avoid (forces layout)
   TransitionAnimation(property="left", ...)
   TransitionAnimation(property="width", ...)
   ```

2. **Limit concurrent animations**:
   ```python
   # Keep under 10 simultaneous animations
   if len(manager.running_animations) < 10:
       manager.play('new-animation')
   ```

3. **Use will-change for complex animations**:
   ```python
   # Hint browser/renderer to optimize
   element.style.will_change = "transform, opacity"
   ```

4. **Cleanup completed animations**:
   ```python
   animation.on_complete = lambda: manager.stop('animation-name')
   ```

### Performance Metrics

| Animation Type | CPU Usage | GPU Usage | Memory |
|---------------|-----------|-----------|--------|
| Opacity | Low | Low | Low |
| Transform | Low | High | Low |
| Position | High | Low | Low |
| Color | Medium | Medium | Medium |
| Width/Height | High | Low | High |

---

## PohLang Integration

### Basic Animation

```poh
Start Program

# Create fade-in animation
Create animation with:
  - name: "hero_fade"
  - property: "opacity"
  - from: 0
  - to: 1
  - duration: 500
  - easing: "ease-out"

# Apply to element
Animate element "hero_section" with "hero_fade"

End Program
```

### Keyframe Animation

```poh
Start Program

# Create pulse animation
Create keyframe_animation with:
  - name: "button_pulse"
  - property: "scale"
  - keyframes:
    * offset: 0.0, value: 1.0
    * offset: 0.5, value: 1.1, easing: "ease-out"
    * offset: 1.0, value: 1.0
  - duration: 800
  - iterations: infinite

# Apply to button
Animate element "cta_button" with "button_pulse"

End Program
```

### Gesture Animation

```poh
Start Program

# Setup drag animation
Create gesture_animation with:
  - name: "card_drag"
  - type: "drag"

# On drag start
On touch_start of "card":
  Start gesture "card_drag" at touch_position

# On drag move
On touch_move of "card":
  Update gesture "card_drag" to touch_position
  Set card_position to gesture_delta

# On drag end
On touch_end of "card":
  End gesture "card_drag"
  Apply momentum to "card"

End Program
```

---

## Examples

### Loading Spinner

```python
# Rotating spinner
spinner = KeyframeAnimation(
    property="rotate",
    keyframes=[
        Keyframe(0.0, 0),
        Keyframe(1.0, 360)
    ],
    duration=1000,
    iterations=-1,
    easing=EasingFunction.LINEAR
)
```

### Modal Entrance

```python
# Fade + scale modal
def show_modal():
    fade = AnimationPresets.fade_in(duration=200)
    scale = TransitionAnimation(
        property="scale",
        from_value=0.8,
        to_value=1.0,
        duration=300,
        easing=EasingFunction.EASE_OUT_BACK
    )
    
    group = AnimationGroup([fade, scale], mode="parallel")
    return group
```

### List Item Entrance

```python
# Staggered list items
items = get_list_items()

def create_item_animation(index):
    return KeyframeAnimation(
        property="transform",
        keyframes=[
            Keyframe(0.0, {'opacity': 0, 'translateX': -30}),
            Keyframe(1.0, {'opacity': 1, 'translateX': 0})
        ],
        duration=400,
        easing=EasingFunction.EASE_OUT_CUBIC
    )

staggered = StaggeredAnimation(
    create_item_animation,
    item_count=len(items),
    stagger_delay=60
)
```

### Pull-to-Refresh

```python
# Spring-based pull-to-refresh
gesture = GestureAnimation(animation_type="drag")

def on_pull_start(x, y):
    gesture.on_start(x, y)

def on_pull_move(x, y):
    gesture.on_move(x, y)
    dx, dy = gesture.get_delta()
    
    # Update pull indicator
    pull_distance = max(0, dy)
    update_indicator(pull_distance)
    
    # Trigger refresh at threshold
    if pull_distance > 80:
        trigger_refresh()

def on_pull_end():
    momentum = gesture.on_end()
    # Spring back to top
    if momentum:
        manager.register('snap-back', momentum)
        manager.play('snap-back')
```

---

## Troubleshooting

### Animation Not Playing

```python
# Check if registered
if 'my-anim' in manager.animations:
    print("Animation registered")

# Check if playing
if 'my-anim' in manager.running_animations:
    print("Animation is running")

# Ensure update loop is running
manager.update()  # Call this repeatedly
```

### Jerky Animation

```python
# Use appropriate easing
animation.easing = EasingFunction.EASE_OUT_CUBIC

# Reduce animation duration
animation.duration = 200  # Shorter = smoother perception

# Use GPU-accelerated properties
animation.property = "transform"  # Not "left" or "width"
```

### Spring Not Settling

```python
# Increase damping
config = SpringConfig(
    stiffness=170,
    damping=40  # Higher damping
)

# Decrease precision threshold
config.precision = 0.1  # More lenient
```

---

## API Reference

### TransitionAnimation
- `property` - Property to animate
- `from_value` - Starting value
- `to_value` - Ending value
- `duration` - Duration in milliseconds
- `easing` - Easing function
- `delay` - Delay before start

### KeyframeAnimation
- `property` - Property to animate
- `keyframes` - List of Keyframe objects
- `duration` - Total duration
- `iterations` - Number of iterations (-1 = infinite)

### SpringAnimation
- `property` - Property to animate
- `from_value` - Starting value
- `to_value` - Target value
- `config` - SpringConfig object

### AnimationManager
- `register(name, animation)` - Register animation
- `play(name)` - Play animation
- `pause(name)` - Pause animation
- `resume(name)` - Resume animation
- `stop(name)` - Stop animation
- `update(delta_time)` - Update all animations

---

## See Also

- [State Management](./STATE_MANAGEMENT_GUIDE.md)
- [Component Library](./COMPONENT_LIBRARY_GUIDE.md)
- [Layout System](./LAYOUT_SYSTEM_GUIDE.md)

---

**PLHub Animation Framework** - Smooth, performant animations for modern applications.
