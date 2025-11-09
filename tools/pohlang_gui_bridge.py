"""
PohLang to GUI Bridge
Maps PohLang natural language commands to Windows GUI framework
"""

import re
import json
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass

from tools.windows_gui_framework import (
    WindowsGUIFramework, WindowConfig, ComponentStyle,
    Button, TextInput, Label, Panel, AppGrid, GUIComponent
)


@dataclass
class GUICommand:
    """Represents a PohLang GUI command"""
    action: str
    target: str
    properties: Dict[str, Any]
    line_number: int


class PohLangGUIBridge:
    """Bridge between PohLang and Windows GUI framework"""
    
    # Command patterns for natural language parsing
    PATTERNS = {
        'create_window': r'Create\s+window\s+(?:titled|named)\s+"([^"]+)"',
        'set_window_size': r'Set\s+window\s+size\s+to\s+(\d+)\s*[x×]\s*(\d+)',
        'create_button': r'Create\s+button\s+"([^"]+)"(?:\s+in\s+(\w+))?',
        'create_input': r'Create\s+(?:text\s+)?input\s+"([^"]+)"(?:\s+in\s+(\w+))?',
        'create_label': r'Create\s+label\s+"([^"]+)"(?:\s+in\s+(\w+))?',
        'create_panel': r'Create\s+panel\s+"(\w+)"(?:\s+with\s+layout\s+"(\w+)")?',
        'add_to_panel': r'Add\s+"([^"]+)"\s+to\s+"(\w+)"',
        'on_click': r'When\s+"([^"]+)"\s+is\s+clicked\s+do',
        'show_window': r'Show\s+(?:the\s+)?window',
        'set_text': r'Set\s+(?:text\s+of\s+)?"([^"]+)"\s+to\s+"([^"]+)"',
        'get_text': r'Get\s+(?:text\s+from\s+)?"([^"]+)"',
        'set_theme': r'Set\s+theme\s+to\s+"(\w+)"',
        'add_app': r'Add\s+app\s+"([^"]+)"\s+with\s+icon\s+"([^"]+)"\s+command\s+"([^"]+)"',
    }
    
    def __init__(self):
        self.framework: Optional[WindowsGUIFramework] = None
        self.components: Dict[str, GUIComponent] = {}
        self.event_handlers: Dict[str, Callable] = {}
        self.current_component: Optional[str] = None
        
    def parse_gui_commands(self, code: str) -> List[GUICommand]:
        """Parse PohLang code for GUI commands"""
        commands = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Try each pattern
            for action, pattern in self.PATTERNS.items():
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    commands.append(GUICommand(
                        action=action,
                        target=match.group(1) if match.lastindex >= 1 else "",
                        properties={
                            f'arg{i}': match.group(i) 
                            for i in range(2, match.lastindex + 1)
                        } if match.lastindex > 1 else {},
                        line_number=line_num
                    ))
                    break
        
        return commands
    
    def execute_commands(self, commands: List[GUICommand]) -> bool:
        """Execute parsed GUI commands"""
        try:
            for cmd in commands:
                method = getattr(self, f'_cmd_{cmd.action}', None)
                if method:
                    method(cmd)
                else:
                    print(f"Warning: Unknown command {cmd.action} at line {cmd.line_number}")
            return True
        except Exception as e:
            print(f"Error executing GUI commands: {e}")
            return False
    
    def _cmd_create_window(self, cmd: GUICommand):
        """Create main window"""
        config = WindowConfig(title=cmd.target)
        self.framework = WindowsGUIFramework(config)
        self.framework.create_window()
    
    def _cmd_set_window_size(self, cmd: GUICommand):
        """Set window dimensions"""
        if self.framework and self.framework.window:
            width = int(cmd.properties.get('arg1', 1200))
            height = int(cmd.properties.get('arg2', 800))
            self.framework.window.resize(width, height)
    
    def _cmd_create_button(self, cmd: GUICommand):
        """Create button component"""
        button = Button(cmd.target)
        if self.framework:
            button.set_style(self.framework.style)
        
        component_id = self._generate_id(cmd.target)
        self.components[component_id] = button
        
        # Add to panel if specified
        parent = cmd.properties.get('arg1')
        if parent and parent in self.components:
            self.components[parent].add(button)
    
    def _cmd_create_input(self, cmd: GUICommand):
        """Create text input"""
        text_input = TextInput(cmd.target)
        if self.framework:
            text_input.set_style(self.framework.style)
        
        component_id = self._generate_id(cmd.target)
        self.components[component_id] = text_input
        
        parent = cmd.properties.get('arg1')
        if parent and parent in self.components:
            self.components[parent].add(text_input)
    
    def _cmd_create_label(self, cmd: GUICommand):
        """Create label"""
        label = Label(cmd.target)
        if self.framework:
            label.set_style(self.framework.style)
        
        component_id = self._generate_id(cmd.target)
        self.components[component_id] = label
        
        parent = cmd.properties.get('arg1')
        if parent and parent in self.components:
            self.components[parent].add(label)
    
    def _cmd_create_panel(self, cmd: GUICommand):
        """Create panel container"""
        layout = cmd.properties.get('arg1', 'vertical')
        panel = Panel(layout)
        if self.framework:
            panel.set_style(self.framework.style)
        
        self.components[cmd.target] = panel
    
    def _cmd_add_to_panel(self, cmd: GUICommand):
        """Add component to panel"""
        component_id = self._generate_id(cmd.target)
        panel_id = cmd.properties.get('arg1')
        
        if component_id in self.components and panel_id in self.components:
            panel = self.components[panel_id]
            component = self.components[component_id]
            panel.add(component)
    
    def _cmd_on_click(self, cmd: GUICommand):
        """Register click handler"""
        component_id = self._generate_id(cmd.target)
        self.current_component = component_id
        
        if component_id in self.components:
            # Handler will be set by next block of code
            pass
    
    def _cmd_show_window(self, cmd: GUICommand):
        """Show the window"""
        if self.framework:
            self.framework.show()
    
    def _cmd_set_text(self, cmd: GUICommand):
        """Set component text"""
        component_id = self._generate_id(cmd.target)
        new_text = cmd.properties.get('arg1', '')
        
        if component_id in self.components:
            component = self.components[component_id]
            if hasattr(component, 'set_text'):
                component.set_text(new_text)
    
    def _cmd_set_theme(self, cmd: GUICommand):
        """Set application theme"""
        if self.framework:
            self.framework.config.theme = cmd.target.lower()
            self.framework._apply_theme()
    
    def _cmd_add_app(self, cmd: GUICommand):
        """Add application to app grid"""
        # Find app grid component
        for comp in self.components.values():
            if isinstance(comp, AppGrid):
                icon = cmd.properties.get('arg1', '')
                command = cmd.properties.get('arg2', '')
                comp.add_app(cmd.target, icon, command)
                break
    
    def _generate_id(self, name: str) -> str:
        """Generate component ID from name"""
        return name.lower().replace(' ', '_').replace('"', '')
    
    def register_event_handler(self, component_id: str, event: str, handler: Callable):
        """Register event handler for component"""
        if component_id in self.components:
            self.components[component_id].on(event, handler)
    
    def run(self) -> int:
        """Start GUI event loop"""
        if self.framework:
            return self.framework.run()
        return 1


def create_launcher_from_pohlang(pohlang_code: str) -> PohLangGUIBridge:
    """Create GUI application from PohLang code"""
    bridge = PohLangGUIBridge()
    
    # Parse and execute commands
    commands = bridge.parse_gui_commands(pohlang_code)
    bridge.execute_commands(commands)
    
    return bridge


# Example PohLang GUI code
EXAMPLE_POHLANG_GUI = """
# Windows Desktop Launcher in PohLang

Start Program

# Create main window
Create window titled "Windows Desktop Launcher"
Set window size to 1200 x 800
Set theme to "dark"

# Create search bar
Create panel "search_panel" with layout "horizontal"
Create input "Search applications..." in search_panel

# Create app grid
Create panel "app_grid" with layout "grid"
Add app "Visual Studio Code" with icon "💻" command "code"
Add app "Chrome" with icon "🌐" command "chrome"
Add app "File Explorer" with icon "📁" command "explorer"
Add app "Terminal" with icon "⚡" command "wt"
Add app "Task Manager" with icon "📊" command "taskmgr"
Add app "Settings" with icon "⚙️" command "ms-settings:"

# Create system controls
Create panel "bottom_panel" with layout "horizontal"
Create button "Lock" in bottom_panel
Create button "Sleep" in bottom_panel
Create button "Restart" in bottom_panel
Create button "Shutdown" in bottom_panel

# Show the window
Show window

End Program
"""


if __name__ == "__main__":
    # Test the bridge with example code
    print("Creating launcher from PohLang code...")
    bridge = create_launcher_from_pohlang(EXAMPLE_POHLANG_GUI)
    
    if bridge.framework:
        print("Starting GUI...")
        exit_code = bridge.run()
        print(f"Application exited with code {exit_code}")
    else:
        print("Failed to create GUI framework")
