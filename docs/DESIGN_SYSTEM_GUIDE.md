# PLHub Design System Guide

## Overview

PLHub's Design System Manager provides a comprehensive token-based design system with color palettes, typography scales, spacing systems, shadows, and automatic documentation generation.

**Key Features**:
- ✅ Design token management
- ✅ Color palette generation
- ✅ Typography scales
- ✅ Spacing systems
- ✅ Shadow definitions
- ✅ WCAG accessibility validation
- ✅ CSS/SCSS export
- ✅ Documentation generator

---

## Quick Start

### Basic Usage

```python
from tools.design_system_manager import DesignSystemManager
from pathlib import Path

# Create manager
manager = DesignSystemManager()

# Generate color palette
manager.generate_color_palette('brand', '#6366f1', steps=10)

# Export tokens
manager.export_tokens(Path('tokens.json'))
manager.export_tokens(Path('tokens.css'), format='css')

# Generate documentation
manager.generate_documentation(Path('docs/design-system'))
```

### With PohLang

```poh
Start Program

# Import design system
Import "plhub/design_system"

# Create design system
Create design_system with:
  - name: "my_app_design"
  - base_color: "#6366f1"

# Generate tokens
Generate design_tokens for "my_app_design"

# Export to CSS
Export design_tokens to "styles/tokens.css"

End Program
```

---

## Color System

### Color Tokens

```python
from tools.design_system_manager import ColorToken

# Create color token
primary = ColorToken(
    name='primary',
    base='#3b82f6',
    variants={
        'light': '#60a5fa',
        'lighter': '#93c5fd',
        'dark': '#2563eb',
        'darker': '#1d4ed8'
    },
    description='Primary brand color'
)

manager.add_color_token(primary)

# Get color values
base_color = manager.get_color('primary')         # '#3b82f6'
light_color = manager.get_color('primary', 'light')  # '#60a5fa'
```

### Generating Color Palettes

```python
from tools.design_system_manager import ColorPalette

# Generate 10-step palette
palette = ColorPalette.generate_palette('#3b82f6', steps=10)

# Result:
# {
#   '0': '#f0f9ff',    # Lightest
#   '100': '#e0f2fe',
#   '200': '#bae6fd',
#   '300': '#7dd3fc',
#   '400': '#38bdf8',
#   '500': '#3b82f6',  # Base
#   '600': '#2563eb',
#   '700': '#1d4ed8',
#   '800': '#1e40af',
#   '900': '#1e3a8a'   # Darkest
# }
```

### Color Manipulation

```python
base = '#3b82f6'

# Lighten/Darken
lighter = ColorPalette.lighten(base, 20)  # 20% lighter
darker = ColorPalette.darken(base, 20)    # 20% darker

# Saturate/Desaturate
saturated = ColorPalette.saturate(base, 15)    # More vibrant
desaturated = ColorPalette.desaturate(base, 15)  # More gray

# Adjust hue
rotated = ColorPalette.adjust_hue(base, 30)  # Rotate 30 degrees
```

### Color Harmonies

```python
base = '#3b82f6'

# Complementary (opposite on color wheel)
complement = ColorPalette.generate_complementary(base)

# Triadic (3 evenly spaced colors)
triadic = ColorPalette.generate_triadic(base)
# ['#3b82f6', '#f63b82', '#82f63b']

# Analogous (adjacent colors)
analogous = ColorPalette.generate_analogous(base, angle=30)
# ['#3b5cf6', '#3b82f6', '#3ba8f6']
```

### Color Format Conversion

```python
# Hex to RGB
r, g, b = ColorPalette.hex_to_rgb('#3b82f6')
# (59, 130, 246)

# RGB to Hex
hex_color = ColorPalette.rgb_to_hex(59, 130, 246)
# '#3b82f6'

# Hex to HSL
h, s, l = ColorPalette.hex_to_hsl('#3b82f6')
# (217.2, 91.2, 59.8)

# HSL to Hex
hex_color = ColorPalette.hsl_to_hex(217.2, 91.2, 59.8)
# '#3b82f6'
```

---

## Accessibility

### WCAG Contrast Checking

```python
# Check contrast ratio
ratio = ColorPalette.get_contrast_ratio('#000000', '#ffffff')
# 21.0

# Check WCAG AA compliance (4.5:1 normal, 3:1 large)
meets_aa = ColorPalette.meets_wcag_aa(
    foreground='#3b82f6',
    background='#ffffff',
    large_text=False
)

# Check WCAG AAA compliance (7:1 normal, 4.5:1 large)
meets_aaa = ColorPalette.meets_wcag_aaa(
    foreground='#1d4ed8',
    background='#ffffff',
    large_text=False
)
```

### Validation Report

```python
result = manager.validate_accessibility('#000000', '#ffffff')

# {
#   'ratio': 21.0,
#   'wcag_aa_normal': True,    # 4.5:1 required
#   'wcag_aa_large': True,     # 3:1 required
#   'wcag_aaa_normal': True,   # 7:1 required
#   'wcag_aaa_large': True     # 4.5:1 required
# }
```

### Contrast Requirements

| Level | Normal Text | Large Text |
|-------|-------------|------------|
| **WCAG AA** | 4.5:1 | 3:1 |
| **WCAG AAA** | 7:1 | 4.5:1 |

**Large Text**: 18pt+ or 14pt+ bold

---

## Typography System

### Typography Scale

```python
from tools.design_system_manager import TypographyScale

# Create typography scale
typography = TypographyScale(
    base_size=16,           # Base font size in pixels
    scale_ratio=1.25,       # Major third (1.25)
    line_height_ratio=1.5,  # 1.5x line height
    font_family='Inter, sans-serif'
)

# Generate scale
scale = typography.generate_scale([
    'xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl'
])

# Result:
# {
#   'xs': {'fontSize': '10px', 'lineHeight': '15px'},
#   'sm': {'fontSize': '13px', 'lineHeight': '20px'},
#   'base': {'fontSize': '16px', 'lineHeight': '24px'},
#   'lg': {'fontSize': '20px', 'lineHeight': '30px'},
#   'xl': {'fontSize': '25px', 'lineHeight': '38px'},
#   '2xl': {'fontSize': '31px', 'lineHeight': '47px'},
#   '3xl': {'fontSize': '39px', 'lineHeight': '59px'},
#   '4xl': {'fontSize': '49px', 'lineHeight': '74px'},
#   '5xl': {'fontSize': '61px', 'lineHeight': '92px'}
# }
```

### Font Weights

```python
# Default font weights
font_weights = {
    'light': 300,
    'regular': 400,
    'medium': 500,
    'semibold': 600,
    'bold': 700
}

# Access weights
typography.font_weights['semibold']  # 600
```

### Scale Ratios

Common typographic scale ratios:

| Ratio | Name | Multiplier |
|-------|------|------------|
| 1.125 | Major Second | 8:9 |
| 1.200 | Minor Third | 5:6 |
| 1.250 | Major Third | 4:5 |
| 1.333 | Perfect Fourth | 3:4 |
| 1.414 | Augmented Fourth | 1:√2 |
| 1.500 | Perfect Fifth | 2:3 |
| 1.618 | Golden Ratio | 1:φ |
| 2.000 | Double Octave | 1:2 |

```python
# Use different ratios
minor_third = TypographyScale(scale_ratio=1.200)
perfect_fourth = TypographyScale(scale_ratio=1.333)
golden_ratio = TypographyScale(scale_ratio=1.618)
```

---

## Spacing System

### Spacing Scale

```python
from tools.design_system_manager import SpacingScale

# Create spacing scale
spacing = SpacingScale(
    base_unit=4,  # 4px base unit
    scale_values=[0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64]
)

# Generate scale
scale = spacing.generate_scale()

# Result:
# {
#   '0': '0px',
#   '1': '4px',
#   '2': '8px',
#   '3': '12px',
#   '4': '16px',
#   '6': '24px',
#   '8': '32px',
#   '12': '48px',
#   '16': '64px',
#   '24': '96px',
#   '32': '128px',
#   '48': '192px',
#   '64': '256px'
# }
```

### Spacing Usage

```css
/* Padding */
.container {
  padding: var(--spacing-4);  /* 16px */
}

/* Margin */
.section {
  margin-bottom: var(--spacing-8);  /* 32px */
}

/* Gap */
.grid {
  gap: var(--spacing-6);  /* 24px */
}
```

### Common Spacing Patterns

| Use Case | Recommended |
|----------|-------------|
| Tight spacing | `spacing-1` (4px) |
| Small gap | `spacing-2` (8px) |
| Default gap | `spacing-4` (16px) |
| Section spacing | `spacing-8` (32px) |
| Large spacing | `spacing-16` (64px) |

---

## Shadow System

### Shadow Tokens

```python
from tools.design_system_manager import ShadowToken

# Create shadow
shadow = ShadowToken(
    name='md',
    x_offset=0,
    y_offset=4,
    blur=6,
    spread=-1,
    color='#000000',
    opacity=0.1
)

manager.add_shadow('md', shadow)

# Convert to CSS
css = shadow.to_css()
# '0px 4px 6px -1px rgba(0, 0, 0, 0.1)'
```

### Default Shadows

```python
# Small shadow
sm = ShadowToken('sm', 0, 1, 2, 0, '#000000', 0.05)

# Medium shadow
md = ShadowToken('md', 0, 4, 6, -1, '#000000', 0.1)

# Large shadow
lg = ShadowToken('lg', 0, 10, 15, -3, '#000000', 0.1)

# Extra large shadow
xl = ShadowToken('xl', 0, 20, 25, -5, '#000000', 0.1)
```

### Shadow Usage

```css
.card {
  box-shadow: var(--shadow-md);
}

.modal {
  box-shadow: var(--shadow-xl);
}

.button:hover {
  box-shadow: var(--shadow-lg);
}
```

---

## Design Tokens

### Creating Tokens

```python
from tools.design_system_manager import DesignToken, TokenType

# Border radius token
radius = DesignToken(
    name='border-radius-lg',
    value='12px',
    type=TokenType.RADIUS,
    description='Large border radius',
    category='borders',
    aliases=['radius-lg']
)

manager.add_token(radius)

# Duration token
duration = DesignToken(
    name='duration-normal',
    value='300ms',
    type=TokenType.DURATION,
    description='Normal animation duration',
    category='animations'
)

manager.add_token(duration)
```

### Token Types

```python
class TokenType(Enum):
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
```

### Getting Tokens

```python
# Get by name
token = manager.get_token('border-radius-lg')

# Get by alias
token = manager.get_token('radius-lg')

# Get value
value = token.value  # '12px'
```

### Token Aliases

```python
# Create token with aliases
token = DesignToken(
    name='spacing-large',
    value='32px',
    type=TokenType.SPACING,
    aliases=['spacing-xl', 'space-8']
)

# All these work:
manager.get_token('spacing-large')
manager.get_token('spacing-xl')
manager.get_token('space-8')
```

### Deprecating Tokens

```python
# Deprecate old token
old_token = DesignToken(
    name='old-spacing',
    value='20px',
    type=TokenType.SPACING,
    deprecated=True,
    replacement='spacing-6'
)

manager.add_token(old_token)
```

---

## Exporting Tokens

### JSON Export

```python
from pathlib import Path

# Export all tokens to JSON
manager.export_tokens(Path('design-tokens.json'))
```

**Output**:
```json
{
  "tokens": {
    "border-radius-sm": {
      "name": "border-radius-sm",
      "value": "4px",
      "type": "radius",
      "description": "",
      "category": "default"
    }
  },
  "colors": {
    "primary": {
      "name": "primary",
      "base": "#3b82f6",
      "variants": {
        "light": "#60a5fa",
        "dark": "#2563eb"
      }
    }
  },
  "typography": { ... },
  "spacing": { ... },
  "shadows": { ... }
}
```

### CSS Export

```python
# Export as CSS custom properties
manager.export_tokens(Path('tokens.css'), format='css')
```

**Output**:
```css
:root {
  --color-primary: #3b82f6;
  --color-primary-light: #60a5fa;
  --color-primary-dark: #2563eb;
  
  --shadow-sm: 0px 1px 2px 0px rgba(0, 0, 0, 0.05);
  --shadow-md: 0px 4px 6px -1px rgba(0, 0, 0, 0.1);
  
  --typography-base-size: 16px;
  --typography-base-line-height: 24px;
  
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-4: 16px;
  
  --border-radius-md: 8px;
  --duration-normal: 300ms;
}
```

### SCSS Export

```python
# Export as SCSS variables
manager.export_tokens(Path('tokens.scss'), format='scss')
```

**Output**:
```scss
$color-primary: #3b82f6;
$color-primary-light: #60a5fa;
$color-primary-dark: #2563eb;

$shadow-sm: 0px 1px 2px 0px rgba(0, 0, 0, 0.05);
$shadow-md: 0px 4px 6px -1px rgba(0, 0, 0, 0.1);

$typography-base-size: 16px;
$typography-base-line-height: 24px;

$spacing-1: 4px;
$spacing-2: 8px;
$spacing-4: 16px;
```

---

## Documentation Generation

### Auto-Generate Docs

```python
from pathlib import Path

# Generate complete documentation
manager.generate_documentation(Path('docs/design-system'))
```

**Generated files**:
- `index.md` - Overview and statistics
- `colors.md` - Color palette documentation
- `typography.md` - Typography scale documentation
- `spacing.md` - Spacing system documentation
- `shadows.md` - Shadow token documentation

### Index Page

```markdown
# Design System Documentation

## Overview

This design system provides comprehensive design tokens.

## Components

- [Colors](colors.md)
- [Typography](typography.md)
- [Spacing](spacing.md)
- [Shadows](shadows.md)

## Token Statistics

- **Colors**: 12 palettes
- **Typography**: 25 tokens
- **Spacing**: 13 tokens
- **Shadows**: 4 variants
```

---

## Complete Example

### Building a Design System

```python
from tools.design_system_manager import (
    DesignSystemManager,
    ColorToken,
    TypographyScale,
    SpacingScale,
    ShadowToken
)
from pathlib import Path

# Create manager
manager = DesignSystemManager()

# 1. Add brand colors
manager.generate_color_palette('brand', '#6366f1', steps=10)
manager.generate_color_palette('success', '#10b981', steps=10)
manager.generate_color_palette('warning', '#f59e0b', steps=10)
manager.generate_color_palette('danger', '#ef4444', steps=10)

# 2. Configure typography
manager.typography_scale = TypographyScale(
    base_size=16,
    scale_ratio=1.25,
    font_family='Inter, system-ui, sans-serif',
    font_weights={
        'light': 300,
        'regular': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,
        'extrabold': 800
    }
)

# 3. Configure spacing
manager.spacing_scale = SpacingScale(
    base_unit=4,
    scale_values=[0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96]
)

# 4. Add custom shadows
manager.add_shadow('inner', ShadowToken(
    'inner', 0, 0, 4, 0, '#000000', 0.06
))
manager.add_shadow('outline', ShadowToken(
    'outline', 0, 0, 0, 3, '#6366f1', 0.5
))

# 5. Validate accessibility
brand_on_white = manager.validate_accessibility('#6366f1', '#ffffff')
if brand_on_white['wcag_aa_normal']:
    print("✅ Brand color meets WCAG AA on white")

# 6. Export tokens
manager.export_tokens(Path('tokens/design-tokens.json'))
manager.export_tokens(Path('styles/tokens.css'), format='css')
manager.export_tokens(Path('styles/_tokens.scss'), format='scss')

# 7. Generate documentation
manager.generate_documentation(Path('docs/design-system'))

print("✅ Design system created successfully!")
```

---

## PohLang Integration

### Complete Design System in PohLang

```poh
Start Program

# Create design system
Create design_system with:
  - name: "my_app"
  - base_color: "#6366f1"

# Configure typography
Set typography_scale with:
  - base_size: 16
  - scale_ratio: 1.25
  - font_family: "Inter, sans-serif"

# Configure spacing
Set spacing_scale with:
  - base_unit: 4

# Generate color palettes
Generate palette "brand" from "#6366f1" with 10 steps
Generate palette "success" from "#10b981" with 10 steps
Generate palette "danger" from "#ef4444" with 10 steps

# Validate accessibility
Check contrast between "#6366f1" and "#ffffff"
If contrast_ratio >= 4.5:
  Print "✅ Passes WCAG AA"

# Export tokens
Export tokens to "design-tokens.json"
Export tokens to "tokens.css" as css
Export tokens to "_tokens.scss" as scss

# Generate documentation
Generate documentation to "docs/design-system"

Print "Design system ready!"

End Program
```

---

## Best Practices

### Color System

1. **Use semantic naming**:
   ```python
   # Good
   'primary', 'success', 'warning', 'danger'
   
   # Avoid
   'blue', 'green', 'yellow', 'red'
   ```

2. **Generate palettes consistently**:
   ```python
   # Always use same step count
   manager.generate_color_palette('primary', '#3b82f6', steps=10)
   manager.generate_color_palette('success', '#10b981', steps=10)
   ```

3. **Check accessibility**:
   ```python
   # Always validate contrast
   result = manager.validate_accessibility(foreground, background)
   assert result['wcag_aa_normal'], "Fails accessibility"
   ```

### Typography

1. **Use consistent scale ratios**:
   ```python
   # Pick one ratio for entire system
   typography = TypographyScale(scale_ratio=1.25)  # Stick with it
   ```

2. **Define limited font weights**:
   ```python
   # Keep to 3-5 weights max
   font_weights = {
       'regular': 400,
       'medium': 500,
       'bold': 700
   }
   ```

### Spacing

1. **Use 4px or 8px base unit**:
   ```python
   # 4px for finer control
   spacing = SpacingScale(base_unit=4)
   
   # 8px for larger designs
   spacing = SpacingScale(base_unit=8)
   ```

2. **Limit scale steps**:
   ```python
   # Don't create too many options
   scale_values = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64]
   # 13 steps is good, 20+ is too many
   ```

---

## See Also

- [Style System](./STYLE_SYSTEM_GUIDE.md)
- [Component Library](./COMPONENT_LIBRARY_GUIDE.md)
- [Animation Framework](./ANIMATION_FRAMEWORK_GUIDE.md)

---

**PLHub Design System Manager** - Token-based design for consistent, accessible interfaces.
