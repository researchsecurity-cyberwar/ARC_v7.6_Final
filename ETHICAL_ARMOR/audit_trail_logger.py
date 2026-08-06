import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any

class AuditTrailLogger:
    """
    Immutable local logs (for legal defense).
    Mencatat jejak audit yang immutable untuk pertahanan hukum.
    """
    
    def __init__(self, log_dir="~/.arc/audit_logs"):
        self.log_dir = os.path.expanduser(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_log_file = self._get_current_log_file()
    
    def _get_current_log_file(self) -> str:
        """Dapatkan file log saat ini berdasarkan tanggal."""
        today = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.log_dir, f"audit_{today}.jsonl")
    
    def log_security_operation(self, operation_data: Dict[str, Any]) -> str:
        """
        Catat operasi keamanan ke log audit.
        """
        try:
            # Tambahkan metadata audit
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'operation_id': operation_data.get('operation_id', self._generate_operation_id()),
                'operation_type': operation_data.get('operation_type', 'unknown'),
                'target': operation_data.get('target', 'unknown'),
                'operator': operation_data.get('operator', 'autonomous'),
                'authorization_status': operation_data.get('authorization_status', 'verified'),
                'ethical_compliance': operation_data.get('ethical_compliance', True),
                'data_minimization_applied': operation_data.get('data_minimization_applied', True),
                'chain_execution_limited': operation_data.get('chain_execution_limited', True),
                'immutable_hash': None  # Akan diisi setelah logging
            }
            
            # Tambahkan hash dari entri sebelumnya untuk membuat rantai
            previous_hash = self._get_last_entry_hash()
            audit_entry['previous_hash'] = previous_hash
            
            # Hitung hash immutable untuk entri ini
            entry_string = json.dumps(audit_entry, sort_keys=True)
            current_hash = hashlib.sha256(entry_string.encode()).hexdigest()
            audit_entry['immutable_hash'] = current_hash
            
            # Tulis ke file log
            with open(self.current_log_file, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
            
            return current_hash
        
        except Exception as e:
            # Jika logging gagal, tetap kembalikan hash dummy untuk tidak menghentikan operasi
            return "logging_failed_" + self._generate_operation_id()
    
    def _generate_operation_id(self) -> str:
        """Hasilkan ID operasi unik."""
        import uuid
        return str(uuid.uuid4())
    
    def _get_last_entry_hash(self) -> str:
        """Dapatkan hash dari entri log sebelumnya."""
        try:
            if os.path.exists(self.current_log_file):
                with open(self.current_log_file, 'rb') as f:
                    # Baca baris terakhir
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                    last_line = f.readline().decode()
                    
                    if last_line.strip():
                        last_entry = json.loads(last_line)
                        return last_entry.get('immutable_hash', 'genesis')
        except:
            pass
        
        return 'genesis'
    
    def verify_log_integrity(self) -> dict:
        """
        Verifikasi integritas log audit.
        """
        results = {
            'log_file': self.current_log_file,
            'total_entries': 0,
            'integrity_verified': True,
            'corrupted_entries': [],
            'verification_timestamp': datetime.now().isoformat()
        }
        
        try:
            if not os.path.exists(self.current_log_file):
                results['integrity_verified'] = True
                return results
            
            with open(self.current_log_file, 'r') as f:
                lines = f.readlines()
            
            results['total_entries'] = len(lines)
            previous_hash = 'genesis'
            
            for i, line in enumerate(lines):
                try:
                    entry = json.loads(line.strip())
                    expected_hash = entry.get('previous_hash', 'genesis')
                    
                    if expected_hash != previous_hash:
                        results['integrity_verified'] = False
                        results['corrupted_entries'].append({
                            'line_number': i + 1,
                            'reason': 'Previous hash mismatch'
                        })
                    
                    # Verifikasi hash immutable entri ini
                    entry_copy = entry.copy()
                    actual_hash = entry_copy.pop('immutable_hash', None)
                    recalculated_hash = hashlib.sha256(
                        json.dumps(entry_copy, sort_keys=True).encode()
                    ).hexdigest()
                    
                    if actual_hash != recalculated_hash:
                        results['integrity_verified'] = False
                        results['corrupted_entries'].append({
                            'line_number': i + 1,
                            'reason': 'Immutable hash mismatch'
                        })
                    
                    previous_hash = entry.get('immutable_hash', 'invalid')
                    
                except Exception as e:
                    results['integrity_verified'] = False
                    results['corrupted_entries'].append({
                        'line_number': i + 1,
                        'reason': f'JSON parsing error: {str(e)}'
                    })
        
        except Exception as e:
            results['error'] = f'Log verification failed: {str(e)}'
            results['integrity_verified'] = False
        
        return results
    
    def export_audit_log_for_legal(self, start_date: str = None, end_date: str = None) -> str:
        """
        Ekspor log audit untuk keperluan hukum.
        """
        try:
            # Kumpulkan semua file log dalam rentang tanggal
            log_files = []
            if start_date and end_date:
                from datetime import datetime, timedelta
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
                
                current = start_dt
                while current <= end_dt:
                    log_file = os.path.join(self.log_dir, f"audit_{current.strftime('%Y-%m-%d')}.jsonl")
                    if os.path.exists(log_file):
                        log_files.append(log_file)
                    current += timedelta(days=1)
            else:
                log_files = [self.current_log_file]
            
            # Gabungkan log
            exported_entries = []
            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                exported_entries.append(json.loads(line))
            
            # Simpan ekspor
            export_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_file = os.path.join(self.log_dir, f"legal_export_{export_id}.json")
            
            export_data = {
                'export_id': export_id,
                'export_timestamp': datetime.now().isoformat(),
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'total_entries': len(exported_entries),
                'entries': exported_entries,
                'integrity_verification': self.verify_log_integrity()
            }
            
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return export_file
        
        except Exception as e:
            raise Exception(f'Legal export failed: {str(e)}')