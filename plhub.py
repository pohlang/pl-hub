#!/usr/bin/env python3
"""
PL-Hub Main Entrypoint

The primary entry point for the PohLang development environment.
PLHub is to PohLang what Flutter is to Dart - a comprehensive development platform.

Usage:
    python plhub.py run <file.poh>           # Run a PohLang program
    python plhub.py create <project_name>    # Create new project
    python plhub.py install <package>        # Install package
    python plhub.py build                    # Build project
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse
import json
import shutil
import datetime
import logging
import platform
import hashlib
import zipfile
import io
from urllib.request import urlopen, Request
from typing import List, Optional

from tools.style_manager import StyleManager
from tools.widget_manager import WidgetManager
from tools.platform_manager import PlatformManager, Platform
from tools.hotreload_manager import HotReloadManager
from tools.test_manager import PohTestManager, PohTestType
from tools.device_manager import UnifiedDeviceManager
from tools.ui_helpers import UI, Icon, Color, Spinner, ProgressBar, confirm, select, input_text
from tools.command_helpers import (
    CommandContext, EnhancedRunner, BuildHelper, InstallHelper,
    PlatformHelper, InteractiveWizard, DebugHelper, ErrorHelper,
    handle_common_errors, suggest_similar_commands
)

def _load_dotenv(dotenv_path: Path) -> None:
    """Lightweight .env loader (KEY=VALUE pairs, no quotes)."""
    # Try python-dotenv if available
    try:
        from dotenv import load_dotenv as _load
        _load(dotenv_path)
        return
    except Exception:
        # Fall back to simple parser
        try:
            if dotenv_path.exists():
                for line in dotenv_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    os.environ.setdefault(k, v)
        except Exception:
            # Non-fatal
            pass


# Load .env if present
_load_dotenv(Path(__file__).parent / ".env")

# Note: PLHub now uses the Rust runtime exclusively.
# The Python interpreter (Interpreter module) is no longer required.
# All PohLang programs are executed via the Rust binary (pohlang.exe/pohlang).


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def find_project_root(start: Optional[Path] = None) -> Optional[Path]:
    """Return the nearest directory (walking upwards) containing plhub.json."""
    current = start or Path.cwd()
    for candidate in [current, *current.parents]:
        if (candidate / 'plhub.json').exists():
            return candidate
    return None


def read_pohlang_version(pohlang_repo: Path) -> tuple[str, str]:
    """Return (version, commit) for PohLang.

    - Prefer Interpreter/__init__.py __version__ (language version)
    - Fallback to pyproject.toml [project].version
    - Fallback to git rev-parse HEAD
    """
    version = None
    commit = None
    interp_init = pohlang_repo / 'Interpreter' / '__init__.py'
    pyproj = pohlang_repo / 'pyproject.toml'
    try:
        if interp_init.exists():
            text = interp_init.read_text(encoding='utf-8')
            for line in text.splitlines():
                if line.strip().startswith('__version__'):
                    version = line.split('=', 1)[1].strip().strip('"\'')
                    break
        if pyproj.exists():
            text = pyproj.read_text(encoding='utf-8')
            for line in text.splitlines():
                if line.strip().startswith('version'):  # naive parse
                    # line like: version = "0.1.0"
                    try:
                        version = line.split('=', 1)[1].strip().strip('"\'')
                        # Do not break if we already have interpreter version
                        if version and not version:
                            break
                    except Exception:
                        pass
        # git commit
        if (pohlang_repo / '.git').exists():
            res = subprocess.run(['git', '-C', str(pohlang_repo), '--no-pager', 'rev-parse', 'HEAD'],
                                 capture_output=True, text=True)
            if res.returncode == 0:
                commit = res.stdout.strip()
    except Exception:
        pass
    return version or 'unknown', commit or 'unknown'


def integrate_pohlang(pohlang_repo: Path, runtime_dir: Path) -> dict:
    """Copy the Interpreter, bin, and transpiler directories from PohLang into PLHub/Runtime.

    Returns metadata dict about the embedded interpreter.
    """
    interpreter_src = pohlang_repo / 'Interpreter'
    if not interpreter_src.exists():
        raise FileNotFoundError(f"PohLang Interpreter not found at {interpreter_src}")

    # Ensure runtime dir
    runtime_dir.mkdir(parents=True, exist_ok=True)

    # Copy Interpreter
    interpreter_dst = runtime_dir / 'Interpreter'
    if interpreter_dst.exists():
        shutil.rmtree(interpreter_dst)
    shutil.copytree(interpreter_src, interpreter_dst)

    # Copy Dart transpiler (optional but recommended)
    transpiler_src = pohlang_repo / 'transpiler'
    transpiler_dst = runtime_dir / 'transpiler'
    if transpiler_src.exists():
        if transpiler_dst.exists():
            shutil.rmtree(transpiler_dst)
        shutil.copytree(transpiler_src, transpiler_dst)

    # Copy Dart bin entrypoints so `dart run` works from Runtime
    bin_src = pohlang_repo / 'bin'
    bin_dst = runtime_dir / 'bin'
    if bin_src.exists():
        if bin_dst.exists():
            shutil.rmtree(bin_dst)
        shutil.copytree(bin_src, bin_dst)

    version, commit = read_pohlang_version(pohlang_repo)
    metadata = {
        'pohlang_version': version,
        'source_repo': 'https://github.com/AlhaqGH/PohLang',
        'source_commit': commit,
        'embedded_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    # Write metadata
    meta_file = runtime_dir / 'pohlang_metadata.json'
    try:
        with meta_file.open('w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        logging.warning(f"Failed to write metadata: {e}")

    return metadata


def run_plhub_tests(plhub_root: Path) -> None:
    """Run PL-Hub tests via pytest or unittest, raising on failure."""
    logging.info('Running PL-Hub tests...')
    tests_dir = plhub_root / 'Tests'
    if (plhub_root / '.venv').exists():
        python_exec = str((plhub_root / '.venv' / 'Scripts' / 'python.exe'))
        if not Path(python_exec).exists():
            python_exec = sys.executable
    else:
        python_exec = sys.executable

    # Prefer pytest if available
    try:
        res = subprocess.run([python_exec, '-m', 'pytest', str(tests_dir)], capture_output=True, text=True)
        if res.returncode == 0:
            logging.info('Tests passed (pytest).')
            return
        else:
            logging.warning('pytest failed, falling back to unittest.\n' + res.stdout + '\n' + res.stderr)
    except Exception:
        logging.info('pytest not available; using unittest discovery.')

    res = subprocess.run([python_exec, '-m', 'unittest', 'discover', '-s', str(tests_dir)], capture_output=True, text=True)
    if res.returncode != 0:
        logging.error(res.stdout)
        logging.error(res.stderr)
        raise RuntimeError('PL-Hub tests failed')
    logging.info('Tests passed (unittest).')


def build_plhub_distribution(plhub_root: Path) -> Path:
    """Build wheel/sdist for PL-Hub using setup.py. Returns dist directory path."""
    logging.info('Building PL-Hub distribution...')
    dist_dir = plhub_root / 'dist'
    if dist_dir.exists():
        for p in dist_dir.glob('*'):
            try:
                p.unlink()
            except Exception:
                pass
    # First try PEP 517 build if available
    res = subprocess.run([sys.executable, '-m', 'build', '--sdist', '--wheel'], cwd=str(plhub_root), capture_output=True, text=True)
    if res.returncode != 0:
        logging.warning('PEP 517 build failed, trying setup.py...')
        logging.debug(res.stdout)
        logging.debug(res.stderr)
        cmd = [sys.executable, 'setup.py', 'sdist', 'bdist_wheel']
        res = subprocess.run(cmd, cwd=str(plhub_root), capture_output=True, text=True)
        if res.returncode != 0:
            logging.error(res.stdout)
            logging.error(res.stderr)
            raise RuntimeError('Build failed')
    logging.info('Build completed.')
    return dist_dir


def git_tag_and_optionally_push(plhub_root: Path, tag_name: str, message: str, push: bool) -> bool:
    """Create a git tag and optionally push commit and tag.

    Returns True if tagging attempted (and likely succeeded), False if skipped.
    """
    # Verify git repo
    res = subprocess.run(['git', '-C', str(plhub_root), 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True)
    if res.returncode != 0 or 'true' not in res.stdout.lower():
        logging.warning('Git repository not detected; skipping tagging/push.')
        return False

    logging.info(f'Creating git tag {tag_name}...')
    # Add any changes (Runtime updates, metadata)
    subprocess.run(['git', '-C', str(plhub_root), 'add', '-A'], check=False)
    # Commit if there are staged changes
    res = subprocess.run(['git', '-C', str(plhub_root), 'diff', '--cached', '--quiet'])
    if res.returncode != 0:
        subprocess.run(['git', '-C', str(plhub_root), 'commit', '-m', message], check=False)
    # Create/replace tag
    subprocess.run(['git', '-C', str(plhub_root), 'tag', '-f', tag_name, '-m', message], check=False)
    if push:
        subprocess.run(['git', '-C', str(plhub_root), 'push'], check=False)
        subprocess.run(['git', '-C', str(plhub_root), 'push', '-f', 'origin', tag_name], check=False)
    return True


def checkout_pohlang_ref(pohlang_repo: Path, ref: Optional[str]) -> None:
    """Optionally checkout a specific ref in the PohLang repository."""
    if not ref:
        return
    # Ensure it's a git repo
    res = subprocess.run(['git', '-C', str(pohlang_repo), 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True)
    if res.returncode != 0:
        logging.warning('PohLang path is not a git repo; cannot checkout ref.')
        return
    if ref == 'latest-tag':
        subprocess.run(['git', '-C', str(pohlang_repo), 'fetch', '--tags'], check=False)
        res = subprocess.run(['git', '-C', str(pohlang_repo), 'describe', '--tags', '--abbrev=0'], capture_output=True, text=True)
        if res.returncode != 0:
            logging.warning('Could not determine latest tag; staying on current ref.')
            return
        ref = res.stdout.strip()
        logging.info(f'Checking out PohLang latest tag: {ref}')
    else:
        logging.info(f'Checking out PohLang ref: {ref}')
    subprocess.run(['git', '-C', str(pohlang_repo), 'checkout', ref], check=False)


def release_command(args) -> int:
    """Orchestrate pre-release integration, tests, build, and git tagging."""
    setup_logging()
    plhub_root = Path(__file__).parent
    pohlang_repo = Path(args.pohlang_path) if args.pohlang_path else plhub_root.parent / 'PohLang'
    runtime_dir = plhub_root / 'Runtime'
    runtime_dir.mkdir(exist_ok=True)

    logging.info('Starting PL-Hub release process...')
    logging.info(f'PohLang repo: {pohlang_repo}')
    logging.info(f'Runtime directory: {runtime_dir}')

    # 1) Integrate PohLang
    try:
        # Optionally switch PohLang repo to requested ref
        checkout_pohlang_ref(pohlang_repo, getattr(args, 'pohlang_ref', None))
        # Warn if uncommitted changes exist in PohLang repo
        res = subprocess.run(['git', '-C', str(pohlang_repo), 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True)
        if res.returncode == 0 and 'true' in res.stdout.lower():
            dirty = subprocess.run(['git', '-C', str(pohlang_repo), 'status', '--porcelain'], capture_output=True, text=True)
            if dirty.stdout.strip():
                logging.warning('PohLang repository has uncommitted changes; integrating a dirty state.')
        metadata = integrate_pohlang(pohlang_repo, runtime_dir)
        logging.info(f"Integrated PohLang interpreter version {metadata.get('pohlang_version')} (commit {metadata.get('source_commit')}).")
    except Exception as e:
        logging.error(f'Integration failed: {e}')
        return 1

    # 2) Run tests
    if not args.skip_tests:
        try:
            run_plhub_tests(plhub_root)
        except Exception as e:
            logging.error(f'Tests failed: {e}')
            return 1
    else:
        logging.info('Skipping tests as requested.')

    # Stop here if dry run
    if getattr(args, 'dry_run', False):
        logging.info('Dry run completed successfully. Integration and tests passed.')
        return 0

    # 3) Build packages
    try:
        dist_dir = build_plhub_distribution(plhub_root)
        built = sorted(dist_dir.glob('*'))
        for p in built:
            logging.info(f'Built artifact: {p.name}')
    except Exception as e:
        logging.error(f'Build failed: {e}')
        return 1

    # 4) Tag release
    # Determine PLHub version from setup.py
    plhub_version = '0.0.0'
    try:
        setup_text = (plhub_root / 'setup.py').read_text(encoding='utf-8')
        for line in setup_text.splitlines():
            if 'version=' in line and 'setup(' not in line and 'version' in line:
                # naive extraction version="2.0.0",
                parts = line.split('version')[-1]
                q1 = parts.find('"')
                q2 = parts.find('"', q1+1)
                if q1 != -1 and q2 != -1:
                    plhub_version = parts[q1+1:q2]
                    break
    except Exception:
        pass

    poh_version = (metadata.get('pohlang_version') or 'unknown')
    # Tag format: plhub-vX.Y.Z (requirement)
    default_tag = f"plhub-v{plhub_version}"
    tag_name = args.tag or default_tag
    tag_message = f"PL-Hub {plhub_version} including PohLang {poh_version}"

    try:
        attempted = git_tag_and_optionally_push(plhub_root, tag_name, tag_message, push=not args.no_push)
        if attempted:
            logging.info(f'Release tagged as {tag_name}.')
        else:
            logging.info('Tagging skipped (no git repository detected).')
    except Exception as e:
        logging.error(f'Git tagging failed: {e}')
        return 1

    logging.info('Release process completed successfully.')
    return 0

def main():
    """Main entry point for PL-Hub."""
    parser = argparse.ArgumentParser(
        description="PL-Hub: PohLang Development Environment",
        prog="plhub",
        epilog="Examples:\n"
               "  python plhub.py run Examples/hello_world.poh\n"
               "  python plhub.py create my_project\n"
               "  python plhub.py doctor                    # Check environment health\n"
               "  python plhub.py --help\n"
               "  python plhub.py --version",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='PL-Hub v0.7.0 - Enterprise-grade UI Framework with Comprehensive Tooling'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a PohLang program')
    run_parser.add_argument('file', help='PohLang file to run (.poh extension)')
    run_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    run_parser.add_argument('--debug', action='store_true', help='Enable debug tracing')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new PohLang project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('--template', default='basic', help='Project template (basic, console, web)')
    create_parser.add_argument('--no-ui', action='store_true', help='Skip generating UI scaffolding (styles/widgets)')
    create_parser.add_argument('--ui-theme', default='default_light', help='Default UI theme to apply when scaffolding (ignored with --no-ui)')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a PohLang package')
    install_parser.add_argument('package', help='Package name to install')
    
    # Build command - support both old and new syntax
    build_parser = subparsers.add_parser('build', help='Build the current project')
    build_parser.add_argument('target', nargs='?', default='bytecode',
                            choices=['python', 'dart', 'native', 'bytecode', 'apk', 'ipa', 'exe', 'app', 'dmg', 'web', 'android', 'ios', 'windows', 'macos', 'linux'],
                            help='Build target: apk (Android), ipa (iOS), exe (Windows), app (macOS), web, or bytecode/dart/native')
    build_parser.add_argument('--release', action='store_true', help='Build in release mode (optimized)')
    build_parser.add_argument('--debug', action='store_true', help='Build in debug mode (with debug info)')
    build_parser.add_argument('--out', default=None, help='Output path for artifacts')
    build_parser.add_argument('--platform', default=None, help='Platform-specific build options')
    # Legacy support
    build_parser.add_argument('--target', dest='legacy_target', default=None, help='(Legacy) Build target')
    
    # Transpile command
    transpile_parser = subparsers.add_parser('transpile', help='Transpile a .poh file to another target')
    transpile_parser.add_argument('file', help='PohLang file to transpile (.poh)')
    transpile_parser.add_argument('--to', default='dart', choices=['dart'], help='Transpile target (currently only dart)')
    transpile_parser.add_argument('--out-dir', default='build', help='Output directory (for transpiled code)')

    # List command
    list_parser = subparsers.add_parser('list', help='List available items')
    list_parser.add_argument('type', choices=['examples', 'templates', 'packages'], help='What to list')

    # Style command
    style_parser = subparsers.add_parser('style', help='Manage project styles and themes')
    style_parser.add_argument('--project-root', dest='project_root', default=None, help='Optional path to a project directory (defaults to current working tree)')
    style_subparsers = style_parser.add_subparsers(dest='style_command', required=True)

    style_list_parser = style_subparsers.add_parser('list', help='List available styles')
    style_list_parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON summary')

    style_show_parser = style_subparsers.add_parser('show', help='Show style metadata and tokens')
    style_show_parser.add_argument('style', help='Style identifier (name, key, or filename)')
    style_show_parser.add_argument('--json', action='store_true', help='Emit raw JSON for the selected style')

    style_apply_parser = style_subparsers.add_parser('apply', help='Activate a style for the current project')
    style_apply_parser.add_argument('style', help='Style identifier to apply (see list)')
    style_apply_parser.add_argument('--force', action='store_true', help='Overwrite existing theme files if they already exist')

    style_create_parser = style_subparsers.add_parser('create', help='Create a new editable project style')
    style_create_parser.add_argument('name', help='Human-friendly name for the new style')
    style_create_parser.add_argument('--base', default=None, help='Existing style to clone (default: default_light)')
    style_create_parser.add_argument('--description', default=None, help='Optional description for the new style')
    style_create_parser.add_argument('--force', action='store_true', help='Overwrite if the destination theme already exists')
    style_create_parser.add_argument('--activate', action='store_true', help='Activate the new style after creation')

    # Widget command
    widget_parser = subparsers.add_parser('widget', help='Scaffold and manage reusable widgets')
    widget_parser.add_argument('--project-root', dest='project_root', default=None, help='Optional path to a project directory (defaults to current working tree)')
    widget_subparsers = widget_parser.add_subparsers(dest='widget_command', required=True)

    widget_list_parser = widget_subparsers.add_parser('list', help='List available widget templates and project widgets')
    widget_list_parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON summary')

    widget_preview_parser = widget_subparsers.add_parser('preview', help='Preview a widget template before generating it')
    widget_preview_parser.add_argument('template', help='Widget template identifier')
    widget_preview_parser.add_argument('--json', action='store_true', help='Emit preview metadata as JSON')

    widget_generate_parser = widget_subparsers.add_parser('generate', help='Generate widget files in the current project')
    widget_generate_parser.add_argument('template', help='Widget template identifier to instantiate')
    widget_generate_parser.add_argument('--name', default=None, help='Customize the widget name used for placeholders and filenames')
    widget_generate_parser.add_argument('--force', action='store_true', help='Overwrite files if they already exist')
    widget_generate_parser.add_argument('--dry-run', action='store_true', help='Show files that would be created without writing them')
    
    # Release command
    release_parser = subparsers.add_parser('release', help='Run PL-Hub release automation')
    release_parser.add_argument('--dry-run', action='store_true', help='Run integration and tests without building or tagging')
    release_parser.add_argument('--no-push', action='store_true', help='Do not push git tags/commits')
    release_parser.add_argument('--tag', default=None, help='Override git tag name (default: v<plhub_version>-poh<version>)')
    release_parser.add_argument('--pohlang-path', default=None, help='Path to PohLang repo to integrate (defaults to sibling PohLang/)')
    release_parser.add_argument('--skip-tests', action='store_true', help='Skip running PL-Hub tests')
    release_parser.add_argument('--pohlang-ref', default='latest-tag', help="Git ref in PohLang to checkout before integration (default: latest-tag; e.g., 'v0.1.0', 'main')")

    # Update-runtime command
    up_parser = subparsers.add_parser('update-runtime', help='Fetch PohLang SDK runtime and install into PL-Hub/bin')
    up_parser.add_argument('--version', default='latest', help="PohLang version to fetch (e.g., 0.5.0) or 'latest'")
    up_parser.add_argument('--validate', action='store_true', help='Validate SHA256 checksum if available (informational)')
    up_parser.add_argument('--zip-url', default=None, help='Override: direct URL to PohLang SDK zip')
    up_parser.add_argument('--sha256', default=None, help='Expected SHA256 of the SDK zip (optional; fail if mismatch)')
    up_parser.add_argument('--os', dest='os', choices=['linux', 'windows', 'macos'], help='Override OS (testing/CI)')
    up_parser.add_argument('--dry-run', action='store_true', help='Download only, do not install')
    up_parser.add_argument('--verbose', action='store_true', help='Verbose output')

    # Sync local Rust build into bin
    sync_parser = subparsers.add_parser('sync-runtime-local', help='Copy local Rust build (pohlang) into PL-Hub/Runtime/bin')
    sync_parser.add_argument('--profile', default='debug', choices=['debug', 'release'], help='Cargo profile to use')
    sync_parser.add_argument('--pohlang-path', default=None, help='Path to PohLang repo (defaults to sibling PohLang/)')

    # Doctor command - environment health check
    doctor_parser = subparsers.add_parser('doctor', help='Check PLHub environment health and configuration')
    doctor_parser.add_argument('--verbose', action='store_true', help='Show detailed diagnostics')

    # Init command - initialize PLHub in current directory
    init_parser = subparsers.add_parser('init', help='Initialize PLHub configuration in current directory')
    init_parser.add_argument('--name', default=None, help='Project name (defaults to directory name)')
    init_parser.add_argument('--force', action='store_true', help='Overwrite existing configuration')

    # Test command - run project tests
    test_parser = subparsers.add_parser('test', help='Run tests in the current project')
    test_parser.add_argument('--filter', default=None, help='Run only tests matching pattern')
    test_parser.add_argument('--verbose', action='store_true', help='Show detailed test output')
    test_parser.add_argument('--watch', action='store_true', help='Watch for changes and re-run tests')
    test_parser.add_argument('--ci', action='store_true', help='Generate CI-friendly report')
    test_parser.add_argument('--ci-format', default='github', choices=['github', 'junit'], help='CI report format')
    test_parser.add_argument('--ci-output', default=None, help='Save CI report to file')

    # Clean command - clean build artifacts
    clean_parser = subparsers.add_parser('clean', help='Clean build artifacts and caches')
    clean_parser.add_argument('--all', action='store_true', help='Also remove downloaded dependencies')

    # Watch command - watch and rebuild automatically
    watch_parser = subparsers.add_parser('watch', help='Watch for changes and rebuild automatically')
    watch_parser.add_argument('--verbose', action='store_true', help='Show detailed build output')

    # Dev command - development server with hot reload
    dev_parser = subparsers.add_parser('dev', help='Start development server with hot reload')
    dev_parser.add_argument('--file', default=None, help='Entry file to run (default: src/main.poh)')
    dev_parser.add_argument('--verbose', action='store_true', help='Show detailed output')

    # Debug command - debug session with breakpoints
    debug_parser = subparsers.add_parser('debug', help='Start debug session')
    debug_parser.add_argument('--file', default=None, help='Entry file to debug (default: src/main.poh)')
    debug_parser.add_argument('--port', type=int, default=5858, help='Debug server port')
    debug_parser.add_argument('--verbose', action='store_true', help='Show detailed output')

    # Platform command - cross-platform development
    platform_parser = subparsers.add_parser('platform', help='Manage cross-platform development (Android, iOS, macOS, Windows, Web)')
    platform_subparsers = platform_parser.add_subparsers(dest='platform_command', required=True)
    
    # Platform create
    platform_create_parser = platform_subparsers.add_parser('create', help='Create new platform project')
    platform_create_parser.add_argument('platform', choices=['android', 'ios', 'macos', 'windows', 'web'], 
                                       help='Target platform')
    platform_create_parser.add_argument('name', help='Project name')
    platform_create_parser.add_argument('--package', default=None, help='Package name (e.g., com.example.app)')
    platform_create_parser.add_argument('--output', default=None, help='Output directory')
    
    # Platform build
    platform_build_parser = platform_subparsers.add_parser('build', help='Build platform project')
    platform_build_parser.add_argument('platform', choices=['android', 'ios', 'macos', 'windows', 'web'], 
                                      help='Target platform')
    platform_build_parser.add_argument('--config', default='debug', choices=['debug', 'release'], 
                                      help='Build configuration')
    platform_build_parser.add_argument('--project-dir', default=None, help='Project directory')
    
    # Platform run
    platform_run_parser = platform_subparsers.add_parser('run', help='Run platform project')
    platform_run_parser.add_argument('platform', choices=['android', 'ios', 'macos', 'windows', 'web'], 
                                    help='Target platform')
    platform_run_parser.add_argument('--device', default=None, help='Target device ID or name')
    platform_run_parser.add_argument('--project-dir', default=None, help='Project directory')
    platform_run_parser.add_argument('--hot-reload', action='store_true', help='Enable hot reload')
    
    # Platform test
    platform_test_parser = platform_subparsers.add_parser('test', help='Run platform tests')
    platform_test_parser.add_argument('platform', choices=['android', 'ios', 'macos', 'windows', 'web'], 
                                     help='Target platform')
    platform_test_parser.add_argument('--type', default='unit', choices=['unit', 'integration', 'ui', 'e2e'], 
                                     help='Test type')
    platform_test_parser.add_argument('--pattern', default=None, help='Test pattern filter')
    platform_test_parser.add_argument('--project-dir', default=None, help='Project directory')
    
    # Platform deploy
    platform_deploy_parser = platform_subparsers.add_parser('deploy', help='Deploy platform project')
    platform_deploy_parser.add_argument('platform', choices=['android', 'ios', 'macos', 'windows', 'web'], 
                                       help='Target platform')
    platform_deploy_parser.add_argument('target', help='Deployment target (e.g., store, device, server)')
    platform_deploy_parser.add_argument('--project-dir', default=None, help='Project directory')
    
    # Platform devices
    platform_devices_parser = platform_subparsers.add_parser('devices', help='List available devices')
    platform_devices_parser.add_argument('--platform', default=None, 
                                        choices=['android', 'ios', 'macos', 'windows', 'web'],
                                        help='Filter by platform (default: all)')
    
    # Platform launch
    platform_launch_parser = platform_subparsers.add_parser('launch', help='Launch emulator/simulator')
    platform_launch_parser.add_argument('platform', choices=['android', 'ios', 'macos', 'windows', 'web'], 
                                       help='Target platform')
    platform_launch_parser.add_argument('device', help='Device/emulator name to launch')

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == 'run':
        return run_program(args)
    elif args.command == 'create':
        return create_project(args)
    elif args.command == 'install':
        return install_package(args)
    elif args.command == 'build':
        return build_project(args)
    elif args.command == 'transpile':
        return transpile_file(args)
    elif args.command == 'list':
        return list_items(args)
    elif args.command == 'style':
        return style_command(args)
    elif args.command == 'widget':
        return widget_command(args)
    elif args.command == 'platform':
        return platform_command(args)
    elif args.command == 'update-runtime':
        return update_runtime_command(args)
    elif args.command == 'release':
        return release_command(args)
    elif args.command == 'sync-runtime-local':
        return sync_runtime_local(args)
    elif args.command == 'doctor':
        return doctor_command(args)
    elif args.command == 'init':
        return init_command(args)
    elif args.command == 'test':
        return test_command(args)
    elif args.command == 'clean':
        return clean_command(args)
    elif args.command == 'watch':
        return watch_command(args)
    elif args.command == 'dev':
        return dev_command(args)
    elif args.command == 'debug':
        return debug_command(args)
    
    return 0


def _find_pohlangc() -> Optional[str]:
    """Locate the Rust pohlang binary shipped in PLHub/Runtime/bin or on PATH."""
    root = Path(__file__).parent
    candidates = []
    exe = 'pohlang.exe' if platform.system().lower().startswith('win') else 'pohlang'
    # Check PLHub/Runtime/bin first
    candidates.append(root / 'Runtime' / 'bin' / exe)
    # Check PLHub/bin (legacy)
    candidates.append(root / 'bin' / exe)
    # PATH search
    for p in os.environ.get('PATH', '').split(os.pathsep):
        cand = Path(p) / exe
        if cand.exists():
            candidates.append(cand)
    for c in candidates:
        if Path(c).exists():
            return str(c)
    return None


@handle_common_errors
def run_program(args):
    """Run a PohLang program using the Rust runtime."""
    file_path = Path(args.file)
    
    with CommandContext(f"Run {file_path.name}") as ctx:
        # Validate file exists
        if not EnhancedRunner.verify_file_exists(file_path, "PohLang script"):
            return 1
        
        # Validate file extension
        if not file_path.suffix == '.poh':
            UI.warning(f"File does not have .poh extension: {file_path}")
            if not confirm("Proceed anyway?", default=True):
                return 1
        
        UI.info(f"Running: {file_path}")
        if args.debug:
            UI.info("Debug mode enabled")
        
        # Use Rust runtime (required)
        pohlangc = _find_pohlangc()
        if not pohlangc:
            UI.error("PohLang Rust runtime not found!")
            UI.tip("Make sure PohLang is installed:")
            UI.tip("  1. Install from: https://github.com/AlhaqGH/PohLang")
            UI.tip("  2. Or run: plhub sync-runtime-local")
            UI.tip("  3. Runtime should be at: Runtime/bin/pohlang(.exe)")
            return 1
        
        try:
            cmd = [pohlangc, '--run', str(file_path)]
            if args.verbose:
                UI.command(' '.join(cmd))
            
            UI.divider()
            result = subprocess.run(cmd)
            UI.divider()
            
            if result.returncode == 0:
                UI.success("Program executed successfully")
                ctx.set_success()
            else:
                UI.error(f"Program exited with code {result.returncode}")
            
            return result.returncode
        except Exception as e:
            UI.error(f"Runtime error: {e}")
            UI.tip("Make sure the Rust runtime is properly installed")
            return 1


def create_project(args):
    """Create a new PohLang project with automated structure."""
    from tools.project_structure import ProjectStructure, ProjectStructureGenerator
    
    project_name = args.name
    template = args.template
    plhub_root = Path(__file__).parent
    
    project_dir = Path.cwd() / project_name
    
    if project_dir.exists():
        print(f"Error: Directory '{project_name}' already exists.")
        return 1
    
    print(f"Creating PohLang project '{project_name}' with template '{template}'...")
    print(f"Using PLHub v0.5.1 automated project structure...")
    
    # Create project structure using automation
    try:
        # Select template creation method
        if template == "basic":
            structure = ProjectStructure.create_basic(project_name)
        elif template == "console":
            structure = ProjectStructure.create_console_app(project_name)
        elif template == "web":
            structure = ProjectStructure.create_web_app(project_name)
        elif template == "library":
            structure = ProjectStructure.create_library(project_name)
        else:
            # Fallback to basic
            print(f"Warning: Unknown template '{template}', using 'basic'")
            structure = ProjectStructure.create_basic(project_name)
        
        # Generate project files
        ProjectStructureGenerator.generate(project_dir, structure, plhub_root)
        
        # Add UI styling if requested
        ui_messages: List[str] = []
        if not getattr(args, 'no_ui', False):
            try:
                manifest = StyleManager.bootstrap_project(
                    plhub_root,
                    project_dir,
                    default_style=getattr(args, 'ui_theme', 'default_light'),
                )
                ui_messages.append(
                    f"🎨 UI styling initialized with theme '{manifest.get('displayName', manifest.get('activeTheme'))}'."
                )
            except Exception as exc:  # noqa: BLE001
                ui_messages.append(f"⚠️  UI styling setup encountered an issue: {exc}")

            try:
                widget_info = WidgetManager.bootstrap_project(
                    plhub_root,
                    project_dir,
                    default_template='card',
                    widget_name='WelcomeCard',
                )
                generated = widget_info.get('files') or []
                if generated:
                    ui_messages.append(
                        "🧩 UI widget scaffolding added: " + ", ".join(generated)
                    )
                elif widget_info.get('error'):
                    ui_messages.append(f"⚠️  Widget scaffolding warning: {widget_info['error']}")
            except Exception as exc:  # noqa: BLE001
                ui_messages.append(f"⚠️  Widget scaffolding encountered an issue: {exc}")
        
        # Copy VS Code configuration files
        vscode_dir = project_dir / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        vscode_templates_dir = plhub_root / "templates" / "vscode"
        if vscode_templates_dir.exists():
            try:
                tasks_template = vscode_templates_dir / "tasks.json"
                launch_template = vscode_templates_dir / "launch.json"
                
                if tasks_template.exists():
                    shutil.copy2(tasks_template, vscode_dir / "tasks.json")
                    ui_messages.append("🔧 VS Code tasks.json created")
                
                if launch_template.exists():
                    shutil.copy2(launch_template, vscode_dir / "launch.json")
                    ui_messages.append("🐛 VS Code launch.json created")
            except Exception as e:
                ui_messages.append(f"⚠️  VS Code config warning: {e}")
        
        print(f"✅ Project '{project_name}' created successfully with '{template}' template!")
        print(f"📁 Location: {project_dir}")
        print(f"� Structure: {len(structure.directories)} directories, {len(structure.files)} files")
        print(f"�🚀 To run: cd {project_name} && python -m plhub run {structure.config['main']}")
        if ui_messages:
            for line in ui_messages:
                print(line)
        elif getattr(args, 'no_ui', False):
            print("ℹ️  UI scaffolding skipped (--no-ui). You can enable styling later with 'plhub style apply'.")
    
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        # Clean up partial project if it exists
        if project_dir.exists():
            shutil.rmtree(project_dir, ignore_errors=True)
        return 1
    
    return 0


@handle_common_errors
def install_package(args):
    """Install a PohLang package with enhanced feedback."""
    package_name = args.package
    
    with CommandContext(f"Install {package_name}") as ctx:
        # Check if we're in a project directory
        if not Path("plhub.json").exists():
            UI.error("Not in a PohLang project directory")
            UI.tip("Run 'plhub create <project_name>' to create a new project")
            UI.tip("Or run 'plhub init' to initialize current directory")
            return 1
        
        UI.info(f"Installing {package_name}")
        
        # Load project config
        UI.step("Loading project configuration")
        with open("plhub.json", "r") as f:
            config = json.load(f)
        
        # For now, just add to dependencies
        # In future, this would integrate with package registry
        UI.step("Resolving package")
        
        # Simulate package resolution
        with Spinner(f"Looking up {package_name}..."):
            time.sleep(0.5)
        
        version = "^1.0.0"  # Default version
        UI.success(f"Resolved {package_name}@{version}")
        
        # Add to dependencies
        UI.step("Updating project configuration")
        config["dependencies"][package_name] = version
        
        # Save updated config
        with open("plhub.json", "w") as f:
            json.dump(config, f, indent=2)
        
        UI.success(f"{package_name} added to dependencies")
        
        # Show dependency summary
        UI.section(f"{Icon.PACKAGE} Dependencies")
        for name, ver in config["dependencies"].items():
            marker = "← new" if name == package_name else ""
            UI.bullet(f"{name} {ver} {Color.GREEN}{marker}{Color.RESET}")
        
        UI.tip(f"Run 'plhub list packages' to see all installed packages")
        
        ctx.set_success()
        return 0


def build_project(args):
    """Build the current project."""
    project_root = find_project_root()
    if not project_root:
        print("Error: Not in a PohLang project directory.")
        return 1
    
    # Handle target mapping (new short syntax to full target names)
    target = args.target
    
    # Support legacy --target flag
    if args.legacy_target:
        target = args.legacy_target
    
    # Map short names to full target names
    target_map = {
        'apk': 'android',
        'ipa': 'ios',
        'exe': 'windows',
        'app': 'macos',
        'dmg': 'macos',
    }
    
    target = target_map.get(target, target)
    build_mode = "release" if getattr(args, 'release', False) else ("debug" if getattr(args, 'debug', False) else "default")
    
    # Handle platform-specific builds
    if target in ['android', 'ios', 'windows', 'macos', 'linux', 'web']:
        plhub_root = Path(__file__).parent
        
        is_release = getattr(args, 'release', False)
        output_path = Path(args.out) if args.out else None
        
        # Use enhanced Android APK builder for android target
        if target == 'android':
            from tools.android_apk_builder import AndroidAPKBuilder
            builder = AndroidAPKBuilder(project_root, plhub_root)
            return 0 if builder.build_apk(is_release, output_path) else 1
        
        # Use platform builder for other platforms
        from tools.platform_builder import BuildManager
        builder = BuildManager(project_root, plhub_root)
        
        if target == 'ios':
            return 0 if builder.build_ios(is_release, output_path) else 1
        elif target in ['windows', 'macos', 'linux']:
            return 0 if builder.build_desktop(target, is_release, output_path) else 1
        elif target == 'web':
            return 0 if builder.build_web(output_path) else 1
    
    mode_str = f" ({build_mode})" if build_mode != "default" else ""
    print(f"Building project for target: {target}{mode_str}")
    
    with open(project_root / "plhub.json", "r") as f:
        config = json.load(f)
    
    main_file = project_root / config.get("main", "src/main.poh")
    
    if not main_file.exists():
        print(f"Error: Main file '{main_file}' not found.")
        return 1
    
    if target == "native":
        # Use Rust pohlang AOT (currently unimplemented); for now compile to bytecode and package with runner instruction.
        pohlang_bin = _find_pohlangc()
        if not pohlang_bin:
            print("Error: Rust runtime not found. Run 'python plhub.py update-runtime' first.")
            return 1
        out = args.out or str(Path('build') / (Path(main_file).stem + ('.exe' if platform.system().lower().startswith('win') else '')))
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        print("Note: AOT is not yet implemented; generating bytecode instead.")
        bc_out = str(Path(out).with_suffix('.pbc'))
        res = subprocess.run([pohlang_bin, '--compile', main_file, '-o', bc_out])
        if res.returncode != 0:
            return res.returncode
        print(f"✅ Bytecode written to {bc_out}. AOT packaging will be added later.")
        return 0
    elif target == "bytecode":
        pohlang_bin = _find_pohlangc()
        if not pohlang_bin:
            print("Error: Rust runtime not found. Run 'python plhub.py update-runtime' first.")
            return 1
        out = args.out or str(Path('build') / (Path(main_file).stem + '.pbc'))
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        res = subprocess.run([pohlang_bin, '--compile', main_file, '-o', out])
        return res.returncode
    elif target == "dart":
        print("Building Dart transpilation...")
        try:
            # Prefer bundled transpiler
            bundled_dart = RUNTIME_DIR / "bin" / "pohlang.dart"
            sibling_dart = (Path(__file__).parent.parent / "PohLang" / "bin" / "pohlang.dart")
            transpiler_path = None
            if bundled_dart.exists():
                transpiler_path = bundled_dart
            elif sibling_dart.exists():
                transpiler_path = sibling_dart
            else:
                # As a last resort, try installed dart package via simple name
                transpiler_path = None

            if transpiler_path is not None:
                result = subprocess.run([
                    "dart", "run", str(transpiler_path),
                    main_file, "--no-run"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Dart build completed successfully!")
                else:
                    print(f"❌ Dart build failed:\n{result.stdout}\n{result.stderr}")
                    return 1
            else:
                print("Warning: Dart transpiler entrypoint not found. Using Python interpreter instead.")
                return run_with_python(main_file)
        except FileNotFoundError:
            print("Error: 'dart' command not found. Please install Dart SDK or use --target python.")
            return 1
        except Exception as e:
            print(f"Error during Dart build: {e}")
            return 1
    else:  # python
        return run_with_python(main_file)
    
    return 0


def list_items(args):
    """List available items."""
    item_type = args.type
    
    if item_type == 'examples':
        examples_dir = Path(__file__).parent / "Examples"
        if examples_dir.exists():
            print("Available example programs:")
            for example in sorted(examples_dir.glob("*.poh")):
                print(f"  - {example.name}")
        else:
            print("No examples found.")
    
    elif item_type == 'templates':
        print("Available project templates:")
        print("  - basic: Simple console application")
        print("  - console: Advanced console application with input/output")
        print("  - web: Web application template (experimental)")
    
    elif item_type == 'packages':
        if Path("plhub.json").exists():
            with open("plhub.json", "r") as f:
                config = json.load(f)
            
            print("Installed packages:")
            deps = config.get("dependencies", {})
            if deps:
                for name, version in deps.items():
                    print(f"  - {name}: {version}")
            else:
                print("  No packages installed.")
        else:
            print("Not in a PohLang project directory.")
    
    return 0


def style_command(args):
    """Handle style management subcommands."""
    plhub_root = Path(__file__).parent
    project_override = getattr(args, 'project_root', None)
    project_root: Optional[Path]
    if project_override:
        project_root = Path(project_override).expanduser().resolve()
        if not (project_root / 'plhub.json').exists():
            print(f"Error: Provided project directory '{project_root}' does not contain plhub.json.")
            return 1
    else:
        project_root = find_project_root()

    action = getattr(args, 'style_command', None)
    manager = StyleManager(plhub_root, project_root)

    if action == 'list':
        summary = manager.export_summary()
        if getattr(args, 'json', False):
            print(json.dumps(summary, indent=2))
            return 0

        builtin = summary.get('builtin', [])
        project_styles = summary.get('project', [])
        manifest = summary.get('active')
        resolved = summary.get('activeResolved')

        if builtin:
            print('Built-in themes:')
            for item in builtin:
                desc = f" - {item['description']}" if item.get('description') else ''
                print(f"  - {item['key']}: {item['name']}{desc}")
        else:
            print('No built-in themes available.')

        if project_root:
            if project_styles:
                print('\nProject themes:')
                for item in project_styles:
                    desc = f" - {item['description']}" if item.get('description') else ''
                    try:
                        rel_path = Path(item['path']).resolve().relative_to(project_root)
                    except ValueError:
                        rel_path = Path(item['path']).name
                    print(f"  - {item['key']}: {item['name']} ({rel_path}){desc}")
            else:
                print('\nNo project themes found. Use `plhub style create` to add one.')
        else:
            print('\nNote: No project detected. Listing built-in themes only. Run this command from a project directory for project-specific themes.')

        if manifest:
            if resolved:
                print(f"\nActive theme: {resolved['name']} ({resolved['key']})")
            else:
                print("\nActive theme manifest found, but the referenced theme file is missing.")
        else:
            print('\nActive theme: none')

        return 0

    if action == 'show':
        try:
            record = manager.resolve(args.style)
        except KeyError as exc:
            print(str(exc))
            return 1
        if args.json:
            print(json.dumps(record.data, indent=2))
        else:
            print(f"Name: {record.name}")
            print(f"Key: {record.key}")
            print(f"Source: {record.source}")
            print(f"Location: {record.path}")
            if record.description:
                print(f"Description: {record.description}")
            tokens = record.data.get('tokens', {})
            print(f"Token groups: {', '.join(tokens.keys()) or 'none'}")
        return 0

    if action == 'apply':
        if not project_root:
            print('Error: Style application must be run inside a PohLang project (plhub.json not found).')
            return 1
        try:
            manifest = manager.apply(args.style, force=getattr(args, 'force', False))
        except (RuntimeError, KeyError, FileExistsError) as exc:
            print(f"Error: {exc}")
            return 1
        print(f"✅ Applied style '{manifest['displayName']}' ({manifest['activeTheme']}).")
        print(f"   Theme file: ui/styles/{manifest['themePath']}")
        return 0

    if action == 'create':
        if not project_root:
            print('Error: Style creation must be run inside a PohLang project (plhub.json not found).')
            return 1
        try:
            record = manager.create_theme(
                args.name,
                base_identifier=getattr(args, 'base', None),
                description=getattr(args, 'description', None),
                force=getattr(args, 'force', False),
            )
        except (RuntimeError, KeyError, FileExistsError) as exc:
            print(f"Error: {exc}")
            return 1

        try:
            rel_path = Path(record.path).resolve().relative_to(project_root)
        except ValueError:
            rel_path = Path(record.path).name
        print(f"✅ Created style '{record.name}' at {rel_path} (key: {record.key}).")

        if getattr(args, 'activate', False):
            try:
                manifest = manager.apply(record.key, force=getattr(args, 'force', False))
                print(f"🔁 Activated '{record.name}' ({manifest['activeTheme']}).")
            except Exception as exc:  # noqa: BLE001
                print(f"Warning: Style created, but activation failed: {exc}")
        return 0

    print('Error: No style subcommand provided. Use --help for usage.')
    return 1


def widget_command(args):
    """Handle widget template subcommands."""
    plhub_root = Path(__file__).parent
    project_override = getattr(args, 'project_root', None)
    if project_override:
        project_root = Path(project_override).expanduser().resolve()
        if not (project_root / 'plhub.json').exists():
            print(f"Error: Provided project directory '{project_root}' does not contain plhub.json.")
            return 1
    else:
        project_root = find_project_root()

    action = getattr(args, 'widget_command', None)
    manager = WidgetManager(plhub_root, project_root)

    if action == 'list':
        summary = manager.export_summary()
        if getattr(args, 'json', False):
            print(json.dumps(summary, indent=2))
            return 0

        templates = summary.get('templates', [])
        project_templates = summary.get('projectTemplates', [])
        project_widgets = summary.get('projectWidgets', [])

        print('Widget templates:')
        for template in templates:
            meta = []
            if template.get('category'):
                meta.append(template['category'])
            if template.get('tags'):
                meta.append(', '.join(template['tags']))
            meta_suffix = f" ({'; '.join(meta)})" if meta else ''
            desc = f" - {template['description']}" if template.get('description') else ''
            print(f"  - {template['key']}: {template['name']}{meta_suffix}{desc}")

        if project_templates:
            print('\nProject-defined templates:')
            for template in project_templates:
                desc = f" - {template['description']}" if template.get('description') else ''
                print(f"  - {template['key']}: {template['name']}{desc}")

        if project_root and project_widgets:
            print('\nProject widgets:')
            for widget_path in project_widgets:
                print(f"  - {widget_path}")
        elif project_root:
            print('\nProject widgets: none yet. Use `plhub widget generate <template>` to scaffold one.')
        else:
            print('\nNote: no project detected. Run this command inside a project to see local widgets.')

        return 0

    if action == 'preview':
        try:
            preview = manager.preview(args.template)
        except KeyError as exc:
            print(str(exc))
            return 1
        if getattr(args, 'json', False):
            print(json.dumps(preview, indent=2))
        else:
            print(f"Template: {preview['name']} ({preview['key']})")
            if preview.get('description'):
                print(preview['description'])
            for file_spec in preview.get('files', []):
                desc = f" - {file_spec['description']}" if file_spec.get('description') else ''
                print(f"  File: {file_spec['path']}{desc}")
            if 'preview' in preview:
                print('\nPreview snippet:\n')
                print(preview['preview'])
        return 0

    if action == 'generate':
        if not project_root:
            print('Error: Widget generation must be run inside a PohLang project (plhub.json not found).')
            return 1
        try:
            template, paths = manager.generate(
                args.template,
                name=getattr(args, 'name', None),
                force=getattr(args, 'force', False),
                dry_run=getattr(args, 'dry_run', False),
            )
        except (RuntimeError, KeyError, FileExistsError) as exc:
            print(f"Error: {exc}")
            return 1

        rel_paths = [str(path.relative_to(project_root)) for path in paths]
        if getattr(args, 'dry_run', False):
            print(f"ℹ️  Dry run: {template.name} ({template.key}) would create:")
            for rel_path in rel_paths:
                print(f"   - {rel_path}")
            return 0

        print(f"✅ Generated widget '{template.name}' ({template.key}).")
        for rel_path in rel_paths:
            print(f"   - {rel_path}")
        return 0

    print('Error: No widget subcommand provided. Use --help for usage.')
    return 1


def get_template_content(template_name):
    """Get content for a project template."""
    templates = {
        "basic": '''Start Program

# Basic PohLang Program
Write "Hello from PohLang!"
Write "This is a basic project template."

End Program
''',
        "console": '''Start Program

# Console Application Template
Write "Welcome to your PohLang console application!"
Write ""

Ask for name
Write "Hello " plus name plus "!"

Set count to 0
Repeat 3
    Set count to count plus 1
    Write "Loop iteration: " plus count
End

Write ""
Write "Thanks for using PohLang!"

End Program
''',
        "web": '''Start Program

# Web Application Template (Experimental)
Write "Web application features coming soon!"
Write "For now, this is a placeholder."

# Future: Web server functionality
# Make start_server with port
#     Write "Starting server on port " plus port
#     # Server implementation
# End
# 
# Use start_server with 8080

End Program
'''
    }
    
    return templates.get(template_name, templates["basic"])


def transpile_file(args):
    """Transpile a single .poh file using the bundled or sibling Dart transpiler."""
    if not Path(args.file).exists():
        print(f"Error: File '{args.file}' not found.")
        return 1
    if args.to != 'dart':
        print("Error: Only 'dart' transpile target is currently supported.")
        return 64
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    bundled_dart = RUNTIME_DIR / "bin" / "pohlang.dart"
    sibling_dart = (Path(__file__).parent.parent / "PohLang" / "bin" / "pohlang.dart")
    transpiler_path = bundled_dart if bundled_dart.exists() else (sibling_dart if sibling_dart.exists() else None)

    try:
        if transpiler_path is None:
            print("Error: Could not locate PohLang Dart transpiler entrypoint.")
            print("Run 'plhub release' to bundle the latest PohLang into Runtime or place PohLang next to PLHub.")
            return 1
        # Use --no-run and optionally pass output directory if supported
        # For now, we run with --no-run and move outputs if the transpiler writes to CWD
        res = subprocess.run([
            "dart", "run", str(transpiler_path), args.file, "--no-run"
        ], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"❌ Transpile failed:\n{res.stdout}\n{res.stderr}")
            return 1
        print("✅ Transpile completed. Check generated Dart files (location depends on transpiler settings).")
        return 0
    except FileNotFoundError:
        print("Error: 'dart' command not found. Please install Dart SDK from https://dart.dev/get-dart.")
        return 1
    except Exception as e:
        print(f"Error during transpile: {e}")
        return 1


def run_with_python(file_path):
    """Run a PohLang file with the Python interpreter."""
    try:
        interp = Interpreter()
        interp.run_file(file_path)
        print("✅ Python execution completed successfully!")
        return 0
    except (RuntimeErrorPoh, ParseError) as e:
        print(f"❌ Python execution failed: {e}")
        return 1


def list_examples():
    """List available example programs (deprecated - use 'list examples')."""
    print("Use 'python plhub.py list examples' instead.")
    return list_items(type('Args', (), {'type': 'examples'})())


def _detect_os_key() -> str:
    import platform
    sysname = platform.system().lower()
    if 'windows' in sysname:
        return 'windows'
    if 'darwin' in sysname or 'mac' in sysname:
        return 'macos'
    return 'linux'


def update_runtime_command(args) -> int:
    """Download PohLang SDK zip and install OS-specific runtime binary into PL-Hub/bin.

    Also updates Runtime/pohlang_metadata.json with version and provenance.
    """
    import io
    import zipfile
    import hashlib
    from urllib.request import urlopen, Request

    root = Path(__file__).parent
    bin_dir = root / 'bin'
    bin_dir.mkdir(parents=True, exist_ok=True)

    os_key = args.os or _detect_os_key()
    runtime_name = {
        'windows': 'pohlang.exe',
        'linux': 'pohlang',
        'macos': 'pohlang',
    }[os_key]

    def sha256_bytes(data: bytes) -> str:
        h = hashlib.sha256()
        h.update(data)
        return h.hexdigest()

    # Determine download URL
    version = args.version
    zip_url = args.zip_url
    # Prefer a local SDK zip if present: ../PohLang/pohlang-sdk.zip
    if zip_url is None:
        local_sdk = (Path(__file__).parent.parent / 'PohLang' / 'pohlang-sdk.zip')
        if local_sdk.exists():
            zip_url = str(local_sdk)
    if zip_url is None:
        try:
            if version == 'latest':
                api = 'https://api.github.com/repos/AlhaqGH/PohLang/releases/latest'
            else:
                api = f'https://api.github.com/repos/AlhaqGH/PohLang/releases/tags/sdk-v{version}'
            req = Request(api, headers={'User-Agent': 'plhub-update-runtime'})
            with urlopen(req, timeout=30) as resp:
                rel = json.loads(resp.read().decode('utf-8'))
            if version == 'latest':
                tag = rel.get('tag_name', '')
                if tag.startswith('sdk-v'):
                    version = tag.replace('sdk-v', '')
                elif tag.startswith('pohlang-v'):
                    version = tag.replace('pohlang-v', '')
            assets = rel.get('assets', [])
            for a in assets:
                n = a.get('name', '')
                if n == f'pohlang-sdk-{version}.zip':
                    zip_url = a.get('browser_download_url')
                    break
            if zip_url is None:
                for a in assets:
                    n = a.get('name', '')
                    if n.endswith('.zip'):
                        zip_url = a.get('browser_download_url')
                        break
            if zip_url is None:
                print('Error: could not determine PohLang SDK zip URL from release assets.')
                return 1
        except Exception as e:
            print(f'Error fetching release info: {e}')
            return 1

    if args.verbose:
        print(f'Downloading PohLang SDK {version} from {zip_url}')
    # Fetch zip bytes from URL or local file
    blob = None
    try:
        if zip_url.startswith('http://') or zip_url.startswith('https://'):
            req = Request(zip_url, headers={'User-Agent': 'plhub-update-runtime'})
            with urlopen(req, timeout=60) as resp:
                blob = resp.read()
            # Try to infer version from filename in URL if version is 'latest'
            if version == 'latest':
                from urllib.parse import urlparse
                fname = Path(urlparse(zip_url).path).name
                if fname.startswith('pohlang-sdk-') and fname.endswith('.zip'):
                    version = fname[len('pohlang-sdk-'):-len('.zip')]
        elif zip_url.startswith('file://'):
            # Local file URL
            from urllib.parse import urlparse, unquote
            p = urlparse(zip_url)
            local_path = Path(unquote(p.path))
            blob = local_path.read_bytes()
            if version == 'latest':
                fname = local_path.name
                if fname.startswith('pohlang-sdk-') and fname.endswith('.zip'):
                    version = fname[len('pohlang-sdk-'):-len('.zip')]
        else:
            # Treat as local filesystem path
            local_path = Path(zip_url)
            if not local_path.exists():
                print(f'Error: zip file not found at {zip_url}')
                return 1
            blob = local_path.read_bytes()
            if version == 'latest':
                fname = local_path.name
                if fname.startswith('pohlang-sdk-') and fname.endswith('.zip'):
                    version = fname[len('pohlang-sdk-'):-len('.zip')]
    except Exception as e:
        print(f'Error obtaining SDK zip: {e}')
        return 1

    sdk_sha = sha256_bytes(blob)
    if args.verbose or args.validate:
        print(f'SDK zip SHA256: {sdk_sha}')
    if args.sha256:
        expected = args.sha256.strip().lower()
        if sdk_sha.lower() != expected:
            print(f'Error: SHA256 mismatch. expected={expected} actual={sdk_sha}')
            return 1

    # Extract OS-specific binary from zip: pohlang-sdk-<ver>/bin/<os_key>/pohlang(.exe)
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names = z.namelist()
            candidates = []
            for n in names:
                p = n.replace('\\', '/')
                if f'/bin/{os_key}/' in p and p.endswith(runtime_name):
                    candidates.append(n)
            if not candidates:
                print('Error: Could not find OS-specific runtime binary in SDK zip.')
                return 1
            member = candidates[0]
            data = z.read(member)
    except Exception as e:
        print(f'Error reading SDK zip: {e}')
        return 1

    if args.dry_run:
        print('Dry run: downloaded and located binary (not installing).')
        return 0

    # Write binary
    dst = bin_dir / runtime_name
    try:
        with open(dst, 'wb') as f:
            f.write(data)
        if os_key != 'windows':
            try:
                os.chmod(dst, 0o755)
            except Exception:
                pass
        print(f'Installed {runtime_name} -> {dst}')
    except Exception as e:
        print(f'Error writing binary: {e}')
        return 1

    # Update metadata
    runtime_dir = root / 'Runtime'
    runtime_dir.mkdir(parents=True, exist_ok=True)
    meta_file = runtime_dir / 'pohlang_metadata.json'
    metadata = {}
    if meta_file.exists():
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception:
            metadata = {}
    metadata.update({
        'pohlang_version': version,
        'source_repo': 'https://github.com/AlhaqGH/PohLang',
        'source_tag': f'sdk-v{version}',
        'download_url': zip_url,
        'sdk_zip_sha256': sdk_sha,
        'installed_binary': str(dst.relative_to(root)),
        'installed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    try:
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f'Updated metadata: {meta_file}')
    except Exception as e:
        print(f'Warning: failed to write metadata: {e}')

    print('✅ Runtime update complete.')
    return 0


def sync_runtime_local(args) -> int:
    """Copy locally built Rust pohlang into PL-Hub/Runtime/bin.

    This is useful during development when GitHub releases are not available.
    """
    root = Path(__file__).parent
    pohlang_repo = Path(args.pohlang_path) if args.pohlang_path else root.parent / 'PohLang'
    cargo_target = pohlang_repo / 'runtime' / 'target'
    exe_name = 'pohlang.exe' if platform.system().lower().startswith('win') else 'pohlang'
    src = cargo_target / args.profile / exe_name
    if not src.exists():
        print(f"Error: {src} not found. Build it first (e.g., cargo build --manifest-path {pohlang_repo / 'runtime' / 'Cargo.toml'}{(' --release' if args.profile=='release' else '')}).")
        return 1
    dst_dir = root / 'Runtime' / 'bin'
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / exe_name
    try:
        shutil.copy2(src, dst)
        if not exe_name.endswith('.exe'):
            try:
                os.chmod(dst, 0o755)
            except Exception:
                pass
        print(f"✅ Copied {src} -> {dst}")
        
        # Update metadata
        runtime_dir = root / 'Runtime'
        meta_file = runtime_dir / 'pohlang_metadata.json'
        metadata = {}
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception:
                metadata = {}
        
        # Read version from Cargo.toml
        version = '0.5.1'
        cargo_toml = pohlang_repo / 'runtime' / 'Cargo.toml'
        if cargo_toml.exists():
            try:
                text = cargo_toml.read_text(encoding='utf-8')
                for line in text.splitlines():
                    if line.strip().startswith('version'):
                        version = line.split('=', 1)[1].strip().strip('"\'')
                        break
            except Exception:
                pass
        
        metadata.update({
            'pohlang_version': version,
            'source_repo': 'https://github.com/AlhaqGH/PohLang',
            'build_profile': args.profile,
            'installed_binary': str(dst.relative_to(root)),
            'installed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source': 'local_build'
        })
        try:
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            print(f"✅ Updated metadata: {meta_file}")
        except Exception as e:
            print(f"Warning: failed to write metadata: {e}")
        
        return 0
    except Exception as e:
        print(f"Error copying runtime: {e}")
        return 1


@handle_common_errors
def doctor_command(args) -> int:
    """Check PLHub environment health and configuration with enhanced feedback."""
    root = Path(__file__).parent
    
    UI.header(f"{Icon.SEARCH} PLHub Environment Diagnostics")
    
    # Show platform status first
    if args.verbose:
        PlatformHelper.show_platform_status()
        print()
    
    issues = []
    warnings = []
    
    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"\n✅ Python: {py_version}")
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    
    # Check PohLang Rust runtime
    print("\n📦 PohLang Runtime:")
    pohlang_bin = _find_pohlangc()
    if pohlang_bin:
        print(f"  ✅ Found: {pohlang_bin}")
        # Try to get version
        try:
            res = subprocess.run([pohlang_bin, '--version'], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                print(f"  ✅ Version: {res.stdout.strip()}")
            else:
                warnings.append("Runtime binary exists but --version failed")
        except Exception as e:
            warnings.append(f"Could not execute runtime: {e}")
    else:
        issues.append("PohLang Rust runtime (pohlang.exe/pohlang) not found")
        print("  ❌ Not found. Run 'plhub sync-runtime-local' or 'plhub update-runtime'")
    
    # Check metadata
    meta_file = root / 'Runtime' / 'pohlang_metadata.json'
    if meta_file.exists():
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            print(f"\n📋 Runtime Metadata:")
            print(f"  Version: {meta.get('pohlang_version', 'unknown')}")
            print(f"  Source: {meta.get('source', 'unknown')}")
            if args.verbose:
                print(f"  Installed: {meta.get('installed_at', 'unknown')}")
                if 'source_commit' in meta:
                    print(f"  Commit: {meta.get('source_commit')[:8]}")
        except Exception as e:
            warnings.append(f"Could not read metadata: {e}")
    else:
        warnings.append("No runtime metadata found")
    
    # Check Python interpreter fallback
    print("\n🐍 Python Interpreter (fallback):")
    try:
        from Interpreter.poh_interpreter import Interpreter
        print("  ✅ Python interpreter available")
    except ImportError as e:
        warnings.append(f"Python interpreter not available: {e}")
        print(f"  ⚠️  Not available: {e}")
    
    # Check Dart SDK (for transpiler)
    print("\n🎯 Dart SDK (optional):")
    try:
        res = subprocess.run(['dart', '--version'], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            version_line = res.stderr.strip() if res.stderr else res.stdout.strip()
            print(f"  ✅ {version_line.split()[0:3]}")
        else:
            print("  ⚠️  Dart not found (transpilation unavailable)")
    except FileNotFoundError:
        print("  ⚠️  Dart not found (transpilation unavailable)")
    except Exception as e:
        warnings.append(f"Dart check failed: {e}")
    
    # Check project configuration
    print("\n📁 Project Configuration:")
    if Path("plhub.json").exists():
        try:
            with open("plhub.json", "r", encoding='utf-8') as f:
                config = json.load(f)
            print(f"  ✅ Project: {config.get('name', 'unnamed')}")
            print(f"  📌 Version: {config.get('version', '0.0.0')}")
            deps = config.get('dependencies', {})
            if deps:
                print(f"  📦 Dependencies: {len(deps)}")
                if args.verbose:
                    for name, ver in deps.items():
                        print(f"      - {name}: {ver}")
        except Exception as e:
            warnings.append(f"Could not read plhub.json: {e}")
    else:
        print("  ℹ️  Not in a project directory")
    
    # Check templates
    templates_dir = root / 'templates'
    if templates_dir.exists():
        templates = list(templates_dir.glob('*.poh'))
        print(f"\n📝 Templates: {len(templates)} available")
        if args.verbose:
            for t in templates:
                print(f"    - {t.stem}")
    
    # Summary
    print("\n" + "=" * 60)
    if not issues and not warnings:
        print("✅ All checks passed! PLHub is ready to use.")
        return 0
    elif issues:
        print(f"❌ Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"    • {issue}")
        if warnings:
            print(f"\n⚠️  {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"    • {warning}")
        return 1
    else:
        print(f"⚠️  Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"    • {warning}")
        print("\n✅ PLHub is functional with minor warnings.")
        return 0


def init_command(args) -> int:
    """Initialize PLHub configuration in current directory."""
    cwd = Path.cwd()
    config_file = cwd / 'plhub.json'
    
    if config_file.exists() and not args.force:
        print(f"Error: plhub.json already exists in {cwd}")
        print("Use --force to overwrite.")
        return 1
    
    project_name = args.name or cwd.name
    
    config = {
        "name": project_name,
        "version": "1.0.0",
        "description": f"PohLang project: {project_name}",
        "main": "src/main.poh",
        "dependencies": {},
        "dev_dependencies": {},
        "scripts": {
            "start": "plhub run src/main.poh",
            "build": "plhub build",
            "test": "plhub test"
        }
    }
    
    # Create basic structure
    (cwd / "src").mkdir(exist_ok=True)
    (cwd / "tests").mkdir(exist_ok=True)
    (cwd / "examples").mkdir(exist_ok=True)
    
    # Write config
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    # Create a basic main file if it doesn't exist
    main_file = cwd / "src" / "main.poh"
    if not main_file.exists():
        main_file.write_text('''Start Program

Write "Hello from PohLang!"
Write "Project: ''' + project_name + '''"

End Program
''', encoding='utf-8')
    
    print(f"✅ Initialized PLHub project: {project_name}")
    print(f"📁 Created:")
    print(f"    - plhub.json")
    print(f"    - src/main.poh")
    print(f"    - src/, tests/, examples/ directories")
    print(f"\n🚀 To run: plhub run src/main.poh")
    
    return 0


def test_command(args) -> int:
    """Run tests in the current project."""
    if not Path("plhub.json").exists():
        print("Error: Not in a PohLang project directory.")
        print("Run 'plhub init' to initialize a project.")
        return 1
    
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("No tests directory found.")
        return 0
    
    test_files = list(tests_dir.glob("**/*.poh"))
    if args.filter:
        test_files = [f for f in test_files if args.filter in f.name]
    
    if not test_files:
        print("No test files found.")
        return 0
    
    print(f"Running {len(test_files)} test file(s)...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    pohlang_bin = _find_pohlangc()
    
    for test_file in test_files:
        try:
            rel_path = test_file.relative_to(Path.cwd())
        except ValueError:
            rel_path = test_file
        print(f"\n📝 {rel_path}")
        
        try:
            if pohlang_bin:
                result = subprocess.run(
                    [pohlang_bin, '--run', str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Fallback to Python interpreter
                interp = Interpreter()
                try:
                    interp.run_file(str(test_file))
                    result = type('Result', (), {'returncode': 0, 'stdout': '', 'stderr': ''})()
                except Exception as e:
                    result = type('Result', (), {'returncode': 1, 'stdout': '', 'stderr': str(e)})()
            
            if result.returncode == 0:
                print("    ✅ PASSED")
                passed += 1
                if args.verbose and result.stdout:
                    print(f"    Output: {result.stdout[:200]}")
            else:
                print("    ❌ FAILED")
                failed += 1
                if result.stderr:
                    print(f"    Error: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print("    ❌ TIMEOUT")
            failed += 1
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1


def clean_command(args) -> int:
    """Clean build artifacts and caches."""
    print("🧹 Cleaning build artifacts...")
    
    cleaned = []
    
    # Clean build directory
    build_dir = Path("build")
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
            cleaned.append("build/")
        except Exception as e:
            print(f"Warning: Could not remove build/: {e}")
    
    # Clean bytecode files
    for pbc in Path(".").glob("**/*.pbc"):
        try:
            pbc.unlink()
            cleaned.append(str(pbc))
        except Exception:
            pass
    
    # Clean Python cache
    for pycache in Path(".").glob("**/__pycache__"):
        try:
            shutil.rmtree(pycache)
            cleaned.append(str(pycache))
        except Exception:
            pass
    
    if args.all:
        # Also clean dependencies (placeholder for future package manager)
        deps_dir = Path("plhub_modules")
        if deps_dir.exists():
            try:
                shutil.rmtree(deps_dir)
                cleaned.append("plhub_modules/")
            except Exception as e:
                print(f"Warning: Could not remove plhub_modules/: {e}")
    
    if cleaned:
        print(f"✅ Cleaned {len(cleaned)} item(s):")
        for item in cleaned[:10]:  # Show first 10
            print(f"    - {item}")
        if len(cleaned) > 10:
            print(f"    ... and {len(cleaned) - 10} more")
    else:
        print("ℹ️  Nothing to clean.")
    
    return 0


def sync_runtime_local(args) -> int:
    """Copy locally built Rust pohlangc into PL-Hub/bin.

    This is useful during development when GitHub releases are not available.
    """
    root = Path(__file__).parent
    pohlang_repo = Path(args.pohlang_path) if args.pohlang_path else root.parent / 'PohLang'
    cargo_target = pohlang_repo / 'runtime' / 'target'
    exe_name = 'pohlang.exe' if platform.system().lower().startswith('win') else 'pohlang'
    src = cargo_target / args.profile / exe_name
    
    if not src.exists():
        print(f"Error: {src} not found.")
        print(f"Build it first with:")
        print(f"  cargo build --manifest-path \"{pohlang_repo / 'runtime' / 'Cargo.toml'}\"")
        if args.profile == 'release':
            print("  (add --release flag for release build)")
        return 1
    
    dst_dir = root / 'Runtime' / 'bin'
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / exe_name
    
    try:
        shutil.copy2(src, dst)
        if not exe_name.endswith('.exe'):
            try:
                os.chmod(dst, 0o755)
            except Exception:
                pass
        print(f"✅ Copied {src} -> {dst}")
        
        # Update metadata
        runtime_dir = root / 'Runtime'
        meta_file = runtime_dir / 'pohlang_metadata.json'
        metadata = {}
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception:
                metadata = {}
        
        # Read version from Cargo.toml
        version = '0.5.1'
        cargo_toml = pohlang_repo / 'runtime' / 'Cargo.toml'
        if cargo_toml.exists():
            try:
                text = cargo_toml.read_text(encoding='utf-8')
                for line in text.splitlines():
                    if line.strip().startswith('version'):
                        version = line.split('=', 1)[1].strip().strip('"\'')
                        break
            except Exception:
                pass
        
        metadata.update({
            'pohlang_version': version,
            'source_repo': 'https://github.com/AlhaqGH/PohLang',
            'build_profile': args.profile,
            'installed_binary': str(dst.relative_to(root)),
            'installed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source': 'local_build'
        })
        try:
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            print(f"✅ Updated metadata: {meta_file}")
        except Exception as e:
            print(f"Warning: failed to write metadata: {e}")
        
        return 0
    except Exception as e:
        print(f"Error copying runtime: {e}")
        return 1


def watch_command(args) -> int:
    """Watch for file changes and rebuild automatically."""
    from tools.build_automation import BuildAutomation
    
    project_root = find_project_root()
    if not project_root:
        print("❌ Not in a PohLang project directory")
        print("   Run this command from a project with plhub.json")
        return 1
    
    builder = BuildAutomation(project_root, verbose=args.verbose)
    
    try:
        builder.watch_mode()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"❌ Watch mode error: {e}")
        return 1


def dev_command(args) -> int:
    """Start development server with hot reload."""
    from tools.hot_reload import HotReloadServer
    
    project_root = find_project_root()
    if not project_root:
        print("❌ Not in a PohLang project directory")
        print("   Run this command from a project with plhub.json")
        return 1
    
    # Determine entry file
    if args.file:
        entry_file = Path(args.file)
    else:
        # Default to src/main.poh
        entry_file = project_root / 'src' / 'main.poh'
    
    if not entry_file.exists():
        print(f"❌ Entry file not found: {entry_file}")
        return 1
    
    server = HotReloadServer(project_root, entry_file, verbose=args.verbose)
    
    try:
        server.watch_and_reload()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"❌ Dev server error: {e}")
        return 1


def platform_command(args) -> int:
    """Handle platform commands for cross-platform development."""
    
    platform_cmd = args.platform_command
    
    if platform_cmd == 'create':
        return platform_create(args)
    elif platform_cmd == 'build':
        return platform_build(args)
    elif platform_cmd == 'run':
        return platform_run(args)
    elif platform_cmd == 'test':
        return platform_test(args)
    elif platform_cmd == 'deploy':
        return platform_deploy(args)
    elif platform_cmd == 'devices':
        return platform_devices(args)
    elif platform_cmd == 'launch':
        return platform_launch(args)
    else:
        print(f"Unknown platform command: {platform_cmd}")
        return 1


def platform_create(args) -> int:
    """Create new platform project."""
    try:
        manager = PlatformManager()
        platform = Platform(args.platform)
        
        output_dir = Path(args.output) if args.output else Path.cwd()
        
        success = manager.create_project(
            platform=platform,
            project_name=args.name,
            output_dir=output_dir,
            package_name=args.package
        )
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return 1


def platform_build(args) -> int:
    """Build platform project."""
    try:
        manager = PlatformManager()
        platform = Platform(args.platform)
        
        project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
        
        success = manager.build(
            platform=platform,
            project_dir=project_dir,
            configuration=args.config
        )
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Build error: {e}")
        return 1


def platform_run(args) -> int:
    """Run platform project."""
    try:
        manager = PlatformManager()
        platform_enum = Platform(args.platform)
        
        project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
        
        # Start hot reload if requested
        if args.hot_reload:
            print("🔄 Starting hot reload...")
            hot_reload = HotReloadManager(project_dir, args.platform)
            hot_reload.start()
            
            try:
                # Run the app
                success = manager.run(
                    platform=platform_enum,
                    project_dir=project_dir,
                    device=args.device
                )
                
                if success:
                    # Keep hot reload running
                    hot_reload.wait()
                else:
                    hot_reload.stop()
                    return 1
                    
            except KeyboardInterrupt:
                hot_reload.stop()
                return 0
        else:
            success = manager.run(
                platform=platform_enum,
                project_dir=project_dir,
                device=args.device
            )
            return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Run error: {e}")
        return 1


def platform_test(args) -> int:
    """Run platform tests."""
    try:
        test_manager = PohTestManager()
        project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
        
        test_type = PohTestType(args.type)
        
        suite = test_manager.run_tests(
            platform=args.platform,
            project_dir=project_dir,
            test_type=test_type,
            pattern=args.pattern
        )
        
        # Return 0 if all tests passed, 1 otherwise
        return 0 if suite.failed == 0 else 1
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return 1


def platform_deploy(args) -> int:
    """Deploy platform project."""
    try:
        manager = PlatformManager()
        platform = Platform(args.platform)
        
        project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
        
        success = manager.deploy(
            platform=platform,
            project_dir=project_dir,
            target=args.target
        )
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Deploy error: {e}")
        return 1


def platform_devices(args) -> int:
    """List available devices."""
    try:
        device_manager = UnifiedDeviceManager()
        
        if args.platform:
            device_manager.display_devices(args.platform)
        else:
            device_manager.display_devices()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error listing devices: {e}")
        return 1


def platform_launch(args) -> int:
    """Launch emulator/simulator."""
    try:
        device_manager = UnifiedDeviceManager()
        
        success = device_manager.launch_device(args.platform, args.device)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Launch error: {e}")
        return 1


def debug_command(args) -> int:
    """Start development server with hot reload."""
    from tools.hot_reload import HotReloadServer
    
    project_root = find_project_root()
    if not project_root:
        print("❌ Not in a PohLang project directory")
        print("   Run this command from a project with plhub.json")
        return 1
    
    # Determine entry file
    if args.file:
        entry_file = Path(args.file)
    else:
        # Default to src/main.poh
        entry_file = project_root / 'src' / 'main.poh'
    
    if not entry_file.exists():
        print(f"❌ Entry file not found: {entry_file}")
        return 1
    
    server = HotReloadServer(project_root, entry_file, verbose=args.verbose)
    
    try:
        server.watch_and_reload()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"❌ Dev server error: {e}")
        return 1


def debug_command(args) -> int:
    """Start debug session with breakpoint support."""
    from tools.hot_reload import DebugServer
    
    project_root = find_project_root()
    if not project_root:
        print("❌ Not in a PohLang project directory")
        print("   Run this command from a project with plhub.json")
        return 1
    
    # Determine entry file
    if args.file:
        entry_file = Path(args.file)
    else:
        entry_file = project_root / 'src' / 'main.poh'
    
    if not entry_file.exists():
        print(f"❌ Entry file not found: {entry_file}")
        return 1
    
    server = DebugServer(project_root, entry_file, verbose=args.verbose, debug_port=args.port)
    
    try:
        server.start_debug_session()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"❌ Debug session error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main() or 0)
