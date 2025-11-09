"""
PLHub Design System Manager
Manages design tokens, color palettes, typography scales, spacing systems,
shadows, borders, and generates design system documentation.

Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
from pathlib import Path
import colorsys
import math


class TokenType(Enum):
    """Design token types"""
    COLOR = "color"
    TYPOGRAPHY = "typography"
    SPACING = "spacing"
    SHADOW = "shadow"
    BORDER = "border"
    RADIUS = "radius"
    DURATION = "duration"
    EASING = "easing"
    Z_INDEX = "z-index"
    BREAKPOINT = "breakpoint"


@dataclass
class DesignToken:
    """Represents a design token"""
    name: str
    value: Any
    type: TokenType
    description: str = ""
    category: str = "default"
    aliases: List[str] = field(default_factory=list)
    deprecated: bool = False
    replacement: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.type.value,
            'description': self.description,
            'category': self.category,
            'aliases': self.aliases,
            'deprecated': self.deprecated,
            'replacement': self.replacement
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DesignToken':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            value=data['value'],
            type=TokenType(data['type']),
            description=data.get('description', ''),
            category=data.get('category', 'default'),
            aliases=data.get('aliases', []),
            deprecated=data.get('deprecated', False),
            replacement=data.get('replacement')
        )


@dataclass
class ColorToken:
    """Color design token with variants"""
    name: str
    base: str  # Hex color
    variants: Dict[str, str] = field(default_factory=dict)  # lighter, darker, etc.
    description: str = ""
    
    def get_variant(self, variant: str) -> str:
        """Get color variant"""
        return self.variants.get(variant, self.base)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'base': self.base,
            'variants': self.variants,
            'description': self.description
        }


@dataclass
class TypographyScale:
    """Typography scale system"""
    base_size: int = 16  # Base font size in pixels
    scale_ratio: float = 1.25  # Major third
    line_height_ratio: float = 1.5
    font_family: str = "system-ui, -apple-system, sans-serif"
    font_weights: Dict[str, int] = field(default_factory=lambda: {
        'light': 300,
        'regular': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700
    })
    
    def get_size(self, step: int) -> int:
        """Get font size for scale step"""
        return round(self.base_size * (self.scale_ratio ** step))
    
    def get_line_height(self, step: int) -> int:
        """Get line height for scale step"""
        size = self.get_size(step)
        return round(size * self.line_height_ratio)
    
    def generate_scale(self, steps: List[str]) -> Dict[str, Dict]:
        """Generate typography scale"""
        scale_map = {
            'xs': -2,
            'sm': -1,
            'base': 0,
            'lg': 1,
            'xl': 2,
            '2xl': 3,
            '3xl': 4,
            '4xl': 5,
            '5xl': 6
        }
        
        result = {}
        for name in steps:
            step = scale_map.get(name, 0)
            size = self.get_size(step)
            line_height = self.get_line_height(step)
            
            result[name] = {
                'fontSize': f'{size}px',
                'lineHeight': f'{line_height}px',
                'fontFamily': self.font_family
            }
        
        return result


@dataclass
class SpacingScale:
    """Spacing scale system"""
    base_unit: int = 4  # Base spacing unit in pixels
    scale_values: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64])
    
    def get_spacing(self, step: int) -> int:
        """Get spacing value"""
        if step < len(self.scale_values):
            return self.base_unit * self.scale_values[step]
        return self.base_unit * step
    
    def generate_scale(self) -> Dict[str, str]:
        """Generate spacing scale"""
        names = ['0', '1', '2', '3', '4', '6', '8', '12', '16', '24', '32', '48', '64']
        result = {}
        
        for i, value in enumerate(self.scale_values):
            if i < len(names):
                result[names[i]] = f'{self.base_unit * value}px'
        
        return result


@dataclass
class ShadowToken:
    """Shadow design token"""
    name: str
    x_offset: int
    y_offset: int
    blur: int
    spread: int
    color: str
    opacity: float = 0.1
    
    def to_css(self) -> str:
        """Convert to CSS shadow string"""
        rgba = self._hex_to_rgba(self.color, self.opacity)
        return f'{self.x_offset}px {self.y_offset}px {self.blur}px {self.spread}px {rgba}'
    
    def _hex_to_rgba(self, hex_color: str, alpha: float) -> str:
        """Convert hex to rgba"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r}, {g}, {b}, {alpha})'
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'value': self.to_css(),
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'blur': self.blur,
            'spread': self.spread,
            'color': self.color,
            'opacity': self.opacity
        }


class ColorPalette:
    """Color palette generator and utilities"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB to hex"""
        return f'#{r:02x}{g:02x}{b:02x}'
    
    @staticmethod
    def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
        """Convert hex to HSL"""
        r, g, b = ColorPalette.hex_to_rgb(hex_color)
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)
    
    @staticmethod
    def hsl_to_hex(h: float, s: float, l: float) -> str:
        """Convert HSL to hex"""
        h, s, l = h / 360.0, s / 100.0, l / 100.0
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return ColorPalette.rgb_to_hex(r, g, b)
    
    @staticmethod
    def lighten(hex_color: str, amount: float) -> str:
        """Lighten color by percentage (0-100)"""
        h, s, l = ColorPalette.hex_to_hsl(hex_color)
        l = min(100, l + amount)
        return ColorPalette.hsl_to_hex(h, s, l)
    
    @staticmethod
    def darken(hex_color: str, amount: float) -> str:
        """Darken color by percentage (0-100)"""
        h, s, l = ColorPalette.hex_to_hsl(hex_color)
        l = max(0, l - amount)
        return ColorPalette.hsl_to_hex(h, s, l)
    
    @staticmethod
    def saturate(hex_color: str, amount: float) -> str:
        """Increase saturation by percentage"""
        h, s, l = ColorPalette.hex_to_hsl(hex_color)
        s = min(100, s + amount)
        return ColorPalette.hsl_to_hex(h, s, l)
    
    @staticmethod
    def desaturate(hex_color: str, amount: float) -> str:
        """Decrease saturation by percentage"""
        h, s, l = ColorPalette.hex_to_hsl(hex_color)
        s = max(0, s - amount)
        return ColorPalette.hsl_to_hex(h, s, l)
    
    @staticmethod
    def adjust_hue(hex_color: str, degrees: float) -> str:
        """Rotate hue by degrees"""
        h, s, l = ColorPalette.hex_to_hsl(hex_color)
        h = (h + degrees) % 360
        return ColorPalette.hsl_to_hex(h, s, l)
    
    @staticmethod
    def generate_palette(base_color: str, steps: int = 10) -> Dict[str, str]:
        """Generate color palette from base color"""
        palette = {}
        
        # Generate lighter shades
        for i in range(steps // 2):
            step = (i + 1) * (100 / (steps // 2 + 1))
            key = f'{(steps // 2 - i - 1) * 100}'
            palette[key] = ColorPalette.lighten(base_color, step)
        
        # Base color
        palette['500'] = base_color
        
        # Generate darker shades
        for i in range(steps // 2):
            step = (i + 1) * (100 / (steps // 2 + 1))
            key = f'{(steps // 2 + i + 1) * 100}'
            palette[key] = ColorPalette.darken(base_color, step)
        
        return palette
    
    @staticmethod
    def generate_complementary(hex_color: str) -> str:
        """Generate complementary color"""
        return ColorPalette.adjust_hue(hex_color, 180)
    
    @staticmethod
    def generate_triadic(hex_color: str) -> List[str]:
        """Generate triadic color scheme"""
        return [
            hex_color,
            ColorPalette.adjust_hue(hex_color, 120),
            ColorPalette.adjust_hue(hex_color, 240)
        ]
    
    @staticmethod
    def generate_analogous(hex_color: str, angle: float = 30) -> List[str]:
        """Generate analogous color scheme"""
        return [
            ColorPalette.adjust_hue(hex_color, -angle),
            hex_color,
            ColorPalette.adjust_hue(hex_color, angle)
        ]
    
    @staticmethod
    def get_contrast_ratio(color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        def get_luminance(hex_color: str) -> float:
            r, g, b = ColorPalette.hex_to_rgb(hex_color)
            r, g, b = r / 255.0, g / 255.0, b / 255.0
            
            # sRGB to linear RGB
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = get_luminance(color1)
        l2 = get_luminance(color2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def meets_wcag_aa(color1: str, color2: str, large_text: bool = False) -> bool:
        """Check if color combination meets WCAG AA standards"""
        ratio = ColorPalette.get_contrast_ratio(color1, color2)
        threshold = 3.0 if large_text else 4.5
        return ratio >= threshold
    
    @staticmethod
    def meets_wcag_aaa(color1: str, color2: str, large_text: bool = False) -> bool:
        """Check if color combination meets WCAG AAA standards"""
        ratio = ColorPalette.get_contrast_ratio(color1, color2)
        threshold = 4.5 if large_text else 7.0
        return ratio >= threshold


class DesignSystemManager:
    """Manages design tokens and generates design system documentation"""
    
    def __init__(self):
        self.tokens: Dict[str, DesignToken] = {}
        self.color_tokens: Dict[str, ColorToken] = {}
        self.typography_scale = TypographyScale()
        self.spacing_scale = SpacingScale()
        self.shadows: Dict[str, ShadowToken] = {}
        
        # Initialize default tokens
        self._init_default_tokens()
    
    def _init_default_tokens(self):
        """Initialize default design tokens"""
        # Default colors
        self.add_color_token(ColorToken(
            name='primary',
            base='#3b82f6',
            variants={
                'light': '#60a5fa',
                'lighter': '#93c5fd',
                'dark': '#2563eb',
                'darker': '#1d4ed8'
            },
            description='Primary brand color'
        ))
        
        self.add_color_token(ColorToken(
            name='secondary',
            base='#8b5cf6',
            variants={
                'light': '#a78bfa',
                'lighter': '#c4b5fd',
                'dark': '#7c3aed',
                'darker': '#6d28d9'
            },
            description='Secondary brand color'
        ))
        
        # Default shadows
        self.add_shadow('sm', ShadowToken('sm', 0, 1, 2, 0, '#000000', 0.05))
        self.add_shadow('md', ShadowToken('md', 0, 4, 6, -1, '#000000', 0.1))
        self.add_shadow('lg', ShadowToken('lg', 0, 10, 15, -3, '#000000', 0.1))
        self.add_shadow('xl', ShadowToken('xl', 0, 20, 25, -5, '#000000', 0.1))
        
        # Default border radii
        self.add_token(DesignToken('border-radius-sm', '4px', TokenType.RADIUS))
        self.add_token(DesignToken('border-radius-md', '8px', TokenType.RADIUS))
        self.add_token(DesignToken('border-radius-lg', '12px', TokenType.RADIUS))
        self.add_token(DesignToken('border-radius-full', '9999px', TokenType.RADIUS))
        
        # Default durations
        self.add_token(DesignToken('duration-fast', '150ms', TokenType.DURATION))
        self.add_token(DesignToken('duration-normal', '300ms', TokenType.DURATION))
        self.add_token(DesignToken('duration-slow', '500ms', TokenType.DURATION))
        
        # Z-index scale
        self.add_token(DesignToken('z-dropdown', 1000, TokenType.Z_INDEX))
        self.add_token(DesignToken('z-modal', 2000, TokenType.Z_INDEX))
        self.add_token(DesignToken('z-tooltip', 3000, TokenType.Z_INDEX))
        self.add_token(DesignToken('z-notification', 4000, TokenType.Z_INDEX))
    
    def add_token(self, token: DesignToken):
        """Add design token"""
        self.tokens[token.name] = token
    
    def add_color_token(self, color_token: ColorToken):
        """Add color token"""
        self.color_tokens[color_token.name] = color_token
    
    def add_shadow(self, name: str, shadow: ShadowToken):
        """Add shadow token"""
        self.shadows[name] = shadow
    
    def get_token(self, name: str) -> Optional[DesignToken]:
        """Get design token by name or alias"""
        # Check direct name
        if name in self.tokens:
            return self.tokens[name]
        
        # Check aliases
        for token in self.tokens.values():
            if name in token.aliases:
                return token
        
        return None
    
    def get_color(self, name: str, variant: Optional[str] = None) -> Optional[str]:
        """Get color value"""
        if name in self.color_tokens:
            color = self.color_tokens[name]
            return color.get_variant(variant) if variant else color.base
        return None
    
    def generate_color_palette(self, name: str, base_color: str, steps: int = 10):
        """Generate and add color palette"""
        palette = ColorPalette.generate_palette(base_color, steps)
        
        variants = {}
        for key, color in palette.items():
            if key != '500':
                variants[key] = color
        
        self.add_color_token(ColorToken(
            name=name,
            base=base_color,
            variants=variants,
            description=f'Generated palette for {name}'
        ))
    
    def generate_typography_tokens(self) -> Dict[str, Any]:
        """Generate typography tokens"""
        scale = self.typography_scale.generate_scale([
            'xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl'
        ])
        
        tokens = {}
        for name, value in scale.items():
            tokens[f'typography-{name}'] = value
        
        # Add font weights
        for name, weight in self.typography_scale.font_weights.items():
            tokens[f'font-weight-{name}'] = weight
        
        return tokens
    
    def generate_spacing_tokens(self) -> Dict[str, str]:
        """Generate spacing tokens"""
        scale = self.spacing_scale.generate_scale()
        
        tokens = {}
        for name, value in scale.items():
            tokens[f'spacing-{name}'] = value
        
        return tokens
    
    def validate_accessibility(self, foreground: str, background: str) -> Dict:
        """Validate color contrast for accessibility"""
        ratio = ColorPalette.get_contrast_ratio(foreground, background)
        
        return {
            'ratio': round(ratio, 2),
            'wcag_aa_normal': ColorPalette.meets_wcag_aa(foreground, background, False),
            'wcag_aa_large': ColorPalette.meets_wcag_aa(foreground, background, True),
            'wcag_aaa_normal': ColorPalette.meets_wcag_aaa(foreground, background, False),
            'wcag_aaa_large': ColorPalette.meets_wcag_aaa(foreground, background, True)
        }
    
    def export_tokens(self, filepath: Path, format: str = 'json'):
        """Export tokens to file"""
        data = {
            'tokens': {name: token.to_dict() for name, token in self.tokens.items()},
            'colors': {name: color.to_dict() for name, color in self.color_tokens.items()},
            'shadows': {name: shadow.to_dict() for name, shadow in self.shadows.items()},
            'typography': self.generate_typography_tokens(),
            'spacing': self.generate_spacing_tokens()
        }
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == 'css':
            self._export_css(filepath, data)
        elif format == 'scss':
            self._export_scss(filepath, data)
    
    def _export_css(self, filepath: Path, data: Dict):
        """Export as CSS custom properties"""
        lines = [':root {']
        
        # Colors
        for name, color in data['colors'].items():
            lines.append(f'  --color-{name}: {color["base"]};')
            for variant, value in color.get('variants', {}).items():
                lines.append(f'  --color-{name}-{variant}: {value};')
        
        # Shadows
        for name, shadow in data['shadows'].items():
            lines.append(f'  --shadow-{name}: {shadow["value"]};')
        
        # Typography
        for name, value in data['typography'].items():
            if isinstance(value, dict):
                lines.append(f'  --{name}-size: {value.get("fontSize", "")};')
                lines.append(f'  --{name}-line-height: {value.get("lineHeight", "")};')
            else:
                lines.append(f'  --{name}: {value};')
        
        # Spacing
        for name, value in data['spacing'].items():
            lines.append(f'  --{name}: {value};')
        
        # Other tokens
        for name, token in data['tokens'].items():
            lines.append(f'  --{name}: {token["value"]};')
        
        lines.append('}')
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
    
    def _export_scss(self, filepath: Path, data: Dict):
        """Export as SCSS variables"""
        lines = []
        
        # Colors
        for name, color in data['colors'].items():
            lines.append(f'$color-{name}: {color["base"]};')
            for variant, value in color.get('variants', {}).items():
                lines.append(f'$color-{name}-{variant}: {value};')
        
        lines.append('')
        
        # Shadows
        for name, shadow in data['shadows'].items():
            lines.append(f'$shadow-{name}: {shadow["value"]};')
        
        lines.append('')
        
        # Typography
        for name, value in data['typography'].items():
            if isinstance(value, dict):
                lines.append(f'${name}-size: {value.get("fontSize", "")};')
                lines.append(f'${name}-line-height: {value.get("lineHeight", "")};')
            else:
                lines.append(f'${name}: {value};')
        
        lines.append('')
        
        # Spacing
        for name, value in data['spacing'].items():
            lines.append(f'${name}: {value};')
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
    
    def generate_documentation(self, output_dir: Path):
        """Generate design system documentation"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate index
        self._generate_index_page(output_dir / 'index.md')
        
        # Generate color documentation
        self._generate_color_docs(output_dir / 'colors.md')
        
        # Generate typography documentation
        self._generate_typography_docs(output_dir / 'typography.md')
        
        # Generate spacing documentation
        self._generate_spacing_docs(output_dir / 'spacing.md')
        
        # Generate shadow documentation
        self._generate_shadow_docs(output_dir / 'shadows.md')
    
    def _generate_index_page(self, filepath: Path):
        """Generate index documentation page"""
        content = f"""# Design System Documentation

## Overview

This design system provides a comprehensive set of design tokens for consistent UI development.

## Components

- [Colors](colors.md) - Color palettes and accessibility guidelines
- [Typography](typography.md) - Type scales and font settings
- [Spacing](spacing.md) - Spacing scale and layout utilities
- [Shadows](shadows.md) - Shadow tokens for depth and elevation

## Token Statistics

- **Colors**: {len(self.color_tokens)} palettes
- **Typography**: {len(self.generate_typography_tokens())} tokens
- **Spacing**: {len(self.generate_spacing_tokens())} tokens
- **Shadows**: {len(self.shadows)} variants
- **Other Tokens**: {len(self.tokens)} tokens

## Usage

### CSS

```css
.button {{
  background-color: var(--color-primary);
  padding: var(--spacing-4);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
}}
```

### SCSS

```scss
.button {{
  background-color: $color-primary;
  padding: $spacing-4;
  border-radius: $border-radius-md;
  box-shadow: $shadow-md;
}}
```

---

Generated by PLHub Design System Manager
"""
        
        with open(filepath, 'w') as f:
            f.write(content)
    
    def _generate_color_docs(self, filepath: Path):
        """Generate color documentation"""
        lines = ['# Color Tokens\n']
        
        for name, color in self.color_tokens.items():
            lines.append(f'## {name.capitalize()}\n')
            lines.append(f'**Description**: {color.description}\n')
            lines.append(f'**Base**: `{color.base}`\n')
            
            if color.variants:
                lines.append('\n**Variants**:\n')
                for variant, value in color.variants.items():
                    lines.append(f'- `{variant}`: `{value}`')
            
            lines.append('\n')
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
    
    def _generate_typography_docs(self, filepath: Path):
        """Generate typography documentation"""
        tokens = self.generate_typography_tokens()
        
        lines = ['# Typography Tokens\n']
        lines.append(f'**Base Size**: {self.typography_scale.base_size}px\n')
        lines.append(f'**Scale Ratio**: {self.typography_scale.scale_ratio}\n')
        lines.append(f'**Font Family**: {self.typography_scale.font_family}\n\n')
        
        lines.append('## Type Scale\n')
        for name, value in tokens.items():
            if 'typography' in name and isinstance(value, dict):
                lines.append(f'### {name}\n')
                lines.append(f'- Font Size: `{value.get("fontSize")}`')
                lines.append(f'- Line Height: `{value.get("lineHeight")}`\n')
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
    
    def _generate_spacing_docs(self, filepath: Path):
        """Generate spacing documentation"""
        tokens = self.generate_spacing_tokens()
        
        lines = ['# Spacing Tokens\n']
        lines.append(f'**Base Unit**: {self.spacing_scale.base_unit}px\n\n')
        
        lines.append('## Spacing Scale\n')
        for name, value in tokens.items():
            lines.append(f'- `{name}`: `{value}`')
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
    
    def _generate_shadow_docs(self, filepath: Path):
        """Generate shadow documentation"""
        lines = ['# Shadow Tokens\n']
        
        for name, shadow in self.shadows.items():
            lines.append(f'## {name}\n')
            lines.append(f'**CSS**: `{shadow.to_css()}`\n')
            lines.append(f'- X Offset: {shadow.x_offset}px')
            lines.append(f'- Y Offset: {shadow.y_offset}px')
            lines.append(f'- Blur: {shadow.blur}px')
            lines.append(f'- Spread: {shadow.spread}px')
            lines.append(f'- Color: {shadow.color}')
            lines.append(f'- Opacity: {shadow.opacity}\n')
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))


# Example usage
if __name__ == '__main__':
    manager = DesignSystemManager()
    
    # Generate custom color palette
    manager.generate_color_palette('brand', '#6366f1', steps=10)
    
    # Check accessibility
    result = manager.validate_accessibility('#000000', '#ffffff')
    print(f"Contrast ratio: {result['ratio']}")
    print(f"WCAG AA: {result['wcag_aa_normal']}")
    
    # Export tokens
    manager.export_tokens(Path('design-tokens.json'))
    manager.export_tokens(Path('design-tokens.css'), format='css')
    
    # Generate documentation
    manager.generate_documentation(Path('design-system-docs'))
