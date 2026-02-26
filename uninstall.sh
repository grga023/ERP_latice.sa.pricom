#!/bin/bash
set -e

echo "ERP Latice - Deinstalacija"
echo ""

# Učitaj config ako postoji
if [ -f "/opt/erp-latice/.erp.conf" ]; then
    source "/opt/erp-latice/.erp.conf"
fi

read -p "Obriši instalaciju? Data i img ostaju. [y/N]: " CONFIRM

if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
    sudo rm -rf "${INSTALL_DIR:-/opt/erp-latice}"
    sudo rm -f /usr/local/bin/erp
    echo "Deinstalirano."
else
    echo "Otkazano."
fi
