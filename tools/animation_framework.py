"""
PLHub Animation Framework
Provides comprehensive animation capabilities including transitions, keyframes, 
easing functions, gesture-driven animations, and physics-based animations

Features:
- CSS-like transitions (fade, slide, scale, rotate)
- Keyframe animations with timelines
- Easing functions (ease-in, ease-out, cubic-bezier)
- Spring physics animations
- Gesture-driven animations (swipe, drag, pinch)
- Animation composition and sequencing
- Animation groups and staggering
- Performance optimization
"""

import math
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class EasingFunction(Enum):
    """Standard easing functions"""
    LINEAR = "linear"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_OUT = "ease-in-out"
    EASE_IN_QUAD = "ease-in-quad"
    EASE_OUT_QUAD = "ease-out-quad"
    EASE_IN_OUT_QUAD = "ease-in-out-quad"
    EASE_IN_CUBIC = "ease-in-cubic"
    EASE_OUT_CUBIC = "ease-out-cubic"
    EASE_IN_OUT_CUBIC = "ease-in-out-cubic"
    EASE_IN_QUART = "ease-in-quart"
    EASE_OUT_QUART = "ease-out-quart"
    EASE_IN_OUT_QUART = "ease-in-out-quart"
    EASE_IN_EXPO = "ease-in-expo"
    EASE_OUT_EXPO = "ease-out-expo"
    EASE_IN_OUT_EXPO = "ease-in-out-expo"
    EASE_IN_BACK = "ease-in-back"
    EASE_OUT_BACK = "ease-out-back"
    EASE_IN_OUT_BACK = "ease-in-out-back"
    EASE_IN_ELASTIC = "ease-in-elastic"
    EASE_OUT_ELASTIC = "ease-out-elastic"
    EASE_IN_OUT_ELASTIC = "ease-in-out-elastic"
    EASE_IN_BOUNCE = "ease-in-bounce"
    EASE_OUT_BOUNCE = "ease-out-bounce"
    EASE_IN_OUT_BOUNCE = "ease-in-out-bounce"


class AnimationType(Enum):
    """Types of animations"""
    FADE = "fade"
    SLIDE = "slide"
    SCALE = "scale"
    ROTATE = "rotate"
    TRANSFORM = "transform"
    COLOR = "color"
    CUSTOM = "custom"


class AnimationDirection(Enum):
    """Animation directions"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    IN = "in"
    OUT = "out"


class Easing:
    """Easing function implementations"""
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear easing (no acceleration)"""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out"""
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out"""
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out"""
        return (--t) * t * t + 1
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out"""
        return 4 * t * t * t if t < 0.5 else (t - 1) * (2 * t - 2) * (2 * t - 2) + 1
    
    @staticmethod
    def ease_in_quart(t: float) -> float:
        """Quartic ease-in"""
        return t * t * t * t
    
    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic ease-out"""
        return 1 - (--t) * t * t * t
    
    @staticmethod
    def ease_in_out_quart(t: float) -> float:
        """Quartic ease-in-out"""
        return 8 * t * t * t * t if t < 0.5 else 1 - 8 * (--t) * t * t * t
    
    @staticmethod
    def ease_in_expo(t: float) -> float:
        """Exponential ease-in"""
        return 0 if t == 0 else math.pow(2, 10 * (t - 1))
    
    @staticmethod
    def ease_out_expo(t: float) -> float:
        """Exponential ease-out"""
        return 1 if t == 1 else 1 - math.pow(2, -10 * t)
    
    @staticmethod
    def ease_in_out_expo(t: float) -> float:
        """Exponential ease-in-out"""
        if t == 0 or t == 1:
            return t
        if t < 0.5:
            return math.pow(2, 20 * t - 10) / 2
        return (2 - math.pow(2, -20 * t + 10)) / 2
    
    @staticmethod
    def ease_in_back(t: float, s: float = 1.70158) -> float:
        """Back ease-in (overshoots)"""
        return t * t * ((s + 1) * t - s)
    
    @staticmethod
    def ease_out_back(t: float, s: float = 1.70158) -> float:
        """Back ease-out (overshoots)"""
        t -= 1
        return t * t * ((s + 1) * t + s) + 1
    
    @staticmethod
    def ease_in_out_back(t: float, s: float = 1.70158) -> float:
        """Back ease-in-out (overshoots)"""
        s *= 1.525
        t *= 2
        if t < 1:
            return 0.5 * (t * t * ((s + 1) * t - s))
        t -= 2
        return 0.5 * (t * t * ((s + 1) * t + s) + 2)
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        """Bounce ease-out"""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375
    
    @staticmethod
    def ease_in_bounce(t: float) -> float:
        """Bounce ease-in"""
        return 1 - Easing.ease_out_bounce(1 - t)
    
    @staticmethod
    def ease_in_out_bounce(t: float) -> float:
        """Bounce ease-in-out"""
        if t < 0.5:
            return Easing.ease_in_bounce(t * 2) * 0.5
        return Easing.ease_out_bounce(t * 2 - 1) * 0.5 + 0.5
    
    @staticmethod
    def ease_out_elastic(t: float, amplitude: float = 1, period: float = 0.3) -> float:
        """Elastic ease-out"""
        if t == 0 or t == 1:
            return t
        s = period / 4
        return amplitude * math.pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / period) + 1
    
    @staticmethod
    def ease_in_elastic(t: float, amplitude: float = 1, period: float = 0.3) -> float:
        """Elastic ease-in"""
        return 1 - Easing.ease_out_elastic(1 - t, amplitude, period)
    
    @staticmethod
    def ease_in_out_elastic(t: float, amplitude: float = 1, period: float = 0.3) -> float:
        """Elastic ease-in-out"""
        if t < 0.5:
            return Easing.ease_in_elastic(t * 2, amplitude, period) * 0.5
        return Easing.ease_out_elastic(t * 2 - 1, amplitude, period) * 0.5 + 0.5
    
    @staticmethod
    def cubic_bezier(t: float, p1x: float, p1y: float, p2x: float, p2y: float) -> float:
        """Cubic Bezier easing (CSS cubic-bezier)"""
        # Simplified implementation
        return 3 * (1 - t) ** 2 * t * p1y + 3 * (1 - t) * t ** 2 * p2y + t ** 3
    
    @staticmethod
    def get_easing_function(easing: EasingFunction) -> Callable[[float], float]:
        """Get easing function by name"""
        mapping = {
            EasingFunction.LINEAR: Easing.linear,
            EasingFunction.EASE_IN: Easing.ease_in_quad,
            EasingFunction.EASE_OUT: Easing.ease_out_quad,
            EasingFunction.EASE_IN_OUT: Easing.ease_in_out_quad,
            EasingFunction.EASE_IN_QUAD: Easing.ease_in_quad,
            EasingFunction.EASE_OUT_QUAD: Easing.ease_out_quad,
            EasingFunction.EASE_IN_OUT_QUAD: Easing.ease_in_out_quad,
            EasingFunction.EASE_IN_CUBIC: Easing.ease_in_cubic,
            EasingFunction.EASE_OUT_CUBIC: Easing.ease_out_cubic,
            EasingFunction.EASE_IN_OUT_CUBIC: Easing.ease_in_out_cubic,
            EasingFunction.EASE_IN_QUART: Easing.ease_in_quart,
            EasingFunction.EASE_OUT_QUART: Easing.ease_out_quart,
            EasingFunction.EASE_IN_OUT_QUART: Easing.ease_in_out_quart,
            EasingFunction.EASE_IN_EXPO: Easing.ease_in_expo,
            EasingFunction.EASE_OUT_EXPO: Easing.ease_out_expo,
            EasingFunction.EASE_IN_OUT_EXPO: Easing.ease_in_out_expo,
            EasingFunction.EASE_IN_BACK: Easing.ease_in_back,
            EasingFunction.EASE_OUT_BACK: Easing.ease_out_back,
            EasingFunction.EASE_IN_OUT_BACK: Easing.ease_in_out_back,
            EasingFunction.EASE_IN_BOUNCE: Easing.ease_in_bounce,
            EasingFunction.EASE_OUT_BOUNCE: Easing.ease_out_bounce,
            EasingFunction.EASE_IN_OUT_BOUNCE: Easing.ease_in_out_bounce,
            EasingFunction.EASE_IN_ELASTIC: Easing.ease_in_elastic,
            EasingFunction.EASE_OUT_ELASTIC: Easing.ease_out_elastic,
            EasingFunction.EASE_IN_OUT_ELASTIC: Easing.ease_in_out_elastic,
        }
        return mapping.get(easing, Easing.linear)


@dataclass
class Keyframe:
    """Animation keyframe"""
    offset: float  # 0.0 to 1.0
    value: Any
    easing: Optional[EasingFunction] = EasingFunction.LINEAR
    
    def to_dict(self) -> Dict:
        return {
            'offset': self.offset,
            'value': self.value,
            'easing': self.easing.value if self.easing else 'linear'
        }


@dataclass
class SpringConfig:
    """Spring physics configuration"""
    stiffness: float = 170  # Spring constant
    damping: float = 26     # Damping coefficient
    mass: float = 1         # Mass
    velocity: float = 0     # Initial velocity
    precision: float = 0.01 # Precision threshold
    
    def to_dict(self) -> Dict:
        return {
            'stiffness': self.stiffness,
            'damping': self.damping,
            'mass': self.mass,
            'velocity': self.velocity,
            'precision': self.precision
        }


class SpringPhysics:
    """Spring physics calculator"""
    
    @staticmethod
    def calculate(from_value: float, to_value: float, config: SpringConfig,
                 delta_time: float = 0.016) -> Tuple[float, float, bool]:
        """
        Calculate spring position and velocity
        Returns: (position, velocity, is_at_rest)
        """
        displacement = from_value - to_value
        spring_force = -config.stiffness * displacement
        damping_force = -config.damping * config.velocity
        acceleration = (spring_force + damping_force) / config.mass
        
        new_velocity = config.velocity + acceleration * delta_time
        new_position = from_value + new_velocity * delta_time
        
        # Check if at rest
        is_at_rest = (abs(new_velocity) < config.precision and 
                     abs(new_position - to_value) < config.precision)
        
        return new_position, new_velocity, is_at_rest


@dataclass
class Animation:
    """Base animation configuration"""
    duration: float = 300  # milliseconds
    easing: EasingFunction = EasingFunction.EASE_IN_OUT
    delay: float = 0
    iterations: int = 1  # -1 for infinite
    direction: str = "normal"  # normal, reverse, alternate
    fill_mode: str = "forwards"  # none, forwards, backwards, both
    
    # Callbacks
    on_start: Optional[Callable] = None
    on_update: Optional[Callable[[float], None]] = None
    on_complete: Optional[Callable] = None
    
    # State
    start_time: Optional[float] = None
    current_time: float = 0
    current_iteration: int = 0
    is_playing: bool = False
    is_paused: bool = False
    is_complete: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'duration': self.duration,
            'easing': self.easing.value,
            'delay': self.delay,
            'iterations': self.iterations,
            'direction': self.direction,
            'fill_mode': self.fill_mode
        }


@dataclass
class TransitionAnimation(Animation):
    """Transition animation (single property)"""
    property: str = "opacity"
    from_value: Any = 0
    to_value: Any = 1
    
    def get_current_value(self, progress: float) -> Any:
        """Calculate current value based on progress (0-1)"""
        easing_fn = Easing.get_easing_function(self.easing)
        eased_progress = easing_fn(progress)
        
        # Interpolate between from_value and to_value
        if isinstance(self.from_value, (int, float)) and isinstance(self.to_value, (int, float)):
            return self.from_value + (self.to_value - self.from_value) * eased_progress
        
        return self.to_value if eased_progress >= 1 else self.from_value


@dataclass
class KeyframeAnimation(Animation):
    """Keyframe-based animation"""
    property: str = "transform"
    keyframes: List[Keyframe] = field(default_factory=list)
    
    def get_current_value(self, progress: float) -> Any:
        """Get interpolated value at progress"""
        if not self.keyframes:
            return None
        
        # Find surrounding keyframes
        prev_kf = self.keyframes[0]
        next_kf = self.keyframes[-1]
        
        for i, kf in enumerate(self.keyframes):
            if kf.offset >= progress:
                next_kf = kf
                if i > 0:
                    prev_kf = self.keyframes[i - 1]
                break
        
        # Calculate local progress between keyframes
        if next_kf.offset == prev_kf.offset:
            return next_kf.value
        
        local_progress = (progress - prev_kf.offset) / (next_kf.offset - prev_kf.offset)
        
        # Apply keyframe-specific easing
        if next_kf.easing:
            easing_fn = Easing.get_easing_function(next_kf.easing)
            local_progress = easing_fn(local_progress)
        
        # Interpolate
        if isinstance(prev_kf.value, (int, float)) and isinstance(next_kf.value, (int, float)):
            return prev_kf.value + (next_kf.value - prev_kf.value) * local_progress
        
        return next_kf.value if local_progress >= 1 else prev_kf.value


@dataclass
class SpringAnimation(Animation):
    """Spring physics-based animation"""
    property: str = "transform"
    from_value: float = 0
    to_value: float = 1
    config: SpringConfig = field(default_factory=SpringConfig)
    
    # Spring state
    current_value: float = 0
    current_velocity: float = 0
    
    def __post_init__(self):
        self.current_value = self.from_value
        self.current_velocity = self.config.velocity
    
    def step(self, delta_time: float = 0.016) -> Tuple[float, bool]:
        """
        Advance spring simulation
        Returns: (current_value, is_at_rest)
        """
        self.current_value, self.current_velocity, is_at_rest = SpringPhysics.calculate(
            self.current_value,
            self.to_value,
            self.config,
            delta_time
        )
        
        # Update config velocity for next step
        self.config.velocity = self.current_velocity
        
        return self.current_value, is_at_rest


class AnimationGroup:
    """Group of animations that play together"""
    
    def __init__(self, animations: List[Animation], mode: str = "parallel"):
        """
        mode: 'parallel' (all at once) or 'sequence' (one after another)
        """
        self.animations = animations
        self.mode = mode
        self.current_index = 0
    
    def get_total_duration(self) -> float:
        """Calculate total duration"""
        if self.mode == "parallel":
            return max(
                anim.duration + anim.delay
                for anim in self.animations
            )
        else:  # sequence
            return sum(anim.duration + anim.delay for anim in self.animations)


class StaggeredAnimation:
    """Staggered animation (items animate one after another)"""
    
    def __init__(self, animation_factory: Callable[[int], Animation],
                 item_count: int, stagger_delay: float = 50):
        """
        animation_factory: Function that creates animation for each item
        item_count: Number of items to animate
        stagger_delay: Delay between each item (ms)
        """
        self.animations = []
        for i in range(item_count):
            anim = animation_factory(i)
            anim.delay += i * stagger_delay
            self.animations.append(anim)
    
    def get_total_duration(self) -> float:
        """Calculate total duration"""
        return max(
            anim.duration + anim.delay
            for anim in self.animations
        )


class GestureAnimation:
    """Gesture-driven animation (swipe, drag, pinch)"""
    
    def __init__(self, animation_type: str = "drag"):
        self.animation_type = animation_type
        self.start_position: Optional[Tuple[float, float]] = None
        self.current_position: Optional[Tuple[float, float]] = None
        self.velocity: Tuple[float, float] = (0, 0)
        self.is_active = False
    
    def on_start(self, x: float, y: float):
        """Gesture started"""
        self.start_position = (x, y)
        self.current_position = (x, y)
        self.is_active = True
    
    def on_move(self, x: float, y: float, delta_time: float = 0.016):
        """Gesture moved"""
        if not self.is_active or not self.current_position:
            return
        
        # Calculate velocity
        dx = x - self.current_position[0]
        dy = y - self.current_position[1]
        self.velocity = (dx / delta_time, dy / delta_time)
        
        self.current_position = (x, y)
    
    def on_end(self) -> Optional[SpringAnimation]:
        """
        Gesture ended
        Returns: Spring animation for momentum if applicable
        """
        self.is_active = False
        
        if self.animation_type == "drag" and self.velocity != (0, 0):
            # Create momentum animation with spring
            speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
            
            config = SpringConfig(
                stiffness=100,
                damping=20,
                velocity=speed
            )
            
            # Create spring animation for deceleration
            return SpringAnimation(
                property="position",
                from_value=0,
                to_value=0,  # Return to rest
                config=config
            )
        
        return None
    
    def get_delta(self) -> Tuple[float, float]:
        """Get distance from start"""
        if not self.start_position or not self.current_position:
            return (0, 0)
        
        return (
            self.current_position[0] - self.start_position[0],
            self.current_position[1] - self.start_position[1]
        )


class AnimationPresets:
    """Predefined animation presets"""
    
    @staticmethod
    def fade_in(duration: float = 300, delay: float = 0) -> TransitionAnimation:
        """Fade in animation"""
        return TransitionAnimation(
            property="opacity",
            from_value=0,
            to_value=1,
            duration=duration,
            delay=delay,
            easing=EasingFunction.EASE_OUT
        )
    
    @staticmethod
    def fade_out(duration: float = 300, delay: float = 0) -> TransitionAnimation:
        """Fade out animation"""
        return TransitionAnimation(
            property="opacity",
            from_value=1,
            to_value=0,
            duration=duration,
            delay=delay,
            easing=EasingFunction.EASE_IN
        )
    
    @staticmethod
    def slide_in(direction: AnimationDirection = AnimationDirection.LEFT,
                duration: float = 400, delay: float = 0) -> TransitionAnimation:
        """Slide in animation"""
        from_value = {
            AnimationDirection.LEFT: -100,
            AnimationDirection.RIGHT: 100,
            AnimationDirection.UP: -100,
            AnimationDirection.DOWN: 100
        }.get(direction, -100)
        
        return TransitionAnimation(
            property="translateX" if direction in [AnimationDirection.LEFT, AnimationDirection.RIGHT] else "translateY",
            from_value=from_value,
            to_value=0,
            duration=duration,
            delay=delay,
            easing=EasingFunction.EASE_OUT_CUBIC
        )
    
    @staticmethod
    def scale_in(duration: float = 300, delay: float = 0) -> TransitionAnimation:
        """Scale in animation"""
        return TransitionAnimation(
            property="scale",
            from_value=0,
            to_value=1,
            duration=duration,
            delay=delay,
            easing=EasingFunction.EASE_OUT_BACK
        )
    
    @staticmethod
    def bounce_in(duration: float = 600, delay: float = 0) -> TransitionAnimation:
        """Bounce in animation"""
        return TransitionAnimation(
            property="scale",
            from_value=0,
            to_value=1,
            duration=duration,
            delay=delay,
            easing=EasingFunction.EASE_OUT_BOUNCE
        )
    
    @staticmethod
    def rotate_in(duration: float = 400, delay: float = 0) -> TransitionAnimation:
        """Rotate in animation"""
        return TransitionAnimation(
            property="rotate",
            from_value=-180,
            to_value=0,
            duration=duration,
            delay=delay,
            easing=EasingFunction.EASE_OUT_BACK
        )
    
    @staticmethod
    def pulse(duration: float = 1000, iterations: int = -1) -> KeyframeAnimation:
        """Pulsing animation"""
        return KeyframeAnimation(
            property="scale",
            keyframes=[
                Keyframe(0.0, 1.0),
                Keyframe(0.5, 1.1, EasingFunction.EASE_IN_OUT),
                Keyframe(1.0, 1.0)
            ],
            duration=duration,
            iterations=iterations
        )
    
    @staticmethod
    def shake(duration: float = 500) -> KeyframeAnimation:
        """Shake animation"""
        return KeyframeAnimation(
            property="translateX",
            keyframes=[
                Keyframe(0.0, 0),
                Keyframe(0.1, -10),
                Keyframe(0.2, 10),
                Keyframe(0.3, -10),
                Keyframe(0.4, 10),
                Keyframe(0.5, -10),
                Keyframe(0.6, 10),
                Keyframe(0.7, -10),
                Keyframe(0.8, 10),
                Keyframe(0.9, -10),
                Keyframe(1.0, 0)
            ],
            duration=duration
        )
    
    @staticmethod
    def wobble(duration: float = 800) -> KeyframeAnimation:
        """Wobble animation"""
        return KeyframeAnimation(
            property="rotate",
            keyframes=[
                Keyframe(0.0, 0),
                Keyframe(0.15, -5),
                Keyframe(0.30, 3),
                Keyframe(0.45, -3),
                Keyframe(0.60, 2),
                Keyframe(0.75, -1),
                Keyframe(1.0, 0)
            ],
            duration=duration
        )


class AnimationManager:
    """Manages and coordinates animations"""
    
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.running_animations: List[str] = []
    
    def register(self, name: str, animation: Animation):
        """Register an animation"""
        self.animations[name] = animation
    
    def play(self, name: str):
        """Play an animation"""
        if name in self.animations:
            anim = self.animations[name]
            anim.is_playing = True
            anim.start_time = time.time() * 1000
            
            if name not in self.running_animations:
                self.running_animations.append(name)
            
            if anim.on_start:
                anim.on_start()
    
    def pause(self, name: str):
        """Pause an animation"""
        if name in self.animations:
            self.animations[name].is_paused = True
    
    def resume(self, name: str):
        """Resume a paused animation"""
        if name in self.animations:
            self.animations[name].is_paused = False
    
    def stop(self, name: str):
        """Stop an animation"""
        if name in self.animations:
            anim = self.animations[name]
            anim.is_playing = False
            anim.is_complete = True
            
            if name in self.running_animations:
                self.running_animations.remove(name)
    
    def update(self, delta_time: float = 0.016):
        """Update all running animations"""
        current_time = time.time() * 1000
        
        for name in self.running_animations[:]:
            anim = self.animations[name]
            
            if anim.is_paused or not anim.is_playing:
                continue
            
            # Calculate elapsed time
            if anim.start_time is None:
                continue
            
            elapsed = current_time - anim.start_time - anim.delay
            
            if elapsed < 0:
                continue  # Still in delay
            
            # Calculate progress (0-1)
            progress = min(elapsed / anim.duration, 1.0)
            
            # Get current value
            if isinstance(anim, (TransitionAnimation, KeyframeAnimation)):
                current_value = anim.get_current_value(progress)
                
                if anim.on_update:
                    anim.on_update(current_value)
            
            elif isinstance(anim, SpringAnimation):
                current_value, is_at_rest = anim.step(delta_time)
                
                if anim.on_update:
                    anim.on_update(current_value)
                
                if is_at_rest:
                    self.stop(name)
                    if anim.on_complete:
                        anim.on_complete()
                continue
            
            # Check if complete
            if progress >= 1.0:
                anim.current_iteration += 1
                
                if anim.iterations == -1 or anim.current_iteration < anim.iterations:
                    # Restart for next iteration
                    anim.start_time = current_time
                else:
                    # Complete
                    self.stop(name)
                    if anim.on_complete:
                        anim.on_complete()
    
    def export_config(self, output_file: Path):
        """Export animation configurations to JSON"""
        config = {
            name: anim.to_dict()
            for name, anim in self.animations.items()
        }
        
        output_file.write_text(json.dumps(config, indent=2))
    
    def import_config(self, config_file: Path):
        """Import animation configurations from JSON"""
        config = json.loads(config_file.read_text())
        
        for name, anim_config in config.items():
            # Create appropriate animation type
            # This is a simplified version - would need proper type detection
            anim = TransitionAnimation(
                duration=anim_config.get('duration', 300),
                easing=EasingFunction(anim_config.get('easing', 'ease-in-out')),
                delay=anim_config.get('delay', 0)
            )
            self.register(name, anim)


# Utility functions

def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation"""
    return start + (end - start) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def create_stagger(items: List[Any], animation_factory: Callable,
                  stagger_delay: float = 50) -> List[Animation]:
    """Create staggered animations for list of items"""
    animations = []
    for i, item in enumerate(items):
        anim = animation_factory(item)
        anim.delay = i * stagger_delay
        animations.append(anim)
    return animations
