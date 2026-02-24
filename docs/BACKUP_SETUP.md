# Automatski dnevni backup baze u JSON fajlove

## Šta radi?
Skripta `export_to_json.py` izvozi sve podatke iz SQLite baze u JSON fajlove u `data/` folderu. Ovo kreira snapshot baze podataka koji može da posluži kao backup.

## Kako pokrenuti ručno?
```bash
python export_to_json.py
```

## Automatsko pokretanje svaki dan u 3 ujutru

### Linux / Raspberry Pi (koristi cron)

1. **Učini `run_export.sh` izvršnim:**
```bash
chmod +x run_export.sh
```

2. **Kreiraj logs folder:**
```bash
mkdir -p logs
```

3. **Otvori crontab:**
```bash
crontab -e
```

4. **Dodaj sledeću liniju na kraju fajla:**
```
0 3 * * * /opt/appl/scripts/ERP_T/ERP_latice.sa.pricom/run_export.sh
```
(Prilagodi putanju ako je projekat negde drugde!)

5. **Sačuvaj i zatvori editor** (Ctrl+X, zatim Y, zatim Enter)

6. **Proveri da li je cron job dodat:**
```bash
crontab -l
```

### Windows (koristi Task Scheduler)

1. **Otvori Task Scheduler** (Start → Task Scheduler)

2. **Klikni "Create Basic Task"**

3. **Ime zadatka:** "ERP Database Backup"

4. **Trigger:** Daily, u 3:00 AM

5. **Action:** Start a program
   - Program/script: `python`
   - Add arguments: `export_to_json.py`
   - Start in: `D:\DSUser\uif80506\ERP_latice.sa.pricom`

6. **Završi i testiranje klikni desni klik → "Run"**

## Provera da li radi

- **Linux:** Proveri log fajl:
```bash
cat logs/export_backup.log
```

- **Windows:** Proveri Task Scheduler → Task History

## Šta se izvozi?

- `data/new_ord.json` - Nove porudžbine
- `data/for_delivery.json` - Porudžbine za dostavu
- `data/realized.json` - Realizovane porudžbine
- `data/lager.json` - Svi artikli iz lagera
- `data/email_config.json` - Email konfiguracija
- `data/notified.json` - Log o poslatim notifikacijama

## Napomene

- Backup se **prepisuje svaki put** - ako želiš da čuvaš historiju, dodaj datum u ime fajla
- JSON fajlovi su sada **izvor podataka za restore** - čuvaj ih na sigurnom mestu!
