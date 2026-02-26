# Instalacione Instrukcije - Latice sa Pričom ERP

## 🚀 Brza Instalacija (Preporučeno)

### Opcija 1: Direktan Download & Instalacija (NAJJEDNOSTAVNIJE)

Trebate samo da pokrenete jednu komandu u terminalu:

```bash
sudo bash <(curl -sSL https://raw.githubusercontent.com/your-username/ERP_latice.sa.pricom/main/install.sh)
```

**To je sve!** Script će automatski:
- ✅ Preuzeti sve potrebne fajlove
- ✅ Instalirati Python zavisnosti
- ✅ Kreirati virtualnog okruženja
- ✅ Podesiti sve konfiguracije
- ✅ Pokrenuti servis

> **Napomena:** Zamjenite `your-username` sa vašim GitHub korisničkim imenom!

### Opcija 2: Sa Kloniranim Repo-jem

Ako već imate kloniran repositorijum:

```bash
git clone https://github.com/your-username/ERP_latice.sa.pricom.git
cd ERP_latice.sa.pricom
sudo ./install.sh
```

---

## 📋 Šta Script Radi Automatski

Kada pokrenete `install.sh`, on će:

1. **Provera sistemskih zavisnosti**
   - Python 3.8+
   - pip & venv

2. **Branding Konfiguracija** (Odgovoriće na par pitanja)
   - Naziv biznisa
   - Email, telefon, adresa
   - Valuta i vremensku zonu

3. **Tehnička Konfiguracija**
   - Instalacione direktorijume
   - Port servera
   - Javni URL (ako imate)

4. **Automatske Instalacije**
   - Python virtualnom okruženju
   - Flask i sve zavisnosti
   - SQLite bazu podataka
   - Sys

5. **Instalacija Servisa**
   - Kreiranje `erp` komande
   - Systemd servis za autostart
   - Cron job za dnevne backup-e

---

## 🎯 Što Trebate Na Početku?

### Minimalno:
- Linux sistem (Ubuntu, Debian, CentOS itd.)
- Internet konekcija
- sudo pristup

### Opcionalno:
- Branding slike (logo, favicon)
- Git pristup za cloud backup

---

## 💻 Primjer Instalacije

```bash
# 1. Preuzmi i pokreni
$ sudo bash <(curl -sSL https://raw.githubusercontent.com/your-username/ERP_latice.sa.pricom/main/install.sh)

╔═══════════════════════════════════════╗
║     Simple ERP Tracking - Setup       ║
╚═══════════════════════════════════════╝

[0/10] Provera sistemskih zavisnosti...
Sve sistemske zavisnosti su već instalirane.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           PODEŠAVANJE BIZNISA          
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Naziv biznisa [Moj Biznis]: Latice sa Pričom
Kratak naziv (za navbar) [Latice sa Pričom]: Latice
Email biznisa []: info@latice.rs
Telefon biznisa []: +381 11 123 4567
Adresa biznisa []: Beograd, Srbija
Website []: https://latice.rs
Valuta [RSD]: RSD
Timezone [Europe/Belgrade]: Europe/Belgrade

# ... (sistem će pokazati preview konfiguracije)

Nastavi sa instalacijom? [Y/n]: y

[2/10] Preuzimanje fajlova...
[3/10] Postavljanje permisija...
[4/10] Kreiranje symlinkova...
[5/10] Kreiranje Python virtualnog okruženja...
[6/10] Instalacija Python zavisnosti...
[7/10] Instalacija 'erp' komande...
[8/10] Čuvanje konfiguracije...
[9/10] Kreiranje systemd servisa...
[10/10] Kreiranje backup cron job-a...

════════════════════════════════════════════════
       Instalacija uspešno završena!            
════════════════════════════════════════════════

Server:
  Lokalni:  http://localhost:8000
  Javni:    https://latice.rs (ako je postavljeno)

Komande:
  erp start         - Pokreni servis
  erp stop          - Zaustavi servis
  erp restart       - Restartuj servis
  erp status        - Proveri status
  erp logs -f       - Prati logove

Pokreni servis sa: erp start
```

---

## ✅ Početak Rada

### 1. Pokrenite Servis
```bash
erp start
```

### 2. Otvorite u Pretraživaču
```
http://localhost:8000
```

### 3. Dodajte Branding (Opcionalno)
```bash
http://localhost:8000/config
```

Ili ručno dodajte slike:
```
~/.erp/images/branding/logo.png
~/.erp/images/branding/logo-small.png
~/.erp/images/branding/favicon.ico
```

---

## 📝 Dostupne Komande

```bash
# Kontrola Servisa
erp start          # Pokrenite servis
erp stop           # Zaustavite servis
erp restart        # Restartujte servis
erp status         # Provera statusa
erp logs -f        # Prati logove (Ctrl+C za izlaz)

# Admin
erp info           # Sve informacije o sistemu
erp config         # Provera konfiguracije
erp backup         # Ručni backup
erp update         # Ažuriranje iz Git-a
erp health         # Healthcheck

# CLI operacije
erp cli --help     # CLI pomoć
```

---

## 🔧 Preusmeravanje Portova

Ako želite da pristupite sa drugi računara ili internet-a:

### Nginx Proxy Setup
```nginx
server {
    server_name latice.rs;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Cloudflare Tunnel (Najjednostavnije)
```bash
cloudflared tunnel create latice
cloudflared tunnel route dns latice latice.rs
cloudflared tunnel run latice --url http://localhost:8000
```

---

## 🆘 Rešavanje Problema

### Problem: "command not found: erp"
**Rešenje:**
```bash
# Odjava i ponovna prijava, ili:
source ~/.bashrc
# ili
sudo systemctl restart erp
```

### Problem: "Permission denied"
**Rešenje:**
```bash
sudo chmod +x /usr/local/bin/erp
sudo chown $USER:$USER ~/.erp/
```

### Problem: "Port već u upotrebi"
**Rešenje:**
```bash
# Promenite port u .erp.conf
sudo nano ~/.erp/config.json
# Promenite "PORT": 8000 u "PORT": 8001
# Restartujte: erp restart
```

### Problem: "Nije dostupan iz interneta"
**Rešenje:**
- Proverate firewall: `sudo ufw allow 8000/tcp`
- Proverat port forwarding na routeru
- Koristite Cloudflare Tunnel (preporučeno)

---

## 🛡️ Bezbednost

### Promenite Podrazumevanu Konfiguraciju
```bash
sudo nano ~/.erp/.erp.conf
```

Preporuke:
- Postavite `DEBUG=false` u produkciji
- Koristite HTTPS (Cloudflare, Let's Encrypt)
- Redovno backup-ujte podatke
- Ažurirajte sistem: `erp update`

---

## 📦 Backup & Restore

### Automatski Backup (3:00 AM svaki dan)
Već je postavljen tokom instalacije.

### Ručni Backup
```bash
erp backup
# Ili
~/ERP_latice.sa.pricom/backup.sh
```

### Restore iz Backup-a
```bash
# Locite backup
cd ~/.erp/backups/
tar -xzf backup_DATE.tar.gz
```

---

## 🪜 Odinstalacija

```bash
# Zaustavi servis
erp stop

# Uklonite sve
sudo rm -rf /opt/erp
sudo rm -rf ~/.erp
sudo rm /usr/local/bin/erp
sudo systemctl disable erp.service
sudo rm /etc/systemd/system/erp.service

# Uklonite cron job
crontab -e
# Obrišite liniju sa backup.sh
```

---

## 📱 Podrška

- **GitHub Issues:** https://github.com/your-username/ERP_latice.sa.pricom/issues
- **Email:** info@latice.rs
- **Dokumentacija:** Pogledajte [README.md](README.md)

---

**© 2024-2026 Latice sa Pričom - Sve prava zadržana**

Sretno sa vašim ERP sistemom! 🚀
