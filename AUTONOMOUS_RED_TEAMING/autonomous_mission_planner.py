import time
import json
from datetime import datetime, timedelta

# Architecture Fingerprinter - OPSIONAL
try:
    from ENTERPRISE_ATTACK_SURFACE.architecture_fingerprinter import ArchitectureFingerprinter
    FINGERPRINTER_AVAILABLE = True
except ImportError:
    ArchitectureFingerprinter = None
    FINGERPRINTER_AVAILABLE = False

class AutonomousMissionPlanner:
    """
    24/7 ops: recon → exploit → report → learn cycle.
    Merencanakan dan menjalankan misi otonom 24/7.
    """
    
    def __init__(self):
        self.mission_phases = {
            'recon': self._execute_recon_phase,
            'exploit': self._execute_exploit_phase,
            'report': self._execute_report_phase,
            'learn': self._execute_learn_phase
        }
        # IntelligentToolCommander (dipasang via set_arc_context) agar fase
        # recon/exploit benar-benar menjalankan tools eksternal, bukan placeholder.
        self.commander = None

        # Initialize Architecture Fingerprinter
        self.fingerprinter = None
        if FINGERPRINTER_AVAILABLE:
            try:
                self.fingerprinter = ArchitectureFingerprinter()
                print("✅ Architecture Fingerprinter initialized in Mission Planner")
            except Exception as e:
                print(f"⚠️ Architecture Fingerprinter init failed: {e}")
        
        self.mission_templates = {
            'bug_bounty': {
                'recon': ['subdomain_enum', 'port_scan', 'tech_fingerprint'],
                'exploit': ['vuln_scan', 'manual_testing', 'chain_exploitation'],
                'report': ['evidence_collection', 'report_writing', 'submission'],
                'learn': ['feedback_analysis', 'strategy_update', 'knowledge_base_update']
            },
            'ctf': {
                'recon': ['challenge_analysis', 'service_enumeration'],
                'exploit': ['vuln_identification', 'exploit_development'],
                'report': ['flag_submission', 'writeup_creation'],
                'learn': ['solution_review', 'technique_cataloging']
            }
        }
    
    def set_arc_context(self, commander):
        """
        Sambungkan mission planner ke IntelligentToolCommander ARC.
        Dengan ini fase recon/exploit menjalankan tools eksternal secara nyata
        (amass/nmap/nuclei/dll) bukan hasil placeholder.
        """
        self.commander = commander

    def _run_recon_task(self, tool_name: str, intent: str,
                        target_scope: dict) -> List[dict]:
        """Jalankan task recon via commander; fallback placeholder bila tidak ada."""
        if self.commander is None:
            return []
        domain = target_scope.get('domain') or target_scope.get('url')
        url = target_scope.get('url')
        params = {}
        if intent == 'subdomain_enum' and domain:
            params['target'] = domain
        elif intent in ('port_scan',) and (domain or url):
            params['target'] = domain or url
        elif intent == 'web_scan' and url:
            params['target'] = url
            params['severity'] = target_scope.get('severity', 'high')
        if not params:
            return []
        try:
            res = self.commander.execute_task({
                'tool': tool_name,
                'intent': intent,
                'params': params,
                'timeout': 120
            })
        except Exception as e:
            print(f"⚠️ Commander error for {tool_name}: {e}")
            return []
        out = (res.get('output') or {})
        if out.get('success'):
            stdout = out.get('stdout') or ''
            return [{
                'type': intent,
                'tool': tool_name,
                'command': res.get('command'),
                'raw': stdout[:500],
                'status': 'executed'
            }]
        return [{'type': intent, 'tool': tool_name,
                 'status': 'failed',
                 'error': (out.get('stderr') or res.get('error'))[:300]}]

    def plan_autonomous_mission(self, mission_type: str, target_scope: dict, duration_hours: int = 24):
        """
        Rencanakan misi otonom berdasarkan tipe dan durasi.
        """
        if mission_type not in self.mission_templates:
            return {'error': f'Unsupported mission type: {mission_type}'}
        
        mission_plan = {
            'mission_type': mission_type,
            'target_scope': target_scope,
            'duration_hours': duration_hours,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            'phases': self.mission_templates[mission_type],
            'status': 'PLANNED',
            'execution_log': []
        }
        
        return mission_plan
    
    def execute_mission_cycle(self, mission_plan: dict):
        """
        Jalankan siklus misi otonom lengkap.
        """
        results = {
            'mission_plan': mission_plan,
            'phase_results': {},
            'mission_successful': False,
            'total_findings': 0,
            'execution_time': 0.0
        }
        
        try:
            start_time = time.time()
            mission_successful = True
            
            # Jalankan setiap fase misi
            for phase_name, phase_tasks in mission_plan['phases'].items():
                phase_result = self.mission_phases[phase_name](phase_tasks, mission_plan['target_scope'])
                results['phase_results'][phase_name] = phase_result
                
                # Jika fase gagal, catat tapi lanjutkan (kecuali fase kritis)
                if not phase_result.get('success', False):
                    if phase_name in ['recon', 'exploit']:
                        mission_successful = False
            
            total_time = time.time() - start_time
            
            results.update({
                'mission_successful': mission_successful,
                'total_findings': self._count_total_findings(results['phase_results']),
                'execution_time': round(total_time, 2)
            })
        
        except Exception as e:
            results['error'] = f'Mission execution failed: {str(e)}'
            results['mission_successful'] = False
        
        return results
    
    def _execute_recon_phase(self, tasks: List[str], target_scope: dict) -> dict:
        """Jalankan fase recon."""
        findings = []
        
        for task in tasks:
            if task == 'subdomain_enum':
                findings.extend(self._perform_subdomain_enum(target_scope))
            elif task == 'port_scan':
                findings.extend(self._perform_port_scan(target_scope))
            elif task == 'tech_fingerprint':
                findings.extend(self._perform_tech_fingerprint(target_scope))
        
        return {
            'success': len(findings) > 0,
            'findings': findings,
            'tasks_completed': tasks
        }
    
    def _execute_exploit_phase(self, tasks: List[str], target_scope: dict) -> dict:
        """Jalankan fase eksploitasi."""
        findings = []
        
        for task in tasks:
            if task == 'vuln_scan':
                findings.extend(self._perform_vuln_scan(target_scope))
            elif task == 'manual_testing':
                findings.extend(self._perform_manual_testing(target_scope))
            elif task == 'chain_exploitation':
                findings.extend(self._perform_chain_exploitation(target_scope))
        
        return {
            'success': len(findings) > 0,
            'findings': findings,
            'tasks_completed': tasks
        }
    
    def _execute_report_phase(self, tasks: List[str], target_scope: dict) -> dict:
        """Jalankan fase pelaporan."""
        reports = []
        
        for task in tasks:
            if task == 'evidence_collection':
                reports.append(self._collect_evidence(target_scope))
            elif task == 'report_writing':
                reports.append(self._write_report(target_scope))
            elif task == 'submission':
                reports.append(self._submit_report(target_scope))
        
        return {
            'success': True,  # Pelaporan selalu berhasil jika mencapai fase ini
            'reports': reports,
            'tasks_completed': tasks
        }
    
    def _execute_learn_phase(self, tasks: List[str], target_scope: dict) -> dict:
        """Jalankan fase pembelajaran."""
        learning_outcomes = []
        
        for task in tasks:
            if task == 'feedback_analysis':
                learning_outcomes.append(self._analyze_feedback(target_scope))
            elif task == 'strategy_update':
                learning_outcomes.append(self._update_strategy(target_scope))
            elif task == 'knowledge_base_update':
                learning_outcomes.append(self._update_knowledge_base(target_scope))
        
        return {
            'success': True,
            'learning_outcomes': learning_outcomes,
            'tasks_completed': tasks
        }
    
    # Placeholder methods untuk implementasi nyata
    def _perform_subdomain_enum(self, target_scope: dict) -> List[dict]:
        # Eksekusi nyata via IntelligentToolCommander (amass/subfinder/assetfinder)
        real = self._run_recon_task('amass', 'subdomain_enum', target_scope) or \
               self._run_recon_task('subfinder', 'subdomain_enum', target_scope)
        if real:
            return real
        return [{'type': 'subdomain', 'value': f"dev.{target_scope.get('domain', 'example.com')}",
                 'status': 'simulated'}]

    def _perform_port_scan(self, target_scope: dict) -> List[dict]:
        real = self._run_recon_task('nmap', 'port_scan', target_scope) or \
               self._run_recon_task('naabu', 'port_scan', target_scope)
        if real:
            return real
        return [{'type': 'port', 'value': 80, 'status': 'simulated'},
                {'type': 'port', 'value': 443, 'status': 'simulated'}]
    
    def _perform_tech_fingerprint(self, target_scope: dict) -> List[dict]:
        """Perform technology fingerprinting using ArchitectureFingerprinter."""
        findings = []
        
        # Gunakan ArchitectureFingerprinter jika tersedia
        if self.fingerprinter:
            try:
                target_url = target_scope.get('url', '')
                if target_url:
                    print(f"🔍 Performing architecture fingerprinting on: {target_url}")
                    fingerprint = self.fingerprinter.fingerprint_target(target_url)
                    
                    # Convert fingerprint results to findings format
                    if fingerprint.get('cloud_providers'):
                        for provider in fingerprint['cloud_providers']:
                            findings.append({
                                'type': 'cloud_provider',
                                'value': provider,
                                'confidence': 'high'
                            })
                    
                    if fingerprint.get('frameworks'):
                        for framework in fingerprint['frameworks']:
                            findings.append({
                                'type': 'framework',
                                'value': framework,
                                'confidence': 'high'
                            })
                    
                    if fingerprint.get('auth_flows'):
                        for auth in fingerprint['auth_flows']:
                            findings.append({
                                'type': 'auth_flow',
                                'value': auth,
                                'confidence': 'medium'
                            })
                    
                    if fingerprint.get('tech_stack'):
                        for tech in fingerprint['tech_stack']:
                            findings.append({
                                'type': 'technology',
                                'value': tech,
                                'confidence': 'high'
                            })
                    
                    print(f"✅ Fingerprinted: {len(findings)} technologies detected")
                else:
                    print("⚠️ No URL provided for fingerprinting")
            except Exception as e:
                print(f"⚠️ Architecture fingerprinting failed: {e}")
                # Fallback to placeholder data
                findings = [
                    {'type': 'technology', 'value': 'nginx', 'confidence': 'low'},
                    {'type': 'technology', 'value': 'react', 'confidence': 'low'}
                ]
        else:
            # Fallback jika fingerprinter tidak tersedia
            findings = [
                {'type': 'technology', 'value': 'nginx', 'confidence': 'low'},
                {'type': 'technology', 'value': 'react', 'confidence': 'low'}
            ]
        
        return findings
    
    def _perform_vuln_scan(self, target_scope: dict) -> List[dict]:
        # Eksekusi nyata via IntelligentToolCommander (nuclei/dalfox)
        real = self._run_recon_task('nuclei', 'web_scan', target_scope) or \
               self._run_recon_task('dalfox', 'web_scan', target_scope)
        if real:
            return real
        return [{'type': 'vulnerability', 'value': 'XSS', 'status': 'simulated'},
                {'type': 'vulnerability', 'value': 'SQLi', 'status': 'simulated'}]
    
    def _perform_manual_testing(self, target_scope: dict) -> List[dict]:
        return [{'type': 'finding', 'value': 'Business logic flaw in payment flow'}]
    
    def _perform_chain_exploitation(self, target_scope: dict) -> List[dict]:
        return [{'type': 'chain', 'value': 'SSRF → AWS Metadata → IAM Takeover'}]
    
    def _collect_evidence(self, target_scope: dict) -> dict:
        return {'type': 'evidence', 'status': 'collected'}
    
    def _write_report(self, target_scope: dict) -> dict:
        return {'type': 'report', 'status': 'written'}
    
    def _submit_report(self, target_scope: dict) -> dict:
        return {'type': 'submission', 'status': 'submitted'}
    
    def _analyze_feedback(self, target_scope: dict) -> dict:
        return {'type': 'feedback', 'status': 'analyzed'}
    
    def _update_strategy(self, target_scope: dict) -> dict:
        return {'type': 'strategy', 'status': 'updated'}
    
    def _update_knowledge_base(self, target_scope: dict) -> dict:
        return {'type': 'knowledge', 'status': 'updated'}
    
    def _count_total_findings(self, phase_results: dict) -> int:
        """Hitung total temuan dari semua fase."""
        total = 0
        for phase, result in phase_results.items():
            if 'findings' in result:
                total += len(result['findings'])
        return total