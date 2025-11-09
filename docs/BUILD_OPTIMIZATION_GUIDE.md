# PLHub Build Optimization Guide

## Overview

PLHub v0.7.0 introduces advanced build optimization features including:
- **Incremental Builds** - Only rebuild changed files
- **Build Caching** - Reuse previous build artifacts
- **Parallel Compilation** - Use multiple CPU cores
- **Dependency Validation** - Check requirements before building
- **Error Recovery** - Better error messages and handling

---

## Quick Start

### Basic Build
```bash
plhub platform build android --config debug
```

### Optimized Build
```bash
plhub platform build android \
  --config release \
  --optimization aggressive \
  --parallel \
  --cache
```

### Clean Build (No Cache)
```bash
plhub platform build android --no-cache --clean
```

---

## Build Configuration Options

### Configuration Levels

#### Debug
- Fast compilation
- No optimization
- Debug symbols included
- Larger binary size
```bash
plhub platform build android --config debug
```

#### Release
- Full optimization
- Dead code elimination
- Minification enabled
- Smaller binary size
```bash
plhub platform build android --config release
```

### Optimization Levels

#### Minimal
- Basic compilation only
- Fastest build time
- Largest output size
- Best for rapid iteration
```bash
plhub platform build android --optimization minimal
```

#### Standard (Default)
- Moderate optimization
- Build caching enabled
- Balanced speed/size
- Recommended for most cases
```bash
plhub platform build android --optimization standard
```

#### Aggressive
- Maximum optimization
- Parallel compilation
- Advanced caching
- Smallest output size
- Best for production builds
```bash
plhub platform build android --optimization aggressive
```

---

## Platform-Specific Optimizations

### Android

#### Gradle Optimization
```bash
# Enable parallel builds
plhub platform build android --parallel

# Use Gradle build cache
plhub platform build android --cache

# Configure in gradle.properties:
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configureondemand=true
org.gradle.daemon=true
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError
```

#### ProGuard/R8 Optimization
```gradle
// app/build.gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

#### APK Size Reduction
- Enable ProGuard/R8 minification
- Use vector drawables instead of PNGs
- Enable resource shrinking
- Split APKs by ABI
```gradle
android {
    splits {
        abi {
            enable true
            reset()
            include 'armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64'
            universalApk false
        }
    }
}
```

### iOS

#### Xcode Build Settings
```bash
# Release build with optimizations
plhub platform build ios --config release

# Optimize in Xcode:
# - Build Settings > Optimization Level > Fastest, Smallest [-Os]
# - Build Settings > Strip Debug Symbols > Yes
# - Build Settings > Dead Code Stripping > Yes
```

#### App Thinning
- Use asset catalogs
- Enable bitcode (for older apps)
- Use on-demand resources
- Leverage app slicing

### Web

#### Webpack/Vite Optimization
```bash
# Production build with minification
plhub platform build web --config release --optimization aggressive
```

```javascript
// vite.config.js
export default {
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['./src/utils']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
}
```

#### Bundle Size Analysis
```bash
npm run build -- --report
```

### Windows

#### .NET Optimization
```bash
# AOT compilation (Ahead of Time)
dotnet publish -c Release -r win-x64 --self-contained /p:PublishSingleFile=true /p:PublishTrimmed=true
```

```xml
<!-- .csproj optimizations -->
<PropertyGroup>
    <PublishTrimmed>true</PublishTrimmed>
    <PublishReadyToRun>true</PublishReadyToRun>
    <TieredCompilation>true</TieredCompilation>
    <InvariantGlobalization>true</InvariantGlobalization>
</PropertyGroup>
```

---

## Build Caching

### Cache Management

#### View Cache Stats
```bash
plhub platform cache-stats
```

#### Clear Cache
```bash
# Clear specific platform
plhub platform clean-cache android

# Clear all caches
plhub platform clean-cache --all
```

### Cache Location
- **Linux/macOS**: `~/.plhub/.build_cache/`
- **Windows**: `%USERPROFILE%\.plhub\.build_cache\`

### Cache Invalidation

Cache is automatically invalidated when:
- Source files change (detected by file hash)
- Build configuration changes
- Platform SDK version changes
- Dependencies are updated

---

## Incremental Builds

### How It Works
1. Calculate hash of all source files
2. Compare with previous build hashes
3. Only rebuild changed files and dependencies
4. Link with cached object files

### Enable Incremental Builds
```bash
plhub platform build android --incremental
```

### Disable for Clean Build
```bash
plhub platform build android --no-incremental --clean
```

---

## Parallel Compilation

### CPU Core Utilization

#### Auto-detect Cores (Default)
```bash
plhub platform build android --parallel
```

#### Specify Core Count
```bash
# Use 4 cores
plhub platform build android --parallel --jobs 4
```

#### Platform Configuration

**Android (Gradle)**:
```gradle
org.gradle.workers.max=4
```

**iOS (Xcode)**:
```bash
xcodebuild -jobs 4
```

**Web (Node.js)**:
```bash
export UV_THREADPOOL_SIZE=4
```

---

## Dependency Validation

### Check Dependencies
```bash
plhub platform check-deps android
```

### Sample Output
```
============================================================
Dependency Check: ANDROID
============================================================

✓ Android SDK [REQUIRED]
✓ Gradle [REQUIRED]
✓ Java JDK (11+) [REQUIRED]
✗ Android NDK [OPTIONAL]
   Install: Download from Android Studio SDK Manager

============================================================
✓ All required dependencies satisfied
============================================================
```

### Platform Requirements

#### Android
- ✓ Android SDK (required)
- ✓ Gradle (required)
- ✓ Java JDK 11+ (required)
- Android NDK (optional - for native code)

#### iOS
- ✓ Xcode (required - macOS only)
- ✓ Xcode Command Line Tools (required)
- CocoaPods (optional - for dependencies)

#### macOS
- ✓ Xcode (required - macOS only)

#### Windows
- ✓ .NET SDK 7.0+ (required)
- Visual Studio 2022 (optional - for IDE)

#### Web
- ✓ Node.js 16+ (required)
- ✓ npm (required - included with Node.js)

---

## Error Handling

### Common Build Errors

#### Missing Dependencies
```
ERROR: Command not found: gradle
Make sure gradle is installed and in your PATH

Solution:
1. Install Android Studio
2. Or download Gradle from https://gradle.org
3. Add to PATH environment variable
```

#### Insufficient Memory
```
ERROR: Java heap space
Out of memory error

Solution:
Add to gradle.properties:
org.gradle.jvmargs=-Xmx4g
```

#### Signing Errors (Android Release)
```
ERROR: No signing config found

Solution:
Add keystore configuration in app/build.gradle:
android {
    signingConfigs {
        release {
            storeFile file("keystore.jks")
            storePassword "password"
            keyAlias "key0"
            keyPassword "password"
        }
    }
}
```

#### Port Already in Use (Web)
```
ERROR: Port 8080 already in use

Solution:
1. Change port in package.json scripts
2. Or kill process: lsof -ti:8080 | xargs kill
```

### Error Recovery

PLHub automatically provides:
- Detailed error messages with context
- Suggestions for fixing common issues
- Links to relevant documentation
- Command history for debugging

---

## Performance Benchmarks

### Build Time Comparison

#### Android App (Medium Size)
| Build Type | Without Cache | With Cache | Speedup |
|------------|--------------|------------|---------|
| Clean      | 2m 30s       | 2m 30s     | 1.0x    |
| Incremental| 2m 30s       | 15s        | 10.0x   |
| No Changes | 2m 30s       | <1s        | 150x+   |

#### Web App (React)
| Build Type | Without Optimization | With Optimization | Size Reduction |
|------------|---------------------|-------------------|----------------|
| Debug      | 5.2 MB              | 5.2 MB            | -              |
| Release    | 5.2 MB              | 850 KB            | 83%            |

### Memory Usage

| Platform | Debug Build | Release Build | Peak Memory |
|----------|-------------|---------------|-------------|
| Android  | 2 GB        | 3 GB          | 4 GB        |
| iOS      | 1.5 GB      | 2.5 GB        | 3 GB        |
| Web      | 500 MB      | 800 MB        | 1 GB        |
| Windows  | 1 GB        | 1.5 GB        | 2 GB        |

---

## Best Practices

### Development Builds
1. Use `--config debug` for faster builds
2. Enable `--incremental` for repeated builds
3. Keep `--cache` enabled
4. Use `--optimization minimal` for fastest iteration

```bash
plhub platform build android \
  --config debug \
  --incremental \
  --cache \
  --optimization minimal
```

### Production Builds
1. Always use `--config release`
2. Use `--optimization aggressive`
3. Enable `--parallel` on multi-core systems
4. Clean cache before major releases

```bash
plhub platform build android \
  --config release \
  --optimization aggressive \
  --parallel \
  --clean
```

### Continuous Integration (CI)
1. Disable cache on CI (fresh builds)
2. Use parallel builds
3. Generate build artifacts
4. Run tests after build

```bash
# CI build script
plhub platform build android \
  --config release \
  --no-cache \
  --parallel \
  --jobs 8

plhub platform test android
```

---

## Monitoring & Profiling

### Build Statistics
```bash
# View build history
plhub platform build-history

# Output:
Build #1: android-release (2m 15s) ✓
Build #2: web-debug (45s) ✓
Build #3: ios-release (3m 30s) ✗
```

### Cache Statistics
```bash
plhub platform cache-stats

# Output:
Cache Directory: ~/.plhub/.build_cache
Total Size: 2.5 GB
Entries: 15
Platforms:
  - android: 1.2 GB (8 entries)
  - web: 800 MB (4 entries)
  - ios: 500 MB (3 entries)
```

### Build Profiling

#### Android (Gradle)
```bash
./gradlew assembleDebug --profile
# Report: build/reports/profile/
```

#### Web (Webpack)
```bash
npm run build -- --profile
```

#### iOS (Xcode)
```bash
xcodebuild -showBuildSettings
```

---

## Advanced Configuration

### Custom Build Scripts

Create `.plhub/build-config.json`:
```json
{
  "android": {
    "gradle_options": [
      "--parallel",
      "--build-cache",
      "--configure-on-demand"
    ],
    "optimization": "aggressive",
    "cache_enabled": true
  },
  "web": {
    "node_env": "production",
    "build_script": "build:optimized",
    "analyze_bundle": true
  }
}
```

### Build Hooks

Create `.plhub/hooks/pre-build.sh`:
```bash
#!/bin/bash
echo "Running pre-build tasks..."
# Clean old artifacts
rm -rf build/
# Update dependencies
npm update
```

Create `.plhub/hooks/post-build.sh`:
```bash
#!/bin/bash
echo "Running post-build tasks..."
# Upload to S3
aws s3 cp dist/ s3://my-bucket/
# Send notification
curl -X POST https://slack.com/webhook -d "Build complete"
```

---

## Troubleshooting

### Build Hangs

**Symptom**: Build process freezes
**Solution**:
1. Check for resource exhaustion (RAM, disk)
2. Disable parallel builds: `--no-parallel`
3. Increase timeout: `--timeout 1800`
4. Check for network issues (if downloading deps)

### Cache Corruption

**Symptom**: Build fails with strange errors after working previously
**Solution**:
```bash
plhub platform clean-cache --all
plhub platform build android --clean
```

### Slow Builds

**Symptom**: Builds take longer than expected
**Solution**:
1. Enable caching: `--cache`
2. Use incremental builds: `--incremental`
3. Enable parallel compilation: `--parallel`
4. Optimize dependencies (remove unused)
5. Use SSD for project files

### Disk Space Issues

**Symptom**: Build fails with "No space left on device"
**Solution**:
```bash
# Check cache size
plhub platform cache-stats

# Clean old caches
plhub platform clean-cache --all

# Clean platform-specific artifacts
plhub platform clean android
```

---

## Migration Guide

### From PLHub v0.6.x

**Old Command**:
```bash
plhub build apk --release
```

**New Command**:
```bash
plhub platform build android --config release
```

**Benefits**:
- ✓ 10x faster incremental builds
- ✓ Build caching enabled by default
- ✓ Better error messages
- ✓ Dependency validation
- ✓ Progress reporting

---

## See Also

- [Platform Manager API](./PLATFORM_MANAGER_API.md)
- [Cross-Platform Guide](./CROSS_PLATFORM_GUIDE.md)
- [CI/CD Integration](./CICD_INTEGRATION.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/AlhaqGH/PLHub/issues
- Documentation: https://plhub.dev/docs
- Discord: https://discord.gg/pohlang
