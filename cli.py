#!/usr/bin/env python3
"""
ERP Latice sa Pričom - CLI Interface
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Učitaj konfiguraciju
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
    """Pokreni aplikaciju"""
    if args.foreground:
        # Pokreni direktno u terminalu
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
        # Pokreni kao servis
        subprocess.run(["sudo", "systemctl", "start", "erp-latice"])
        print("ERP servis pokrenut.")
        cmd_status(args)

def cmd_stop(args):
    """Zaustavi servis"""
    subprocess.run(["sudo", "systemctl", "stop", "erp-latice"])
    print("ERP servis zaustavljen.")

def cmd_restart(args):
    """Restartuj servis"""
    subprocess.run(["sudo", "systemctl", "restart", "erp-latice"])
    print("ERP servis restartovan.")

def cmd_status(args):
    """Proveri status aplikacije"""
    print("ERP Latice sa Pričom - Status")
    print("=" * 40)
    print(f"Instalacija: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"Data dir:    {CONFIG.get('DATA_DIR', 'N/A')}")
    print(f"Img dir:     {CONFIG.get('IMG_DIR', 'N/A')}")
    print(f"Verzija:     {CONFIG.get('VERSION', 'N/A')}")
    
    # Proveri symlinkove
    data_link = SCRIPT_DIR / "data"
    img_link = SCRIPT_DIR / "img"
    
    print(f"\nSymlinkovi:")
    print(f"  data: {'✓ OK' if data_link.is_symlink() else '✗ NEDOSTAJE'}")
    print(f"  img:  {'✓ OK' if img_link.is_symlink() else '✗ NEDOSTAJE'}")
    
    # Proveri servis status
    print(f"\nServis status:")
    subprocess.run(["systemctl", "status", "erp-latice", "--no-pager", "-l"])

def cmd_logs(args):
    """Prikaži logove"""
    if args.service:
        # Systemd journal logovi
        cmd = ["sudo", "journalctl", "-u", "erp-latice", "-n", str(args.lines)]
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
    """Prikaži ili izmeni konfiguraciju"""
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
    """Uključi autostart"""
    subprocess.run(["sudo", "systemctl", "enable", "erp-latice"])
    print("Autostart uključen.")

def cmd_disable(args):
    """Isključi autostart"""
    subprocess.run(["sudo", "systemctl", "disable", "erp-latice"])
    print("Autostart isključen.")

def cmd_uninstall(args):
    """Deinstaliraj aplikaciju"""
    print("ERP Latice - Deinstalacija")
    print("=" * 40)
    print(f"Instalacija: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"Data dir:    {CONFIG.get('DATA_DIR', 'N/A')} (NEĆE biti obrisano)")
    print(f"Img dir:     {CONFIG.get('IMG_DIR', 'N/A')} (NEĆE biti obrisano)")
    print("")
    
    confirm = input("Da li ste sigurni da želite da deinstalirate? [y/N]: ")
    if confirm.lower() == 'y':
        print("\nDeinstalacija u toku...")
        
        # Zaustavi servis
        print("  - Zaustavljanje servisa...")
        subprocess.run(["sudo", "systemctl", "stop", "erp-latice"], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "systemctl", "disable", "erp-latice"], stderr=subprocess.DEVNULL)
        
        # Obriši servis fajl
        print("  - Brisanje servis fajla...")
        subprocess.run(["sudo", "rm", "-f", "/etc/systemd/system/erp-latice.service"])
        subprocess.run(["sudo", "systemctl", "daemon-reload"])
        
        # Obriši CLI komandu
        print("  - Brisanje 'erp' komande...")
        subprocess.run(["sudo", "rm", "-f", "/usr/local/bin/erp"])
        
        # Obriši instalaciju
        install_dir = CONFIG.get('INSTALL_DIR', '')
        if install_dir and os.path.exists(install_dir):
            print(f"  - Brisanje instalacije: {install_dir}")
            subprocess.run(["sudo", "rm", "-rf", install_dir])
        
        print("\n✓ Deinstalacija završena.")
        print(f"  Data i img folderi su sačuvani.")
    else:
        print("Deinstalacija otkazana.")

def cmd_port(args):
    """Promeni port"""
    new_port = args.port
    
    if not new_port:
        # Samo prikaži trenutni port
        print(f"Trenutni port: {CONFIG.get('PORT', '8000')}")
        return
    
    # Validiraj port
    try:
        port_int = int(new_port)
        if port_int < 1 or port_int > 65535:
            raise ValueError
    except ValueError:
        print(f"GREŠKA: Nevažeći port: {new_port}")
        sys.exit(1)
    
    # Ažuriraj config fajl
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
    
    # Ažuriraj systemd servis
    print("Ažuriranje systemd servisa...")
    
    service_file = "/etc/systemd/system/erp-latice.service"
    subprocess.run([
        "sudo", "sed", "-i", 
        f"s/--port [0-9]*/--port {new_port}/g",
        service_file
    ])
    
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    
    # Pitaj za restart
    restart = input("Restartovati servis sada? [Y/n]: ").strip()
    if restart.lower() != 'n':
        subprocess.run(["sudo", "systemctl", "restart", "erp-latice"])
        print("Servis restartovan.")
    else:
        print("Restartuj servis ručno sa: erp restart")


def main():
    parser = argparse.ArgumentParser(
        prog='erp',
        description='ERP Latice sa Pričom - CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Primeri:
  erp status          Proveri status aplikacije i servisa
  erp start           Pokreni kao systemd servis
  erp start -f        Pokreni u terminalu (foreground)
  erp stop            Zaustavi servis
  erp restart         Restartuj servis
  erp logs -f         Prati aplikacijske logove
  erp logs -s -f      Prati systemd journal
  erp config --edit   Edituj konfiguraciju
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Dostupne komande')
    
    # status
    subparsers.add_parser('status', help='Proveri status')
    
    # start
    start_parser = subparsers.add_parser('start', help='Pokreni aplikaciju')
    start_parser.add_argument('-f', '--foreground', action='store_true', 
                               help='Pokreni u foreground modu (ne kao servis)')
    start_parser.add_argument('extra', nargs='*', help='Dodatni argumenti')
    
    # stop
    subparsers.add_parser('stop', help='Zaustavi servis')
    
    # restart
    subparsers.add_parser('restart', help='Restartuj servis')
    
    # logs
    logs_parser = subparsers.add_parser('logs', help='Prikaži logove')
    logs_parser.add_argument('-f', '--follow', action='store_true', help='Prati log')
    logs_parser.add_argument('-n', '--lines', type=int, default=50, help='Broj linija')
    logs_parser.add_argument('-s', '--service', action='store_true', 
                              help='Prikaži systemd journal umesto app loga')
    
    # config
    config_parser = subparsers.add_parser('config', help='Konfiguracija')
    config_parser.add_argument('--show', action='store_true', help='Prikaži config fajl')
    config_parser.add_argument('--edit', action='store_true', help='Edituj config')
    
    # enable/disable autostart
    subparsers.add_parser('enable', help='Uključi autostart na boot')
    subparsers.add_parser('disable', help='Isključi autostart')
    
    # uninstall
    subparsers.add_parser('uninstall', help='Deinstaliraj aplikaciju')

    # port
    port_parser = subparsers.add_parser('port', help='Prikaži ili promeni port')
    port_parser.add_argument('port', nargs='?', help='Novi port (npr. 9000)')
    
    args = parser.parse_args()
    
    commands = {
        'status': cmd_status,
        'start': cmd_start,
        'stop': cmd_stop,
        'restart': cmd_restart,
        'config': cmd_config,
        'logs': cmd_logs,
        'enable': cmd_enable,
        'disable': cmd_disable,
        'uninstall': cmd_uninstall,
        'port': cmd_port,
    }
    
    if args.command:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
