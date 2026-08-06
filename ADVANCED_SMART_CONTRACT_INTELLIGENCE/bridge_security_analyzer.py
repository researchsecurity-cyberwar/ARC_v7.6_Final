import json
import re

class BridgeSecurityAnalyzer:
    """
    Cross-chain bridge security analysis.
    Menganalisis keamanan bridge cross-chain.
    """
    
    def __init__(self):
        self.bridge_patterns = {
            'message_passing': r'messageBus|messageHandler|sendMessage',
            'lock_mint': r'lock\(|mint\(|burn\(|unlock\(',
            'oracle_based': r'oracle|priceFeed|aggregator',
            'multisig': r'multisig|signers|minSignatures'
        }
    
    def analyze_bridge_security(self, contract_path: str, bridge_type: str = None):
        """
        Analisis keamanan bridge cross-chain.
        """
        results = {
            'contract_path': contract_path,
            'bridge_type': bridge_type,
            'detected_bridge_type': None,
            'security_vulnerabilities': [],
            'consensus_risks': [],
            'analysis_successful': False
        }
        
        try:
            with open(contract_path, 'r') as f:
                contract_code = f.read()
            
            # Deteksi tipe bridge
            detected_type = self._detect_bridge_type(contract_code)
            results['detected_bridge_type'] = detected_type or bridge_type
            
            # Identifikasi kerentanan keamanan
            vulnerabilities = self._identify_bridge_vulnerabilities(contract_code, detected_type or bridge_type)
            results['security_vulnerabilities'] = vulnerabilities
            
            # Identifikasi risiko konsensus
            consensus_risks = self._identify_consensus_risks(contract_code, detected_type or bridge_type)
            results['consensus_risks'] = consensus_risks
            
            results['analysis_successful'] = True
        
        except Exception as e:
            results['error'] = f'Bridge security analysis failed: {str(e)}'
        
        return results
    
    def _detect_bridge_type(self, contract_code: str) -> str:
        """Deteksi tipe bridge berdasarkan pola kode."""
        for bridge_type, pattern in self.bridge_patterns.items():
            if re.search(pattern, contract_code, re.IGNORECASE):
                return bridge_type
        return 'unknown'
    
    def _identify_bridge_vulnerabilities(self, contract_code: str, bridge_type: str) -> list:
        """Identifikasi kerentanan keamanan bridge."""
        vulnerabilities = []
        
        # Kerentanan umum untuk semua tipe bridge
        if 'require(' not in contract_code and 'if (' not in contract_code:
            vulnerabilities.append('Missing input validation in bridge functions')
        
        if 'msg.sender' in contract_code and 'onlyRole' not in contract_code:
            vulnerabilities.append('Missing access control on critical bridge functions')
        
        # Kerentanan spesifik berdasarkan tipe bridge
        if bridge_type == 'message_passing':
            if 'nonce' not in contract_code.lower():
                vulnerabilities.append('Missing nonce mechanism for replay protection')
        
        elif bridge_type == 'lock_mint':
            if 'balanceOf' in contract_code and 'transferFrom' in contract_code:
                if 'approve' not in contract_code:
                    vulnerabilities.append('Missing approval mechanism for token transfers')
        
        elif bridge_type == 'oracle_based':
            if 'updatePrice' in contract_code and 'onlyOracle' not in contract_code:
                vulnerabilities.append('Oracle price update lacks proper access control')
        
        elif bridge_type == 'multisig':
            if 'minSignatures' in contract_code:
                min_sigs_match = re.search(r'minSignatures\s*=\s*(\d+)', contract_code)
                if min_sigs_match:
                    min_sigs = int(min_sigs_match.group(1))
                    if min_sigs < 2:
                        vulnerabilities.append('Multisig threshold too low - single point of failure')
        
        return vulnerabilities
    
    def _identify_consensus_risks(self, contract_code: str, bridge_type: str) -> list:
        """Identifikasi risiko konsensus bridge."""
        risks = []
        
        if bridge_type == 'multisig':
            signer_count_match = re.search(r'signers\.length\s*(?:==|>=)\s*(\d+)', contract_code)
            if signer_count_match:
                signer_count = int(signer_count_match.group(1))
                if signer_count < 5:
                    risks.append('Insufficient number of signers for decentralization')
        
        if 'emergencyShutdown' not in contract_code:
            risks.append('Missing emergency shutdown mechanism for critical incidents')
        
        if 'pause' not in contract_code:
            risks.append('Missing pause functionality for emergency situations')
        
        return risks