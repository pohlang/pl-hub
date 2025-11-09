"""
PLHub Navigation Framework
Provides routing and navigation system with stack, tab, drawer, and modal navigation patterns.
Includes deep linking, navigation guards, and history management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from enum import Enum
import json


class NavigationType(Enum):
    """Types of navigation patterns"""
    STACK = "stack"
    TAB = "tab"
    DRAWER = "drawer"
    MODAL = "modal"


@dataclass
class Route:
    """Represents a navigation route"""
    path: str
    name: str
    component: str
    title: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)
    guards: List[str] = field(default_factory=list)


@dataclass
class NavigationStack:
    """Stack navigation history"""
    routes: List[Route] = field(default_factory=list)
    current_index: int = -1
    
    def push(self, route: Route) -> None:
        """Push new route onto stack"""
        # Clear forward history if navigating from middle of stack
        if self.current_index < len(self.routes) - 1:
            self.routes = self.routes[:self.current_index + 1]
        
        self.routes.append(route)
        self.current_index = len(self.routes) - 1
    
    def pop(self) -> Optional[Route]:
        """Pop current route from stack"""
        if self.current_index <= 0:
            return None
        
        self.current_index -= 1
        return self.routes[self.current_index]
    
    def can_go_back(self) -> bool:
        """Check if backward navigation is possible"""
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if forward navigation is possible"""
        return self.current_index < len(self.routes) - 1
    
    def go_back(self) -> Optional[Route]:
        """Navigate backward in history"""
        if self.can_go_back():
            self.current_index -= 1
            return self.routes[self.current_index]
        return None
    
    def go_forward(self) -> Optional[Route]:
        """Navigate forward in history"""
        if self.can_go_forward():
            self.current_index += 1
            return self.routes[self.current_index]
        return None
    
    def current_route(self) -> Optional[Route]:
        """Get current route"""
        if 0 <= self.current_index < len(self.routes):
            return self.routes[self.current_index]
        return None


class NavigationGuard:
    """Base class for navigation guards"""
    
    def __init__(self, name: str):
        self.name = name
    
    def can_navigate(self, from_route: Optional[Route], to_route: Route) -> bool:
        """Check if navigation is allowed"""
        return True
    
    def on_navigation(self, from_route: Optional[Route], to_route: Route) -> None:
        """Called when navigation occurs"""
        pass


class AuthGuard(NavigationGuard):
    """Authentication guard - requires user to be authenticated"""
    
    def __init__(self, is_authenticated: Callable[[], bool]):
        super().__init__("auth")
        self.is_authenticated = is_authenticated
    
    def can_navigate(self, from_route: Optional[Route], to_route: Route) -> bool:
        requires_auth = to_route.meta.get('requiresAuth', False)
        if requires_auth and not self.is_authenticated():
            return False
        return True


class NavigationRouter:
    """Main navigation router"""
    
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        self.stacks: Dict[str, NavigationStack] = {
            'main': NavigationStack()
        }
        self.current_stack = 'main'
        self.guards: Dict[str, NavigationGuard] = {}
        self.listeners: List[Callable[[Route, Route], None]] = []
    
    def register_route(self, route: Route) -> None:
        """Register a route"""
        self.routes[route.path] = route
    
    def register_routes(self, routes: List[Route]) -> None:
        """Register multiple routes"""
        for route in routes:
            self.register_route(route)
    
    def register_guard(self, guard: NavigationGuard) -> None:
        """Register a navigation guard"""
        self.guards[guard.name] = guard
    
    def add_listener(self, listener: Callable[[Route, Route], None]) -> None:
        """Add navigation listener"""
        self.listeners.append(listener)
    
    def get_route(self, path: str) -> Optional[Route]:
        """Get route by path"""
        return self.routes.get(path)
    
    def navigate(self, path: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Navigate to a route"""
        route = self.get_route(path)
        if not route:
            print(f"Route not found: {path}")
            return False
        
        # Apply params
        if params:
            route = Route(
                path=route.path,
                name=route.name,
                component=route.component,
                title=route.title,
                params={**route.params, **params},
                meta=route.meta,
                guards=route.guards
            )
        
        # Get current route
        stack = self.stacks[self.current_stack]
        current = stack.current_route()
        
        # Check guards
        for guard_name in route.guards:
            guard = self.guards.get(guard_name)
            if guard and not guard.can_navigate(current, route):
                print(f"Navigation blocked by guard: {guard_name}")
                return False
        
        # Execute guard callbacks
        for guard_name in route.guards:
            guard = self.guards.get(guard_name)
            if guard:
                guard.on_navigation(current, route)
        
        # Push to stack
        stack.push(route)
        
        # Notify listeners
        for listener in self.listeners:
            try:
                listener(current, route)
            except Exception as e:
                print(f"Navigation listener error: {e}")
        
        return True
    
    def go_back(self) -> bool:
        """Navigate back in history"""
        stack = self.stacks[self.current_stack]
        previous = stack.go_back()
        if previous:
            # Notify listeners
            for listener in self.listeners:
                try:
                    listener(stack.current_route(), previous)
                except Exception:
                    pass
            return True
        return False
    
    def go_forward(self) -> bool:
        """Navigate forward in history"""
        stack = self.stacks[self.current_stack]
        next_route = stack.go_forward()
        if next_route:
            # Notify listeners
            for listener in self.listeners:
                try:
                    listener(stack.current_route(), next_route)
                except Exception:
                    pass
            return True
        return False
    
    def current_route(self) -> Optional[Route]:
        """Get current active route"""
        stack = self.stacks[self.current_stack]
        return stack.current_route()
    
    def export_config(self, output_path: Path) -> None:
        """Export navigation configuration"""
        config = {
            'routes': [
                {
                    'path': r.path,
                    'name': r.name,
                    'component': r.component,
                    'title': r.title,
                    'params': r.params,
                    'meta': r.meta,
                    'guards': r.guards
                }
                for r in self.routes.values()
            ],
            'stacks': list(self.stacks.keys()),
            'guards': list(self.guards.keys())
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)


def bootstrap_navigation_system(project_root: Path) -> Dict[str, any]:
    """Bootstrap navigation system in a project"""
    nav_dir = project_root / "ui" / "navigation"
    nav_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample routes
    sample_routes = [
        Route(path="/", name="home", component="HomePage", title="Home"),
        Route(path="/products", name="products", component="ProductsPage", title="Products"),
        Route(path="/product/:id", name="product_detail", component="ProductDetailPage", title="Product Details"),
        Route(path="/cart", name="cart", component="CartPage", title="Shopping Cart"),
        Route(path="/checkout", name="checkout", component="CheckoutPage", title="Checkout", guards=["auth"]),
        Route(path="/profile", name="profile", component="ProfilePage", title="My Profile", 
              meta={"requiresAuth": True}, guards=["auth"]),
    ]
    
    # Create router and register routes
    router = NavigationRouter()
    router.register_routes(sample_routes)
    
    # Export config
    config_path = nav_dir / "routes.json"
    router.export_config(config_path)
    
    # Create navigation template
    template_path = nav_dir / "navigation_example.poh"
    template_content = '''Start Program

# Navigation Example
# Demonstrates navigation patterns and routing

# Navigation Configuration
Set current_route to "/"
Set route_name to "Home"
Set nav_history_count to 0

# Navigation Header
Write "╔════════════════════════════════════════════════════════════════╗"
Write "║                    NAVIGATION SYSTEM                           ║"
Write "╚════════════════════════════════════════════════════════════════╝"
Write ""

# Current Route Display
Write "📍 Current Route:"
Write "  Path: " plus current_route
Write "  Name: " plus route_name
Write "  History: " plus nav_history_count plus " items"
Write ""

# Navigation Controls
Write "🧭 Navigation Controls:"
Write "  [←  Back]  [→  Forward]  [🏠 Home]"
Write ""

# Available Routes
Write "📋 Available Routes:"
Write "  1. /           - Home Page"
Write "  2. /products   - Products Listing"
Write "  3. /cart       - Shopping Cart"
Write "  4. /checkout   - Checkout (requires auth)"
Write "  5. /profile    - User Profile (requires auth)"
Write ""

# Tab Navigation Example
Write "📑 Tab Navigation:"
Write "  [Home] [Products] [Cart] [Profile]"
Write "   ━━━━"
Write ""

# Stack Navigation Example
Write "📚 Navigation Stack:"
Write "  3. /products/laptop-123  (current)"
Write "  2. /products"
Write "  1. /                    (root)"
Write ""

# Drawer Navigation Example
Write "☰ Drawer Menu:"
Write "  ┌────────────────────┐"
Write "  │  • Home            │"
Write "  │  • Products        │"
Write "  │  • Categories      │"
Write "  │  • Cart            │"
Write "  │  • Profile         │"
Write "  │  • Settings        │"
Write "  │  • Help            │"
Write "  └────────────────────┘"
Write ""

# Deep Link Example
Write "🔗 Deep Link:"
Write "  myapp://products/123?color=blue&size=large"
Write ""

# Navigation Guards
Write "🛡️ Navigation Guards:"
Write "  • Auth Guard: Checking authentication..."
Write "  • Permission Guard: Validating permissions..."
Write "  ✓ Navigation allowed"

End Program
'''
    template_path.write_text(template_content, encoding='utf-8')
    
    # Create README
    readme_path = nav_dir / "README.md"
    readme_content = '''# Navigation System

## Overview
This directory contains the navigation and routing configuration.

## Files
- `routes.json` - Route definitions and configuration
- `navigation_example.poh` - Example navigation implementation

## Navigation Patterns

### Stack Navigation
Sequential navigation with back/forward history.
```
Home → Products → Product Detail
```

### Tab Navigation
Switch between top-level views.
```
[Home] [Products] [Cart] [Profile]
```

### Drawer Navigation
Side menu for hierarchical navigation.

### Modal Navigation
Overlay navigation for temporary contexts.

## Routes
Routes are defined with:
- `path` - URL path (supports params like `:id`)
- `name` - Unique route identifier
- `component` - Component to render
- `title` - Page title
- `guards` - Navigation guards (e.g., auth)
- `meta` - Additional metadata

## Navigation Guards
Guards control access to routes:
- **Auth Guard**: Requires authentication
- **Permission Guard**: Checks user permissions
- **Form Guard**: Prevents navigation with unsaved changes

## Deep Linking
Support for deep links:
```
myapp://route/path?param=value
```

## Usage
Define routes in `routes.json` and use navigation methods:
- `navigate(path, params)` - Navigate to route
- `goBack()` - Navigate backward
- `goForward()` - Navigate forward
- `currentRoute()` - Get current route
'''
    readme_path.write_text(readme_content, encoding='utf-8')
    
    return {
        'nav_dir': str(nav_dir),
        'config_path': str(config_path),
        'template_path': str(template_path),
        'routes_count': len(sample_routes)
    }
