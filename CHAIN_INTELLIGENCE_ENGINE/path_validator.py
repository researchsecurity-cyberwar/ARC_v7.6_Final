class PathValidator:
    """
    Autonomous step-by-step proof (max 6 steps).
    Memvalidasi jalur serangan secara otonom langkah demi langkah.
    """
    
    def __init__(self):
        self.max_steps = 6
        self.validation_criteria = {
            'technical_feasibility': 0.8,
            'business_impact': 0.7,
            'ethical_compliance': 0.9,
            'legal_boundaries': 0.95
        }
    
    def validate_attack_path(self, attack_path: Dict, target_context: Dict) -> Dict:
        """
        Validasi jalur serangan langkah demi langkah.
        """
        results = {
            'attack_path': attack_path,
            'target_context': target_context,
            'validation_successful': False,
            'step_validations': [],
            'overall_confidence': 0.0,
            'validation_errors': [],
            'proof_artifacts': []
        }
        
        try:
            # Cek panjang jalur
            if len(attack_path.get('path', [])) > self.max_steps:
                results['validation_errors'].append(f'Path exceeds maximum steps ({self.max_steps})')
                return results
            
            # Validasi setiap langkah
            step_validations = []
            all_steps_valid = True
            
            for i, step in enumerate(attack_path.get('nodes', [])):
                step_result = self._validate_single_step(step, i, target_context)
                step_validations.append(step_result)
                
                if not step_result.get('valid', False):
                    all_steps_valid = False
                    results['validation_errors'].extend(step_result.get('errors', []))
            
            results['step_validations'] = step_validations
            results['validation_successful'] = all_steps_valid
            
            # Hitung kepercayaan keseluruhan
            if all_steps_valid:
                results['overall_confidence'] = self._calculate_overall_confidence(step_validations)
                results['proof_artifacts'] = self._generate_proof_artifacts(attack_path, target_context)
        
        except Exception as e:
            results['error'] = f'Path validation failed: {str(e)}'
        
        return results
    
    def _validate_single_step(self, step_data: Dict, step_index: int, target_context: Dict) -> Dict:
        """Validasi satu langkah dalam jalur serangan."""
        validation = {
            'step_index': step_index,
            'vulnerability_type': step_data.get('vulnerability', {}).get('type', 'unknown'),
            'valid': True,
            'confidence': 1.0,
            'errors': []
        }
        
        try:
            # Validasi kelayakan teknis
            technical_valid = self._validate_technical_feasibility(step_data, target_context)
            if not technical_valid['valid']:
                validation['valid'] = False
                validation['errors'].extend(technical_valid['errors'])
                validation['confidence'] *= technical_valid['confidence']
            
            # Validasi batas etis dan hukum
            ethical_valid = self._validate_ethical_compliance(step_data, target_context)
            if not ethical_valid['valid']:
                validation['valid'] = False
                validation['errors'].extend(ethical_valid['errors'])
                validation['confidence'] *= ethical_valid['confidence']
        
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f'Validation error: {str(e)}')
            validation['confidence'] = 0.0
        
        return validation
    
    def _validate_technical_feasibility(self, step_data: Dict, target_context: Dict) -> Dict:
        """Validasi kelayakan teknis langkah."""
        vuln_type = step_data.get('vulnerability', {}).get('type', 'unknown')
        exploitability = step_data.get('exploitability', 0.5)
        
        validation = {
            'valid': True,
            'confidence': exploitability,
            'errors': []
        }
        
        # Cek apakah tipe kerentanan didukung
        supported_vulns = ['xss', 'sqli', 'ssrf', 'idor', 'rce', 'lfi']
        if vuln_type not in supported_vulns:
            validation['valid'] = False
            validation['errors'].append(f'Unsupported vulnerability type: {vuln_type}')
            validation['confidence'] = 0.1
        
        # Cek konteks target
        target_tech = target_context.get('technology_stack', [])
        if vuln_type == 'sqli' and 'database' not in str(target_tech).lower():
            validation['valid'] = False
            validation['errors'].append('SQLi unlikely without database backend')
            validation['confidence'] *= 0.3
        
        return validation
    
    def _validate_ethical_compliance(self, step_data: Dict, target_context: Dict) -> Dict:
        """Validasi kepatuhan etis dan hukum."""
        validation = {
            'valid': True,
            'confidence': 0.95,
            'errors': []
        }
        
        # Cek cakupan program
        scope_valid = target_context.get('in_scope', False)
        if not scope_valid:
            validation['valid'] = False
            validation['errors'].append('Target out of authorized scope')
            validation['confidence'] = 0.0
        
        # Cek batasan hukum
        legal_jurisdiction = target_context.get('jurisdiction', 'international')
        if legal_jurisdiction == 'critical_infra' and step_data.get('category') == 'impact':
            validation['valid'] = False
            validation['errors'].append('Critical infrastructure exploitation prohibited')
            validation['confidence'] = 0.0
        
        return validation
    
    def _calculate_overall_confidence(self, step_validations: List[Dict]) -> float:
        """Hitung kepercayaan keseluruhan dari validasi langkah."""
        if not step_validations:
            return 0.0
        
        min_confidence = min(step.get('confidence', 0.0) for step in step_validations)
        avg_confidence = sum(step.get('confidence', 0.0) for step in step_validations) / len(step_validations)
        
        # Gunakan minimum untuk konservatif, tapi pertimbangkan rata-rata
        return min_confidence * 0.7 + avg_confidence * 0.3
    
    def _generate_proof_artifacts(self, attack_path: Dict, target_context: Dict) -> List[Dict]:
        """Hasilkan artefak bukti untuk jalur yang divalidasi."""
        artifacts = []
        
        # Video PoC
        artifacts.append({
            'type': 'video_poc',
            'description': 'Step-by-step video proof of concept',
            'format': 'mp4',
            'duration_seconds': len(attack_path.get('nodes', [])) * 30
        })
        
        # HAR file
        artifacts.append({
            'type': 'har_capture',
            'description': 'HTTP Archive format network capture',
            'format': 'har',
            'size_estimate_kb': 500
        })
        
        # Reproduction script
        artifacts.append({
            'type': 'reproduction_script',
            'description': 'Automated reproduction script',
            'format': 'python',
            'complexity': 'medium'
        })
        
        return artifacts