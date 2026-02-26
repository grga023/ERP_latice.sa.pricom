#!/bin/bash

set -e

# Boje za output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════
# GLOBAL VARIABLES
# ═══════════════════════════════════════════════
# Replace with your actual GitHub username
GIT_REPO="https://github.com/grga023/Simple_ERP.git"

# Detektuj branch ili tag
CURRENT_BRANCH=""

# Parsiraj argumente (-b za branch)
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--branch)
            CURRENT_BRANCH="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# If branch is not provided as argument, try to detect
if [ -z "$CURRENT_BRANCH" ]; then
    # Try to find latest tag with "_stabile" in name
    if command -v git &>/dev/null; then
        STABLE_TAG=$(git ls-remote --tags "$GIT_REPO" | grep "_stabile" | awk '{print $2}' | sed 's|refs/tags/||' | sed 's/\^{}//' | sort -V | tail -1 2>/dev/null || echo "")
        if [ -n "$STABLE_TAG" ]; then
            CURRENT_BRANCH="$STABLE_TAG"
        else
            CURRENT_BRANCH="master"
        fi
    else
        CURRENT_BRANCH="master"
    fi
fi

echo -e "${CYAN}Instalacija Simple ERP Tracking - Branch/Tag: ${CURRENT_BRANCH}${NC}"

# ═══════════════════════════════════════════════
# STANDALONE MODE INFORMATION
# ═══════════════════════════════════════════════
# This script can be used in two ways:
#
# 1. DOWNLOAD MODE - from 'installation' branch (recommended):
#    bash <(curl -sSL https://raw.githubusercontent.com/grga023/ERP_latice.sa.pricom/installation/install.sh)
#
# 2. DOWNLOAD MODE - from custom branch/tag:
#    bash <(curl -sSL https://raw.githubusercontent.com/grga023/ERP_latice.sa.pricom/installation/install.sh) -b v3.0_stabile
#
# 3. LOCAL MODE (executed from cloned repository):
#    git clone https://github.com/grga023/ERP_latice.sa.pricom.git
#    cd ERP_latice.sa.pricom
#    ./install.sh
#    or with specific branch:
#    ./install.sh -b develop
#
# ═══════════════════════════════════════════════

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║     Simple ERP Tracking - Setup       ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# ═══════════════════════════════════════════════
# Check and install system dependencies
# ═══════════════════════════════════════════════
echo -e "${YELLOW}[0/10]${NC} Provera sistemskih zavisnosti..."

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
# Branding konfiguracija
# ═══════════════════════════════════════════════
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}           PODEŠAVANJE BIZNISA          ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Naziv biznisa [Moj Biznis]: " BUSINESS_NAME
BUSINESS_NAME="${BUSINESS_NAME:-Moj Biznis}"

read -p "Kratak naziv (za navbar) [${BUSINESS_NAME}]: " BUSINESS_SHORT_NAME
BUSINESS_SHORT_NAME="${BUSINESS_SHORT_NAME:-$BUSINESS_NAME}"

read -p "Email biznisa []: " BUSINESS_EMAIL

read -p "Telefon biznisa []: " BUSINESS_PHONE

read -p "Adresa biznisa []: " BUSINESS_ADDRESS

read -p "Website []: " BUSINESS_WEBSITE

read -p "Valuta [RSD]: " CURRENCY
CURRENCY="${CURRENCY:-RSD}"

read -p "Timezone [Europe/Belgrade]: " TIMEZONE
TIMEZONE="${TIMEZONE:-Europe/Belgrade}"

echo ""

# ═══════════════════════════════════════════════
# Technical configuration
# ═══════════════════════════════════════════════
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}        TEHNIČKA KONFIGURACIJA          ${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Default vrednosti
DEFAULT_INSTALL_DIR="/opt/.erp"
DEFAULT_DATA_DIR="/usb/ERP_data/data"
DEFAULT_IMG_DIR="/usb/ERP_data/images"
DEFAULT_PORT="8000"
DEFAULT_VERSION="1.0.0"

read -p "Instalacioni direktorijum [$DEFAULT_INSTALL_DIR]: " INSTALL_DIR
INSTALL_DIR="${INSTALL_DIR:-$DEFAULT_INSTALL_DIR}"

read -p "Data direktorijum [$DEFAULT_DATA_DIR]: " DATA_DIR
DATA_DIR="${DATA_DIR:-$DEFAULT_DATA_DIR}"

read -p "Img direktorijum [$DEFAULT_IMG_DIR]: " IMG_DIR
IMG_DIR="${IMG_DIR:-$DEFAULT_IMG_DIR}"

read -p "Port [$DEFAULT_PORT]: " PORT
PORT="${PORT:-$DEFAULT_PORT}"

read -p "Javni URL (Cloudflare, ostaviti prazno ako nema) []: " PUBLIC_URL

echo ""
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}           PREGLED KONFIGURACIJE       ${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Biznis:${NC}"
echo "  Naziv:        $BUSINESS_NAME"
echo "  Kratak naziv: $BUSINESS_SHORT_NAME"
echo "  Email:        ${BUSINESS_EMAIL:-N/A}"
echo "  Telefon:      ${BUSINESS_PHONE:-N/A}"
echo "  Adresa:       ${BUSINESS_ADDRESS:-N/A}"
echo "  Website:      ${BUSINESS_WEBSITE:-N/A}"
echo "  Valuta:       $CURRENCY"
echo "  Timezone:     $TIMEZONE"
echo ""
echo -e "${CYAN}Tehnički:${NC}"
echo "  Instalacija:  $INSTALL_DIR"
echo "  Data:         $DATA_DIR"
echo "  Slike:        $IMG_DIR"
echo "  Port:         $PORT"
if [ -n "$PUBLIC_URL" ]; then
    echo "  Javni URL:    $PUBLIC_URL"
fi
echo ""

read -p "Nastavi sa instalacijom? [Y/n]: " CONFIRM
CONFIRM="${CONFIRM:-Y}"

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Instalacija otkazana."
    exit 1
fi

# ═══════════════════════════════════════════════
# Installation
# ═══════════════════════════════════════════════

# Copy files
echo -e "${GREEN}[2/10]${NC} Preuzimanje fajlova..."

# Detect where script is executed
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_SOURCE="${BASH_SOURCE[0]}"

# If script is executed from /tmp or pipe (e.g. `bash <(curl ...)`), we need to clone
if [[ "$SCRIPT_SOURCE" == "/dev/stdin" ]] || [[ "$SCRIPT_DIR" == "/tmp"* ]] || [[ ! -d "$SCRIPT_DIR/.git" && ! -f "$SCRIPT_DIR/ERP_server.py" ]]; then
    TEMP_CLONE_DIR=$(mktemp -d)
    echo -e "${CYAN}Preuzimam repository ($CURRENT_BRANCH)...${NC}"
    
    # Try git clone first
    if command -v git &>/dev/null; then
        read -p "Git branch/tag [$CURRENT_BRANCH]: " BRANCH_INPUT
        CURRENT_BRANCH="${BRANCH_INPUT:-$CURRENT_BRANCH}"
        
        if git clone -b "$CURRENT_BRANCH" "$GIT_REPO" "$TEMP_CLONE_DIR" 2>/dev/null; then
            SCRIPT_DIR="$TEMP_CLONE_DIR"
            echo -e "${GREEN}Repository kloniran iz grane/tag-a: $CURRENT_BRANCH${NC}"
        else
            echo -e "${RED}Greška: Ne mogu da kloniram repository sa granom/tag-om: $CURRENT_BRANCH${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Greška: git nije instaliran${NC}"
        exit 1
    fi
else
    # Executed from local directory with files
    # Detect branch from local git repository
    LOCAL_BRANCH=$(cd "$SCRIPT_DIR" && git branch --show-current 2>/dev/null || echo "")
    if [ -n "$LOCAL_BRANCH" ]; then
        CURRENT_BRANCH="$LOCAL_BRANCH"
    fi
    TEMP_CLONE_DIR=""
fi

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Git repo već postoji, radim pull..."
    cd "$INSTALL_DIR"
    sudo git fetch --all
    sudo git checkout "$CURRENT_BRANCH" 2>/dev/null || sudo git checkout -b "$CURRENT_BRANCH" "origin/$CURRENT_BRANCH" 2>/dev/null || true
    sudo git pull origin "$CURRENT_BRANCH" || true
else
    echo "Kopiranje fajlova u $INSTALL_DIR..."
    sudo rm -rf "$INSTALL_DIR"
    sudo cp -r "$SCRIPT_DIR" "$INSTALL_DIR"
    
    # If ".git" directory exists, copy it with special permissions
    if [ -d "$SCRIPT_DIR/.git" ]; then
        sudo cp -r "$SCRIPT_DIR/.git" "$INSTALL_DIR/" 2>/dev/null || true
    fi
fi

# Clean temp clone if it's real
if [ -n "$TEMP_CLONE_DIR" ] && [ -d "$TEMP_CLONE_DIR" ]; then
    rm -rf "$TEMP_CLONE_DIR"
fi

# Set owner to current user
echo -e "${GREEN}[3/10]${NC} Postavljanje permisija..."
sudo chown -R $USER:$USER "$INSTALL_DIR"

# Remove existing data/img if they exist, create symlinks
echo -e "${GREEN}[4/10]${NC} Kreiranje symlinkova..."
rm -rf "$INSTALL_DIR/data" 2>/dev/null || true
rm -rf "$INSTALL_DIR/images" 2>/dev/null || true
ln -sf "$DATA_DIR" "$INSTALL_DIR/data"
ln -sf "$IMG_DIR" "$INSTALL_DIR/images"

# Python virtual environment
echo -e "${GREEN}[5/10]${NC} Kreiranje Python virtualnog okruženja..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip

# Instalacija zavisnosti
echo -e "${GREEN}[6/10]${NC} Instalacija Python zavisnosti..."
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
else
    echo -e "${YELLOW}UPOZORENJE: requirements.txt nije pronađen${NC}"
fi

# Create CLI command
echo -e "${GREEN}[7/10]${NC} Instalacija 'erp' komande..."

sudo tee /usr/local/bin/erp > /dev/null << 'WRAPPER'
#!/bin/bash
INSTALL_DIR="__INSTALL_DIR__"
source "$INSTALL_DIR/venv/bin/activate"
python "$INSTALL_DIR/cli.py" "$@"
WRAPPER

sudo sed -i "s|__INSTALL_DIR__|$INSTALL_DIR|g" /usr/local/bin/erp
sudo chmod +x /usr/local/bin/erp

# Save configuration
echo -e "${GREEN}[8/10]${NC} Čuvanje konfiguracije..."

tee "$INSTALL_DIR/.erp.conf" > /dev/null << EOF
# ═══════════════════════════════════════
# Simple ERP Tracking - Konfiguracija
# ═══════════════════════════════════════

# Biznis informacije
BUSINESS_NAME=$BUSINESS_NAME
BUSINESS_SHORT_NAME=$BUSINESS_SHORT_NAME
BUSINESS_EMAIL=$BUSINESS_EMAIL
BUSINESS_PHONE=$BUSINESS_PHONE
BUSINESS_ADDRESS=$BUSINESS_ADDRESS
BUSINESS_WEBSITE=$BUSINESS_WEBSITE
CURRENCY=$CURRENCY
TIMEZONE=$TIMEZONE

# Logo (relativna putanja u images/branding/)
LOGO_FILE=logo.png
LOGO_SMALL_FILE=logo-small.png
FAVICON_FILE=favicon.ico

# Putanje
INSTALL_DIR=$INSTALL_DIR
DATA_DIR=$DATA_DIR
IMG_DIR=$IMG_DIR

# Server
PORT=$PORT
HOST=0.0.0.0
PUBLIC_URL=$PUBLIC_URL
DEBUG=false

# Sistem
VERSION=$DEFAULT_VERSION
INSTALLED_DATE=$(date -Is)
EOF

# Kreiraj JSON config za frontend
tee "$DATA_DIR/config.json" > /dev/null << EOF
{
    "business": {
        "name": "$BUSINESS_NAME",
        "shortName": "$BUSINESS_SHORT_NAME",
        "email": "$BUSINESS_EMAIL",
        "phone": "$BUSINESS_PHONE",
        "address": "$BUSINESS_ADDRESS",
        "website": "$BUSINESS_WEBSITE"
    },
    "locale": {
        "currency": "$CURRENCY",
        "timezone": "$TIMEZONE"
    },
    "branding": {
        "logo": "/images/branding/logo.png",
        "logoSmall": "/images/branding/logo-small.png",
        "favicon": "/images/branding/favicon.ico",
        "primaryColor": "#4F46E5",
        "secondaryColor": "#10B981"
    },
    "version": "$DEFAULT_VERSION"
}
EOF

# ═══════════════════════════════════════════════
# Create systemd service
# ═══════════════════════════════════════════════
echo -e "${GREEN}[9/10]${NC} Kreiranje systemd servisa..."

sudo tee /etc/systemd/system/erp.service > /dev/null << EOF
[Unit]
Description=Simple ERP Tracking - $BUSINESS_NAME
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/ERP_server.py --port $PORT
Restart=on-failure
RestartSec=5
StandardOutput=append:$DATA_DIR/logs/erp.log
StandardError=append:$DATA_DIR/logs/erp-error.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable erp.service

echo -e "${GREEN}Servis 'erp' kreiran i uključen za autostart.${NC}"

# ═══════════════════════════════════════════════
# Create backup cron job
# ═══════════════════════════════════════════════
echo -e "${GREEN}[10/10]${NC} Kreiranje backup cron job-a..."

chmod +x "$INSTALL_DIR/backup.sh" 2>/dev/null || true

CRON_JOB="0 3 * * * $INSTALL_DIR/backup.sh"

if crontab -l 2>/dev/null | grep -q "backup.sh"; then
    echo -e "${YELLOW}Backup cron job već postoji.${NC}"
else
    (crontab -l 2>/dev/null || echo "") | grep -v "backup.sh" | { cat; echo "$CRON_JOB"; } | crontab -
    
    if crontab -l 2>/dev/null | grep -q "backup.sh"; then
        echo -e "${GREEN}Backup zakazan za 3:00 AM svaki dan.${NC}"
    else
        echo -e "${YELLOW}UPOZORENJE: Dodaj ručno cron job:${NC}"
        echo -e "${YELLOW}  crontab -e${NC}"
        echo -e "${YELLOW}  $CRON_JOB${NC}"
    fi
fi

# ═══════════════════════════════════════════════
# Check Git configuration for backup
# ═══════════════════════════════════════════════
echo ""
echo -e "${CYAN}Git backup konfiguracija...${NC}"

if [ -d "$DATA_DIR/.git" ]; then
    echo -e "${GREEN}Git repo već postoji u DATA_DIR.${NC}"
else
    read -p "Inicijalizovati git repo u $DATA_DIR za backup? [Y/n]: " INIT_GIT
    INIT_GIT="${INIT_GIT:-Y}"
    if [[ "$INIT_GIT" =~ ^[Yy]$ ]]; then
        cd "$DATA_DIR"
        git init
        read -p "Git remote URL (ostaviti prazno za preskočiti): " GIT_REMOTE
        if [ -n "$GIT_REMOTE" ]; then
            git remote add origin "$GIT_REMOTE"
            echo -e "${GREEN}Git remote dodat: $GIT_REMOTE${NC}"
        fi
    fi
fi

# ═══════════════════════════════════════════════
# Final message
# ═══════════════════════════════════════════════
echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}       Instalacija uspešno završena!            ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}$BUSINESS_NAME${NC} - Simple ERP Tracking"
echo ""
echo -e "${YELLOW}Server:${NC}"
echo "  Lokalni:  http://localhost:$PORT"
if [ -n "$PUBLIC_URL" ]; then
    echo "  Javni:    $PUBLIC_URL"
fi
echo ""
echo -e "${YELLOW}Branding (dodaj slike):${NC}"
echo "  Logo:         $IMG_DIR/branding/logo.png"
echo "  Mali logo:    $IMG_DIR/branding/logo-small.png"
echo "  Favicon:      $IMG_DIR/branding/favicon.ico"
echo "  Ili koristi:  http://localhost:$PORT/config"
echo ""
echo -e "${YELLOW}Komande:${NC}"
echo "  erp start         - Pokreni servis"
echo "  erp stop          - Zaustavi servis"
echo "  erp restart       - Restartuj servis"
echo "  erp status        - Proveri status"
echo "  erp info          - Sve informacije"
echo "  erp logs -f       - Prati logove"
echo "  erp config        - Konfiguracija"
echo "  erp backup        - Ručni backup"
echo "  erp update        - Ažuriraj iz git-a"
echo ""
echo -e "${YELLOW}Healthcheck:${NC}"
echo "  curl http://localhost:$PORT/health"
echo ""
echo -e "${GREEN}Pokreni servis sa: erp start${NC}"
echo ""
