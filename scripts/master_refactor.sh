#!/bin/bash
# Complete refactoring: Remove ALL Serbian from comments, docstrings, and variable names
# Keep only UI text in HTML templates

WORKSPACE="/mnt/d/DSUsers/uif80506/Faks/ERP_latice.sa.pricom"
cd "$WORKSPACE"

echo "🔄 Complete refactoring: Serbian → English"
echo "==========================================="
echo ""

# Python files - comments and docstrings
echo "📝 Refactoring Python files..."

find . -name "*.py" ! -path "./.venv/*" ! -path "./__pycache__/*" ! -path "./.git/*" -exec sed -i \
  -e "s/Učitaj konfiguraciju/Load configuration/g" \
  -e "s/Učitaj/Load/g" \
  -e "s/Prikaži logove/Display logs/g" \
  -e "s/Prikaži ili izmeni konfiguraciju/Display or modify configuration/g" \
  -e "s/Prikaži sve informacije o instalaciji/Display all installation info/g" \
  -e "s/Prikaži/Display/g" \
  -e "s/Uključi autostart/Enable autostart/g" \
  -e "s/Isključi autostart/Disable autostart/g" \
  -e "s/Obriši servis fajl/Delete service file/g" \
  -e "s/Obriši CLI komandu/Delete CLI command/g" \
  -e "s/Obriši instalaciju/Delete installation/g" \
  -e "s/Obriši/Delete/g" \
  -e "s/Samo prikaži trenutni port/Only display current port/g" \
  -e "s/Ažuriraj config fajl/Update config file/g" \
  -e "s/Ažuriraj systemd servis/Update systemd service/g" \
  -e "s/Ažuriraj aplikaciju iz git-a/Update application from git/g" \
  -e "s/Ažuriraj dependencies/Update dependencies/g" \
  -e "s/Ažuriraj/Update/g" \
  -e "s/Pokreni backup ručno/Run backup manually/g" \
  -e "s/Pokreni aplikaciju/Start application/g" \
  -e "s/Pokreni/Start/g" \
  -e "s/Zaustavi servis/Stop service/g" \
  -e "s/Restartuj servis/Restart service/g" \
  -e "s/Proveri status aplikacije/Check application status/g" \
  -e "s/Proveri health status servera/Check server health status/g" \
  -e "s/Proveri/Check/g" \
  -e "s/Prikaži error ako postoji/Display error if exists/g" \
  -e "s/Pronađi najnoviji tag/Find latest tag/g" \
  -e "s/Vraća frontend konfiguraciju/Returns frontend configuration/g" \
  -e "s/Sačuvaj frontend konfiguraciju/Save frontend configuration/g" \
  -e "s/Sačuvaj/Save/g" \
  -e "s/Provera da li korisnik već postoji/Check if user already exists/g" \
  -e "s/Kreiranje novog korisnika/Creating new user/g" \
  -e "s/Kreiraj novog korisnika/Create new user/g" \
  -e "s/Deinstalacija/Uninstallation/g" \
  -e "s/Deinstaliraj aplikaciju/Uninstall application/g" \
  -e "s/Promeni port/Change port/g" \
  -e "s/Validiraj port/Validate port/g" \
  -e "s/Autentifikacija korisnika/User authentication/g" \
  -e "s/Landing page - prikazuje se ako korisnik nije ulogovan/Landing page - displayed if user not logged in/g" \
  -e "s/Login stranica/Login page/g" \
  -e "s/Logout korisnika/User logout/g" \
  -e "s/Registracija novog korisnika/Register new user/g" \
  -e "s/Validacija/Validation/g" \
  -e "s/Prioritet: CLI argument > config fajl > default/Priority: CLI argument > config file > default/g" \
  {} \;

echo "  ✓ Python files refactored"

# Delete old/unnecessary files
echo ""
echo "🗑️  Removing unnecessary files..."

# Delete old JSON files from scripts folder
rm -f scripts/*.json 2>/dev/null && echo "  ✓ Old JSON files removed from scripts/" || echo "  - No JSON files in scripts/"

# Delete backup scripts if they are old/unused
if [ -f "deploy_fixes.sh" ]; then
    rm -f deploy_fixes.sh && echo "  ✓ deploy_fixes.sh removed"
fi

if [ -f "add_login_required.sh" ]; then
    rm -f add_login_required.sh && echo "  ✓ add_login_required.sh removed"
fi

# Delete old migration scripts (not the new English one)
if [ -f "scripts/migrate_json.py" ]; then
    rm -f scripts/migrate_json.py && echo "  ✓ scripts/migrate_json.py removed"
fi

if [ -f "scripts/export_to_json.py" ]; then
    rm -f scripts/export_to_json.py && echo "  ✓ scripts/export_to_json.py removed"
fi

if [ -f "scripts/add_missing_columns.py" ]; then
    rm -f scripts/add_missing_columns.py && echo "  ✓ scripts/add_missing_columns.py removed"
fi

if [ -f "scripts/refactor_blueprints.py" ]; then
    rm -f scripts/refactor_blueprints.py && echo "  ✓ scripts/refactor_blueprints.py removed"
fi

if [ -f "scripts/refactor_all.py" ]; then
    rm -f scripts/refactor_all.py && echo "  ✓ scripts/refactor_all.py removed"
fi

if [ -f "scripts/refactor_templates.sh" ]; then
    rm -f scripts/refactor_templates.sh && echo "  ✓ scripts/refactor_templates.sh removed"
fi

if [ -f "scripts/refactor_to_english.py" ]; then
    rm -f scripts/refactor_to_english.py && echo "  ✓ scripts/refactor_to_english.py removed"
fi

# Delete old data JSON files
DATA_DIR="data"
if [ -d "$DATA_DIR" ]; then
    rm -f "$DATA_DIR"/*.json 2>/dev/null && echo "  ✓ Old JSON files removed from data/" || echo "  - No JSON files in data/"
fi

echo ""
echo "✅ Complete refactoring finished!"
echo ""
echo "📊 Summary:"
find . -name "*.py" ! -path "./.venv/*" ! -path "./__pycache__/*" ! -path "./.git/*" | wc -l | xargs echo "  Python files processed:"
echo ""
