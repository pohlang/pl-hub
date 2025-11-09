"""
PLHub Platform Manager
Manages cross-platform project creation, building, and deployment for:
- Android
- iOS  
- macOS
- Windows
- Web

Enhanced with:
- Incremental builds with caching
- Better error handling and recovery
- Dependency resolution and validation
- Build optimization and parallel processing
- Platform-specific optimizations
"""

import os
import json
import shutil
import subprocess
import sys
import hashlib
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import pickle


class Platform(Enum):
    """Supported platforms"""
    ANDROID = "android"
    IOS = "ios"
    MACOS = "macos"
    WINDOWS = "windows"
    WEB = "web"


@dataclass
class BuildConfig:
    """Build configuration with caching support"""
    platform: Platform
    configuration: str
    project_dir: Path
    enable_cache: bool = True
    parallel: bool = True
    optimization_level: str = "standard"  # minimal, standard, aggressive
    incremental: bool = True
    
    def cache_key(self) -> str:
        """Generate cache key for this build"""
        return hashlib.md5(
            f"{self.platform.value}-{self.configuration}-{self.optimization_level}".encode()
        ).hexdigest()


@dataclass
class BuildResult:
    """Result of a build operation"""
    success: bool
    duration: float
    cached: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    artifacts: List[Path] = field(default_factory=list)
    
    def summary(self) -> str:
        """Generate build summary"""
        status = "✓ SUCCESS" if self.success else "✗ FAILED"
        cache_info = " (cached)" if self.cached else ""
        return (
            f"{status}{cache_info} - {self.duration:.2f}s\n"
            f"  Errors: {len(self.errors)}\n"
            f"  Warnings: {len(self.warnings)}\n"
            f"  Artifacts: {len(self.artifacts)}"
        )


@dataclass
class DependencyInfo:
    """Platform dependency information"""
    name: str
    version: Optional[str] = None
    required: bool = True
    installed: bool = False
    install_command: Optional[str] = None
    check_command: Optional[str] = None


class BuildCache:
    """Manages build caching for incremental builds"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate file hash"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return ""
    
    def has_changed(self, file_path: Path, cache_key: str) -> bool:
        """Check if file has changed since last build"""
        current_hash = self.get_file_hash(file_path)
        cached_hash = self.metadata.get(cache_key, {}).get(str(file_path))
        return current_hash != cached_hash
    
    def update_cache(self, file_path: Path, cache_key: str):
        """Update cache entry for file"""
        current_hash = self.get_file_hash(file_path)
        if cache_key not in self.metadata:
            self.metadata[cache_key] = {}
        self.metadata[cache_key][str(file_path)] = current_hash
        self._save_metadata()
    
    def get_changed_files(self, file_paths: List[Path], cache_key: str) -> List[Path]:
        """Get list of files that have changed"""
        return [f for f in file_paths if self.has_changed(f, cache_key)]
    
    def clear_cache(self, cache_key: Optional[str] = None):
        """Clear cache entries"""
        if cache_key:
            self.metadata.pop(cache_key, None)
        else:
            self.metadata.clear()
        self._save_metadata()


class DependencyValidator:
    """Validates platform dependencies"""
    
    PLATFORM_DEPS = {
        Platform.ANDROID: [
            DependencyInfo("Android SDK", required=True, 
                          check_command="adb --version",
                          install_command="Install Android Studio from https://developer.android.com/studio"),
            DependencyInfo("Gradle", required=True,
                          check_command="gradle --version",
                          install_command="Installed with Android Studio or from https://gradle.org"),
            DependencyInfo("Java JDK", version="11+", required=True,
                          check_command="java -version",
                          install_command="Install from https://adoptium.net/"),
        ],
        Platform.IOS: [
            DependencyInfo("Xcode", required=True,
                          check_command="xcodebuild -version",
                          install_command="Install from Mac App Store (macOS only)"),
            DependencyInfo("Xcode Command Line Tools", required=True,
                          check_command="xcode-select -p",
                          install_command="xcode-select --install"),
            DependencyInfo("CocoaPods", required=False,
                          check_command="pod --version",
                          install_command="sudo gem install cocoapods"),
        ],
        Platform.MACOS: [
            DependencyInfo("Xcode", required=True,
                          check_command="xcodebuild -version",
                          install_command="Install from Mac App Store (macOS only)"),
        ],
        Platform.WINDOWS: [
            DependencyInfo(".NET SDK", version="7.0+", required=True,
                          check_command="dotnet --version",
                          install_command="Install from https://dotnet.microsoft.com/download"),
            DependencyInfo("Visual Studio", required=False,
                          check_command="where msbuild",
                          install_command="Install from https://visualstudio.microsoft.com/"),
        ],
        Platform.WEB: [
            DependencyInfo("Node.js", version="16+", required=True,
                          check_command="node --version",
                          install_command="Install from https://nodejs.org/"),
            DependencyInfo("npm", required=True,
                          check_command="npm --version",
                          install_command="Included with Node.js"),
        ],
    }
    
    @classmethod
    def check_dependencies(cls, platform: Platform) -> Tuple[bool, List[DependencyInfo]]:
        """Check if platform dependencies are satisfied"""
        deps = cls.PLATFORM_DEPS.get(platform, [])
        all_satisfied = True
        
        for dep in deps:
            if dep.check_command:
                try:
                    result = subprocess.run(
                        dep.check_command.split(),
                        capture_output=True,
                        timeout=5
                    )
                    dep.installed = result.returncode == 0
                except:
                    dep.installed = False
                
                if dep.required and not dep.installed:
                    all_satisfied = False
        
        return all_satisfied, deps
    
    @classmethod
    def print_dependency_report(cls, platform: Platform):
        """Print dependency status report"""
        satisfied, deps = cls.check_dependencies(platform)
        
        print(f"\n{'='*60}")
        print(f"Dependency Check: {platform.value.upper()}")
        print(f"{'='*60}\n")
        
        for dep in deps:
            status = "✓" if dep.installed else "✗"
            req_label = "REQUIRED" if dep.required else "OPTIONAL"
            version = f" ({dep.version})" if dep.version else ""
            
            print(f"{status} {dep.name}{version} [{req_label}]")
            
            if not dep.installed and dep.install_command:
                print(f"   Install: {dep.install_command}")
        
        print(f"\n{'='*60}")
        if satisfied:
            print("✓ All required dependencies satisfied")
        else:
            print("✗ Missing required dependencies")
        print(f"{'='*60}\n")


class PlatformManager:
    """Manages cross-platform development with enhanced build capabilities"""
    
    def __init__(self, plhub_root: Optional[Path] = None):
        self.plhub_root = plhub_root or Path(__file__).parent.parent
        self.templates_dir = self.plhub_root / "templates"
        self.cache_dir = self.plhub_root / ".build_cache"
        self.build_cache = BuildCache(self.cache_dir)
        
        self.builders = {
            Platform.ANDROID: AndroidBuilder(self.build_cache),
            Platform.IOS: IOSBuilder(self.build_cache),
            Platform.MACOS: MacOSBuilder(self.build_cache),
            Platform.WINDOWS: WindowsBuilder(self.build_cache),
            Platform.WEB: WebBuilder(self.build_cache)
        }
    
    def check_dependencies(self, platform: Platform) -> bool:
        """Check and display platform dependencies"""
        DependencyValidator.print_dependency_report(platform)
        satisfied, _ = DependencyValidator.check_dependencies(platform)
        return satisfied
    
    def create_project(self, platform: Platform, project_name: str, 
                      output_dir: Path, package_name: Optional[str] = None) -> bool:
        """Create a new platform-specific project"""
        try:
            print(f"Creating {platform.value} project: {project_name}")
            
            # Get template
            template_dir = self.templates_dir / platform.value
            if not template_dir.exists():
                print(f"Error: Template not found for {platform.value}")
                return False
            
            # Load project structure
            structure_file = template_dir / "project_structure.json"
            with open(structure_file, 'r') as f:
                structure = json.load(f)
            
            # Create project directory
            project_dir = output_dir / project_name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate package name if not provided
            if not package_name:
                package_name = f"com.pohlang.{project_name.lower().replace('-', '_')}"
            
            # Create project structure
            self._create_structure(project_dir, structure['structure'], 
                                  template_dir, project_name, package_name)
            
            print(f"✓ Project created at: {project_dir}")
            print(f"  Platform: {platform.value}")
            print(f"  Package: {package_name}")
            
            # Display next steps
            self._display_next_steps(platform, project_dir)
            
            return True
            
        except Exception as e:
            print(f"Error creating project: {e}")
            return False
    
    def _create_structure(self, base_dir: Path, structure: Dict, 
                         template_dir: Path, app_name: str, package_name: str):
        """Recursively create project structure"""
        for name, content in structure.items():
            # Replace placeholders
            name = name.replace("{{APP_NAME}}", app_name)
            path = base_dir / name
            
            if isinstance(content, dict):
                # Directory
                path.mkdir(parents=True, exist_ok=True)
                self._create_structure(path, content, template_dir, 
                                     app_name, package_name)
            elif isinstance(content, list):
                # Directory with specific files
                path.mkdir(parents=True, exist_ok=True)
                for file in content:
                    file_path = path / file
                    file_path.touch()
            elif content is True:
                # File - copy from template if exists
                template_file = self._find_template_file(template_dir, name)
                if template_file and template_file.exists():
                    content_text = template_file.read_text(encoding='utf-8')
                    # Replace placeholders
                    content_text = content_text.replace("{{APP_NAME}}", app_name)
                    content_text = content_text.replace("{{PACKAGE_NAME}}", package_name)
                    path.write_text(content_text, encoding='utf-8')
                else:
                    path.touch()
    
    def _find_template_file(self, template_dir: Path, filename: str) -> Optional[Path]:
        """Find template file by name"""
        # Try direct path
        direct_path = template_dir / filename
        if direct_path.exists():
            return direct_path
        
        # Search recursively
        for file in template_dir.rglob(filename):
            return file
        
        return None
    
    def _display_next_steps(self, platform: Platform, project_dir: Path):
        """Display platform-specific next steps"""
        print("\n📋 Next Steps:")
        
        if platform == Platform.ANDROID:
            print("  1. Open project in Android Studio")
            print("  2. Sync Gradle files")
            print("  3. Run: plhub platform run android")
            print("  4. Connect device or start emulator")
            
        elif platform == Platform.IOS:
            print("  1. Open {project_dir.name}.xcodeproj in Xcode")
            print("  2. Select target device/simulator")
            print("  3. Run: plhub platform run ios")
            print("  4. Requires macOS with Xcode")
            
        elif platform == Platform.MACOS:
            print("  1. Open {project_dir.name}.xcodeproj in Xcode")
            print("  2. Build for macOS target")
            print("  3. Run: plhub platform run macos")
            
        elif platform == Platform.WINDOWS:
            print("  1. Open project in Visual Studio 2022")
            print("  2. Restore NuGet packages")
            print("  3. Run: plhub platform run windows")
            print("  4. Requires Windows 10/11 with WinUI3 SDK")
            
        elif platform == Platform.WEB:
            print("  1. Install dependencies: npm install")
            print("  2. Start dev server: plhub platform run web")
            print("  3. Open http://localhost:8080")
            print("  4. Hot reload enabled automatically")
    
    
    def build(self, platform: Platform, project_dir: Path, 
             configuration: str = "debug", **kwargs) -> BuildResult:
        """Build project for specified platform with caching"""
        try:
            # Check dependencies first
            satisfied, _ = DependencyValidator.check_dependencies(platform)
            if not satisfied:
                print("⚠️  Missing required dependencies. Build may fail.")
                if not kwargs.get('force', False):
                    response = input("Continue anyway? (y/N): ")
                    if response.lower() != 'y':
                        return BuildResult(
                            success=False,
                            duration=0,
                            errors=["Missing required dependencies"]
                        )
            
            # Create build config
            config = BuildConfig(
                platform=platform,
                configuration=configuration,
                project_dir=project_dir,
                enable_cache=kwargs.get('enable_cache', True),
                parallel=kwargs.get('parallel', True),
                optimization_level=kwargs.get('optimization', 'standard'),
                incremental=kwargs.get('incremental', True)
            )
            
            # Execute build
            builder = self.builders[platform]
            return builder.build_enhanced(config)
            
        except Exception as e:
            print(f"Build error: {e}")
            import traceback
            traceback.print_exc()
            return BuildResult(
                success=False,
                duration=0,
                errors=[str(e)]
            )
    
    def run(self, platform: Platform, project_dir: Path, 
           device: Optional[str] = None) -> bool:
        """Run project on specified platform"""
        try:
            builder = self.builders[platform]
            return builder.run(project_dir, device)
        except Exception as e:
            print(f"Run error: {e}")
            return False
    
    def test(self, platform: Platform, project_dir: Path) -> bool:
        """Run tests for specified platform"""
        try:
            builder = self.builders[platform]
            return builder.test(project_dir)
        except Exception as e:
            print(f"Test error: {e}")
            return False
    
    def deploy(self, platform: Platform, project_dir: Path, 
              target: str) -> bool:
        """Deploy project to specified target"""
        try:
            builder = self.builders[platform]
            return builder.deploy(project_dir, target)
        except Exception as e:
            print(f"Deploy error: {e}")
            return False
    
    def list_devices(self, platform: Platform) -> List[Dict[str, Any]]:
        """List available devices for platform"""
        try:
            builder = self.builders[platform]
            return builder.list_devices()
        except Exception as e:
            print(f"Error listing devices: {e}")
            return []
    
    
    def clean_cache(self, platform: Optional[Platform] = None):
        """Clean build cache"""
        if platform:
            config = BuildConfig(platform, "", Path("."))
            self.build_cache.clear_cache(config.cache_key())
            print(f"✓ Cleared cache for {platform.value}")
        else:
            self.build_cache.clear_cache()
            print("✓ Cleared all build caches")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_size = sum(
            f.stat().st_size 
            for f in self.cache_dir.rglob('*') 
            if f.is_file()
        )
        
        return {
            'cache_dir': str(self.cache_dir),
            'total_size_mb': total_size / (1024 * 1024),
            'entry_count': len(self.build_cache.metadata),
            'entries': self.build_cache.metadata
        }


class PlatformBuilder:
    """Base class for platform builders with enhanced capabilities"""
    
    def __init__(self, build_cache: BuildCache):
        self.build_cache = build_cache
        self.build_history: List[BuildResult] = []
    
    def build(self, project_dir: Path, configuration: str) -> bool:
        """Legacy build method (kept for compatibility)"""
        config = BuildConfig(
            platform=Platform.ANDROID,  # Will be overridden
            configuration=configuration,
            project_dir=project_dir
        )
        result = self.build_enhanced(config)
        return result.success
    
    def build_enhanced(self, config: BuildConfig) -> BuildResult:
        """Enhanced build with caching and optimization"""
        start_time = time.time()
        result = BuildResult(success=False, duration=0)
        
        try:
            print(f"\n{'='*60}")
            print(f"Building {config.platform.value} - {config.configuration}")
            print(f"{'='*60}\n")
            
            # Check for incremental build
            if config.incremental and config.enable_cache:
                source_files = self._get_source_files(config.project_dir)
                changed_files = self.build_cache.get_changed_files(
                    source_files,
                    config.cache_key()
                )
                
                if not changed_files:
                    result.cached = True
                    result.success = True
                    print("✓ No changes detected - using cached build")
                else:
                    print(f"ℹ Incremental build: {len(changed_files)} files changed")
                    result = self._execute_build(config, changed_files)
            else:
                result = self._execute_build(config, [])
            
            # Update cache if successful
            if result.success and config.enable_cache:
                source_files = self._get_source_files(config.project_dir)
                for file in source_files:
                    self.build_cache.update_cache(file, config.cache_key())
            
        except Exception as e:
            result.errors.append(str(e))
            import traceback
            result.errors.append(traceback.format_exc())
        
        result.duration = time.time() - start_time
        self.build_history.append(result)
        
        print(f"\n{result.summary()}\n")
        return result
    
    def _get_source_files(self, project_dir: Path) -> List[Path]:
        """Get list of source files for incremental build detection"""
        # Override in subclasses for platform-specific patterns
        patterns = ['*.poh', '*.json', '*.xml', '*.java', '*.kt', '*.swift', '*.ts', '*.js']
        files = []
        for pattern in patterns:
            files.extend(project_dir.rglob(pattern))
        return files
    
    def _execute_build(self, config: BuildConfig, changed_files: List[Path]) -> BuildResult:
        """Execute the actual build - must be implemented by subclasses"""
        raise NotImplementedError
    
    def run(self, project_dir: Path, device: Optional[str]) -> bool:
        raise NotImplementedError
    
    def test(self, project_dir: Path) -> bool:
        raise NotImplementedError
    
    def deploy(self, project_dir: Path, target: str) -> bool:
        raise NotImplementedError
    
    def list_devices(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    def _run_command(self, cmd: List[str], cwd: Path, 
                    capture_errors: bool = True) -> Tuple[bool, str, str]:
        """Run shell command with enhanced error handling"""
        try:
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            stdout = result.stdout
            stderr = result.stderr
            
            if stdout:
                print(stdout)
            
            if stderr and capture_errors:
                if result.returncode != 0:
                    print(f"ERROR: {stderr}", file=sys.stderr)
                else:
                    # Some tools output to stderr even on success
                    print(f"INFO: {stderr}")
            
            return result.returncode == 0, stdout, stderr
            
        except subprocess.TimeoutExpired:
            print("ERROR: Command timed out after 10 minutes")
            return False, "", "Timeout"
        except FileNotFoundError:
            print(f"ERROR: Command not found: {cmd[0]}")
            print(f"Make sure {cmd[0]} is installed and in your PATH")
            return False, "", f"Command not found: {cmd[0]}"
        except Exception as e:
            print(f"ERROR: Command failed: {e}")
            return False, "", str(e)
    
    def _validate_project_structure(self, project_dir: Path, 
                                   required_files: List[str]) -> Tuple[bool, List[str]]:
        """Validate project has required files"""
        missing = []
        for file_pattern in required_files:
            if not list(project_dir.glob(file_pattern)):
                missing.append(file_pattern)
        
        if missing:
            print(f"⚠️  Missing required files: {', '.join(missing)}")
        
        return len(missing) == 0, missing


class AndroidBuilder(PlatformBuilder):
    """Android platform builder with optimizations"""
    
    def _execute_build(self, config: BuildConfig, changed_files: List[Path]) -> BuildResult:
        """Execute Android build with Gradle"""
        result = BuildResult(success=False, duration=0)
        
        # Validate project structure
        valid, missing = self._validate_project_structure(
            config.project_dir,
            ['build.gradle*', 'gradlew*', 'app/']
        )
        if not valid:
            result.errors.append(f"Invalid Android project structure")
            return result
        
        # Determine Gradle wrapper
        gradlew = "gradlew.bat" if sys.platform == "win32" else "./gradlew"
        
        # Build task based on configuration
        if config.configuration == "debug":
            task = "assembleDebug"
        else:
            task = "assembleRelease"
        
        # Add optimization flags
        gradle_args = [gradlew, task, "--stacktrace"]
        
        if config.parallel:
            gradle_args.append("--parallel")
        
        if config.optimization_level == "aggressive":
            gradle_args.extend(["--build-cache", "--configure-on-demand"])
        elif config.optimization_level == "standard":
            gradle_args.append("--build-cache")
        
        if config.incremental and changed_files:
            # Gradle handles incremental builds automatically
            gradle_args.append("--continuous")
        
        # Execute build
        success, stdout, stderr = self._run_command(gradle_args, config.project_dir)
        
        result.success = success
        
        if not success:
            result.errors.append("Gradle build failed")
            if stderr:
                result.errors.append(stderr)
        else:
            # Find built APK/AAB
            output_dir = config.project_dir / "app" / "build" / "outputs"
            if config.configuration == "debug":
                apks = list(output_dir.rglob("*-debug.apk"))
            else:
                apks = list(output_dir.rglob("*-release.apk"))
                apks.extend(list(output_dir.rglob("*-release.aab")))
            
            result.artifacts = apks
            
            if apks:
                print(f"\n✓ Built artifacts:")
                for apk in apks:
                    size_mb = apk.stat().st_size / (1024 * 1024)
                    print(f"  - {apk.name} ({size_mb:.2f} MB)")
        
        # Parse warnings from output
        if stdout:
            for line in stdout.split('\n'):
                if 'warning' in line.lower():
                    result.warnings.append(line.strip())
        
        return result
    
    def _get_source_files(self, project_dir: Path) -> List[Path]:
        """Get Android source files"""
        files = []
        patterns = ['*.java', '*.kt', '*.xml', '*.gradle', '*.gradle.kts', '*.poh']
        for pattern in patterns:
            files.extend((project_dir / "app" / "src").rglob(pattern))
        return files
    
    def run(self, project_dir: Path, device: Optional[str]) -> bool:
        """Run on Android device/emulator with better error handling"""
        print("Running Android application...")
        
        # Check for devices first
        devices = self.list_devices()
        if not devices:
            print("⚠️  No Android devices connected")
            print("Connect a device or start an emulator:")
            print("  - Physical device: Enable USB debugging and connect")
            print("  - Emulator: Launch from Android Studio or run 'emulator -avd <avd_name>'")
            return False
        
        # Select device
        if not device and len(devices) > 1:
            print("\nAvailable devices:")
            for i, dev in enumerate(devices):
                print(f"  {i+1}. {dev['id']} ({dev['type']})")
            device = devices[0]['id']
            print(f"\nUsing: {device}")
        elif not device:
            device = devices[0]['id']
        
        # Build and install
        gradlew = "gradlew.bat" if sys.platform == "win32" else "./gradlew"
        cmd = [gradlew, "installDebug"]
        
        if device:
            # Set ANDROID_SERIAL environment variable
            env = os.environ.copy()
            env['ANDROID_SERIAL'] = device
        
        success, _, _ = self._run_command(cmd, project_dir)
        if not success:
            print("Failed to install APK")
            return False
        
        # Launch activity
        package = self._get_package_name(project_dir)
        activity = f"{package}.MainActivity"
        
        adb_cmd = ["adb"]
        if device:
            adb_cmd.extend(["-s", device])
        adb_cmd.extend(["shell", "am", "start", "-n", f"{package}/{activity}"])
        
        success, _, _ = self._run_command(adb_cmd, project_dir)
        
        if success:
            print(f"\n✓ App launched on {device}")
            print(f"  Package: {package}")
            print(f"\nView logs: adb logcat | grep {package}")
        
        return success
    
    def test(self, project_dir: Path) -> bool:
        """Run Android tests with detailed reporting"""
        print("Running Android tests...")
        
        gradlew = "gradlew.bat" if sys.platform == "win32" else "./gradlew"
        
        # Run unit tests
        print("\n📝 Running unit tests...")
        success, stdout, _ = self._run_command([gradlew, "test", "--info"], project_dir)
        
        if not success:
            print("Unit tests failed")
            return False
        
        # Parse test results
        test_report = project_dir / "app" / "build" / "reports" / "tests"
        if test_report.exists():
            print(f"\n✓ Unit test report: {test_report}")
        
        # Run instrumented tests if devices available
        devices = self.list_devices()
        if devices:
            print("\n📱 Running instrumented tests...")
            success, _, _ = self._run_command(
                [gradlew, "connectedAndroidTest"],
                project_dir
            )
            
            if not success:
                print("Instrumented tests failed")
                return False
        else:
            print("\n⚠️  Skipping instrumented tests (no devices connected)")
        
        print("\n✓ All tests passed")
        return True
    
    def deploy(self, project_dir: Path, target: str) -> bool:
        """Deploy to Google Play"""
        print(f"Deploying Android app to {target}...")
        
        # Build release bundle
        gradlew = "./gradlew.bat" if sys.platform == "win32" else "./gradlew"
        return self._run_command([gradlew, "bundleRelease"], project_dir)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List connected Android devices"""
        try:
            result = subprocess.run(["adb", "devices", "-l"], 
                                  capture_output=True, text=True)
            devices = []
            
            for line in result.stdout.split('\n')[1:]:
                if line.strip() and 'device' in line:
                    parts = line.split()
                    devices.append({
                        'id': parts[0],
                        'status': parts[1],
                        'type': 'emulator' if 'emulator' in parts[0] else 'physical'
                    })
            
            return devices
        except Exception as e:
            print(f"Error listing devices: {e}")
            return []
    
    def _get_package_name(self, project_dir: Path) -> str:
        """Extract package name from AndroidManifest.xml"""
        manifest = project_dir / "app" / "src" / "main" / "AndroidManifest.xml"
        if manifest.exists():
            import xml.etree.ElementTree as ET
            tree = ET.parse(manifest)
            return tree.getroot().get('package', 'com.pohlang.app')
        return "com.pohlang.app"


class IOSBuilder(PlatformBuilder):
    """iOS platform builder"""
    
    def build(self, project_dir: Path, configuration: str) -> bool:
        """Build iOS app"""
        print(f"Building iOS project ({configuration})...")
        
        xcodeproj = list(project_dir.glob("*.xcodeproj"))[0]
        scheme = xcodeproj.stem
        
        cmd = [
            "xcodebuild",
            "-project", str(xcodeproj),
            "-scheme", scheme,
            "-configuration", configuration.capitalize(),
            "-sdk", "iphoneos",
            "build"
        ]
        
        return self._run_command(cmd, project_dir)
    
    def run(self, project_dir: Path, device: Optional[str]) -> bool:
        """Run on iOS device/simulator"""
        print("Running iOS application...")
        
        # Build first
        if not self.build(project_dir, "debug"):
            return False
        
        # Launch simulator
        xcodeproj = list(project_dir.glob("*.xcodeproj"))[0]
        scheme = xcodeproj.stem
        
        destination = f"platform=iOS Simulator,name={device}" if device else "platform=iOS Simulator"
        
        cmd = [
            "xcodebuild",
            "-project", str(xcodeproj),
            "-scheme", scheme,
            "-destination", destination,
            "run"
        ]
        
        return self._run_command(cmd, project_dir)
    
    def test(self, project_dir: Path) -> bool:
        """Run iOS tests"""
        print("Running iOS tests...")
        
        xcodeproj = list(project_dir.glob("*.xcodeproj"))[0]
        scheme = xcodeproj.stem
        
        cmd = [
            "xcodebuild",
            "-project", str(xcodeproj),
            "-scheme", scheme,
            "-destination", "platform=iOS Simulator",
            "test"
        ]
        
        return self._run_command(cmd, project_dir)
    
    def deploy(self, project_dir: Path, target: str) -> bool:
        """Deploy to App Store"""
        print(f"Deploying iOS app to {target}...")
        
        # Build archive
        xcodeproj = list(project_dir.glob("*.xcodeproj"))[0]
        scheme = xcodeproj.stem
        archive_path = project_dir / "build" / f"{scheme}.xcarchive"
        
        cmd = [
            "xcodebuild",
            "-project", str(xcodeproj),
            "-scheme", scheme,
            "-configuration", "Release",
            "-archivePath", str(archive_path),
            "archive"
        ]
        
        return self._run_command(cmd, project_dir)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List iOS simulators and devices"""
        try:
            result = subprocess.run(["xcrun", "simctl", "list", "devices", "available"],
                                  capture_output=True, text=True)
            devices = []
            
            for line in result.stdout.split('\n'):
                if '(' in line and ')' in line:
                    name = line.split('(')[0].strip()
                    udid = line.split('(')[1].split(')')[0]
                    devices.append({
                        'name': name,
                        'udid': udid,
                        'type': 'simulator'
                    })
            
            return devices
        except Exception as e:
            print(f"Error listing devices: {e}")
            return []


class MacOSBuilder(PlatformBuilder):
    """macOS platform builder"""
    
    def build(self, project_dir: Path, configuration: str) -> bool:
        """Build macOS app"""
        print(f"Building macOS project ({configuration})...")
        
        xcodeproj = list(project_dir.glob("*.xcodeproj"))[0]
        scheme = xcodeproj.stem
        
        cmd = [
            "xcodebuild",
            "-project", str(xcodeproj),
            "-scheme", scheme,
            "-configuration", configuration.capitalize(),
            "build"
        ]
        
        return self._run_command(cmd, project_dir)
    
    def run(self, project_dir: Path, device: Optional[str]) -> bool:
        """Run macOS app"""
        print("Running macOS application...")
        
        # Build first
        if not self.build(project_dir, "debug"):
            return False
        
        # Find and launch app
        build_dir = project_dir / "build" / "Debug"
        app = list(build_dir.glob("*.app"))[0]
        
        cmd = ["open", str(app)]
        return self._run_command(cmd, project_dir)
    
    def test(self, project_dir: Path) -> bool:
        """Run macOS tests"""
        print("Running macOS tests...")
        
        xcodeproj = list(project_dir.glob("*.xcodeproj"))[0]
        scheme = xcodeproj.stem
        
        cmd = [
            "xcodebuild",
            "-project", str(xcodeproj),
            "-scheme", scheme,
            "test"
        ]
        
        return self._run_command(cmd, project_dir)
    
    def deploy(self, project_dir: Path, target: str) -> bool:
        """Deploy macOS app"""
        print(f"Deploying macOS app to {target}...")
        
        # Build release
        return self.build(project_dir, "release")
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List macOS devices (always just local machine)"""
        return [{'name': 'Local Mac', 'type': 'physical'}]


class WindowsBuilder(PlatformBuilder):
    """Windows platform builder"""
    
    def build(self, project_dir: Path, configuration: str) -> bool:
        """Build Windows app"""
        print(f"Building Windows project ({configuration})...")
        
        csproj = list(project_dir.glob("*.csproj"))[0]
        
        cmd = [
            "dotnet", "build",
            str(csproj),
            "-c", configuration.capitalize()
        ]
        
        return self._run_command(cmd, project_dir)
    
    def run(self, project_dir: Path, device: Optional[str]) -> bool:
        """Run Windows app"""
        print("Running Windows application...")
        
        csproj = list(project_dir.glob("*.csproj"))[0]
        
        cmd = [
            "dotnet", "run",
            "--project", str(csproj)
        ]
        
        return self._run_command(cmd, project_dir)
    
    def test(self, project_dir: Path) -> bool:
        """Run Windows tests"""
        print("Running Windows tests...")
        
        test_proj = list(project_dir.glob("*.Tests/*.csproj"))[0]
        
        cmd = [
            "dotnet", "test",
            str(test_proj)
        ]
        
        return self._run_command(cmd, project_dir)
    
    def deploy(self, project_dir: Path, target: str) -> bool:
        """Deploy Windows app"""
        print(f"Deploying Windows app to {target}...")
        
        csproj = list(project_dir.glob("*.csproj"))[0]
        
        cmd = [
            "dotnet", "publish",
            str(csproj),
            "-c", "Release",
            "-r", "win-x64",
            "--self-contained"
        ]
        
        return self._run_command(cmd, project_dir)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List Windows devices (always just local machine)"""
        return [{'name': 'Local PC', 'type': 'physical'}]


class WebBuilder(PlatformBuilder):
    """Web platform builder with optimizations"""
    
    def _execute_build(self, config: BuildConfig, changed_files: List[Path]) -> BuildResult:
        """Execute web build with npm/webpack"""
        result = BuildResult(success=False, duration=0)
        
        # Validate project structure
        valid, missing = self._validate_project_structure(
            config.project_dir,
            ['package.json']
        )
        if not valid:
            result.errors.append("Invalid web project structure")
            return result
        
        # Install dependencies if needed
        node_modules = config.project_dir / "node_modules"
        package_lock = config.project_dir / "package-lock.json"
        
        if not node_modules.exists() or self.build_cache.has_changed(package_lock, config.cache_key()):
            print("📦 Installing dependencies...")
            success, _, stderr = self._run_command(["npm", "ci"], config.project_dir)
            if not success:
                # Try regular install if ci fails
                success, _, stderr = self._run_command(["npm", "install"], config.project_dir)
            
            if not success:
                result.errors.append("Failed to install dependencies")
                result.errors.append(stderr)
                return result
        
        # Determine build script
        script = "build" if config.configuration == "release" else "build:dev"
        
        # Check if script exists in package.json
        package_json = json.loads((config.project_dir / "package.json").read_text())
        scripts = package_json.get("scripts", {})
        
        if script not in scripts:
            # Fallback to default build script
            script = "build"
        
        if script not in scripts:
            result.errors.append(f"No build script found in package.json")
            return result
        
        # Build with npm
        build_args = ["npm", "run", script]
        
        if config.optimization_level == "aggressive":
            # Set NODE_ENV for production optimizations
            env = os.environ.copy()
            env['NODE_ENV'] = 'production'
        
        success, stdout, stderr = self._run_command(build_args, config.project_dir)
        
        result.success = success
        
        if not success:
            result.errors.append("Build failed")
            if stderr:
                result.errors.append(stderr)
        else:
            # Find build output
            dist_dirs = ['dist', 'build', 'out', 'public']
            for dist_dir in dist_dirs:
                dist_path = config.project_dir / dist_dir
                if dist_path.exists() and list(dist_path.iterdir()):
                    result.artifacts = [dist_path]
                    
                    # Calculate bundle size
                    total_size = sum(
                        f.stat().st_size 
                        for f in dist_path.rglob('*') 
                        if f.is_file()
                    )
                    size_mb = total_size / (1024 * 1024)
                    print(f"\n✓ Build output: {dist_path}")
                    print(f"  Total size: {size_mb:.2f} MB")
                    break
        
        # Parse warnings
        if stdout:
            for line in stdout.split('\n'):
                if 'warning' in line.lower():
                    result.warnings.append(line.strip())
        
        return result
    
    def _get_source_files(self, project_dir: Path) -> List[Path]:
        """Get web source files"""
        files = []
        patterns = ['*.js', '*.ts', '*.jsx', '*.tsx', '*.css', '*.scss', '*.html', '*.poh']
        src_dir = project_dir / "src"
        if src_dir.exists():
            for pattern in patterns:
                files.extend(src_dir.rglob(pattern))
        return files
    
    def run(self, project_dir: Path, device: Optional[str]) -> bool:
        """Run web dev server with better error handling"""
        print("Starting web development server...")
        
        # Install dependencies if needed
        if not (project_dir / "node_modules").exists():
            print("📦 Installing dependencies...")
            success, _, _ = self._run_command(["npm", "install"], project_dir)
            if not success:
                return False
        
        # Check for dev script
        package_json = json.loads((project_dir / "package.json").read_text())
        scripts = package_json.get("scripts", {})
        
        dev_script = None
        for script_name in ['dev', 'start', 'serve']:
            if script_name in scripts:
                dev_script = script_name
                break
        
        if not dev_script:
            print("⚠️  No dev server script found in package.json")
            print("Add a 'dev', 'start', or 'serve' script")
            return False
        
        print(f"\n✓ Starting server with 'npm run {dev_script}'")
        print("📝 Press Ctrl+C to stop\n")
        
        # Run in foreground (blocking)
        try:
            subprocess.run(
                ["npm", "run", dev_script],
                cwd=project_dir,
                check=False
            )
            return True
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")
            return True
        except Exception as e:
            print(f"Server error: {e}")
            return False
    
    def test(self, project_dir: Path) -> bool:
        """Run web tests"""
        print("Running web tests...")
        
        return self._run_command(["npm", "run", "test"], project_dir)
    
    def deploy(self, project_dir: Path, target: str) -> bool:
        """Deploy web app"""
        print(f"Deploying web app to {target}...")
        
        # Build production
        if not self.build(project_dir, "release"):
            return False
        
        print(f"Build artifacts ready in: {project_dir / 'dist'}")
        print(f"Deploy to {target} using your preferred method")
        
        return True
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List web browsers"""
        browsers = []
        
        if sys.platform == "win32":
            browsers = [
                {'name': 'Chrome', 'type': 'browser'},
                {'name': 'Edge', 'type': 'browser'},
                {'name': 'Firefox', 'type': 'browser'}
            ]
        elif sys.platform == "darwin":
            browsers = [
                {'name': 'Safari', 'type': 'browser'},
                {'name': 'Chrome', 'type': 'browser'},
                {'name': 'Firefox', 'type': 'browser'}
            ]
        else:
            browsers = [
                {'name': 'Chrome', 'type': 'browser'},
                {'name': 'Firefox', 'type': 'browser'}
            ]
        
        return browsers
