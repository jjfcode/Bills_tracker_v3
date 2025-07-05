# Migrations

This folder contains database migration scripts for Bills Tracker v3.

## Purpose

Database migrations are scripts that modify the database schema to add new features or fix existing issues. They ensure that the database structure stays up-to-date with the application code.

## Files

- `migrate_confirmation_number.py` - Adds confirmation_number column to bills table
- `migrate_payment_methods.py` - Adds payment_methods table and updates bills table

## Usage

To run a migration script:

```bash
cd migrations
python migrate_confirmation_number.py
python migrate_payment_methods.py
```

## Important Notes

- Always backup your database before running migrations
- Run migrations in the correct order (check dependencies)
- Test migrations on a copy of your data first
- Migrations are idempotent - safe to run multiple times

## Creating New Migrations

When adding new features that require database changes:

1. Create a new migration script in this folder
2. Use a descriptive filename (e.g., `migrate_feature_name.py`)
3. Include proper error handling and rollback capabilities
4. Test the migration thoroughly
5. Update this README with the new migration details 