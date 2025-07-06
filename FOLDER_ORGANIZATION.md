# Bills Tracker v3 - Folder Organization Guide

## 📁 Project Structure

```
Bills_tracker_v3/
├── 📄 main_desktop.py              # Main application entry point
├── 📄 requirements.txt             # Python dependencies
├── 📄 config.json                  # Application configuration
├── 📄 saved_credentials.json       # User credentials (encrypted)
├── 📄 bills_tracker.db             # Main SQLite database
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 src/                         # Source code
│   ├── 📁 core/                    # Core business logic
│   │   ├── 📄 auth.py              # Authentication system
│   │   ├── 📄 config_manager.py    # Configuration management
│   │   ├── 📄 config.py            # Legacy config (deprecated)
│   │   ├── 📄 db.py                # Database operations
│   │   ├── 📄 reminder_service.py  # Reminder notifications
│   │   ├── 📄 services.py          # Business services
│   │   └── 📄 validation.py        # Data validation
│   │
│   ├── 📁 gui/                     # User interface
│   │   ├── 📁 components/          # Reusable UI components
│   │   │   └── 📄 bills_table.py   # Bills table component
│   │   ├── 📄 icon_utils.py        # Icon management system
│   │   ├── 📄 login_dialog.py      # Login/registration dialogs
│   │   ├── 📄 main_window.py       # Main application window
│   │   ├── 📄 notification_dialog.py # Notification system
│   │   └── 📄 validation.py        # UI validation
│   │
│   └── 📁 utils/                   # Utility functions
│       ├── 📄 constants.py         # Application constants
│       ├── 📄 helpers.py           # Helper functions
│       └── 📄 ui_helpers.py        # UI helper functions
│
├── 📁 resources/                   # Application resources
│   └── 📁 icons/                   # Icon sets
│       ├── 📁 default/             # Default icon set
│       │   ├── 📄 add.png          # Add/plus icon
│       │   ├── 📄 edit.png         # Edit/pencil icon
│       │   ├── 📄 delete.png       # Delete/trash icon
│       │   ├── 📄 save.png         # Save/disk icon
│       │   ├── 📄 cancel.png       # Cancel/X icon
│       │   ├── 📄 search.png       # Search/magnifying glass
│       │   ├── 📄 calendar.png     # Calendar icon
│       │   ├── 📄 export.png       # Export/download icon
│       │   ├── 📄 import.png       # Import/upload icon
│       │   ├── 📄 refresh.png      # Refresh/reload icon
│       │   ├── 📄 settings.png     # Settings/gear icon
│       │   ├── 📄 categories.png   # Categories/tags icon
│       │   ├── 📄 bills.png        # Bills/document icon
│       │   ├── 📄 apply.png        # Apply/checkmark icon
│       │   └── 📄 clear.png        # Clear/reset icon
│       │
│       └── 📁 outline/             # Outline icon set (white borders)
│           └── [same files as default/]
│
├── 📁 migrations/                  # Database migrations
│   ├── 📄 initialize_database.py   # Initial database setup
│   ├── 📄 migrate_add_amount_field.py
│   ├── 📄 migrate_auth_schema.py   # Authentication schema
│   ├── 📄 migrate_confirmation_number.py
│   ├── 📄 migrate_payment_methods.py
│   └── 📄 README.md                # Migration documentation
│
├── 📁 tests/                       # Test suite
│   ├── 📁 unit/                    # Unit tests
│   │   ├── 📄 test_config_manager.py
│   │   ├── 📄 test_services.py
│   │   ├── 📄 test_utils.py
│   │   └── 📄 test_validation.py
│   │
│   ├── 📁 integration/             # Integration tests
│   │   └── 📄 test_database_integration.py
│   │
│   ├── 📁 table_features/          # Table-specific tests
│   │   ├── 📄 test_multi_select.py
│   │   ├── 📄 test_pagination.py
│   │   └── 📄 test_table_styling.py
│   │
│   ├── 📁 validation/              # Validation tests
│   ├── 📄 conftest.py              # Test configuration
│   ├── 📄 run_tests.py             # Test runner
│   └── 📄 README.md                # Testing documentation
│
├── 📁 docs/                        # Documentation
│   ├── 📁 features/                # Feature documentation
│   │   └── 📄 AUTHENTICATION.md    # Authentication guide
│   ├── 📁 implementation/          # Implementation docs
│   │   └── 📄 VALIDATION_README.md # Validation system docs
│   └── 📄 README.md                # Documentation index
│
├── 📁 demo/                        # Demo and examples
│   ├── 📄 demo_advanced_filtering.py
│   ├── 📄 demo_confirmation_number.py
│   ├── 📄 demo_date_selector.py
│   ├── 📄 demo_next_month_filter.py
│   ├── 📄 demo_reminders_notifications.py
│   └── 📄 README.md                # Demo documentation
│
├── 📁 scripts/                     # Utility scripts
│   └── 📄 reset_admin_password.py  # Admin password reset
│
├── 📁 backups/                     # Database backups
│   ├── 📄 bills_tracker_backup_20250706_005554.db
│   └── 📄 backup.db
│
├── 📄 README.md                    # Main project documentation
├── 📄 REFACTORING_GUIDE.md         # Code refactoring guide
├── 📄 UI_IMPROVEMENTS.md           # UI improvement documentation
├── 📄 future_coding.md             # Future development roadmap
└── 📄 instruction.md               # Development instructions
```

## 🗂️ Directory Purposes

### **Root Level Files**
- `main_desktop.py` - Application entry point
- `requirements.txt` - Python package dependencies
- `config.json` - Application settings and preferences
- `bills_tracker.db` - Main SQLite database
- `*.md` files - Documentation and guides

### **Source Code (`src/`)**
- **`core/`** - Business logic, database operations, authentication
- **`gui/`** - User interface components and dialogs
- **`utils/`** - Helper functions and constants

### **Resources (`resources/`)**
- **`icons/`** - Icon sets for different visual styles
  - `default/` - Standard black icons
  - `outline/` - White-bordered icons

### **Database (`migrations/`)**
- Database schema migrations and version control
- Each migration file handles a specific schema change

### **Testing (`tests/`)**
- **`unit/`** - Individual component tests
- **`integration/`** - End-to-end functionality tests
- **`table_features/`** - UI table component tests
- **`validation/`** - Data validation tests

### **Documentation (`docs/`)**
- Feature guides and implementation documentation
- Organized by feature area and implementation details

### **Demo (`demo/`)**
- Example scripts demonstrating specific features
- Useful for testing and learning

### **Scripts (`scripts/`)**
- Utility scripts for maintenance and administration
- Database management and user administration tools

### **Backups (`backups/`)**
- Database backup files
- Automatic and manual backups

## 🔧 Development Workflow

### **Adding New Features**
1. Create feature branch from `main`
2. Add code to appropriate `src/` subdirectory
3. Add tests to `tests/` directory
4. Update documentation in `docs/`
5. Create demo if needed in `demo/`

### **Database Changes**
1. Create migration script in `migrations/`
2. Test migration with sample data
3. Update database schema documentation

### **UI Changes**
1. Modify files in `src/gui/`
2. Add new icons to `resources/icons/` if needed
3. Update UI documentation in `docs/`

### **Configuration Changes**
1. Update `src/core/config_manager.py`
2. Add new settings to default config
3. Update configuration documentation

## 📋 File Naming Conventions

- **Python files**: `snake_case.py`
- **Directories**: `snake_case/`
- **Test files**: `test_*.py`
- **Migration files**: `migrate_*.py`
- **Documentation**: `*.md`
- **Configuration**: `*.json`
- **Database**: `*.db`

## 🚀 Deployment Structure

For deployment, the following structure is recommended:

```
deployment/
├── main_desktop.py
├── requirements.txt
├── config.json
├── bills_tracker.db
├── src/
├── resources/
├── migrations/
└── scripts/
```

This keeps the deployment clean while maintaining all necessary functionality.

## 📝 Maintenance Notes

- **Regular backups**: Database backups are stored in `backups/`
- **Test files**: Temporary test files should be cleaned up after use
- **Documentation**: Keep documentation updated with code changes
- **Migrations**: Always test migrations before applying to production
- **Icons**: New icon sets can be added to `resources/icons/`

---

*This organization ensures a clean, maintainable codebase that's easy to navigate and extend.* 