#!/usr/bin/env python3
"""
ERP Latice sa Pričom - CLI Interface
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Load configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = SCRIPT_DIR / ".erp.conf"

def load_config():
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    return config

CONFIG = load_config()

def cmd_start(args):
    """Start application"""
    if args.foreground:
        # Start direktno u terminalu
        main_script = SCRIPT_DIR / "ERP_server.py"
        venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
        
        if not venv_python.exists():
            print(f"GREŠKA: Venv Python nije pronađen: {venv_python}")
            sys.exit(1)
        
        if main_script.exists():
            os.execv(str(venv_python), [str(venv_python), str(main_script)] + args.extra)
        else:
            print(f"GREŠKA: Glavni skript nije pronađen: {main_script}")
            sys.exit(1)
    else:
        # Start kao servis
        subprocess.run(["sudo", "systemctl", "start", "erp"])
        print("ERP servis pokrenut.")
        cmd_status(args)

def cmd_stop(args):
    """Stop service"""
    subprocess.run(["sudo", "systemctl", "stop", "erp"])
    print("ERP servis zaustavljen.")

def cmd_restart(args):
    """Restart service"""
    subprocess.run(["sudo", "systemctl", "restart", "erp"])
    print("ERP servis restartovan.")

def cmd_status(args):
    """Check application status"""
    print("ERP Latice sa Pričom - Status")
    print("=" * 40)
    print(f"Instalacija: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"Data dir:    {CONFIG.get('DATA_DIR', 'N/A')}")
    print(f"Img dir:     {CONFIG.get('IMG_DIR', 'N/A')}")
    print(f"Verzija:     {CONFIG.get('VERSION', 'N/A')}")
    
    # Check symlinkove
    data_link = SCRIPT_DIR / "data"
    img_link = SCRIPT_DIR / "img"
    
    print(f"\nSymlinkovi:")
    print(f"  data: {'✓ OK' if data_link.is_symlink() else '✗ NEDOSTAJE'}")
    print(f"  img:  {'✓ OK' if img_link.is_symlink() else '✗ NEDOSTAJE'}")
    
    # Check servis status
    print(f"\nServis status:")
    subprocess.run(["systemctl", "status", "erp", "--no-pager", "-l"])

def cmd_logs(args):
    """Display logs"""
    if args.service:
        # Systemd journal logovi
        cmd = ["sudo", "journalctl", "-u", "erp", "-n", str(args.lines)]
        if args.follow:
            cmd.append("-f")
        subprocess.run(cmd)
    else:
        # Aplikacijski logovi
        log_file = Path(CONFIG.get('DATA_DIR', '')) / "erp.log"
        if log_file.exists():
            if args.follow:
                subprocess.run(["tail", "-f", str(log_file)])
            else:
                subprocess.run(["tail", "-n", str(args.lines), str(log_file)])
        else:
            print("Log fajl ne postoji.")

def cmd_config(args):
    """Display or modify configuration"""
    if args.show:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                print(f.read())
        else:
            print("Config fajl ne postoji.")
    elif args.edit:
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.run([editor, str(CONFIG_FILE)])
    else:
        # Default: prikaži status
        print("ERP Konfiguracija:")
        print("=" * 40)
        for key, value in CONFIG.items():
            print(f"  {key}: {value}")
        print("\nKoristi --show za sirovi config ili --edit za editovanje.")

def cmd_enable(args):
    """Enable autostart"""
    subprocess.run(["sudo", "systemctl", "enable", "erp"])
    print("Autostart uključen.")

def cmd_disable(args):
    """Disable autostart"""
    subprocess.run(["sudo", "systemctl", "disable", "erp"])
    print("Autostart isključen.")

def cmd_uninstall(args):
    """Uninstall application"""
    print("ERP Latice - Uninstallation")
    print("=" * 40)
    print(f"Instalacija: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"Data dir:    {CONFIG.get('DATA_DIR', 'N/A')} (NEĆE biti obrisano)")
    print(f"Img dir:     {CONFIG.get('IMG_DIR', 'N/A')} (NEĆE biti obrisano)")
    print("")
    
    confirm = input("Da li ste sigurni da želite da deinstalirate? [y/N]: ")
    if confirm.lower() == 'y':
        print("\nUninstallation u toku...")
        
        # Stop service
        print("  - Zaustavljanje servisa...")
        subprocess.run(["sudo", "systemctl", "stop", "erp"], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "systemctl", "disable", "erp"], stderr=subprocess.DEVNULL)
        
        # Delete service file
        print("  - Brisanje servis fajla...")
        subprocess.run(["sudo", "rm", "-f", "/etc/systemd/system/erp.service"])
        subprocess.run(["sudo", "systemctl", "daemon-reload"])
        
        # Delete CLI command
        print("  - Brisanje 'erp' komande...")
        subprocess.run(["sudo", "rm", "-f", "/usr/local/bin/erp"])
        
        # Delete installation
        install_dir = CONFIG.get('INSTALL_DIR', '')
        if install_dir and os.path.exists(install_dir):
            print(f"  - Brisanje instalacije: {install_dir}")
            subprocess.run(["sudo", "rm", "-rf", install_dir])
        
        print("\n✓ Uninstallation završena.")
        print(f"  Data i img folderi su sačuvani.")
    else:
        print("Uninstallation otkazana.")

def cmd_port(args):
    """Change port"""
    new_port = args.port
    
    if not new_port:
        # Only display current port
        print(f"Trenutni port: {CONFIG.get('PORT', '8000')}")
        return
    
    # Validate port
    try:
        port_int = int(new_port)
        if port_int < 1 or port_int > 65535:
            raise ValueError
    except ValueError:
        print(f"GREŠKA: Nevažeći port: {new_port}")
        sys.exit(1)
    
    # Update config file
    config_lines = []
    port_found = False
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            for line in f:
                if line.startswith('PORT='):
                    config_lines.append(f'PORT={new_port}\n')
                    port_found = True
                else:
                    config_lines.append(line)
    
    if not port_found:
        config_lines.append(f'PORT={new_port}\n')
    
    # Snimi config
    with open(CONFIG_FILE, 'w') as f:
        f.writelines(config_lines)
    
    print(f"Port promenjen na: {new_port}")
    
    # Update systemd service
    print("Ažuriranje systemd servisa...")
    
    service_file = "/etc/systemd/system/erp.service"
    subprocess.run([
        "sudo", "sed", "-i", 
        f"s/--port [0-9]*/--port {new_port}/g",
        service_file
    ])
    
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    
    # Pitaj za restart
    restart = input("Restartovati servis sada? [Y/n]: ").strip()
    if restart.lower() != 'n':
        subprocess.run(["sudo", "systemctl", "restart", "erp"])
        print("Servis restartovan.")
    else:
        print("Restart service ručno sa: erp restart")

def cmd_backup(args):
    """Run backup manually"""
    backup_script = SCRIPT_DIR / "backup.sh"
    
    if not backup_script.exists():
        print(f"GREŠKA: Backup skripta nije pronađena: {backup_script}")
        sys.exit(1)
    
    print("Pokretanje backup-a...")
    print(f"  INSTALL_DIR: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"  DATA_DIR:    {CONFIG.get('DATA_DIR', 'N/A')}")
    print("")
    
    if args.verbose:
        result = subprocess.run(["bash", str(backup_script)])
    else:
        result = subprocess.run(["bash", str(backup_script)], capture_output=True)
    
    if result.returncode == 0:
        print("✓ Backup uspešno završen.")
        log_file = Path(CONFIG.get('DATA_DIR', '')) / "logs" / "backup.log"
        print(f"  Log: {log_file}")
    else:
        print("✗ Backup nije uspeo.")
        if not args.verbose:
            print("Start sa -v za više detalja.")
            # Display error ako postoji
            if result.stderr:
                print(f"\nGreška:\n{result.stderr.decode()}")
        sys.exit(1)

def cmd_health(args):
    """Check server health status"""
    import urllib.request
    import urllib.error
    
    port = CONFIG.get('PORT', '8000')
    url = f"http://localhost:{port}/health"
    
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            print(f"✓ Server je ZDRAV")
            print(f"  URL: {url}")
            print(f"  Status: {response.status}")
            if args.verbose:
                print(f"  Response: {response.read().decode()}")
    except urllib.error.URLError as e:
        print(f"✗ Server nije dostupan")
        print(f"  URL: {url}")
        print(f"  Greška: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Greška: {e}")
        sys.exit(1)


def cmd_info(args):
    """Display all installation info"""
    print("ERP Latice sa Pričom - Info")
    print("=" * 50)
    print(f"\n📁 Putanje:")
    print(f"   Instalacija:  {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"   Data:         {CONFIG.get('DATA_DIR', 'N/A')}")
    print(f"   Slike:        {CONFIG.get('IMG_DIR', 'N/A')}")
    
    print(f"\n🌐 Server:")
    print(f"   Host:         {CONFIG.get('HOST', '0.0.0.0')}")
    print(f"   Port:         {CONFIG.get('PORT', '8000')}")
    print(f"   URL:          http://localhost:{CONFIG.get('PORT', '8000')}")
    
    print(f"\n📋 Verzija:")
    print(f"   Verzija:      {CONFIG.get('VERSION', 'N/A')}")
    print(f"   Instalirano:  {CONFIG.get('INSTALLED_DATE', 'N/A')}")
    
    # Disk usage
    data_dir = CONFIG.get('DATA_DIR', '')
    if data_dir and os.path.exists(data_dir):
        result = subprocess.run(['du', '-sh', data_dir], capture_output=True, text=True)
        if result.returncode == 0:
            size = result.stdout.split()[0]
            print(f"\n💾 Disk:")
            print(f"   Data folder:  {size}")
    
    # Cron status
    print(f"\n⏰ Backup:")
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if 'backup.sh' in result.stdout:
        print(f"   Cron:         ✓ Aktivan (3:00 AM)")
    else:
        print(f"   Cron:         ✗ Nije podešen")


def cmd_update(args):
    """Update application from git"""
    install_dir = SCRIPT_DIR
    
    print("Ažuriranje ERP aplikacije...")
    
    # Check da li je git repo
    git_dir = install_dir / ".git"
    if not git_dir.exists():
        print(f"✗ {install_dir} nije git repozitorijum.")
        print("")
        print("Opcije za ažuriranje:")
        print("  1. Ručno ažuriraj:")
        print(f"     cd /putanja/do/ERP_latice.sa.pricom")
        print(f"     git pull")
        print(f"     ./install.sh")
        print("")
        print("  2. Ili konvertuj instalaciju u git repo:")
        print(f"     cd {install_dir}")
        print(f"     sudo git init")
        print(f"     sudo git remote add origin https://github.com/grga023/ERP_latice.sa.pricom.git")
        print(f"     sudo git fetch origin")
        print(f"     sudo git reset --hard origin/master")
        sys.exit(1)
    
    # Stop service
    print("  Zaustavljanje servisa...")
    subprocess.run(["sudo", "systemctl", "stop", "erp"], stderr=subprocess.DEVNULL)
    
    # Ako je specifikovan branch, koristi branch
    if hasattr(args, 'branch') and args.branch:
        print(f"  Ažuriram na branch: {args.branch}")
        result = subprocess.run(["sudo", "git", "fetch", "origin"], cwd=str(install_dir), 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Git fetch nije uspeo: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        result = subprocess.run(["sudo", "git", "checkout", args.branch], cwd=str(install_dir), 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Nije moguće preći na branch {args.branch}: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        result = subprocess.run(["sudo", "git", "pull", "origin", args.branch], cwd=str(install_dir), 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Git pull nije uspeo: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        print(result.stdout)
    else:
        # Koristi stabilne tagove (default)
        print("  Pronalazim najnoviji stabilni tag...")
        
        # Fetch tags
        subprocess.run(["sudo", "git", "fetch", "--tags", "origin"], cwd=str(install_dir), 
                      capture_output=True, text=True)
        
        # Dobavi trenutni tag
        result = subprocess.run(["git", "describe", "--tags", "--exact-match"], 
                              cwd=str(install_dir), capture_output=True, text=True)
        current_tag = result.stdout.strip() if result.returncode == 0 else None
        
        # Dobavi sve stabilne tagove
        result = subprocess.run(["git", "tag", "-l", "*_stabile"], cwd=str(install_dir), 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Nije moguće dohvatiti tagove: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        stable_tags = sorted([t.strip() for t in result.stdout.strip().split('\n') if t.strip()])
        
        if not stable_tags:
            print("✗ Nema dostupnih stabilnih tagova (_stabile)")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        # Find latest tag
        latest_tag = stable_tags[-1]
        
        if current_tag:
            print(f"  Trenutna verzija: {current_tag}")
            if current_tag == latest_tag:
                print(f"✓ Već ste na najnovijoj stabilnoj verziji: {latest_tag}")
                subprocess.run(["sudo", "systemctl", "start", "erp"])
                return
        else:
            print(f"  Trenutno niste na tag-u")
        
        print(f"  Ažuriram na najnoviji stabilni tag: {latest_tag}")
        
        # Checkout na najnoviji stabilni tag
        result = subprocess.run(["sudo", "git", "checkout", latest_tag], cwd=str(install_dir), 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ Checkout na {latest_tag} nije uspeo: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        print(f"✓ Prebačeno na verziju: {latest_tag}")
    
    # Update dependencies
    print("  Ažuriranje Python paketa...")
    venv_pip = install_dir / "venv" / "bin" / "pip"
    req_file = install_dir / "requirements.txt"
    if req_file.exists():
        subprocess.run(["sudo", str(venv_pip), "install", "-r", str(req_file)], 
                      capture_output=not args.verbose)
    
    # Start servis
    print("  Pokretanje servisa...")
    subprocess.run(["sudo", "systemctl", "start", "erp"])
    
    print("✓ Ažuriranje završeno.")

def cmd_db(args):
    """Database operacije"""
    data_dir = Path(CONFIG.get('DATA_DIR', ''))
    db_file = data_dir / 'erp.db'
    
    if args.action == 'info':
        if db_file.exists():
            size = db_file.stat().st_size / (1024 * 1024)  # MB
            print(f"Database: {db_file}")
            print(f"Veličina: {size:.2f} MB")
        else:
            print("Database ne postoji.")
    
    elif args.action == 'backup':
        if db_file.exists():
            backup_file = data_dir / f"erp_backup_{subprocess.run(['date', '+%Y%m%d_%H%M%S'], capture_output=True, text=True).stdout.strip()}.db"
            subprocess.run(['cp', str(db_file), str(backup_file)])
            print(f"✓ Backup kreiran: {backup_file}")
        else:
            print("Database ne postoji.")
    
    elif args.action == 'vacuum':
        print("Optimizacija baze...")
        venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
        subprocess.run([
            str(venv_python), '-c',
            f"import sqlite3; c=sqlite3.connect('{db_file}'); c.execute('VACUUM'); c.close(); print('✓ VACUUM završen')"
        ])

def main():
    parser = argparse.ArgumentParser(
        prog='erp',
        description='ERP Latice sa Pričom - CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Primeri:
            erp status          Check application status i servisa
            erp start           Start kao systemd servis
            erp start -f        Start u terminalu (foreground)
            erp stop            Stop service
            erp restart         Restart service
            erp logs -f         Prati aplikacijske logove
            erp config --edit   Edituj konfiguraciju
            erp health          Check da li server radi
            erp backup          Ručni backup
            erp update          Update iz git-a
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Dostupne komande')
    
    # status
    subparsers.add_parser('status', help='Check status')
    
    # info
    subparsers.add_parser('info', help='Display sve informacije')
    
    # health
    health_parser = subparsers.add_parser('health', help='Check health servera')
    health_parser.add_argument('-v', '--verbose', action='store_true', help='Display response')
    
    # start
    start_parser = subparsers.add_parser('start', help='Start application')
    start_parser.add_argument('-f', '--foreground', action='store_true', 
                               help='Start u foreground modu (ne kao servis)')
    start_parser.add_argument('extra', nargs='*', help='Dodatni argumenti')
    
    # stop
    subparsers.add_parser('stop', help='Stop service')
    
    # restart
    subparsers.add_parser('restart', help='Restart service')
    
    # logs
    logs_parser = subparsers.add_parser('logs', help='Display logs')
    logs_parser.add_argument('-f', '--follow', action='store_true', help='Prati log')
    logs_parser.add_argument('-n', '--lines', type=int, default=50, help='Broj linija')
    logs_parser.add_argument('-s', '--service', action='store_true', 
                              help='Display systemd journal umesto app loga')
    
    # config
    config_parser = subparsers.add_parser('config', help='Konfiguracija')
    config_parser.add_argument('--show', action='store_true', help='Display config fajl')
    config_parser.add_argument('--edit', action='store_true', help='Edituj config')
    
    # port
    port_parser = subparsers.add_parser('port', help='Display ili promeni port')
    port_parser.add_argument('port', nargs='?', help='Novi port (npr. 9000)')
    
    # backup
    backup_parser = subparsers.add_parser('backup', help='Run backup manually')
    backup_parser.add_argument('-v', '--verbose', action='store_true', help='Display detalje')
    
    # update
    update_parser = subparsers.add_parser('update', help='Update application from git')
    update_parser.add_argument('-v', '--verbose', action='store_true', help='Display detalje')
    update_parser.add_argument('-b', '--branch', help='Specifikuj branch (default: koristi stabilne tagove)')
    
    # db
    db_parser = subparsers.add_parser('db', help='Database operacije')
    db_parser.add_argument('action', choices=['info', 'backup', 'vacuum'], 
                           help='info/backup/vacuum')
    
    # enable/disable autostart
    subparsers.add_parser('enable', help='Enable autostart na boot')
    subparsers.add_parser('disable', help='Disable autostart')
    
    # uninstall
    subparsers.add_parser('uninstall', help='Uninstall application')
    
    args = parser.parse_args()
    
    commands = {
        'status': cmd_status,
        'info': cmd_info,
        'health': cmd_health,
        'start': cmd_start,
        'stop': cmd_stop,
        'restart': cmd_restart,
        'config': cmd_config,
        'port': cmd_port,
        'logs': cmd_logs,
        'backup': cmd_backup,
        'update': cmd_update,
        'db': cmd_db,
        'enable': cmd_enable,
        'disable': cmd_disable,
        'uninstall': cmd_uninstall,
    }
    
    if args.command:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
