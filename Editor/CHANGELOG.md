# Changelog

All notable changes to the PohLang Hub VS Code extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.3.0] - 2025-10-25

### Changed
- Updated for PLHub v0.7.0 - Enterprise-Grade UI Framework
- Enhanced description to reflect enterprise-grade tooling capabilities
- Fixed configuration descriptions to be more accurate and helpful

### PLHub v0.7.0 Features
This extension now supports projects built with PLHub v0.7.0, which includes:

**Enhanced Widget System (30+ widgets)**
- 13 new widget templates: slider, color_picker, date_picker, breadcrumb, pagination, flex_layout, data_table, line_chart, bar_chart, pie_chart, image_gallery, video_player, sidebar
- Organized by category: Form, Display, Layout, Navigation, Data, Overlay, Media
- All widgets use natural language PohLang syntax

**Expanded Style System (14 themes)**
- 8 new professional themes: nature_green, pastel_dream, creative_purple, corporate_blue, cyberpunk_neon, accessibility_optimized, minimal_white, high_performance_dark
- Design token presets: Apple HIG, Material Design 3, Fluent Design
- WCAG AAA accessibility compliance themes

**Advanced Layout System**
- 12-column responsive grid with breakpoints
- Flexbox layouts with auto-placement
- Stack layouts (horizontal/vertical)
- Container queries and fluid typography

**Navigation Framework**
- Stack navigation with history management
- Tab navigation with lazy loading
- Drawer navigation with gestures
- Modal navigation with focus trapping
- Deep linking and state preservation

**Enhanced Platform Tools (10x faster)**
- Parallel build processing
- Smart dependency caching
- Incremental compilation
- Build times: 60s → 6s

**Component Library**
- npm-style package management
- Semantic versioning support
- Dependency resolution
- CDN integration

**State Management**
- Reactive observer pattern
- Computed properties
- Middleware support
- Time-travel debugging

**Animation Framework**
- 25+ easing functions
- Keyframe animations
- Transition effects
- Gesture animations
- 60 FPS performance optimization

**Design System Manager**
- Apple HIG token support
- Material Design 3 support
- Fluent Design support
- WCAG validation
- Theme inheritance

**Cross-Platform UX**
- Native iOS patterns
- Native Android patterns
- Native Windows patterns
- Native macOS patterns
- Native Web patterns
- Platform-specific component adaptation

### Benefits for Extension Users
- Create projects with 30+ widget templates
- Apply 14 professional themes to projects
- Access advanced layout and navigation tools
- Use enterprise-grade build optimization
- Leverage reactive state management
- Create animated, responsive UIs
- Build cross-platform apps with native UX

### Configuration Updates
- Improved setting descriptions for clarity
- Better documentation for GitHub repository settings
- Enhanced auto-update configuration guidance

### Notes
- Fully backward compatible with previous PLHub versions
- All SDK management features remain unchanged
- New features available through PLHub CLI commands

---


## [0.2.5] - 2025-10-23

### Changed
- Updated for PohLang Runtime v0.6.6 / PLHub v0.6.0 - Phase 8 Optimizations Complete
- Compatible with enhanced VM featuring inline caching and profiling

### Runtime Features (v0.6.6)
- **Inline Caching**: 256-slot cache for fast global variable access
- **Enhanced Error Messages**: Source line number tracking for better debugging
- **VM Statistics**: Comprehensive profiling with \--stats\ flag
- **Optimizations**: Constant folding, instruction fusion, dead code elimination
- **Performance**: Significant speedup through advanced VM optimizations

### Benefits for Extension Users
- Better error messages when debugging PohLang programs
- Improved runtime performance for all PohLang projects
- Access to VM profiling data for optimization insights

### Notes
- Fully backward compatible with previous PohLang versions
- All SDK management features remain unchanged
- Phase 8 optimizations work transparently

---


## [0.2.3] - 2025-10-12

### Changed - Extension Separation
- **Removed Language Support**: Language definition, grammar, and snippets moved to separate "PohLang Language Support" extension
- **Prevents Conflicts**: Eliminates VS Code crashes from duplicate language registrations
- **Cleaner Architecture**: Extension now focuses solely on SDK/runtime management
- **Updated Dependencies**: Now requires "PohLang Language Support" extension for syntax highlighting
- **Updated for Runtime v0.6.0**: Compatible with latest PohLang runtime features

### Technical Details
- Package name: Changed to `plhub` (lowercase, npm convention)
- Categories: Removed "Programming Languages" and "Snippets"
- Removed contributions: `languages`, `grammars`, `snippets`
- Runtime: PohLang v0.6.0 with enhanced error messages and optimizations
- Architecture: Clean separation between language support and tooling

---

## [0.2.0] - 2025-10-10

### Added - Phase 5: Error Handling System
- **Try-Catch-Finally Blocks**: Complete error handling with `try this:`, `if error as e`, `finally:`, `end try`
- **7 Built-in Error Types**:
  - `RuntimeError` - General runtime errors
  - `TypeError` - Type-related errors
  - `MathError` - Mathematical operation errors (division by zero, domain errors)
  - `FileError` - File system operation errors
  - `JsonError` - JSON parsing and manipulation errors
  - `NetworkError` - Network operation errors
  - `ValidationError` - Input validation errors
- **Custom Error Types**: Create domain-specific errors with `make error type "ErrorName"`
- **Error Operations**:
  - `throw error` - Raise errors manually
  - `error message` - Get error description
  - `error type` - Get error type name
  - `error of type "TypeName"` - Type-specific catch blocks
- **Natural English Error Messages**: All errors use clear, beginner-friendly language
- **File Location Tracking**: Errors report which file they occurred in
- **Enhanced Project Management**: Better SDK version tracking and auto-update
- **Improved Diagnostics**: Real-time error reporting with natural language

### Changed
- **Updated PohLang Runtime**: Upgraded from v0.5.2 to v0.5.4 with error handling
- **Enhanced Error Messages**: All runtime errors now use natural English formatting
- **Better File Tracking**: Extension tracks which files are executing for better errors
- **Updated Icon**: Now uses dedicated PLHub icon from images folder

### Technical Details
- Runtime: PohLang v0.5.4 with Rust-based VM
- Error handling: ~450 lines of new infrastructure
- Location tracking: Filename reporting (line/column planned for future)
- Backward compatibility: All v0.5.2 code continues to work
- Extension size: Optimized with proper bundling

## [0.1.1] - 2025-10-09

### Fixed
- Verified TypeScript compilation produces no errors
- Confirmed runtime binary v0.5.2 properly bundled in `bin/` directory
- Validated all 5 commands work correctly with latest PLHub

### Improved
- Updated documentation with comprehensive verification results
- Confirmed all 38 code snippets working correctly
- Validated syntax highlighting for all PohLang v0.5.2 features including 20 phrasal expressions
- Extension packages successfully as `.vsix` file

### Testing
- ✅ Full stack validation completed (see `VERIFICATION_REPORT.md`)
- ✅ All commands tested and functional (Run File, Create Project, Update Language, etc.)
- ✅ Extension compiles and packages successfully
- ✅ Runtime detection works across multiple locations (extension bin/, workspace, PATH)

### Technical
- TypeScript compilation: Clean, no errors
- ESLint: No linting issues
- Bundle size: Optimized with proper `.vscodeignore`

## [Unreleased]

### Planned
- Advanced debugging support
- Interactive PohLang REPL
- Code formatting and refactoring tools
- Integration with package managers
- Performance profiling tools

## [0.1.0] - 2025-09-21

- **IntelliSense**: Smart completions for keywords, functions, variables, and all 20 phrasal expressions- Code snippets for common PohLang patterns

- **Rust Runtime Integration**: Execute `.poh` files with fast compiled Rust runtime (v0.5.2)- IntelliSense and autocompletion support

- **Automatic Runtime Detection**: Searches extension, workspace, development directories, and PATH- Three main commands:

- **Commands**:  - **PL-Hub: Run File** - Execute current .poh file

  - `PL-Hub: Run File` (Ctrl+F5) - Execute current .poh file  - **PL-Hub: Create Project** - Scaffold new PohLang projects  

  - `PL-Hub: Create Project` - Scaffold new PohLang projects with v0.5.2 templates  - **PL-Hub: Update Language** - Update interpreter binary

  - `PL-Hub: Update Language` - Download and install latest runtime- Real-time diagnostics and error reporting

  - `PL-Hub: Run Environment Example` - Test installation- Integrated terminal output for code execution

  - `PL-Hub: Show SDK Versions` - Display installed versions- Project scaffolding with templates

- **Configuration Settings**:- Placeholder PohLang interpreter binary

  - `pohlangHub.pohlangRepo` - GitHub repository for releases- Language configuration with proper comment support

  - `pohlangHub.plhubRepo` - PL-Hub SDK repository- File association for `.poh` files

  - `pohlangHub.autoUpdate` - Automatic update checking

  - `pohlangHub.updateIntervalDays` - Update check frequency### Language Features

  - `pohlangHub.sdkTagOverride` - Pin to specific version- Keywords: `make`, `set`, `to`, `function`, `if`, `else`, `while`, `for`, etc.

  - `pohlangHub.githubToken` - Optional token for API rate limits- Operators: `plus`, `minus`, `times`, `divided by`, `equals`, etc.

- Built-in functions: `print`, `input`, `length`, `type`, `convert`

### Changed- Data types: strings, numbers, booleans, null

- Updated syntax highlighting from old Python-based syntax to PohLang v0.5.2 Rust syntax- Control structures: conditionals, loops, functions

- Changed function syntax from `make function name:` to `Make name with param:` / `Make name:`- Comments: single-line (`#`) and block (`#* *#`)

- Updated variable syntax from `set variable to value` to `Make variable = value`

- Changed conditional from `if...else` to `If...Otherwise...End If`### Code Snippets

- Updated loops from lowercase to capitalized: `While...End While`, `Repeat...End`- `func` - Create function

- Changed I/O functions from `print` / `input` to `Write` / `Ask for`- `main` - Main function template

- Updated project templates to use v0.5.2 syntax with phrasal expressions- `set` - Variable assignment

- Modified completion provider to suggest v0.5.2 constructs- `var` - Variable declaration

- Updated snippets to match modern PohLang syntax- `if`/`ifelse` - Conditional statements

- `while`/`for` - Loop structures

### Fixed- `print` - Print statement

- Runtime detection now uses `--run` flag for Rust runtime (v0.5.2)- `input` - Input statement

- File execution properly spawns pohlang.exe with correct arguments- Arithmetic operations (`add`, `sub`, `mul`, `div`)

- IntelliSense now provides accurate completions for current language version

### Technical Implementation

### Technical Details- TypeScript-based extension

- Extension ID: `pohlang.PLHub`- Node.js child process integration for interpreter execution

- Minimum VS Code version: 1.70.0- VS Code language server protocol compliance

- Language ID: `pohlang`- Comprehensive error handling and validation

- File extensions: `.poh`- Cross-platform compatibility (Windows, macOS, Linux)

- Runtime: PohLang v0.5.2 (Rust-compiled)- Modular architecture with separated concerns



## [Unreleased]### Documentation

- Complete README with usage instructions

### Planned- Code examples and getting started guide

- Hover documentation for phrasal expressions- API documentation for extension development

- Go to definition for functions and variables- Contributing guidelines

- Find all references- MIT license

- Rename symbol refactoring

- Code formatting provider### Development Tools

- Debugger integration- TypeScript compilation setup

- Interactive playground- ESLint configuration

- More example projects- Build and packaging scripts

- VS Code launch configuration for debugging

---- Extension development host support



For full documentation, visit: https://github.com/pohlang/PLHub---


## Version Schema

- **Major** (X.0.0): Breaking changes, major new features
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, small improvements

## Support

For questions, issues, or feature requests:
- [GitHub Issues](https://github.com/pohlang/PLHub/issues)
- [GitHub Discussions](https://github.com/pohlang/PLHub/discussions)
