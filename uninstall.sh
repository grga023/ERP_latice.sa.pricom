#!/bin/bash
set -e

echo "ERP Latice - Uninstallation"
echo ""

# Load config if exists
if [ -f "/opt/erp-latice/.erp.conf" ]; then
    source "/opt/erp-latice/.erp.conf"
fi

read -p "Delete installation? Data and img will remain. [y/N]: " CONFIRM

if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
    sudo rm -rf "${INSTALL_DIR:-/opt/erp-latice}"
    sudo rm -f /usr/local/bin/erp
    echo "Uninstalled."
else
    echo "Cancelled."
fi
