# 🔐 Vodič za Autentifikaciju - ERP Sistem

## 📋 Pregled

ERP sistem sada zahteva autentifikacijevim korisnika pre pristupa bilo kojoj funkcionalnosti. Ovo osigurava da samo ovlašćeni korisnici mogu da pristupe podacima.

## 🚀 Prvi Korak - Registracija Prvog Korisnika

### 1. Pokrenite Server
```bash
python3 ERP_server.py
# ili
erp start
```

### 2. Otvorite Pretraživač
```
http://localhost:8000
```

### 3. Kreirajte Prvi Nalog
- Kliknite na **"Registruj se"** dugme
- Popunite formu:
  - **Korisničko ime**: Vaše jedinstveno korisničko ime
  - **Email**: Vaša email adresa
  - **Lozinka**: Sigurna lozinka (minimum 6 karaktera)
  - **Potvrda lozinke**: Ponovite lozinku

⚡ **VAŽNO**: Prvi korisnik automatski postaje **administrator** sa punim pristupom!

## 👤 Prijavljivanje

### Standardna Prijava
1. Idite na `/login` ili kliknite "Prijavi se"
2. Unesite korisničko ime i lozinku
3. Kliknite "Prijavi se"

### Automatska Prijava
- Sesija se automatski čuva
- Ne morate se stalno prijavljivati
- Sesija ostaje aktivna i nakon zatvaranja pretraživačastrana

## 🔑 Tipovi Korisnika

### Administrator
- **Prvi korisnik** koji se registruje
- Pun pristup svim funkcijama
- Može dodavati/brisati/menjati korisnike (u budućnosti)
- Može menjati sve konfiguracije

### Standardni Korisnik
- Pristup osnovnim funkcijama
- Može dodavati narudžbine
- Može pregledati lager
- Ne može menjati sistemske postavke

## 🛡️ Bezbednost

### Lozinke
- Šifrovane pomoću `werkzeug.security` 
- Koriste se bcrypt hash algoritmi
- Nikada se ne čuvaju u plain text formatu

### Sesije
- Automatski upravljane pomoću Flask-Login
- Siguran cookie-based sistem
- Automatic timeout nakon neaktivnosti

### Zaštita Ruta
- Sve stranice zaštićene sa `@login_required`
- Automatsko preusmeravanje na login stranicu
- API endpoint takođe zahtevaju autentifikaciju

## 📱 Funkcionalnosti Sistema

### Landing Page
- **URL**: `http://localhost:8000/`
- Prikazuje se samo za neulogovane korisnike
- Lista svih funkcionalnosti
- Dugmad za registraciju i prijavu

### Glavna Stranica (Dashboard)
- **URL**: `http://localhost:8000/index.html`
- Prikazuje se nakon uspešne prijave
- Dodavanje novih narudžbina
- Brzi pregled statusa

### Ostale Stranice
- `/porudzbenice` - Sve narudžbine
- `/realizovano` - Realizovane narudžbine
- `/za-dostavu` - Narudžbine za dostavu
- `/lager` - Skladište
- `/config` - Konfiguracija
- `/podesavanja` - Email podešavanja

## 🔧 Administratorske Opcije

### Reset Lozinke (Planirana funkcionalnost)
```python
# Preko CLI-a
python cli.py reset-password <username>
```

### Dodavanje Novog Korisnika (Planirana funkcionalnost)
```python
# Preko CLI-a
python cli.py add-user --username <name> --email <email> --admin
```

## ❓ Česta Pitanja (FAQ)

### Kako da resetujem lozinku?
Trenutno ne postoji automatski način. Kontaktirajte administratora ili ručno obrišite bazu i kreirajte novi nalog.

### Mogu li imati više administratora?
Da, ali trenutno samo prvi korisnik automatski postaje admin. Ostale administragore treba manuelno dodati.

### Šta ako zaboravim lozinku?
Trenutno morate ručno resetovati bazu ili kontaktirati administratora. Email reset funkcionalnost je planirana za buduće verzije.

### Kako da obrišem korisnika?
Administratori mogu obrisati korisnike direktno iz baze podataka ili preko planiranog admin panela.

### Da li mogu da promenim email nakon registracije?
Trenutno ne. Ova funkcionalnost je planirana za buduće verzije.

## 🛠️ Troubleshooting

### Problem: "Morate biti ulogovani..."
**Rešenje**: Vaša sesija je istekla. Prijavite se ponovo na `/login`.

### Problem: "Korisničko ime već postoji"
**Rešenje**: Izaberite drugo korisničko ime ili prijavite se sa postojećim nalogom.

### Problem: "Lozinke se ne podudaraju"
**Rešenje**: Proverite da ste pravilno uneli lozinku dva puta.

### Problem: Ne mogu da pristupim ni jednoj stranici
**Rešenje**: 
1. Proverite da li ste ulogovani
2. Očistite cookies u pretraživachu
3. Prijavite se ponovo

### Problem: Server se ne pokreće nakon izmene
**Rešenje**:
```bash
# Reinstalirajte zavisnosti
pip install -r requirements.txt

# Ili sa install.sh
./install.sh
```

## 📊 Baza Podataka

### User Tabela
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at VARCHAR(50)
);
```

### Direktan Pristup Bazi
```bash
# Otvorite SQLite bazu
sqlite3 data/erp.db

# Pogledajte sve korisnike
SELECT * FROM users;

# Napravite korisnika admin-om
UPDATE users SET is_admin = 1 WHERE username = 'ime_korisnika';
```

## 🔄 Upgrade sa Starije Verzije

Ako imate staru verziju bez autentifikacije:

1. **Backup podataka**:
```bash
./backup.sh
```

2. **Reinstalirajte zavisnosti**:
```bash
pip install -r requirements.txt
```

3. **Pokrenite server**:
```bash
python3 ERP_server.py
```

4. **Registrujte prvog korisnika**

Svi vaši podaci iz orders i lager tabela ostaju netaknuti!

## 📞 Podrška

Za dodatna pitanja ili problem:
- GitHub Issues: https://github.com/grga023/ERP_latice.sa.pricom/issues
- Email: info@latice.rs

---

**© 2024-2026 Latice sa Pričom - Sva prava zadržana**

Verzija: 1.0.0 (sa autentifikacijom)
