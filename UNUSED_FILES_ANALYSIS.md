📁 AlgoAnchor - Unused Files Analysis

## 🗑️ FILES THAT CAN BE SAFELY REMOVED

### 1. Duplicate Strategy Templates

These are older versions or duplicates that are no longer referenced in views:

**In `/core/templates/strategies/`:**

- `strategy_create.html` (duplicate of `create.html`)
- `strategy_delete.html` (duplicate of `delete.html`)
- `strategy_detail.html` (duplicate of `detail.html`)
- `strategy_edit.html` (duplicate of `edit.html`)

### 2. Unused CSS Files

**In `/core/static/css/`:**

- `login.css` (not referenced in any template - auth.css is used instead)

### 3. Empty Python Files

**In `/core/`:**

- `signals.py` (completely empty file)

**In `/scripts/`:**

- `load_data.py` (completely empty file)

### 4. Legacy Utility File

**In `/core/utils/`:**

- `backtest.py` (contains old backtest logic, replaced by `services/backtest_engine.py`)

### 5. Demo Scripts (Optional Cleanup)

**In root directory:**

- `demo_admin_interface.py` (demo script, not needed for production)
- `demo_strategy_detail.py` (demo script, not needed for production)

### 6. Dataset Files (Optional)

**In `/dataset/`:**

- `spy.csv` (sample data file, may not be needed if not used)

## ✅ FILES THAT ARE BEING USED

### Templates Currently Used:

- `base.html` - Base template
- `home.html` - Home page
- `dashboard.html` - Dashboard
- `strategies/create.html` - Strategy creation
- `strategies/detail.html` - Strategy detail view
- `strategies/edit.html` - Strategy editing
- `strategies/delete.html` - Strategy deletion
- `backtests/detail.html` - Backtest results
- `backtests/compare.html` - Backtest comparison
- `profile/profile.html` - User profile
- `profile/edit_profile.html` - Edit profile
- `profile/change_password.html` - Change password
- `registration/login.html` - Login page
- `registration/register.html` - Registration

### CSS Files Currently Used:

- `global.css` - Global styles (referenced in base.html)
- `strategy.css` - Strategy pages
- `dashboard.css` - Dashboard
- `profile.css` - Profile pages
- `auth.css` - Authentication pages
- `home.css` - Home page

### Python Files Currently Used:

All files in:

- `views/` directory (all view files)
- `models.py` - Database models
- `forms.py` - Form definitions
- `admin.py` - Admin interface
- `urls.py` - URL patterns
- `apps.py` - App configuration
- `utils/charting.py` - Chart generation
- `services/` directory (backtest engine, data services)
- `management/commands/` - Management commands

## 🧹 CLEANUP COMMANDS

To remove the unused files, run these commands:

```bash
# Remove duplicate strategy templates
rm core/templates/strategies/strategy_create.html
rm core/templates/strategies/strategy_delete.html
rm core/templates/strategies/strategy_detail.html
rm core/templates/strategies/strategy_edit.html

# Remove unused CSS
rm core/static/css/login.css

# Remove empty Python files
rm core/signals.py
rm scripts/load_data.py

# Remove legacy utility
rm core/utils/backtest.py

# Optional: Remove demo scripts
rm demo_admin_interface.py
rm demo_strategy_detail.py

# Optional: Remove sample data
rm dataset/spy.csv
rmdir dataset  # Only if empty
```

## 📊 CLEANUP SUMMARY

**Safe to Remove:**

- 8 files are definitively unused and can be removed
- 3 additional files are demo/sample files that can be optionally removed

**Storage Saved:**

- Removes redundant template files
- Eliminates unused CSS
- Cleans up empty Python files
- Removes legacy code

**Benefits:**

- Cleaner project structure
- Reduced confusion about which files to use
- Easier maintenance
- Smaller repository size
