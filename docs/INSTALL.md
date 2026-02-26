# Installation Instructions - Simple ERP

## 🚀 Fast Installation (Recommended)

### Option 1: Direct Download & Installation (EASIEST)

You only need to run one command in the terminal:

```bash
sudo bash <(curl -sSL https://raw.githubusercontent.com/your-username/ERP_latice.sa.pricom/main/install.sh)
```

**That's it!** The script will automatically:
- ✅ Download all necessary files
- ✅ Install Python dependencies
- ✅ Create virtual environment
- ✅ Set up all configurations
- ✅ Start the service

> **Note:** Replace `your-username` with your GitHub username!

### Option 2: With Cloned Repository

If you already have the repository cloned:

```bash
git clone https://github.com/your-username/ERP_latice.sa.pricom.git
cd ERP_latice.sa.pricom
sudo ./install.sh
```

---

## 📋 What the Script Does Automatically

When you run `install.sh`, it will:

1. **System Dependencies Check**
   - Python 3.8+
   - pip & venv

2. **Business Configuration** (Answer a few questions)
   - Business name
   - Email, phone, address
   - Currency and timezone

3. **Technical Configuration**
   - Installation directories
   - Server port
   - Public URL (if you have one)

4. **Automatic Installations**
   - Python virtual environment
   - Flask and all dependencies
   - SQLite database
   - System user

5. **Service Installation**
   - Creating `erp` command
   - Systemd service for autostart
   - Cron job for daily backups

---

## 🎯 What You Need At The Start?

### Minimum:
- Linux system (Ubuntu, Debian, CentOS etc.)
- Internet connection
- sudo access

### Optional:
- Branding images (logo, favicon)
- Git access for cloud backup

---

## 💻 Installation Example

```bash
# 1. Download and run
$ sudo bash <(curl -sSL https://raw.githubusercontent.com/your-username/ERP_latice.sa.pricom/main/install.sh)

╔═══════════════════════════════════════╗
║     Simple ERP Tracking - Setup       ║
╚═══════════════════════════════════════╝

[0/10] Checking system dependencies...
All system dependencies are already installed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           BUSINESS SETUP              
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Business name [My Business]: Simple ERP Store
Short name (for navbar) [Simple ERP Store]: Simple ERP
Business email []: info@simple-erp.com
Business phone []: +1 234 567 8900
Business address []: New York, USA
Website []: https://simple-erp.com
Currency [RSD]: USD
Timezone [Europe/Belgrade]: America/New_York

# ... (system will show configuration preview)

Continue with installation? [Y/n]: y

[2/10] Downloading files...
[3/10] Setting permissions...
[4/10] Creating symlinks...
[5/10] Creating Python virtual environment...
[6/10] Installing Python dependencies...
[7/10] Installing 'erp' command...
[8/10] Saving configuration...
[9/10] Creating systemd service...
[10/10] Creating backup cron job...

════════════════════════════════════════════════
       Installation completed successfully!      
════════════════════════════════════════════════

Server:
  Local:    http://localhost:8000
  Public:   https://simple-erp.com (if configured)

Commands:
  erp start         - Start service
  erp stop          - Stop service
  erp restart       - Restart service
  erp status        - Check status
  erp logs -f       - Follow logs

Start service with: erp start
```

---

## ✅ Getting Started

### 1. Start the Service
```bash
erp start
```

### 2. Open in Browser
```
http://localhost:8000
```

### 3. Add Branding (Optional)
```bash
http://localhost:8000/config
```

Or manually add images:
```
~/.erp/images/branding/logo.png
~/.erp/images/branding/logo-small.png
~/.erp/images/branding/favicon.ico
```

---

## 📝 Available Commands

```bash
# Service Control
erp start          # Start the service
erp stop           # Stop the service
erp restart        # Restart the service
erp status         # Check status
erp logs -f        # Follow logs (Ctrl+C to exit)

# Admin
erp info           # All system information
erp config         # Check configuration
erp backup         # Manual backup
erp update         # Update from Git
erp health         # Healthcheck

# CLI operations
erp cli --help     # CLI help
```

---

## 🔧 Port Forwarding

If you want to access from another computer or the internet:

### Nginx Proxy Setup
```nginx
server {
    server_name simple-erp.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Cloudflare Tunnel (Easiest)
```bash
cloudflared tunnel create simple-erp
cloudflared tunnel route dns simple-erp simple-erp.com
cloudflared tunnel run simple-erp --url http://localhost:8000
```

---

## 🆘 Troubleshooting

### Problem: "command not found: erp"
**Solution:**
```bash
# Logout and login again, or:
source ~/.bashrc
# or
sudo systemctl restart erp
```

### Problem: "Permission denied"
**Solution:**
```bash
sudo chmod +x /usr/local/bin/erp
sudo chown $USER:$USER ~/.erp/
```

### Problem: "Port already in use"
**Solution:**
```bash
# Change port in .erp.conf
sudo nano ~/.erp/config.json
# Change "PORT": 8000 to "PORT": 8001
# Restart: erp restart
```

### Problem: "Not accessible from internet"
**Solution:**
- Check firewall: `sudo ufw allow 8000/tcp`
- Check port forwarding on your router
- Use Cloudflare Tunnel (recommended)

---

## 🛡️ Security

### Change Default Configuration
```bash
sudo nano ~/.erp/.erp.conf
```

Recommendations:
- Set `DEBUG=false` in production
- Use HTTPS (Cloudflare, Let's Encrypt)
- Backup your data regularly
- Keep system updated: `erp update`

---

## 📦 Backup & Restore

### Automatic Backup (3:00 AM daily)
Already set up during installation.

### Manual Backup
```bash
erp backup
# Or
~/ERP_latice.sa.pricom/backup.sh
```

### Restore from Backup
```bash
# Find backup
cd ~/.erp/backups/
tar -xzf backup_DATE.tar.gz
```

---

## 🪜 Uninstallation

```bash
# Stop the service
erp stop

# Remove everything
sudo rm -rf /opt/erp
sudo rm -rf ~/.erp
sudo rm /usr/local/bin/erp
sudo systemctl disable erp.service
sudo rm /etc/systemd/system/erp.service

# Remove cron job
crontab -e
# Delete line with backup.sh
```

---

## 📱 Support

- **GitHub Issues:** https://github.com/your-username/ERP_latice.sa.pricom/issues
- **Email:** support@simple-erp.com
- **Documentation:** See [README.md](README.md)

---

**© 2024-2026 Simple ERP - All rights reserved**

Good luck with your ERP system! 🚀
