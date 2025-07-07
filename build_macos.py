#!/usr/bin/env python3
"""
Build script for Bills Tracker v3 - macOS
Compiles the application into a standalone macOS app bundle
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def check_dependencies():
    """Check if required tools are installed"""
    print("🔍 Checking build dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller is installed")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        run_command("pip install pyinstaller", "Installing PyInstaller")
    
    # Check if all requirements are installed
    try:
        import customtkinter
        import cryptography
        import tkcalendar
        from PIL import Image
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Installing requirements...")
        run_command("pip install -r requirements.txt", "Installing requirements")

def create_spec_file():
    """Create PyInstaller spec file for macOS"""
    print("\n📝 Creating PyInstaller spec file...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icons', 'resources/icons'),
        ('config.json', '.'),
        ('saved_credentials.json', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'tkcalendar',
        'cryptography',
        'PIL',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        'tkinter.colorchooser',
        'sqlite3',
        'json',
        'datetime',
        'threading',
        'queue',
        'pathlib',
        'shutil',
        'tempfile',
        'uuid',
        'hashlib',
        'base64',
        'csv',
        'zipfile',
        'tarfile',
        'gzip',
        'bz2',
        'lzma',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BillsTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BillsTracker',
)

app = BUNDLE(
    coll,
    name='BillsTracker.app',
    icon='resources/icons/bill_tracker_v3.ico',
    bundle_identifier='com.billstracker.desktop',
    info_plist={
        'CFBundleName': 'Bills Tracker',
        'CFBundleDisplayName': 'Bills Tracker',
        'CFBundleVersion': '3.0.0',
        'CFBundleShortVersionString': '3.0.0',
        'CFBundleExecutable': 'BillsTracker',
        'CFBundleIdentifier': 'com.billstracker.desktop',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundleDevelopmentRegion': 'en',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        },
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Bills Tracker Database',
                'CFBundleTypeExtensions': ['db'],
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Owner'
            }
        ]
    }
)
'''
    
    with open('BillsTracker.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Spec file created: BillsTracker.spec")

def build_application():
    """Build the macOS application"""
    print("\n🏗️ Building macOS application...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Build using PyInstaller
    run_command("pyinstaller BillsTracker.spec", "Building application")
    
    print("\n✅ Build completed successfully!")
    print("📁 Application location: dist/BillsTracker.app")

def create_dmg():
    """Create a DMG installer (optional)"""
    print("\n📦 Creating DMG installer...")
    
    # Check if create-dmg is installed
    try:
        subprocess.run(['which', 'create-dmg'], check=True, capture_output=True)
        print("✅ create-dmg is available")
    except subprocess.CalledProcessError:
        print("⚠️ create-dmg not found. Install with: brew install create-dmg")
        print("Skipping DMG creation...")
        return
    
    # Create DMG
    dmg_name = "BillsTracker-v3.0.0-macOS.dmg"
    run_command(
        f'create-dmg --volname "Bills Tracker v3" --window-pos 200 120 --window-size 600 400 --icon-size 100 --icon "BillsTracker.app" 175 120 --hide-extension "BillsTracker.app" --app-drop-link 425 120 "{dmg_name}" "dist/"',
        "Creating DMG installer"
    )
    
    print(f"✅ DMG created: {dmg_name}")

def main():
    """Main build process"""
    print("🚀 Bills Tracker v3 - macOS Build Script")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    # Create spec file
    create_spec_file()
    
    # Build application
    build_application()
    
    # Create DMG (optional)
    create_dmg()
    
    print("\n🎉 Build process completed!")
    print("\n📋 Next steps:")
    print("1. Test the application: open dist/BillsTracker.app")
    print("2. Code sign the app (if distributing): codesign --deep --sign 'Developer ID Application: Your Name' dist/BillsTracker.app")
    print("3. Notarize the app (if distributing): xcrun altool --notarize-app --primary-bundle-id com.billstracker.desktop --username your-apple-id --password your-app-specific-password --file dist/BillsTracker.app")
    print("4. Distribute the app or DMG file")

if __name__ == "__main__":
    main() 