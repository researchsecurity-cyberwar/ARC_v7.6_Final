"""
Learning Bridge - Jembatan universal yang menghubungkan SEMUA komponen ARC
ke SelfLearningOrchestrator secara terpusat dan tanpa duplikasi.

Komponen yang di-bridge:
1. Semua Vulnerability Detectors (web, api, cloud, mobile, crypto, ai, mfa, spa, realtime)
2. CTF Intelligence (challenge analyzer, playbook solvers, post-mortem)
3. Writeup scrapers (HackerOne, BugCrowd, Intigriti, YesWeHack, Immunefi)
4. Platform scrapers (SHADOW_INTELLIGENCE_RADAR)

Didesain agar:
- TIDAK mengubah interface detektor yang sudah ada
- TIDAK menduplikasi kode
- TIDAK error jika komponen tidak tersedia
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class LearningBridge:
    """
    Bridge terpusat untuk mengintegrasikan semua komponen ARC ke self-learning.
    Menyediakan API seragam untuk mengirim data pembelajaran dari sumber apapun.
    """

    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self._connected_detectors = {}
        self._connected_sources = set()
        self._bridge_log = []
        self._max_log = 200

    def set_orchestrator(self, orchestrator):
        """Hubungkan bridge dengan SelfLearningOrchestrator."""
        self.orchestrator = orchestrator

    def attach_detector(self, name: str, detector) -> bool:
        """
        Hubungkan detector ke learning bridge.
        Bisa handle detector dengan berbagai interface:
        - Punya set_learning_engine() → inject bridge
        - Punya recent_findings / get_recent_findings() → auto-fetch
        """
        if not detector:
            return False

        # Dedup: jangan attach dua kali
        detector_id = id(detector)
        if detector_id in [id(d) for d in self._connected_detectors.values()]:
            return True

        self._connected_detectors[name] = detector

        # 1. Jika detector punya set_learning_engine, inject bridge sebagai engine
        #    (bridge akan meneruskan ke orchestrator)
        if hasattr(detector, 'set_learning_engine'):
            try:
                detector.set_learning_engine(self)
            except Exception:
                pass

        # 2. Jika detector punya _report_to_learning, patching tidak diperlukan
        #    karena kita sudah inject sebagai learning_engine

        return True

    def connect_detector_findings(self, detector_name: str, findings: List[Dict[str, Any]]):
        """
        Interface yang sama dengan SelfLearningOrchestrator.connect_detector_findings.
        Dipanggil oleh detector yang sudah terhubung (via bridge injection).
        Meneruskan ke orchestrator asli.
        """
        if not findings:
            return

        # Teruskan ke orchestrator asli
        if self.orchestrator:
            try:
                self.orchestrator.connect_detector_findings(detector_name, findings)
                self._log(f"Detector '{detector_name}' → learning ({len(findings)} findings)")
            except Exception as e:
                self._log(f"Detector '{detector_name}' → learning ERROR: {e}")
        else:
            self._log(f"Detector '{detector_name}' → no orchestrator (skipped)")

    def get_learning_recommendations(self, context: Dict[str, Any], experience_type: str) -> Dict[str, Any]:
        """Teruskan permintaan rekomendasi ke orchestrator."""
        if self.orchestrator:
            try:
                return self.orchestrator.get_learning_recommendations(context, experience_type)
            except Exception:
                pass
        return {'success_probability': 0.5, 'relevant_lessons': []}

    def report_ctf_insight(self, challenge_data: Dict[str, Any], solution_data: Dict[str, Any],
                           category: str = "ctf") -> bool:
        """
        Kirim insight dari tantangan CTF ke self-learning.
        Mengubah hasil CTF menjadi pengalaman pembelajaran.

        Args:
            challenge_data: Data tantangan CTF (judul, deskripsi, kategori, dll)
            solution_data: Data solusi (teknik, vulnerability_type, approach, dll)
            category: Kategori sumber (ctf, hackthebox, tryhackme)

        Returns:
            True jika berhasil direkam
        """
        if not self.orchestrator:
            return False

        try:
            vulnerability_type = solution_data.get('vulnerability_type') or \
                challenge_data.get('vulnerability_type') or \
                self._detect_vuln_type(challenge_data.get('title', '') + ' ' +
                                       challenge_data.get('description', ''))

            technique_patterns = solution_data.get('technique_patterns', []) or []
            solution_approach = solution_data.get('solution_approach') or \
                solution_data.get('approach') or ''

            context = {
                'technique': vulnerability_type or 'ctf_generic',
                'source': category,
                'challenge_title': challenge_data.get('title', ''),
                'category': challenge_data.get('category', ''),
                'platform': challenge_data.get('platform', category),
                'difficulty': challenge_data.get('difficulty', ''),
                'technique_patterns': technique_patterns,
            }

            result_data = {
                'lesson': f"CTF insight: {vulnerability_type or 'generic'} via {solution_approach or 'unknown approach'}",
                'solution_approach': solution_approach,
                'vulnerability_type': vulnerability_type,
                'technique_patterns': technique_patterns,
                'source_type': category,
            }

            # Rekam sebagai experience success (hasil belajar CTF)
            result = self.orchestrator.record_and_learn(
                experience_type="ctf_solution",
                outcome="success",
                context=context,
                actions_taken=[{
                    'type': 'ctf_analysis',
                    'source': category,
                    'vulnerability_type': vulnerability_type,
                }],
                result_data=result_data
            )

            self._log(f"CTF insight recorded: {challenge_data.get('title', 'untitled')} → {vulnerability_type}")
            return result.get('experience_recorded', False)

        except Exception as e:
            self._log(f"CTF insight ERROR: {e}")
            return False

    def report_writeup_insight(self, writeup_data: Dict[str, Any], platform: str) -> bool:
        """
        Kirim insight dari writeup bug bounty ke self-learning.
        Writeup adalah sumber pengetahuan paling berharga karena berisi
        teknik nyata yang telah berhasil dieksploitasi.

        Args:
            writeup_data: Data writeup (title, vulnerability, technique, dll)
            platform: Platform asal (hackerone, bugcrowd, dll)

        Returns:
            True jika berhasil direkam
        """
        if not self.orchestrator:
            return False

        try:
            title = writeup_data.get('title') or writeup_data.get('name') or ''
            vulnerability = writeup_data.get('vulnerability') or \
                writeup_data.get('vulnerability_type') or \
                writeup_data.get('bug_type') or \
                self._detect_vuln_type(title)

            description = writeup_data.get('description') or \
                writeup_data.get('summary') or ''

            technique = writeup_data.get('technique') or \
                writeup_data.get('exploitation_technique') or ''

            context = {
                'technique': vulnerability or 'writeup_generic',
                'source': 'writeup',
                'platform': platform,
                'title': title,
                'bounty': writeup_data.get('bounty_amount'),
                'severity': writeup_data.get('severity', ''),
            }

            result_data = {
                'lesson': f"Writeup insight: {vulnerability or 'generic'} on {platform} - {title[:80]}",
                'vulnerability_type': vulnerability,
                'technique': technique,
                'description': description[:1000],
                'source_type': 'writeup',
                'platform': platform,
            }

            # Rekam sebagai experience sukses (writeup = teknik valid yang terbukti)
            result = self.orchestrator.record_and_learn(
                experience_type="writeup_insight",
                outcome="success",
                context=context,
                actions_taken=[{
                    'type': 'writeup_analysis',
                    'platform': platform,
                    'vulnerability_type': vulnerability,
                }],
                result_data=result_data
            )

            self._log(f"Writeup insight recorded: {title[:60]} → {vulnerability}")
            return result.get('experience_recorded', False)

        except Exception as e:
            self._log(f"Writeup insight ERROR: {e}")
            return False

    def report_vulnerability_pattern(self, patterns: List[Dict[str, Any]], source: str) -> bool:
        """
        Kirim pola kerentanan terunifikasi ke self-learning.
        Berguna untuk VulnerabilityPatternUnifier dan post-mortem analyzer.
        """
        if not self.orchestrator or not patterns:
            return False

        success_count = 0
        for pattern in patterns:
            try:
                vuln_type = pattern.get('unified_type') or pattern.get('category') or \
                    pattern.get('vulnerability_type') or 'generic'

                context = {
                    'technique': vuln_type,
                    'source': source,
                    'confidence': pattern.get('confidence_score', 0.5),
                    'original_type': pattern.get('original_type', ''),
                }

                result_data = {
                    'lesson': f"Pattern learned from {source}: {vuln_type}",
                    'vulnerability_type': vuln_type,
                    'source_type': source,
                }

                result = self.orchestrator.record_and_learn(
                    experience_type="vulnerability_pattern",
                    outcome="success",
                    context=context,
                    actions_taken=[{
                        'type': 'pattern_unification',
                        'source': source,
                        'pattern': vuln_type,
                    }],
                    result_data=result_data
                )

                if result.get('experience_recorded'):
                    success_count += 1

            except Exception:
                continue

        self._log(f"Pattern insights recorded: {success_count}/{len(patterns)} from {source}")
        return success_count > 0

    def sync_all_detectors(self) -> int:
        """
        Sinkronkan temuan dari SEMUA detektor yang terhubung ke learning engine.
        Metode ini dipanggil oleh arc_main secara periodik.

        Returns:
            Jumlah findings yang disinkronkan
        """
        total = 0
        for name, detector in self._connected_detectors.items():
            try:
                # Detector dengan get_recent_findings
                if hasattr(detector, 'get_recent_findings'):
                    findings = detector.get_recent_findings()
                    if findings:
                        self.connect_detector_findings(name, findings)
                        total += len(findings)

                # Detector dengan recent_findings attribute langsung
                elif hasattr(detector, 'recent_findings'):
                    findings = detector.recent_findings
                    if findings:
                        self.connect_detector_findings(name, findings)
                        total += len(findings)

            except Exception:
                continue

        return total

    def get_bridge_statistics(self) -> Dict[str, Any]:
        """Dapatkan statistik bridge."""
        return {
            'connected_detectors': list(self._connected_detectors.keys()),
            'connected_sources': sorted(self._connected_sources),
            'orchestrator_connected': self.orchestrator is not None,
            'log_entries': len(self._bridge_log),
            'last_activity': self._bridge_log[-1] if self._bridge_log else None,
        }

    def _detect_vuln_type(self, text: str) -> Optional[str]:
        """Deteksi tipe kerentanan dari teks secara sederhana."""
        if not text:
            return None

        text_lower = text.lower()
        mapping = {
            'xss': ['xss', 'cross-site scripting', 'cross site scripting'],
            'sqli': ['sql injection', 'sqli', 'sql injection'],
            'ssrf': ['ssrf', 'server-side request forgery', 'server side request forgery'],
            'csrf': ['csrf', 'cross-site request forgery', 'cross site request forgery'],
            'idor': ['idor', 'insecure direct object reference', 'access control'],
            'rce': ['remote code execution', 'rce', 'code execution', 'command injection'],
            'lfi': ['local file inclusion', 'lfi', 'file inclusion', 'path traversal'],
            'rfi': ['remote file inclusion', 'rfi'],
            'reentrancy': ['reentrancy', 're-entrancy'],
            'flash_loan': ['flash loan', 'flashloan'],
            'prompt_injection': ['prompt injection', 'jailbreak'],
            'jwt': ['jwt', 'json web token'],
            'smuggling': ['request smuggling', 'http smuggling'],
            'prototype_pollution': ['prototype pollution'],
            'websocket': ['websocket', 'socket'],
            'mfa': ['mfa', 'two-factor', '2fa', 'otp'],
            'ssti': ['template injection', 'ssti'],
            'deserialization': ['deserialization', 'insecure deserialization'],
            'crypto': ['weak crypto', 'weak encryption', 'cipher'],
            'buffer_overflow': ['buffer overflow', 'stack overflow', 'heap overflow'],
            'binary': ['reverse engineering', 'binary exploitation', 'pwn'],
            'forensics': ['forensics', 'stego', 'memory analysis', 'pcap'],
        }

        for vuln_type, keywords in mapping.items():
            if any(k in text_lower for k in keywords):
                return vuln_type

        return None

    def _log(self, message: str):
        """Catat aktivitas bridge."""
        entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        self._bridge_log.append(entry)
        if len(self._bridge_log) > self._max_log:
            self._bridge_log = self._bridge_log[-self._max_log:]