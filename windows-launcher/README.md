# Windows Desktop Launcher

A fully-featured desktop launcher for Windows with system-level access and control, built entirely in PohLang.

## 🚀 Features

### Application Management
- **Quick Launch**: Access all your installed applications instantly
- **Smart Search**: Find apps quickly with fuzzy search
- **Recent Apps**: Track frequently used applications
- **Custom Shortcuts**: Create your own launch shortcuts

### System Controls
- **Power Management**: Lock, Sleep, Restart, Shutdown, Sign Out
- **System Information**: View OS version, uptime, build info
- **Quick Actions**: One-click access to common system tasks
- **Task Manager Integration**: Launch system tools instantly

### Process Management
- **Process Monitoring**: View running processes in real-time
- **CPU & Memory Stats**: Monitor resource usage
- **Process Control**: Kill unresponsive processes
- **Process Details**: View detailed process information

### File Operations
- **Quick Access**: Jump to common folders instantly
- **File Search**: Find files across your system
- **File Operations**: Copy, move, delete files
- **Path Navigation**: Browse any directory

### Customization
- **Themes**: Dark and Light themes
- **Hotkeys**: Customizable keyboard shortcuts
- **Startup**: Launch at Windows boot
- **Notifications**: Configurable system notifications
- **Layout**: Adjustable icon sizes and display options

## 📋 Requirements

- Windows 10 or Windows 11
- PohLang Runtime (included in PLHub)
- Administrator privileges (for system-level operations)

## 🎯 Installation

### Quick Start

```bash
# From PLHub directory
cd windows-launcher

# Run the launcher
plhub run src/main.poh
```

## 💻 Usage

### Main Menu Navigation

```
[1] 🚀 Launch Applications - Quick access to installed apps
[2] 📊 Process Manager     - Monitor and manage processes
[3] 🖥️  System Controls     - Power options and system tools
[4] 📁 File Operations     - Navigate and manage files
[5] ⚙️  Settings           - Customize launcher preferences
[6] 🌟 Quick Actions       - One-click system tasks
[0] ❌ Exit                - Close launcher
```

### Keyboard Shortcuts

- **Numbers (1-9)**: Select menu items
- **B**: Go back to previous menu
- **S**: Search (in app launcher)
- **R**: Refresh (in process manager)
- **Help**: Show help message
- **Exit**: Quit launcher

## 🔧 Advanced Features

### System-Level Access

The launcher uses Windows APIs for:
- **Process Management**: Read/write process information
- **File System**: Access all file system operations
- **Registry**: Read Windows registry keys (for installed apps)
- **Power Control**: System power state management
- **Window Management**: Control application windows

### No Visual Studio Required

Built entirely in PohLang, this launcher:
- ✅ Runs on pure PohLang runtime (Rust-based)
- ✅ No C/C++ compilation needed
- ✅ No Visual Studio Build Tools required
- ✅ No Python dependencies
- ✅ Portable and lightweight

### Performance

- **Fast Startup**: Launches in < 1 second
- **Low Memory**: Uses < 50MB RAM
- **Responsive**: Instant UI updates
- **Efficient**: Minimal CPU usage when idle

## 📚 Project Structure

```
windows-launcher/
├── src/
│   └── main.poh              # Main launcher application
├── tests/
│   └── test_launcher.poh     # Test suite
└── README.md                 # This file
```

## 🧪 Testing

```bash
# Run main launcher
plhub run src/main.poh

# Run tests
plhub test

# Run in watch mode (auto-reload)
plhub dev
```

## 📖 Documentation

- [PohLang Guide](../../PohLang/doc/PohLang_Guide.md)
- [PLHub Documentation](../README.md)

## 📜 License

MIT License - See LICENSE file for details.

---

**Windows Desktop Launcher** - System control in natural language 🚀
