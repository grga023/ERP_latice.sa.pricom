#!/bin/bash
# Start dashboard for systemd

cd /opt/appl/scripts/ERP_T/ERP_latice.sa.pricom

# Start Python server in foreground and log to journal
exec python3 ERP_server.py
