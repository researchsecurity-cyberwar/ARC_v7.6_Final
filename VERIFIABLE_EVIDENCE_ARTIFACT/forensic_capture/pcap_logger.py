import subprocess
import os
import time
from datetime import datetime

class PCAPLogger:
    """
    Network packet capture for forensic analysis.
    Menangkap paket jaringan untuk analisis forensik.
    """
    
    def __init__(self, output_dir="~/.arc/evidence"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.tcpdump_path = "/usr/bin/tcpdump"
    
    def start_pcap_capture(self, target_host: str, duration: int = 60, 
                          report_id: str = None, interface: str = "any"):
        """
        Mulai capture paket jaringan selama durasi tertentu.
        """
        if report_id is None:
            report_id = f"pcap_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        pcap_filename = f"{report_id}.pcap"
        pcap_path = os.path.join(self.output_dir, pcap_filename)
        
        try:
            # Build tcpdump command
            if target_host:
                filter_expr = f"host {target_host}"
            else:
                filter_expr = "tcp or udp"
            
            cmd = [
                self.tcpdump_path,
                "-i", interface,
                "-w", pcap_path,
                "-G", str(duration),
                "-W", "1",
                filter_expr
            ]
            
            # Start capture process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for duration
            time.sleep(duration + 2)  # Add buffer
            
            # Check if file was created
            if os.path.exists(pcap_path) and os.path.getsize(pcap_path) > 0:
                return {
                    'report_id': report_id,
                    'pcap_path': pcap_path,
                    'capture_successful': True,
                    'duration_seconds': duration,
                    'target_host': target_host,
                    'file_size_bytes': os.path.getsize(pcap_path)
                }
            else:
                return {
                    'report_id': report_id,
                    'error': 'PCAP file not created or empty',
                    'capture_successful': False
                }
        
        except FileNotFoundError:
            return {
                'report_id': report_id,
                'error': 'tcpdump not found. Install with: sudo apt install tcpdump',
                'capture_successful': False
            }
        except Exception as e:
            return {
                'report_id': report_id,
                'error': f'PCAP capture failed: {str(e)}',
                'capture_successful': False
            }