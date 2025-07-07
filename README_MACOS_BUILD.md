# Bills Tracker v3 - macOS Build Guide

This guide will help you compile the Bills Tracker desktop application for macOS, creating a standalone `.app` bundle that can be distributed to other Mac users.

## 🍎 Prerequisites

### Required Software
- **macOS 10.13 (High Sierra) or later**
- **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/macos/)
- **Xcode Command Line Tools** - Install with: `xcode-select --install`

### Optional Tools (for distribution)
- **Homebrew** - Install with: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- **create-dmg** - Install with: `brew install create-dmg` (for creating DMG installers)

## 🚀 Quick Start

### Method 1: Automated Build (Recommended)

1. **Clone or download the project** to your Mac
2. **Open Terminal** and navigate to the project directory
3. **Run the automated build script**:
   ```bash
   python3 build_macos.py
   ```

The script will:
- ✅ Check all dependencies
- ✅ Install missing packages
- ✅ Create the PyInstaller configuration
- ✅ Build the application
- ✅ Create a DMG installer (if create-dmg is available)

### Method 2: Manual Build

If you prefer to build manually or need to customize the process:

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   pip3 install pyinstaller
   ```

2. **Run PyInstaller**:
   ```bash
   pyinstaller --onefile --windowed --icon=resources/icons/bill_tracker_v3.ico --name="BillsTracker" main_desktop.py
   ```

## 📁 Build Output

After successful compilation, you'll find:

- **`dist/BillsTracker.app`** - The main application bundle
- **`BillsTracker-v3.0.0-macOS.dmg`** - DMG installer (if created)
- **`build/`** - Temporary build files (can be deleted)

## 🧪 Testing the Build

1. **Test the application**:
   ```bash
   open dist/BillsTracker.app
   ```

2. **Verify functionality**:
   - ✅ Application launches without errors
   - ✅ All features work (add bills, categories, etc.)
   - ✅ Database operations work correctly
   - ✅ Settings and preferences save properly

## 🔐 Code Signing (For Distribution)

If you plan to distribute the app outside your Mac, you'll need to code sign it:

### 1. Get a Developer ID Certificate
- Enroll in the Apple Developer Program ($99/year)
- Download your Developer ID Application certificate

### 2. Code Sign the App
```bash
codesign --deep --sign "Developer ID Application: Your Name" dist/BillsTracker.app
```

### 3. Notarize the App
```bash
xcrun altool --notarize-app \
  --primary-bundle-id com.billstracker.desktop \
  --username your-apple-id@example.com \
  --password your-app-specific-password \
  --file dist/BillsTracker.app
```

### 4. Staple the Notarization
```bash
xcrun stapler staple dist/BillsTracker.app
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "Python not found" error
```bash
# Make sure Python 3 is installed and in PATH
python3 --version
# If not found, install from python.org
```

#### 2. "PyInstaller not found" error
```bash
pip3 install pyinstaller
```

#### 3. "Permission denied" errors
```bash
# Make the build script executable
chmod +x build_macos.py
```

#### 4. App crashes on launch
- Check Console.app for error messages
- Ensure all dependencies are properly bundled
- Try running from Terminal: `./dist/BillsTracker.app/Contents/MacOS/BillsTracker`

#### 5. Missing icons or resources
- Verify `resources/icons/` directory exists
- Check that all required files are included in the spec file

### Debug Mode

To build with debug information:
```bash
pyinstaller --debug=all BillsTracker.spec
```

## 📦 Distribution Options

### 1. Direct App Distribution
- Share the `.app` file directly
- Users can drag to Applications folder
- No installer required

### 2. DMG Installer
- Professional distribution method
- Includes drag-to-install instructions
- Created automatically by the build script

### 3. Mac App Store
- Requires additional code signing
- Must follow App Store guidelines
- More complex submission process

## 🔧 Customization

### Modify App Metadata
Edit the `info_plist` section in `BillsTracker.spec`:
- Change bundle identifier
- Update version numbers
- Modify app name and description

### Add Custom Icons
Replace `resources/icons/bill_tracker_v3.ico` with your own icon file

### Include Additional Files
Add files to the `datas` list in the spec file:
```python
datas=[
    ('resources/icons', 'resources/icons'),
    ('config.json', '.'),
    ('additional_file.txt', '.'),
],
```

## 📊 Build Statistics

Typical build results:
- **App size**: ~50-100 MB
- **Build time**: 2-5 minutes
- **Dependencies**: ~20-30 packages bundled
- **Compatibility**: macOS 10.13+

## 🆘 Support

If you encounter issues:

1. **Check the logs** in Terminal output
2. **Verify all prerequisites** are installed
3. **Try a clean build** (delete `build/` and `dist/` folders)
4. **Check Python version** compatibility
5. **Review PyInstaller documentation** for advanced options

## 📝 Notes

- The built app is self-contained and doesn't require Python installation
- Database files are stored in the user's home directory
- Settings are preserved between app updates
- The app works offline and doesn't require internet connection

---

**Happy Building! 🎉**

For more information, see the main [README.md](README.md) file. 