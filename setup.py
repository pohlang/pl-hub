#!/usr/bin/env python3
"""
PL-Hub Setup Script

Installation script for the PohLang development environment.
PLHub is to PohLang what Flutter is to Dart - a comprehensive development platform.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for the long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="plhub",
    version="0.7.0",
    author="PohLang Team",
    author_email="contact@pohlang.org",
    description="PL-Hub: Enterprise-grade UI framework with comprehensive tooling for PohLang",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlhaqGH/PLHub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pohlang>=0.1.0",  # Require PohLang core language (tracks interpreter version)
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "env": [
            "python-dotenv>=1.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
        "editor": [
            "pygments>=2.10",  # For syntax highlighting
            "python-lsp-server>=1.0",  # Language server support
        ],
    },
    entry_points={
        "console_scripts": [
            "plhub=plhub:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.poh", "*.md", "*.txt", "*.json"],
        "Examples": ["*.poh"],
        "templates": ["*"],
        "docs": ["*.md"],
        "tools": ["*.py"],
        "widgets": [
            "README.md",
            "templates/*.json",
        ],
        "styles": [
            "*.json",
            "design-tokens/*.json",
        ],
        "Runtime": [
            "pohlang_metadata.json",
            "Interpreter/*.py",
            "Interpreter/examples/*.poh",
            "Interpreter/stdlib/**/*",
            "Interpreter/__main__.py",
            "Interpreter/__init__.py",
            "bin/*.dart",
            "transpiler/**/*",
        ],
    },
    zip_safe=False,
    keywords="pohlang development-environment build-tools package-manager ide framework",
    project_urls={
        "Bug Reports": "https://github.com/AlhaqGH/PLHub/issues",
        "Source": "https://github.com/AlhaqGH/PLHub",
        "Documentation": "https://github.com/AlhaqGH/PLHub/docs",
        "PohLang Core": "https://github.com/AlhaqGH/PohLang",
    },
)
