import sys
from datetime import datetime

class CLINotifier:
    """
    CLI dashboard notifications.
    Menampilkan notifikasi di terminal CLI.
    """
    
    def __init__(self):
        self.notification_styles = {
            'info': '\033[94m',      # Biru
            'warning': '\033[93m',   # Kuning
            'error': '\033[91m',     # Merah
            'success': '\033[92m',   # Hijau
            'reset': '\033[0m'       # Reset
        }
    
    def notify(self, message: str, level: str = 'info', source: str = 'ARC'):
        """
        Tampilkan notifikasi di CLI.
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        style = self.notification_styles.get(level, self.notification_styles['info'])
        reset = self.notification_styles['reset']
        
        notification = f"{style}[{timestamp}] [{source.upper()}] {message}{reset}"
        print(notification, file=sys.stderr)
    
    def show_dashboard_header(self, target: str = None):
        """Tampilkan header dashboard CLI."""
        header = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    🧠 ARC v7.6 FINAL DASHBOARD               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(header)
        
        if target:
            print(f"🎯 Target: {target}")
            print("📊 Status: Active Monitoring")
            print("-" * 60)
    
    def update_progress(self, current: int, total: int, description: str = "Processing"):
        """Tampilkan progress bar."""
        percent = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        sys.stdout.write(f'\r{description}: |{bar}| {percent:.1f}% ({current}/{total})')
        sys.stdout.flush()
        
        if current == total:
            print()  # New line when complete