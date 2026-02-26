# ⚡ Quick Start Guide - ERP Sistem

Brzi vodič za pokretanje i korišćenje ERP  sistema sa novim autentifikacijskim sistemom i landing page-om.

## 🎯 Za Nove Korisnike

### 1. Instalacija (5 minuta)

**Opcija A: Direktan Download**
```bash
bash <(curl -sSL https://raw.githubusercontent.com/grga023/ERP_latice.sa.pricom/installation/install.sh)
```

**Opcija B: Git Clone**
```bash
git clone https://github.com/grga023/ERP_latice.sa.pricom.git
cd ERP_latice.sa.pricom
./install.sh
```

### 2. Prvo PokretanjeФайл (2 minuta)

```bash
# Pokrenite server
erp start
# ili
python3 ERP_server.py
```

### 3. Kreiranje Naloga (1 minut)

1. Otvorite pretraživač: `http://localhost:8000`
2. Videćete **Landing Page** sa svim mogućnostima
3. Kliknite **"Registruj se"**
4. Popunite formu (prvi korisnik postaje admin!)
5. Kliknite **"Registruj se"**

### 4. Prijavljivanje

1. Nakon registracije, preusmereni ste na login stranicu
2. Unesite korisničko ime i lozinku
3. Kliknite **"Prijavi se"**
4. Dobrodošli u ERP sistem! 🎉

## 📋 Šta Nudi Landing Page?

Kada otvorite `http://localhost:8000` (bez prijave), videćete:

### 🌟 Hero Sekcija
- Glavni naslov i opis sistema
- Dugmad za **registraciju** i **login**
- Brz pristup funkcionalnostima

### 📦 Features Sekcija

**1. Upravljanje Narudžbinama**
- Kreiranje novih narudžbina
- Praćenje statusa dostave
- Evidencija plaćanja
- Detaljna istorija

**2. Skladišno Poslovanje**
- Praćenje stanja zaliha
- Lokacije proizvoda
- Automatska sinkronizacija
- Upozorenja o niskim zalihama

**3. Evidencija Klijenata**
- Kontakt informacije
- Istorija kupovina
- Analiza ponašanja
- Personalizovana komunikacija

**4. Email Notifikacije**
- Nadolazeće dostave
- Niske zalihe
- Nova porudžbina
- Prilagodljivi šabloni

**5. Izveštaji i Analitika**
- Prodajni izveštaji
- Finansijska analiza
- Grafikoni i statistike
- Export u različite formate

**6. Prilagodljiva Konfiguracija**
- Branding opcije
- Konfiguracija email-a
- Valuta i timezone
- Korisničke postavke

### 📊 Stats Sekcija
- 100% Besplatno
- 24/7 Dostupnost
- ∞ Narudžbina
- ⚡ Brzo

### 📞 CTA Sekcija
- Poziv na akciju za registraciju
- Direktan link ka registraciji

## 🔐 Autentifikacijski Sistem

### Login Stranica (`/login`)
- Moderan, responsive dizajn
- Validation u real-time
- "Zapamti me" funkcionalnost
- Link ka registraciji

### Register Stranica (`/register`)
- Jednostavna forma
- Password strength indicator
- Email validacija
- Auto-login nakon registracije

### Zaštita Ruta
- Sve stranice zahtevaju prijavu
- Automatsko preusmeravanje na login
- Sigurne sesije

## 🎨 Dizajn i UX

### Boje
- **Primarna**: #667eea (ljubičasto-plava)
- **Sekundarna**: #764ba2 (tamno ljubičasta)
- **Gradient**: Od #667eea do #764ba2

### Responsive
- Mobilni uređaji ✅
- Tableti ✅
- Desktop ✅

### Animacije
- Hover efekti na dugmadima
- Card hover elevacija
- Smooth scroll
- Fade-in efekti

## 🛠️ Tipične Radnje

### Dodavanje Nove Narudžbine
1. Login kao korisnik
2. Idite na početnu stranicu (`/`)
3. Popunite formu za dodavanje
4. Kliknite "Dodaj porudžbinu"

### Pregled Skladišta
1. Kliknite na "Lager" u navigaciji
2. Videćete sve stavke u skladištu
3. Možete dodati nove stavke ili ažurirati postojeće

### Praćenje  Narudžbina
1. Idite na "Sve porudžbine" (`/porudzbenice`)
2. Filteri i search po kupcima
3. Ažuriranje statusa
4. Brisanje ili izmena narudžbina

### Podešavanje Email Notifikacija
1. Idite na "Podešavanja" (`/podesavanja`)
2. Unesite SMTP podatke
3. Testirajte email
4. Aktivirajte notifikacije

## 🔧 Konfiguracija

### Promena Porta
```bash
# U CLI-u
python3 ERP_server.py --port 9000

# Ili u .erp.conf
PORT=9000
```

### Dodavanje Branding-a
1. Login kao admin
2. Idite na `/config`
3. Upload logo, favicon
4. Sačuvajte promene

### Postavljanje Email-a
1. Idite na `/podesavanja`
2. Unesite:
   - Gmail adresa
   - App password (ne obična lozinka!)
   - Receiver email(s)
3. Test email
4. Enable notifications

## 📱 Mobilni Pristup

ERP sistem je potpuno responsive:

```
http://[your-server-ip]:8000
```

Na mobilnom uređaju:
- Sve funkcije dostupne
- Touch-optimized
- Brz i efikasan

## 🚀 Deployment u Produkciju

### Sa Nginx
```nginx
server {
    server_name erp.mojdomen.rs;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Sa Cloudflare Tunnel
```bash
cloudflared tunnel create erp
cloudflared tunnel route dns erp erp.mojdomen.rs
cloudflared tunnel run erp --url http://localhost:8000
```

## 📊 Healthcheck

Proverite da li server radi:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

## ❓ Troubleshooting

### Landing Page se ne učitava
```bash
# Proverite da li server radi
erp status

# Pogledajte logove
erp logs
```

### Ne mogu da se registrujem
```bash
# Proverite da li database postoji
ls -la data/erp.db

# Ako ne postoji, reinicijalizujte
rm data/erp.db
erp restart
```

### "Morate biti ulogovani" poruka
```bash
# Očistite cookies i prijavite se ponovo
# Ili proverite sesiju u browseru
```

## 🎓 Dalje Korišćenje

Nakon što ste se prijavili:

1. **Početna stranica** → Dodajte narudžbine
2. **Lager** → Upravljajte zalihama
3. **Sve porudžbine** → Pratite statuse
4. **Realizovano** → Pregledajte završene
5. **Podešavanja** → Aktivirajte email notifikacije
6. **Config** → Prilagodite branding

## 📚 Dodatna Dokumentacija

- [README.md](../README.md) - Kompletan pregled
- [AUTHENTICATION.md](AUTHENTICATION.md) - Detalji o autentifikaciji
- [INSTALL.md](../INSTALL.md) - Instalacione instrukcije
- [BACKUP_SETUP.md](BACKUP_SETUP.md) - Backup konfiguracija

## 💡 Pro Tips

1. **Prvi korisnik je admin** - Budite sigurni da je to vaš nalog!
2. **Backup redovno** - Koristite `erp backup` ili automatski cron
3. **Email notifikacije** - Postavi Gmail App Password, ne običnu lozinku
4. **Branding** - Dodajte logo za profesionalan izgled
5. **Mobilni pristup** - Sve radi na telefonu!

## 🎉 To je to!

Vaš ERP sistem je spreman za korišćenje. Uživajte! 🚀

---

**Pitanja?** Otvorite issue na GitHub-u ili nas kontaktirajte.

**© 2024-2026 Latice sa Pričom - Sva prava zadržana**
