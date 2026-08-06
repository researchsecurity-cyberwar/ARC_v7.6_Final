import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ToolDiscoveryWatcher(FileSystemEventHandler):
    """
    Watch ~/arc/plugins/ for new tools.
    Memantau direktori plugins untuk alat baru.
    """
    
    def __init__(self, plugins_dir="~/arc/plugins", callback=None):
        self.plugins_dir = os.path.expanduser(plugins_dir)
        os.makedirs(self.plugins_dir, exist_ok=True)
        self.callback = callback
        self.observer = Observer()
        self.observer.schedule(self, self.plugins_dir, recursive=False)
    
    def start_watching(self):
        """Mulai memantau direktori plugins."""
        self.observer.start()
    
    def stop_watching(self):
        """Hentikan pemantauan."""
        self.observer.stop()
        self.observer.join()
    
    def on_created(self, event):
        """Tangani file baru yang dibuat."""
        if not event.is_directory:
            if self.callback:
                self.callback(event.src_path)
    
    def on_modified(self, event):
        """Tangani file yang dimodifikasi."""
        if not event.is_directory:
            if self.callback:
                self.callback(event.src_path)