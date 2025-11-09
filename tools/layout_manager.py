"""
PLHub Layout System Manager
Provides responsive layout engine with breakpoints, grid system, flexbox utilities,
and advanced positioning capabilities for building sophisticated UI layouts.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


@dataclass
class Breakpoint:
    """Represents a responsive breakpoint"""
    name: str
    min_width: int
    max_width: Optional[int] = None
    columns: int = 12
    gutter: int = 16
    margin: int = 16


@dataclass
class GridConfig:
    """Grid system configuration"""
    columns: int = 12
    gutter: int = 16
    container_max_width: Dict[str, int] = None
    
    def __post_init__(self):
        if self.container_max_width is None:
            self.container_max_width = {
                'mobile': 540,
                'tablet': 720,
                'desktop': 960,
                'wide': 1140
            }


@dataclass
class LayoutConfig:
    """Complete layout configuration"""
    breakpoints: List[Breakpoint]
    grid: GridConfig
    spacing_scale: Dict[str, int]
    z_index_scale: Dict[str, int]


class LayoutManager:
    """Manages layout systems and responsive design utilities"""
    
    DEFAULT_BREAKPOINTS = [
        Breakpoint('mobile', 0, 767, columns=12, gutter=12, margin=16),
        Breakpoint('tablet', 768, 1023, columns=12, gutter=16, margin=24),
        Breakpoint('desktop', 1024, 1439, columns=12, gutter=20, margin=32),
        Breakpoint('wide', 1440, None, columns=12, gutter=24, margin=48),
    ]
    
    DEFAULT_SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
        '3xl': 64,
        '4xl': 96,
        '5xl': 128
    }
    
    DEFAULT_Z_INDEX = {
        'base': 0,
        'dropdown': 1000,
        'sticky': 1020,
        'fixed': 1030,
        'modal_backdrop': 1040,
        'modal': 1050,
        'popover': 1060,
        'tooltip': 1070,
        'notification': 1080
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize layout manager with optional custom config"""
        if config_path and config_path.exists():
            self.config = self._load_config(config_path)
        else:
            self.config = LayoutConfig(
                breakpoints=self.DEFAULT_BREAKPOINTS,
                grid=GridConfig(),
                spacing_scale=self.DEFAULT_SPACING,
                z_index_scale=self.DEFAULT_Z_INDEX
            )
    
    def _load_config(self, path: Path) -> LayoutConfig:
        """Load layout configuration from JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        breakpoints = [
            Breakpoint(**bp) for bp in data.get('breakpoints', [])
        ]
        
        grid_data = data.get('grid', {})
        grid = GridConfig(
            columns=grid_data.get('columns', 12),
            gutter=grid_data.get('gutter', 16),
            container_max_width=grid_data.get('container_max_width')
        )
        
        return LayoutConfig(
            breakpoints=breakpoints,
            grid=grid,
            spacing_scale=data.get('spacing_scale', self.DEFAULT_SPACING),
            z_index_scale=data.get('z_index_scale', self.DEFAULT_Z_INDEX)
        )
    
    def save_config(self, path: Path) -> None:
        """Save layout configuration to JSON file"""
        data = {
            'breakpoints': [
                {
                    'name': bp.name,
                    'min_width': bp.min_width,
                    'max_width': bp.max_width,
                    'columns': bp.columns,
                    'gutter': bp.gutter,
                    'margin': bp.margin
                }
                for bp in self.config.breakpoints
            ],
            'grid': {
                'columns': self.config.grid.columns,
                'gutter': self.config.grid.gutter,
                'container_max_width': self.config.grid.container_max_width
            },
            'spacing_scale': self.config.spacing_scale,
            'z_index_scale': self.config.z_index_scale
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_breakpoint(self, name: str) -> Optional[Breakpoint]:
        """Get breakpoint configuration by name"""
        for bp in self.config.breakpoints:
            if bp.name == name:
                return bp
        return None
    
    def calculate_column_width(self, columns: int, breakpoint: str = 'desktop') -> float:
        """Calculate column width percentage for grid system"""
        bp = self.get_breakpoint(breakpoint)
        if not bp:
            return 0.0
        
        return (columns / bp.columns) * 100.0
    
    def generate_grid_classes(self) -> Dict[str, str]:
        """Generate CSS-like grid classes for all breakpoints"""
        classes = {}
        
        for bp in self.config.breakpoints:
            for col in range(1, bp.columns + 1):
                class_name = f"col-{bp.name}-{col}"
                width = self.calculate_column_width(col, bp.name)
                classes[class_name] = f"width: {width:.2f}%"
        
        return classes
    
    def generate_spacing_utilities(self) -> Dict[str, str]:
        """Generate spacing utility classes"""
        utilities = {}
        
        for name, value in self.config.spacing_scale.items():
            # Margin utilities
            utilities[f"m-{name}"] = f"margin: {value}px"
            utilities[f"mt-{name}"] = f"margin-top: {value}px"
            utilities[f"mr-{name}"] = f"margin-right: {value}px"
            utilities[f"mb-{name}"] = f"margin-bottom: {value}px"
            utilities[f"ml-{name}"] = f"margin-left: {value}px"
            utilities[f"mx-{name}"] = f"margin-left: {value}px; margin-right: {value}px"
            utilities[f"my-{name}"] = f"margin-top: {value}px; margin-bottom: {value}px"
            
            # Padding utilities
            utilities[f"p-{name}"] = f"padding: {value}px"
            utilities[f"pt-{name}"] = f"padding-top: {value}px"
            utilities[f"pr-{name}"] = f"padding-right: {value}px"
            utilities[f"pb-{name}"] = f"padding-bottom: {value}px"
            utilities[f"pl-{name}"] = f"padding-left: {value}px"
            utilities[f"px-{name}"] = f"padding-left: {value}px; padding-right: {value}px"
            utilities[f"py-{name}"] = f"padding-top: {value}px; padding-bottom: {value}px"
            
            # Gap utilities (for flex/grid)
            utilities[f"gap-{name}"] = f"gap: {value}px"
        
        return utilities
    
    def generate_z_index_utilities(self) -> Dict[str, str]:
        """Generate z-index utility classes"""
        utilities = {}
        
        for name, value in self.config.z_index_scale.items():
            utilities[f"z-{name}"] = f"z-index: {value}"
        
        return utilities
    
    def export_layout_tokens(self, output_path: Path) -> None:
        """Export layout tokens as JSON for use in stylesheets"""
        tokens = {
            'breakpoints': {
                bp.name: {
                    'minWidth': f"{bp.min_width}px",
                    'maxWidth': f"{bp.max_width}px" if bp.max_width else None,
                    'columns': bp.columns,
                    'gutter': f"{bp.gutter}px",
                    'margin': f"{bp.margin}px"
                }
                for bp in self.config.breakpoints
            },
            'grid': {
                'columns': self.config.grid.columns,
                'gutter': f"{self.config.grid.gutter}px",
                'containerMaxWidth': {
                    k: f"{v}px" for k, v in self.config.grid.container_max_width.items()
                }
            },
            'spacing': {
                k: f"{v}px" for k, v in self.config.spacing_scale.items()
            },
            'zIndex': self.config.z_index_scale
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, indent=2)
    
    def generate_responsive_template(self, project_root: Path) -> None:
        """Generate a responsive layout template file"""
        template = '''Start Program

# Responsive Layout Template
# Demonstrates responsive design with breakpoints and grid system

# Layout Configuration
Set layout_name to "Responsive Dashboard"
Set container_width to "1200px"
Set breakpoint to "desktop"

# Grid System (12-column)
Set grid_columns to 12
Set grid_gutter to "16px"

# Header Section (Full Width)
Write "╔════════════════════════════════════════════════════════════════╗"
Write "║                      RESPONSIVE LAYOUT                         ║"
Write "║                    Desktop (1024px+)                           ║"
Write "╚════════════════════════════════════════════════════════════════╝"
Write ""

# Three Column Layout (4-4-4 grid)
Write "┌──────────────────┬──────────────────┬──────────────────┐"
Write "│   Column 1       │   Column 2       │   Column 3       │"
Write "│   (col-4)        │   (col-4)        │   (col-4)        │"
Write "│                  │                  │                  │"
Write "│   Content Area   │   Content Area   │   Content Area   │"
Write "│                  │                  │                  │"
Write "└──────────────────┴──────────────────┴──────────────────┘"
Write ""

# Tablet Layout (768-1023px)
Write "Tablet (768px - 1023px):"
Write "┌──────────────────────────────┬──────────────────────────────┐"
Write "│   Column 1 (col-6)           │   Column 2 (col-6)           │"
Write "└──────────────────────────────┴──────────────────────────────┘"
Write "┌────────────────────────────────────────────────────────────────┐"
Write "│   Column 3 (col-12 - Full Width)                              │"
Write "└────────────────────────────────────────────────────────────────┘"
Write ""

# Mobile Layout (<768px)
Write "Mobile (<768px):"
Write "┌────────────────────────────────────────────────────────────────┐"
Write "│   Column 1 (col-12 - Full Width)                              │"
Write "└────────────────────────────────────────────────────────────────┘"
Write "┌────────────────────────────────────────────────────────────────┐"
Write "│   Column 2 (col-12 - Full Width)                              │"
Write "└────────────────────────────────────────────────────────────────┘"
Write "┌────────────────────────────────────────────────────────────────┐"
Write "│   Column 3 (col-12 - Full Width)                              │"
Write "└────────────────────────────────────────────────────────────────┘"
Write ""

# Breakpoint Information
Write "📐 Breakpoints:"
Write "  • Mobile: 0-767px (12 columns)"
Write "  • Tablet: 768-1023px (12 columns)"
Write "  • Desktop: 1024-1439px (12 columns)"
Write "  • Wide: 1440px+ (12 columns)"
Write ""

# Spacing Scale
Write "📏 Spacing Scale:"
Write "  • xs: 4px   • sm: 8px   • md: 16px"
Write "  • lg: 24px  • xl: 32px  • xxl: 48px"

End Program
'''
        
        template_path = project_root / "ui" / "layouts" / "responsive_template.poh"
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(template, encoding='utf-8')


def bootstrap_layout_system(project_root: Path) -> Dict[str, any]:
    """Bootstrap layout system in a project"""
    layout_dir = project_root / "ui" / "layouts"
    layout_dir.mkdir(parents=True, exist_ok=True)
    
    manager = LayoutManager()
    
    # Save layout configuration
    config_path = layout_dir / "layout_config.json"
    manager.save_config(config_path)
    
    # Export layout tokens
    tokens_path = layout_dir / "layout_tokens.json"
    manager.export_layout_tokens(tokens_path)
    
    # Generate responsive template
    manager.generate_responsive_template(project_root)
    
    # Create README
    readme_path = layout_dir / "README.md"
    readme_content = '''# Layout System

## Overview
This directory contains the responsive layout system configuration and utilities.

## Files
- `layout_config.json` - Layout configuration (breakpoints, grid, spacing)
- `layout_tokens.json` - Design tokens for stylesheets
- `responsive_template.poh` - Example responsive layout

## Grid System
- 12-column responsive grid
- Configurable gutters and margins per breakpoint
- Fluid container with max-widths

## Breakpoints
- **Mobile**: 0-767px
- **Tablet**: 768-1023px
- **Desktop**: 1024-1439px
- **Wide**: 1440px+

## Spacing Scale
- xs: 4px, sm: 8px, md: 16px
- lg: 24px, xl: 32px, xxl: 48px
- 3xl: 64px, 4xl: 96px, 5xl: 128px

## Z-Index Scale
- base: 0, dropdown: 1000, sticky: 1020
- modal: 1050, tooltip: 1070, notification: 1080

## Usage
Use layout tokens in your stylesheets and reference grid classes
in your PohLang UI components for responsive layouts.
'''
    readme_path.write_text(readme_content, encoding='utf-8')
    
    return {
        'layout_dir': str(layout_dir),
        'config_path': str(config_path),
        'tokens_path': str(tokens_path),
        'template_path': str(layout_dir / "responsive_template.poh")
    }
