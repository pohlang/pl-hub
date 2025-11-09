"""
Windows GUI Framework for PLHub
Native Windows application framework with modern UI
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

# Check for PyQt6 availability
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QPushButton, QLabel, QLineEdit, QTextEdit,
        QListWidget, QTreeWidget, QTreeWidgetItem, QTabWidget,
        QMenuBar, QMenu, QToolBar, QStatusBar, QScrollArea,
        QFrame, QSplitter, QDialog, QMessageBox, QSystemTrayIcon
    )
    from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread
    from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QAction
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not available. Install with: pip install PyQt6")


@dataclass
class WindowConfig:
    """Configuration for a GUI window"""
    title: str = "PLHub Application"
    width: int = 1200
    height: int = 800
    min_width: int = 800
    min_height: int = 600
    icon: Optional[str] = None
    theme: str = "dark"
    resizable: bool = True
    center_on_screen: bool = True


@dataclass
class ComponentStyle:
    """Styling configuration for UI components"""
    background_color: str = "#2b2b2b"
    text_color: str = "#ffffff"
    accent_color: str = "#0078d4"
    border_color: str = "#3f3f3f"
    hover_color: str = "#3c3c3c"
    font_family: str = "Segoe UI"
    font_size: int = 10
    border_radius: int = 4
    padding: int = 8
    margin: int = 4


class GUIComponent:
    """Base class for all GUI components"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.widget = None
        self.style = ComponentStyle()
        self.event_handlers = {}
        
    def set_style(self, style: ComponentStyle):
        """Apply styling to component"""
        self.style = style
        if self.widget:
            self._apply_style()
    
    def _apply_style(self):
        """Apply CSS styling to widget"""
        if not self.widget:
            return
            
        css = f"""
            QWidget {{
                background-color: {self.style.background_color};
                color: {self.style.text_color};
                font-family: {self.style.font_family};
                font-size: {self.style.font_size}pt;
                border-radius: {self.style.border_radius}px;
                padding: {self.style.padding}px;
                margin: {self.style.margin}px;
            }}
            QPushButton {{
                background-color: {self.style.accent_color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: {self.style.border_radius}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.style.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.style.border_color};
            }}
            QLineEdit, QTextEdit {{
                background-color: {self.style.background_color};
                color: {self.style.text_color};
                border: 1px solid {self.style.border_color};
                border-radius: {self.style.border_radius}px;
                padding: {self.style.padding}px;
            }}
            QLabel {{
                background-color: transparent;
                color: {self.style.text_color};
            }}
        """
        self.widget.setStyleSheet(css)
    
    def on(self, event: str, handler: Callable):
        """Register event handler"""
        self.event_handlers[event] = handler
    
    def emit(self, event: str, *args, **kwargs):
        """Emit event to handler"""
        if event in self.event_handlers:
            self.event_handlers[event](*args, **kwargs)


class Button(GUIComponent):
    """Modern button component"""
    
    def __init__(self, text: str = "Button", parent=None):
        super().__init__(parent)
        if PYQT_AVAILABLE:
            self.widget = QPushButton(text)
            self.widget.clicked.connect(self._on_click)
            self._apply_style()
    
    def _on_click(self):
        self.emit('click')
    
    def set_text(self, text: str):
        if self.widget:
            self.widget.setText(text)
    
    def set_icon(self, icon_path: str):
        if self.widget and Path(icon_path).exists():
            self.widget.setIcon(QIcon(icon_path))


class TextInput(GUIComponent):
    """Text input field"""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        if PYQT_AVAILABLE:
            self.widget = QLineEdit()
            self.widget.setPlaceholderText(placeholder)
            self.widget.textChanged.connect(self._on_change)
            self._apply_style()
    
    def _on_change(self, text):
        self.emit('change', text)
    
    def get_text(self) -> str:
        return self.widget.text() if self.widget else ""
    
    def set_text(self, text: str):
        if self.widget:
            self.widget.setText(text)


class Label(GUIComponent):
    """Text label component"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        if PYQT_AVAILABLE:
            self.widget = QLabel(text)
            self._apply_style()
    
    def set_text(self, text: str):
        if self.widget:
            self.widget.setText(text)
    
    def set_font_size(self, size: int):
        if self.widget:
            font = self.widget.font()
            font.setPointSize(size)
            self.widget.setFont(font)


class Panel(GUIComponent):
    """Container panel for grouping components"""
    
    def __init__(self, layout: str = "vertical", parent=None):
        super().__init__(parent)
        if PYQT_AVAILABLE:
            self.widget = QFrame()
            self.layout = self._create_layout(layout)
            self.widget.setLayout(self.layout)
            self.children = []
            self._apply_style()
    
    def _create_layout(self, layout_type: str):
        if layout_type == "horizontal":
            return QHBoxLayout()
        elif layout_type == "grid":
            return QGridLayout()
        else:
            return QVBoxLayout()
    
    def add(self, component: GUIComponent, *args):
        """Add child component"""
        if component.widget:
            if isinstance(self.layout, QGridLayout) and len(args) >= 2:
                self.layout.addWidget(component.widget, args[0], args[1])
            else:
                self.layout.addWidget(component.widget)
            self.children.append(component)


class AppGrid(GUIComponent):
    """Grid layout for application icons"""
    
    def __init__(self, columns: int = 4, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.apps = []
        
        if PYQT_AVAILABLE:
            self.widget = QScrollArea()
            self.container = QWidget()
            self.layout = QGridLayout()
            self.container.setLayout(self.layout)
            self.widget.setWidget(self.container)
            self.widget.setWidgetResizable(True)
            self._apply_style()
    
    def add_app(self, name: str, icon: str, command: str):
        """Add application to grid"""
        app_data = {
            'name': name,
            'icon': icon,
            'command': command
        }
        self.apps.append(app_data)
        self._refresh_grid()
    
    def _refresh_grid(self):
        """Rebuild grid with current apps"""
        if not self.layout:
            return
        
        # Clear existing
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        
        # Add apps
        for idx, app in enumerate(self.apps):
            row = idx // self.columns
            col = idx % self.columns
            
            btn = QPushButton(app['name'])
            btn.clicked.connect(lambda checked, cmd=app['command']: self._launch_app(cmd))
            btn.setMinimumSize(QSize(120, 100))
            
            self.layout.addWidget(btn, row, col)
    
    def _launch_app(self, command: str):
        """Launch application"""
        self.emit('app_launch', command)


class WindowsGUIFramework:
    """Main GUI framework for Windows applications"""
    
    def __init__(self, config: Optional[WindowConfig] = None):
        self.config = config or WindowConfig()
        self.app = None
        self.window = None
        self.style = ComponentStyle()
        self.components = {}
        
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt6 is required. Install with: pip install PyQt6")
    
    def create_window(self) -> QMainWindow:
        """Create main application window"""
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        
        # Configure window
        self.window.setWindowTitle(self.config.title)
        self.window.resize(self.config.width, self.config.height)
        self.window.setMinimumSize(self.config.min_width, self.config.min_height)
        
        # Apply theme
        self._apply_theme()
        
        # Center on screen
        if self.config.center_on_screen:
            self._center_window()
        
        return self.window
    
    def _apply_theme(self):
        """Apply visual theme to application"""
        if self.config.theme == "dark":
            self.style = ComponentStyle(
                background_color="#2b2b2b",
                text_color="#ffffff",
                accent_color="#0078d4",
                border_color="#3f3f3f",
                hover_color="#3c3c3c"
            )
        else:  # light theme
            self.style = ComponentStyle(
                background_color="#f0f0f0",
                text_color="#000000",
                accent_color="#0078d4",
                border_color="#cccccc",
                hover_color="#e0e0e0"
            )
        
        # Apply to application
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.style.background_color))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self.style.text_color))
        palette.setColor(QPalette.ColorRole.Base, QColor(self.style.background_color))
        palette.setColor(QPalette.ColorRole.Text, QColor(self.style.text_color))
        self.app.setPalette(palette)
    
    def _center_window(self):
        """Center window on screen"""
        if not self.window:
            return
        screen = self.app.primaryScreen().geometry()
        window_geo = self.window.geometry()
        x = (screen.width() - window_geo.width()) // 2
        y = (screen.height() - window_geo.height()) // 2
        self.window.move(x, y)
    
    def create_menu_bar(self) -> QMenuBar:
        """Create menu bar"""
        return self.window.menuBar()
    
    def create_toolbar(self) -> QToolBar:
        """Create toolbar"""
        return self.window.addToolBar("Main Toolbar")
    
    def create_status_bar(self) -> QStatusBar:
        """Create status bar"""
        return self.window.statusBar()
    
    def set_central_widget(self, widget: QWidget):
        """Set central widget"""
        self.window.setCentralWidget(widget)
    
    def show(self):
        """Show window"""
        if self.window:
            self.window.show()
    
    def run(self) -> int:
        """Start event loop"""
        if self.app:
            return self.app.exec()
        return 1


def create_launcher_ui() -> WindowsGUIFramework:
    """Create the desktop launcher UI"""
    
    # Create framework
    config = WindowConfig(
        title="Windows Desktop Launcher",
        width=1200,
        height=800,
        theme="dark"
    )
    framework = WindowsGUIFramework(config)
    framework.create_window()
    
    # Create main layout
    central_widget = QWidget()
    main_layout = QVBoxLayout()
    central_widget.setLayout(main_layout)
    
    # Search bar at top
    search_panel = Panel("horizontal")
    search_input = TextInput("Search applications...")
    search_input.widget.setMinimumHeight(40)
    search_panel.add(search_input)
    main_layout.addWidget(search_panel.widget)
    
    # Application grid
    app_grid = AppGrid(columns=5)
    
    # Add applications
    apps = [
        ("Visual Studio Code", "💻", "code"),
        ("Chrome", "🌐", "chrome"),
        ("File Explorer", "📁", "explorer"),
        ("Terminal", "⚡", "wt"),
        ("Task Manager", "📊", "taskmgr"),
        ("Settings", "⚙️", "ms-settings:"),
        ("Calculator", "🔢", "calc"),
        ("Notepad", "📝", "notepad"),
    ]
    
    for name, icon, cmd in apps:
        app_grid.add_app(f"{icon} {name}", icon, cmd)
    
    main_layout.addWidget(app_grid.widget)
    
    # Bottom panel with system controls
    bottom_panel = Panel("horizontal")
    
    lock_btn = Button("🔒 Lock")
    sleep_btn = Button("😴 Sleep")
    restart_btn = Button("🔄 Restart")
    shutdown_btn = Button("⚡ Shutdown")
    
    bottom_panel.add(lock_btn)
    bottom_panel.add(sleep_btn)
    bottom_panel.add(restart_btn)
    bottom_panel.add(shutdown_btn)
    
    main_layout.addWidget(bottom_panel.widget)
    
    # Set central widget
    framework.set_central_widget(central_widget)
    
    # Create menu bar
    menu_bar = framework.create_menu_bar()
    file_menu = menu_bar.addMenu("File")
    file_menu.addAction("Settings")
    file_menu.addAction("Exit")
    
    view_menu = menu_bar.addMenu("View")
    view_menu.addAction("Light Theme")
    view_menu.addAction("Dark Theme")
    
    # Create status bar
    status_bar = framework.create_status_bar()
    status_bar.showMessage("Ready")
    
    return framework


if __name__ == "__main__":
    if not PYQT_AVAILABLE:
        print("ERROR: PyQt6 is required")
        print("Install with: pip install PyQt6")
        sys.exit(1)
    
    # Create and run launcher
    launcher = create_launcher_ui()
    launcher.show()
    sys.exit(launcher.run())
