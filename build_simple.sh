#!/bin/bash

# Bills Tracker v3 - Simple macOS Build Script
# This script provides a quick way to build the application

set -e  # Exit on any error

echo "🚀 Bills Tracker v3 - Simple macOS Build"
echo "========================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ from python.org"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install requirements
echo "📦 Installing requirements..."
pip3 install -r requirements_macos.txt

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build the application
echo "🏗️ Building application..."
pyinstaller \
    --onefile \
    --windowed \
    --icon=resources/icons/bill_tracker_v3.ico \
    --name="BillsTracker" \
    --add-data="resources/icons:resources/icons" \
    --add-data="config.json:." \
    --add-data="saved_credentials.json:." \
    --hidden-import=customtkinter \
    --hidden-import=tkcalendar \
    --hidden-import=cryptography \
    --hidden-import=PIL \
    --hidden-import=PIL._tkinter_finder \
    main_desktop.py

echo "✅ Build completed!"
echo "📁 Application location: dist/BillsTracker"
echo ""
echo "To test the application:"
echo "  open dist/BillsTracker"
echo ""
echo "To create a proper .app bundle, run:"
echo "  python3 build_macos.py" 