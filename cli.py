#!/usr/bin/env python3
"""
Simple ERP - CLI Interface
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
        # Start directly in the terminal
        main_script = SCRIPT_DIR / "ERP_server.py"
        venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
        
        if not venv_python.exists():
            print(f"ERROR: Venv Python not found: {venv_python}")
            sys.exit(1)
        
        if main_script.exists():
            os.execv(str(venv_python), [str(venv_python), str(main_script)] + args.extra)
        else:
            print(f"ERROR: Main script not found: {main_script}")
            sys.exit(1)
    else:
        # Start as a service
        subprocess.run(["sudo", "systemctl", "start", "erp"])
        print("ERP service started.")
        cmd_status(args)

def cmd_stop(args):
    """Stop service"""
    subprocess.run(["sudo", "systemctl", "stop", "erp"])
    print("ERP service stopped.")

def cmd_restart(args):
    """Restart service"""
    subprocess.run(["sudo", "systemctl", "restart", "erp"])
    print("ERP service restarted.")

def cmd_status(args):
    """Check application status"""
    print("Simple ERP - Status")
    print("=" * 40)
    print(f"Instalacija: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"Data dir:    {CONFIG.get('DATA_DIR', 'N/A')}")
    print(f"Img dir:     {CONFIG.get('IMG_DIR', 'N/A')}")
    print(f"Verzija:     {CONFIG.get('VERSION', 'N/A')}")
    
    # Check symlinks
    data_link = SCRIPT_DIR / "data"
    img_link = SCRIPT_DIR / "img"
    
    print(f"\nSymlinks:")
    print(f"  data: {'✓ OK' if data_link.is_symlink() else '✗ MISSING'}")
    print(f"  img:  {'✓ OK' if img_link.is_symlink() else '✗ MISSING'}")
    
    # Check service status
    print(f"\nService status:")
    subprocess.run(["systemctl", "status", "erp", "--no-pager", "-l"])

def cmd_logs(args):
    """Display logs"""
    if args.service:
        # Systemd journal logs
        cmd = ["sudo", "journalctl", "-u", "erp", "-n", str(args.lines)]
        if args.follow:
            cmd.append("-f")
        subprocess.run(cmd)
    else:
        # Application logs
        log_file = Path(CONFIG.get('DATA_DIR', '')) / "erp.log"
        if log_file.exists():
            if args.follow:
                subprocess.run(["tail", "-f", str(log_file)])
            else:
                subprocess.run(["tail", "-n", str(args.lines), str(log_file)])
        else:
            print("Log file does not exist.")

def cmd_config(args):
    """Display or modify configuration"""
    if args.show:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                print(f.read())
        else:
            print("Config file does not exist.")
    elif args.edit:
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.run([editor, str(CONFIG_FILE)])
    else:
        # Default: show status
        print("Simple ERP Configuration:")
        print("=" * 40)
        for key, value in CONFIG.items():
            print(f"  {key}: {value}")
        print("\nUse --show for raw config or --edit to edit.")

def cmd_enable(args):
    """Enable autostart"""
    subprocess.run(["sudo", "systemctl", "enable", "erp"])
    print("Autostart enabled.")

def cmd_disable(args):
    """Disable autostart"""
    subprocess.run(["sudo", "systemctl", "disable", "erp"])
    print("Autostart disabled.")

def cmd_uninstall(args):
    """Uninstall application"""
    print("Simple ERP - Uninstallation")
    print("=" * 40)
    print(f"Installation: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"Data dir:     {CONFIG.get('DATA_DIR', 'N/A')} (WILL NOT be deleted)")
    print(f"Img dir:      {CONFIG.get('IMG_DIR', 'N/A')} (WILL NOT be deleted)")
    print("")
    
    confirm = input("Are you sure you want to uninstall? [y/N]: ")
    if confirm.lower() == 'y':
        print("\nUninstallation in progress...")
        
        # Stop service
        print("  - Stopping service...")
        subprocess.run(["sudo", "systemctl", "stop", "erp"], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "systemctl", "disable", "erp"], stderr=subprocess.DEVNULL)
        
        # Delete service file
        print("  - Deleting service file...")
        subprocess.run(["sudo", "rm", "-f", "/etc/systemd/system/erp.service"])
        subprocess.run(["sudo", "systemctl", "daemon-reload"])
        
        # Delete CLI command
        print("  - Deleting 'erp' command...")
        subprocess.run(["sudo", "rm", "-f", "/usr/local/bin/erp"])
        
        # Delete installation
        install_dir = CONFIG.get('INSTALL_DIR', '')
        if install_dir and os.path.exists(install_dir):
            print(f"  - Deleting installation: {install_dir}")
            subprocess.run(["sudo", "rm", "-rf", install_dir])
        
        print("\n✓ Uninstallation completed.")
        print(f"  Data and img folders are preserved.")
    else:
        print("Uninstallation cancelled.")

def cmd_port(args):
    """Change port"""
    new_port = args.port
    
    if not new_port:
        # Only display current port
        print(f"Current port: {CONFIG.get('PORT', '8000')}")
        return
    
    # Validate port
    try:
        port_int = int(new_port)
        if port_int < 1 or port_int > 65535:
            raise ValueError
    except ValueError:
        print(f"ERROR: Invalid port: {new_port}")
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
    
    # Save config
    with open(CONFIG_FILE, 'w') as f:
        f.writelines(config_lines)
    
    print(f"Port changed to: {new_port}")
    
    # Update systemd service
    print("Updating systemd service...")
    
    service_file = "/etc/systemd/system/erp.service"
    subprocess.run([
        "sudo", "sed", "-i", 
        f"s/--port [0-9]*/--port {new_port}/g",
        service_file
    ])
    
    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    
    # Ask for restart
    restart = input("Restart service now? [Y/n]: ").strip()
    if restart.lower() != 'n':
        subprocess.run(["sudo", "systemctl", "restart", "erp"])
        print("Service restarted.")
    else:
        print("Restart service manually with: erp restart")

def cmd_backup(args):
    """Run backup manually"""
    backup_script = SCRIPT_DIR / "backup.sh"
    
    if not backup_script.exists():
        print(f"ERROR: Backup script not found: {backup_script}")
        sys.exit(1)
    
    print("Running backup...")
    print(f"  INSTALL_DIR: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"  DATA_DIR:    {CONFIG.get('DATA_DIR', 'N/A')}")
    print("")
    
    if args.verbose:
        result = subprocess.run(["bash", str(backup_script)])
    else:
        result = subprocess.run(["bash", str(backup_script)], capture_output=True)
    
    if result.returncode == 0:
        print("✓ Backup completed successfully.")
        log_file = Path(CONFIG.get('DATA_DIR', '')) / "logs" / "backup.log"
        print(f"  Log: {log_file}")
    else:
        print("✗ Backup failed.")
        if not args.verbose:
            print("Start with -v for more details.")
            # Display error if it exists
            if result.stderr:
                print(f"\nError:\n{result.stderr.decode()}")
        sys.exit(1)

def cmd_health(args):
    """Check server health status"""
    import urllib.request
    import urllib.error
    
    port = CONFIG.get('PORT', '8000')
    url = f"http://localhost:{port}/health"
    
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            print(f"✓ Server is HEALTHY")
            print(f"  URL: {url}")
            print(f"  Status: {response.status}")
            if args.verbose:
                print(f"  Response: {response.read().decode()}")
    except urllib.error.URLError as e:
        print(f"✗ Server is not available")
        print(f"  URL: {url}")
        print(f"  Error: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def cmd_info(args):
    """Display all installation info"""
    print("Simple ERP - Info")
    print("=" * 50)
    print(f"\n📁 Paths:")
    print(f"   Installation: {CONFIG.get('INSTALL_DIR', 'N/A')}")
    print(f"   Data:         {CONFIG.get('DATA_DIR', 'N/A')}")
    print(f"   Images:       {CONFIG.get('IMG_DIR', 'N/A')}")
    
    print(f"\n🌐 Server:")
    print(f"   Host:         {CONFIG.get('HOST', '0.0.0.0')}")
    print(f"   Port:         {CONFIG.get('PORT', '8000')}")
    print(f"   URL:          http://localhost:{CONFIG.get('PORT', '8000')}")
    
    print(f"\n📋 Version:")
    print(f"   Version:      {CONFIG.get('VERSION', 'N/A')}")
    print(f"   Installed:    {CONFIG.get('INSTALLED_DATE', 'N/A')}")
    
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
        print(f"   Cron:         ✓ Active (3:00 AM)")
    else:
        print(f"   Cron:         ✗ Not configured")


def cmd_update(args):
    """Update application from git"""
    install_dir = SCRIPT_DIR
    
    print("Updating ERP application...")
    
    # Check if it's a git repository
    git_dir = install_dir / ".git"
    if not git_dir.exists():
        print(f"✗ {install_dir} is not a git repository.")
        print("")
        print("Update options:")
        print("  1. Update manually:")
        print(f"     cd /putanja/do/ERP_latice.sa.pricom")
        print(f"     git pull")
        print(f"     ./install.sh")
        print("")
        print("  2. Or convert your installation to a git repository:")
        print(f"     cd {install_dir}")
        print(f"     sudo git init")
        print(f"     sudo git remote add origin https://github.com/grga023/ERP_latice.sa.pricom.git")
        print(f"     sudo git fetch origin")
        print(f"     sudo git reset --hard origin/master")
        sys.exit(1)
    
    # Stop service
    print("  Stopping service...")
    subprocess.run(["sudo", "systemctl", "stop", "erp"], stderr=subprocess.DEVNULL)
    
    # If a branch is specified, use it
    if hasattr(args, 'branch') and args.branch:
        print(f"  Updating to branch: {args.branch}")
        result = subprocess.run(["sudo", "git", "fetch", "origin"], cwd=str(install_dir), 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Git fetch failed: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        result = subprocess.run(["sudo", "git", "checkout", args.branch], cwd=str(install_dir), 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Cannot switch to branch {args.branch}: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        result = subprocess.run(["sudo", "git", "pull", "origin", args.branch], cwd=str(install_dir), 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Git pull failed: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        print(result.stdout)
    else:
        # Use stable tags (default)
        print("  Finding latest stable tag...")
        
        # Fetch tags
        subprocess.run(["sudo", "git", "fetch", "--tags", "origin"], cwd=str(install_dir), 
                      capture_output=True, text=True)
        
        # Get current tag
        result = subprocess.run(["git", "describe", "--tags", "--exact-match"], 
                              cwd=str(install_dir), capture_output=True, text=True)
        current_tag = result.stdout.strip() if result.returncode == 0 else None
        
        # Get all stable tags
        result = subprocess.run(["git", "tag", "-l", "*_stabile"], cwd=str(install_dir), 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Cannot retrieve tags: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        stable_tags = sorted([t.strip() for t in result.stdout.strip().split('\n') if t.strip()])
        
        if not stable_tags:
            print("✗ No stable tags available (_stabile)")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        # Find latest tag
        latest_tag = stable_tags[-1]
        
        if current_tag:
            print(f"  Current version: {current_tag}")
            if current_tag == latest_tag:
                print(f"✓ Already on latest stable version: {latest_tag}")
                subprocess.run(["sudo", "systemctl", "start", "erp"])
                return
        else:
            print(f"  Currently not on a tag")
        
        print(f"  Updating to latest stable tag: {latest_tag}")
        
        # Checkout na najnoviji stabilni tag
        result = subprocess.run(["sudo", "git", "checkout", latest_tag], cwd=str(install_dir), 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ Checkout to {latest_tag} failed: {result.stderr}")
            subprocess.run(["sudo", "systemctl", "start", "erp"])
            sys.exit(1)
        
        print(f"✓ Switched to version: {latest_tag}")
    
    # Update dependencies
    print("  Updating Python packages...")
    venv_pip = install_dir / "venv" / "bin" / "pip"
    req_file = install_dir / "requirements.txt"
    if req_file.exists():
        subprocess.run(["sudo", str(venv_pip), "install", "-r", str(req_file)], 
                      capture_output=not args.verbose)
    
    # Start service
    print("  Starting service...")
    subprocess.run(["sudo", "systemctl", "start", "erp"])
    
    print("✓ Update completed.")

def cmd_db(args):
    """Database operations"""
    data_dir = Path(CONFIG.get('DATA_DIR', ''))
    db_file = data_dir / 'erp.db'
    
    if args.action == 'info':
        if db_file.exists():
            size = db_file.stat().st_size / (1024 * 1024)  # MB
            print(f"Database: {db_file}")
            print(f"Size: {size:.2f} MB")
        else:
            print("Database does not exist.")
    
    elif args.action == 'backup':
        if db_file.exists():
            backup_file = data_dir / f"erp_backup_{subprocess.run(['date', '+%Y%m%d_%H%M%S'], capture_output=True, text=True).stdout.strip()}.db"
            subprocess.run(['cp', str(db_file), str(backup_file)])
            print(f"✓ Backup created: {backup_file}")
        else:
            print("Database does not exist.")
    
    elif args.action == 'vacuum':
        print("Optimizing database...")
        venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
        subprocess.run([
            str(venv_python), '-c',
            f"import sqlite3; c=sqlite3.connect('{db_file}'); c.execute('VACUUM'); c.close(); print('✓ VACUUM completed')"
        ])

def main():
    parser = argparse.ArgumentParser(
        prog='erp',
        description='Simple ERP - CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            erp status          Check application status and service
            erp start           Start as systemd service
            erp start -f        Start in terminal (foreground)
            erp stop            Stop service
            erp restart         Restart service
            erp logs -f         Follow application logs
            erp config --edit   Edit configuration
            erp health          Check if server is running
            erp backup          Manual backup
            erp update          Update from git
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # status
    subparsers.add_parser('status', help='Check status')
    
    # info
    subparsers.add_parser('info', help='Display all information')
    
    # health
    health_parser = subparsers.add_parser('health', help='Check server health')
    health_parser.add_argument('-v', '--verbose', action='store_true', help='Display response')
    
    # start
    start_parser = subparsers.add_parser('start', help='Start application')
    start_parser.add_argument('-f', '--foreground', action='store_true', 
                               help='Start in foreground mode (not as a service)')
    start_parser.add_argument('extra', nargs='*', help='Extra arguments')
    
    # stop
    subparsers.add_parser('stop', help='Stop service')
    
    # restart
    subparsers.add_parser('restart', help='Restart service')
    
    # logs
    logs_parser = subparsers.add_parser('logs', help='Display logs')
    logs_parser.add_argument('-f', '--follow', action='store_true', help='Follow log')
    logs_parser.add_argument('-n', '--lines', type=int, default=50, help='Number of lines')
    logs_parser.add_argument('-s', '--service', action='store_true', 
                              help='Display systemd journal instead of app logs')
    
    # config
    config_parser = subparsers.add_parser('config', help='Configuration')
    config_parser.add_argument('--show', action='store_true', help='Display config file')
    config_parser.add_argument('--edit', action='store_true', help='Edit config')
    
    # port
    port_parser = subparsers.add_parser('port', help='Display or change port')
    port_parser.add_argument('port', nargs='?', help='New port (e.g. 9000)')
    
    # backup
    backup_parser = subparsers.add_parser('backup', help='Run backup manually')
    backup_parser.add_argument('-v', '--verbose', action='store_true', help='Display details')
    
    # update
    update_parser = subparsers.add_parser('update', help='Update application from git')
    update_parser.add_argument('-v', '--verbose', action='store_true', help='Display details')
    update_parser.add_argument('-b', '--branch', help='Specify branch (default: use stable tags)')
    
    # db
    db_parser = subparsers.add_parser('db', help='Database operations')
    db_parser.add_argument('action', choices=['info', 'backup', 'vacuum'], 
                           help='info/backup/vacuum')
    
    # enable/disable autostart
    subparsers.add_parser('enable', help='Enable autostart on boot')
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
