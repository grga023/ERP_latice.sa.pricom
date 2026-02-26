#!/bin/bash

set -e

# Boje za output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║     ERP Latice sa Pričom - Setup      ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# ═══════════════════════════════════════════════
# Provera i instalacija sistemskih zavisnosti
# ═══════════════════════════════════════════════
echo -e "${YELLOW}[0/7]${NC} Provera sistemskih zavisnosti..."

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
VENV_PACKAGE="python${PYTHON_VERSION}-venv"

PACKAGES_TO_INSTALL=""

TEST_VENV="/tmp/test_venv_$$"
if ! python3 -m venv "$TEST_VENV" 2>/dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL $VENV_PACKAGE"
else
    rm -rf "$TEST_VENV"
fi

if ! command -v pip3 &>/dev/null; then
    PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL python3-pip"
fi

if [ -n "$PACKAGES_TO_INSTALL" ]; then
    echo -e "${YELLOW}Instalacija paketa:${PACKAGES_TO_INSTALL}${NC}"
    sudo apt update
    sudo apt install -y $PACKAGES_TO_INSTALL
    echo -e "${GREEN}Sistemske zavisnosti instalirane.${NC}"
else
    echo -e "${GREEN}Sve sistemske zavisnosti su već instalirane.${NC}"
fi

echo ""

# ═══════════════════════════════════════════════
# Korisnička konfiguracija
# ═══════════════════════════════════════════════

# Default vrednosti
DEFAULT_INSTALL_DIR="/opt/erp-latice"
DEFAULT_DATA_DIR="$HOME/.erp-latice/data"
DEFAULT_IMG_DIR="$HOME/.erp-latice/img"
DEFAULT_PORT="8000"

# Pitanja za korisnika
read -p "Instalacioni direktorijum [$DEFAULT_INSTALL_DIR]: " INSTALL_DIR
INSTALL_DIR="${INSTALL_DIR:-$DEFAULT_INSTALL_DIR}"

read -p "Data direktorijum [$DEFAULT_DATA_DIR]: " DATA_DIR
DATA_DIR="${DATA_DIR:-$DEFAULT_DATA_DIR}"

read -p "Img direktorijum [$DEFAULT_IMG_DIR]: " IMG_DIR
IMG_DIR="${IMG_DIR:-$DEFAULT_IMG_DIR}"

read -p "Port [$DEFAULT_PORT]: " PORT
PORT="${PORT:-$DEFAULT_PORT}"

echo ""
echo -e "${YELLOW}Konfiguracija:${NC}"
echo "  Instalacija: $INSTALL_DIR"
echo "  Data:        $DATA_DIR"
echo "  Slike:       $IMG_DIR"
echo "  Port:        $PORT"
echo ""

read -p "Nastavi sa instalacijom? [Y/n]: " CONFIRM
CONFIRM="${CONFIRM:-Y}"

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Instalacija otkazana."
    exit 1
fi

# ═══════════════════════════════════════════════
# Instalacija
# ═══════════════════════════════════════════════

# Kreiranje direktorijuma
echo -e "${GREEN}[1/7]${NC} Kreiranje direktorijuma..."
sudo mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$IMG_DIR"

# Kopiranje fajlova
echo -e "${GREEN}[2/7]${NC} Preuzimanje fajlova..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ako instaliramo iz git klona, kopiraj sve
# Ako već postoji instalacija, proveri da li je git repo
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Git repo već postoji, radim pull..."
    cd "$INSTALL_DIR"
    sudo git pull
else
    # Proveri da li source dir ima .git
    if [ -d "$SCRIPT_DIR/.git" ]; then
        # Kloniraj umesto kopiranja
        echo "Kloniranje repozitorijuma..."
        GIT_REMOTE=$(cd "$SCRIPT_DIR" && git remote get-url origin 2>/dev/null || echo "")
        if [ -n "$GIT_REMOTE" ]; then
            sudo rm -rf "$INSTALL_DIR"
            sudo git clone "$GIT_REMOTE" "$INSTALL_DIR"
        else
            # Nema remote, samo kopiraj
            sudo cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
            sudo cp -r "$SCRIPT_DIR"/.git "$INSTALL_DIR/" 2>/dev/null || true
        fi
    else
        # Običan direktorijum, samo kopiraj
        sudo cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    fi
fi

# Postavi vlasnika na trenutnog usera (ne root)
echo -e "${GREEN}[2.5/7]${NC} Postavljanje permisija..."
sudo chown -R $USER:$USER "$INSTALL_DIR"

# Ukloni postojeće data/img ako postoje, napravi symlinkove
echo -e "${GREEN}[3/7]${NC} Kreiranje symlinkova..."
sudo rm -rf "$INSTALL_DIR/data" 2>/dev/null || true
sudo rm -rf "$INSTALL_DIR/img" 2>/dev/null || true
sudo ln -sf "$DATA_DIR" "$INSTALL_DIR/data"
sudo ln -sf "$IMG_DIR" "$INSTALL_DIR/img"

# Python virtual environment
echo -e "${GREEN}[4/7]${NC} Kreiranje Python virtualnog okruženja..."
sudo python3 -m venv "$INSTALL_DIR/venv"
sudo "$INSTALL_DIR/venv/bin/pip" install --upgrade pip

# Instalacija zavisnosti
echo -e "${GREEN}[5/7]${NC} Instalacija Python zavisnosti..."
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    sudo "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
else
    echo -e "${YELLOW}UPOZORENJE: requirements.txt nije pronađen${NC}"
fi

# Kreiranje CLI komande
echo -e "${GREEN}[6/7]${NC} Instalacija 'erp' komande..."

sudo tee /usr/local/bin/erp > /dev/null << 'WRAPPER'
#!/bin/bash
INSTALL_DIR="__INSTALL_DIR__"
source "$INSTALL_DIR/venv/bin/activate"
python "$INSTALL_DIR/cli.py" "$@"
WRAPPER

sudo sed -i "s|__INSTALL_DIR__|$INSTALL_DIR|g" /usr/local/bin/erp
sudo chmod +x /usr/local/bin/erp

# Sačuvaj konfiguraciju
sudo tee "$INSTALL_DIR/.erp.conf" > /dev/null << EOF
INSTALL_DIR=$INSTALL_DIR
DATA_DIR=$DATA_DIR
IMG_DIR=$IMG_DIR
PORT=$PORT
HOST=0.0.0.0
DEBUG=false
VERSION=1.0.0
INSTALLED_DATE=$(date -Is)
EOF

# ═══════════════════════════════════════════════
# Kreiranje systemd servisa
# ═══════════════════════════════════════════════
echo -e "${GREEN}[7/7]${NC} Kreiranje systemd servisa..."

sudo tee /etc/systemd/system/erp-latice.service > /dev/null << EOF
[Unit]
Description=ERP Latice sa Pricom
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/ERP_server.py --port $PORT
Restart=on-failure
RestartSec=5
StandardOutput=append:$DATA_DIR/erp.log
StandardError=append:$DATA_DIR/erp-error.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable erp-latice.service

echo -e "${GREEN}Servis 'erp-latice' kreiran i uključen za autostart.${NC}"

# ═══════════════════════════════════════════════
# Kreiranje backup cron job-a
# ═══════════════════════════════════════════════
echo -e "${GREEN}[8/8]${NC} Kreiranje backup cron job-a..."

# Kopiraj backup skriptu i postavi executable
sudo chmod +x "$INSTALL_DIR/backup.sh"

# Kreiraj logs direktorijum
mkdir -p "$DATA_DIR/logs"

# Dodaj u crontab
CRON_JOB="0 3 * * * $INSTALL_DIR/backup.sh"

# Proveri da li već postoji crontab
if crontab -l 2>/dev/null | grep -q "backup.sh"; then
    echo -e "${YELLOW}Backup cron job već postoji.${NC}"
else
    # Dodaj novi cron job
    (crontab -l 2>/dev/null || echo "") | grep -v "backup.sh" | { cat; echo "$CRON_JOB"; } | crontab -
    
    # Verifikuj
    if crontab -l 2>/dev/null | grep -q "backup.sh"; then
        echo -e "${GREEN}Backup zakazan za 3:00 AM svaki dan.${NC}"
    else
        echo -e "${YELLOW}UPOZORENJE: Nije uspelo automatsko dodavanje cron job-a.${NC}"
        echo -e "${YELLOW}Dodaj ručno sa: crontab -e${NC}"
        echo -e "${YELLOW}Linija: $CRON_JOB${NC}"
    fi
fi

# ═══════════════════════════════════════════════
# Provera Git konfiguracije za backup
# ═══════════════════════════════════════════════
echo -e "${YELLOW}[9/9]${NC} Provera Git konfiguracije..."

if [ -d "$DATA_DIR/.git" ]; then
    echo -e "${GREEN}Git repo već postoji u DATA_DIR.${NC}"
else
    echo -e "${YELLOW}Git repo ne postoji u DATA_DIR.${NC}"
    read -p "Inicijalizovati git repo u $DATA_DIR? [Y/n]: " INIT_GIT
    INIT_GIT="${INIT_GIT:-Y}"
    if [[ "$INIT_GIT" =~ ^[Yy]$ ]]; then
        cd "$DATA_DIR"
        git init
        read -p "Git remote URL (ostaviti prazno za preskočiti): " GIT_REMOTE
        if [ -n "$GIT_REMOTE" ]; then
            git remote add origin "$GIT_REMOTE"
            echo -e "${GREEN}Git remote dodat.${NC}"
        fi
    fi
fi


echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}   Instalacija uspešno završena!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "Server će raditi na: http://0.0.0.0:$PORT"
echo ""
echo "Korišćenje:"
echo "  erp status        - Proveri status"
echo "  erp start         - Pokreni servis"
echo "  erp start -f      - Pokreni u terminalu"
echo "  erp stop          - Zaustavi servis"
echo "  erp restart       - Restartuj servis"
echo "  erp logs -f       - Prati logove"
echo "  erp config        - Prikaži konfiguraciju"
echo "  erp config --edit - Izmeni konfiguraciju"
echo "  erp port 9000     - Promeni port"
echo ""
echo ""
echo -e "${YELLOW}Healthcheck:${NC}"
echo "  curl http://localhost:$PORT/health"
echo ""
echo -e "${YELLOW}Backup:${NC}"
echo "  erp backup        - Ručni backup"
echo "  Automatski backup: svaki dan u 3:00 AM"
echo ""
