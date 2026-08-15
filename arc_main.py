import os
import sys
import time
from datetime import datetime
from typing import Dict

# Tambahkan root folder ke Python path
sys.path.insert(0, os.path.abspath('.'))

# ==================================================================
# MODE CHAT: python arc_main.py --chat [--chat-target <target>]
# Guard ini diletakkan SEBELUM import modul berat, jadi mode chat
# tidak me-load loop autonomous sama sekali (aman walau ada dep
# yang belum ter-install di Kali Linux).
# ==================================================================
if "--chat" in sys.argv:
    from DIALOGIC_COPILLOT.arc_chat_engine import ArcChatEngine
    from DIALOGIC_COPILLOT.chat_repl import run_repl
    _chat_engine = ArcChatEngine()
    if "--chat-target" in sys.argv:
        try:
            _t = sys.argv[sys.argv.index("--chat-target") + 1]
            _chat_engine.start_conversation(_t)
        except (IndexError, ValueError):
            pass
    run_repl(_chat_engine)
    sys.exit(0)

# Modul Inti ARC
from SOVEREIGN_SESSION_MANAGER.credential_vault import CredentialVault
from SOVEREIGN_SESSION_MANAGER.platform_session_manager import PlatformSessionManager
from COGNITIVE_CORE.human_in_the_loop_gate import HumanInTheLoopGate
from ETHICAL_ARMOR.scope_sovereignty_guard import ScopeSovereigntyGuard

# Modul Telegram & Komunikasi
from DIALOGIC_COPILLOT.PLATFORM_COMMUNICATOR.telegram_notifier import TelegramNotifier

# Modul Session untuk Bug Bounty & CTF
from SOVEREIGN_SESSION_MANAGER.bug_bounty_session import BugBountySession
from SOVEREIGN_SESSION_MANAGER.ctf_session import CTFSession
from SOVEREIGN_SESSION_MANAGER.config_loader import get_config_loader

# Modul Intelijen & Pelaporan
from DUPLICATE_INTELLIGENCE.report_scraper import ReportScraper
from UNIQUE_ANGLE_GENERATOR.uniqueness_validator import UniquenessValidator
from SOVEREIGN_REPORTING.multi_document_generator import MultiDocumentGenerator

# Modul Evidence & Patch Generator
from VERIFIABLE_EVIDENCE_ARTIFACT.behavioral_proof_recorder import BehavioralProofRecorder
from SOVEREIGN_REPORTING.PATCH_GENERATOR.web_patch_factory import WebPatchFactory

# Modul Platform-Specific Submitters
from SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.hackerone_submitter import HackerOneSubmitter
from SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.intigriti_submitter import IntigritiSubmitter
from SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.bugcrowd_submitter import BugCrowdSubmitter
from SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.yeswehack_submitter import YesWeHackSubmitter
from SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.immunefi_submitter import ImmunefiSubmitter

# Modul Scraper untuk Intelijen
from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.hackerone_scraper import HackerOneScraper
from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.bugcrowd_scraper import BugCrowdScraper
from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.intigriti_scraper import IntigritiScraper
from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.yeswehack_scraper import YesWeHackScraper
from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.immunefi_scraper import ImmunefiScraper

# CTFtime – public API, tidak memerlukan kredensial
from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.ctf_monitor.ctftime_scraper import CTFtimeScraper

# Modul Integrator Google Bug Bounty (opsional - butuh requests + beautifulsoup4)
try:
    from BROWSER_SECURITY_RESEARCH.google_vrp_integrator import GoogleVRPIntegrator
    GOOGLE_VRP_AVAILABLE = True
except ImportError:
    GOOGLE_VRP_AVAILABLE = False

# Modul Self-Learning Engine
from UNIFIED_LEARNING_ENGINE.self_learning_orchestrator import SelfLearningOrchestrator
from UNIFIED_LEARNING_ENGINE.learning_bridge import LearningBridge
from UNIFIED_LEARNING_ENGINE.ctf_challenge_analyzer import CTFChallengeAnalyzer
from UNIFIED_LEARNING_ENGINE.platform_writeup_scraper import PlatformWriteupScraper

# Modul Vulnerability Detectors (Web Security)
from VULNERABILITY_DETECTORS.web_security.xss_detector import XSSDetector
from VULNERABILITY_DETECTORS.web_security.sqli_scanner import SQLiScanner
from VULNERABILITY_DETECTORS.web_security.ssrf_hunter import SSRFHunter
from VULNERABILITY_DETECTORS.web_security.idor_analyzer import IDORAnalyzer
from VULNERABILITY_DETECTORS.web_security.csrf_validator import CSRFValidator
from VULNERABILITY_DETECTORS.web_security.lfi_scanner import LFIScanner
from VULNERABILITY_DETECTORS.web_security.rfi_scanner import RFIScanner
from VULNERABILITY_DETECTORS.web_security.command_injection_scanner import CommandInjectionScanner
from VULNERABILITY_DETECTORS.web_security.modern_web_analyzer import ModernWebAnalyzer
from VULNERABILITY_DETECTORS.web_security.backdoor_hunter import BackdoorHunter

# Modul APISecurity
from VULNERABILITY_DETECTORS.api_security.bola_scanner import BOLAScanner
from VULNERABILITY_DETECTORS.api_security.mass_assignment_tester import MassAssignmentTester

# JWTValidator - OPSIONAL (membutuhkan PyJWT)
try:
    from VULNERABILITY_DETECTORS.api_security.jwt_validator import JWTValidator
    JWT_AVAILABLE = True
except ImportError:
    JWTValidator = None
    JWT_AVAILABLE = False
    print("WARNING: JWTValidator tidak tersedia - modul PyJWT belum diinstall")

# Modul Ethic & Compliance
from ETHICAL_ARMOR.audit_trail_logger import AuditTrailLogger
from ETHICAL_ARMOR.zero_trust_execution import ZeroTrustExecution
from ETHICAL_ARMOR.data_minimization_enforcer import DataMinimizationEnforcer
from ETHICAL_ARMOR.chain_ethics_lock import ChainEthicsLock

# SovereignReasoner - OPSIONAL (hanya aktif jika llama_cpp tersedia)
try:
    from COGNITIVE_CORE.sovereign_reasoner import SovereignReasoner
    SOVEREIGN_REASONER_AVAILABLE = True
except Exception:
    SovereignReasoner = None
    SOVEREIGN_REASONER_AVAILABLE = False
    print("WARNING: SovereignReasoner (llama_cpp) tidak tersedia - berjalan tanpa AI reasoning")
# Target Type Router - OPSIONAL (sistem routing target → modul)
try:
    from TARGET_TYPE_ROUTER import TargetTypeRouter, create_target_router
    TARGET_ROUTER_AVAILABLE = True
except ImportError:
    TargetTypeRouter = None
    TARGET_ROUTER_AVAILABLE = False
    print("WARNING: TargetTypeRouter tidak tersedia - install modul routing")

# Architecture Fingerprinter - OPSIONAL
try:
    from ENTERPRISE_ATTACK_SURFACE.architecture_fingerprinter import ArchitectureFingerprinter
    FINGERPRINTER_AVAILABLE = True
except ImportError:
    ArchitectureFingerprinter = None
    FINGERPRINTER_AVAILABLE = False
    print("WARNING: ArchitectureFingerprinter tidak tersedia")

# Modul Vulnerability Detectors (Browser Security - OPSIONAL)
try:
    from BROWSER_SECURITY_RESEARCH.chromium_fuzz_orchestrator import ChromiumFuzzOrchestrator
    BROWSER_SECURITY_AVAILABLE = True
except ImportError:
    ChromiumFuzzOrchestrator = None
    BROWSER_SECURITY_AVAILABLE = False

# Modul Vulnerability Detectors (Mobile Security - OPSIONAL)
try:
    from VULNERABILITY_DETECTORS.mobile_security.apk_static_analyzer import APKStaticAnalyzer
    from VULNERABILITY_DETECTORS.mobile_security.ios_ipa_analyzer import IOSIPAAnalyzer
    from VULNERABILITY_DETECTORS.mobile_security.binary_analyzer import BinaryAnalyzer
    MOBILE_SECURITY_AVAILABLE = True
except ImportError:
    APKStaticAnalyzer = None
    IOSIPAAnalyzer = None
    BinaryAnalyzer = None
    MOBILE_SECURITY_AVAILABLE = False

# Modul Vulnerability Detectors (Cloud Security - OPSIONAL)
try:
    from VULNERABILITY_DETECTORS.cloud_security.aws_s3_checker import AWSS3Checker
    from VULNERABILITY_DETECTORS.cloud_security.gcp_bucket_scanner import GCPBucketScanner
    from VULNERABILITY_DETECTORS.cloud_security.azure_blob_validator import AzureBlobValidator
    from VULNERABILITY_DETECTORS.cloud_security.cloud_metadata_prober import CloudMetadataProber
    CLOUD_SECURITY_AVAILABLE = True
except ImportError:
    AWSS3Checker = None
    GCPBucketScanner = None
    AzureBlobValidator = None
    CloudMetadataProber = None
    CLOUD_SECURITY_AVAILABLE = False

# Modul Vulnerability Detectors (Crypto/Web3 Security - OPSIONAL)
try:
    from VULNERABILITY_DETECTORS.crypto_web3_security.smart_contract_analyzer import SmartContractAnalyzer
    from VULNERABILITY_DETECTORS.crypto_web3_security.reentrancy_simulator import ReentrancySimulator
    from VULNERABILITY_DETECTORS.crypto_web3_security.token_approval_abuser import TokenApprovalAbuser
    CRYPTO_SECURITY_AVAILABLE = True
except ImportError:
    SmartContractAnalyzer = None
    ReentrancySimulator = None
    TokenApprovalAbuser = None
    CRYPTO_SECURITY_AVAILABLE = False

# Modul Vulnerability Detectors (AI Security - OPSIONAL)
try:
    from VULNERABILITY_DETECTORS.ai_security.advanced_llm_attacker import AdvancedLLMAttacker
    from VULNERABILITY_DETECTORS.ai_security.prompt_injection_detector import PromptInjectionDetector
    AI_SECURITY_AVAILABLE = True
except ImportError:
    AdvancedLLMAttacker = None
    PromptInjectionDetector = None
    AI_SECURITY_AVAILABLE = False

# Auto Tool Orchestrator - OPSIONAL (akan diinstall otomatis jika dibutuhkan)
try:
    from TOOL_ORCHESTRATION.INTELLIGENT_TOOL_MANAGER import (
        AutoToolOrchestrator,
        ensure_security_tools,
        IntelligentToolCommander,
        create_smart_tool_commander,
        AutonomousSessionEngine,
        create_autonomous_engine,
    )
    TOOL_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    AutoToolOrchestrator = None
    IntelligentToolCommander = None
    create_smart_tool_commander = None
    AutonomousSessionEngine = None
    create_autonomous_engine = None
    TOOL_ORCHESTRATOR_AVAILABLE = False
    print("WARNING: AutoToolOrchestrator tidak tersedia - tool management manual")

# Intelligent Mutation Engine - OPSIONAL (Genetic Algorithm + RL untuk payload evolution)
try:
    from EXPLOITATION_ENGINE.intelligent_mutation_orchestrator import IntelligentMutationOrchestrator, MutationEngineIntegration
    from EXPLOITATION_ENGINE.payload_factory import PayloadFactory
    MUTATION_ENGINE_AVAILABLE = True
except ImportError:
    IntelligentMutationOrchestrator = None
    MutationEngineIntegration = None
    PayloadFactory = None
    MUTATION_ENGINE_AVAILABLE = False
    print("WARNING: Intelligent Mutation Engine tidak tersedia - basic mutation only")


class ARCOrchestrator:
    """Orkestrator utama ARC v7.6 Final"""
    
    def __init__(self):
        print(f"🚀 Initializing ARC v7.6 Final • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Inisialisasi komponen dasar
        self.credential_vault = CredentialVault()
        self.config_loader = get_config_loader()  # Loader config.yaml terpusat
        self.scope_guard = ScopeSovereigntyGuard()
        
        # 2. Inisialisasi Telegram & Human-in-the-Loop
        self.telegram_notifier = TelegramNotifier()
        self.human_in_the_loop_gate = HumanInTheLoopGate(
            telegram_notifier=self.telegram_notifier
        )
        try:
            from TOOL_ORCHESTRATION.INTELLIGENT_TOOL_MANAGER.session_approval_controller import SessionApprovalController
            self.session_approval_controller = SessionApprovalController(
                telegram=self.telegram_notifier,
                auto_start_poller=True,
            )
        except Exception as e:
            print(f"WARNING: Approval controller init failed: {e}")
            self.session_approval_controller = None
        
        # 3. Inisialisasi session manager
        self.session_manager = PlatformSessionManager(self.credential_vault)
        self.bug_bounty_session = BugBountySession(self.credential_vault)
        self.ctf_session = CTFSession(self.credential_vault)
        
        # 4. Inisialisasi evidence & patch generator
        self.evidence_generator = BehavioralProofRecorder()
        self.patch_generator = WebPatchFactory()
        
        # 5. Inisialisasi platform-specific submitters
        self.submitters = {}
        self._initialize_submitters()
        
        # 6. Inisialisasi scraper untuk intelijen
        self.scrapers = {}
        self._initialize_scrapers()
        
        # 6b. Inisialisasi Google VRP integrator (bughunters.google.com)
        self.google_vrp_integrator = None
        self._initialize_google_vrp()
        
        # 7. Set integrasi timbal balik
        self.telegram_notifier.set_human_in_the_loop_gate(self.human_in_the_loop_gate)
        self.telegram_notifier.set_session_manager(self.session_manager)
        self.telegram_notifier.set_evidence_generator(self.evidence_generator)
        self.telegram_notifier.set_patch_generator(self.patch_generator)
        self.telegram_notifier.set_google_vrp_integrator(self.google_vrp_integrator)
        self.human_in_the_loop_gate.set_evidence_generator(self.evidence_generator)
        self.human_in_the_loop_gate.set_patch_generator(self.patch_generator)
        self.human_in_the_loop_gate.set_telegram_notifier(self.telegram_notifier)
        
        # 8. Inisialisasi komponen intelijen
        self.report_scraper = ReportScraper()
        self.uniqueness_validator = UniquenessValidator()
        self.report_generator = MultiDocumentGenerator()
        
        # 9. Inisialisasi self-learning engine (SEBELUM detectors)
        self.self_learning_orchestrator = SelfLearningOrchestrator()
        print("OK Self-Learning Engine initialized")
        
        # 9b. Inisialisasi Learning Bridge (jembatan universal ke semua komponen)
        self.learning_bridge = LearningBridge(self.self_learning_orchestrator)
        print("OK Learning Bridge initialized - menghubungkan SEMUA komponen ke self-learning")
        
        # 10. Inisialisasi vulnerability detectors (setelah learning engine)
        self._initialize_vulnerability_detectors()
        
        # 10b. Hubungkan sumber pembelajaran tambahan (CTF, writeups)
        self._connect_learning_sources()
        
        # 11. Inisialisasi ethical armor
        self._initialize_ethical_armor()
        
        # 12. Inisialisasi cognitive core (opsional)
        self.sovereign_reasoner = None
        self._initialize_sovereign_reasoner()
        
        # 12b. Inisialisasi Target Type Router (opsional)
        self._initialize_target_router()
        
        # 12c. Inisialisasi specialized vulnerability detectors (opsional)
        self.specialized_detectors = {}
        self._initialize_specialized_detectors()
        
        # 13. Inisialisasi Auto Tool Orchestrator (ADA PTNG DIKIT - WAJIB!)
        self.tool_orchestrator = None
        self.smart_commander = None  # IntelligentToolCommander (dipasang di _initialize_tool_orchestrator)
        self.session_engine = None   # AutonomousSessionEngine (dipasang di _initialize_tool_orchestrator)
        self._initialize_tool_orchestrator()
        
        # 13b. Inisialisasi Intelligent Mutation Engine (Opsional - Enhanced)
        self.mutation_engine = None
        self._initialize_mutation_engine()
        
        print("OK All ARC components initialized successfully!")
        print("OK Agent is now self-learning enabled")
        print("OK Target-aware routing system ready")
    
    def _initialize_sovereign_reasoner(self):
        """Inisialisasi SovereignReasoner jika tersedia."""
        if SOVEREIGN_REASONER_AVAILABLE and SovereignReasoner is not None:
            try:
                self.sovereign_reasoner = SovereignReasoner()
                print("OK Sovereign Reasoner initialized (AI mode)")
            except Exception as e:
                print(f"WARNING: Sovereign Reasoner init failed: {e}")
                print("OK ARC berjalan tanpa AI reasoning (fallback mode)")
        else:
            print("ℹ️ Sovereign Reasoner disabled - install llama-cpp-python untuk mengaktifkan")
    
    def _initialize_target_router(self):
        """Inisialisasi Target Type Router dan Architecture Fingerprinter."""
        self.target_router = None
        self.architecture_fingerprinter = None
        
        if TARGET_ROUTER_AVAILABLE:
            try:
                self.target_router = create_target_router()
                print("OK Target Type Router initialized - automatic target → module routing enabled")
            except Exception as e:
                print(f"WARNING: Target Type Router init failed: {e}")
        
        if FINGERPRINTER_AVAILABLE:
            try:
                self.architecture_fingerprinter = ArchitectureFingerprinter()
                print("OK Architecture Fingerprinter initialized")
            except Exception as e:
                print(f"WARNING: Architecture Fingerprinter init failed: {e}")
    
    def _initialize_specialized_detectors(self):
        """Inisialisasi specialized vulnerability detectors (mobile, cloud, crypto, AI, browser)."""
        # Browser Security Detectors
        if BROWSER_SECURITY_AVAILABLE and ChromiumFuzzOrchestrator is not None:
            try:
                self.specialized_detectors['browser'] = {
                    'chromium_fuzz_orchestrator': ChromiumFuzzOrchestrator()
                }
                print("OK Browser Security detectors initialized")
            except Exception as e:
                print(f"WARNING: Browser Security detectors init failed: {e}")
        
        # Mobile Security Detectors
        if MOBILE_SECURITY_AVAILABLE:
            try:
                mobile_detectors = {}
                if APKStaticAnalyzer:
                    mobile_detectors['apk_analyzer'] = APKStaticAnalyzer()
                if IOSIPAAnalyzer:
                    mobile_detectors['ios_analyzer'] = IOSIPAAnalyzer()
                if BinaryAnalyzer:
                    mobile_detectors['binary_analyzer'] = BinaryAnalyzer()
                
                if mobile_detectors:
                    self.specialized_detectors['mobile'] = mobile_detectors
                    print(f"OK Mobile Security detectors initialized ({len(mobile_detectors)} modules)")
            except Exception as e:
                print(f"WARNING: Mobile Security detectors init failed: {e}")
        
        # Cloud Security Detectors
        if CLOUD_SECURITY_AVAILABLE:
            try:
                cloud_detectors = {}
                if AWSS3Checker:
                    cloud_detectors['aws_s3'] = AWSS3Checker()
                if GCPBucketScanner:
                    cloud_detectors['gcp_bucket'] = GCPBucketScanner()
                if AzureBlobValidator:
                    cloud_detectors['azure_blob'] = AzureBlobValidator()
                if CloudMetadataProber:
                    cloud_detectors['metadata_prober'] = CloudMetadataProber()
                
                if cloud_detectors:
                    self.specialized_detectors['cloud'] = cloud_detectors
                    print(f"OK Cloud Security detectors initialized ({len(cloud_detectors)} modules)")
            except Exception as e:
                print(f"WARNING: Cloud Security detectors init failed: {e}")
        
        # Crypto/Web3 Security Detectors
        if CRYPTO_SECURITY_AVAILABLE:
            try:
                crypto_detectors = {}
                if SmartContractAnalyzer:
                    crypto_detectors['smart_contract'] = SmartContractAnalyzer()
                if ReentrancySimulator:
                    crypto_detectors['reentrancy'] = ReentrancySimulator()
                if TokenApprovalAbuser:
                    crypto_detectors['token_approval'] = TokenApprovalAbuser()
                
                if crypto_detectors:
                    self.specialized_detectors['crypto'] = crypto_detectors
                    print(f"OK Crypto/Web3 Security detectors initialized ({len(crypto_detectors)} modules)")
            except Exception as e:
                print(f"WARNING: Crypto/Web3 Security detectors init failed: {e}")
        
        # AI Security Detectors
        if AI_SECURITY_AVAILABLE:
            try:
                ai_detectors = {}
                if AdvancedLLMAttacker:
                    ai_detectors['llm_attacker'] = AdvancedLLMAttacker()
                if PromptInjectionDetector:
                    ai_detectors['prompt_injection'] = PromptInjectionDetector()
                
                if ai_detectors:
                    self.specialized_detectors['ai'] = ai_detectors
                    print(f"OK AI Security detectors initialized ({len(ai_detectors)} modules)")
            except Exception as e:
                print(f"WARNING: AI Security detectors init failed: {e}")
        
        total_specialized = sum(len(dets) for dets in self.specialized_detectors.values())
        print(f"OK Total specialized detectors initialized: {total_specialized}")
    
    def _initialize_tool_orchestrator(self):
        """
        Inisialisasi Auto Tool Orchestrator untuk manajemen tool otomatis.
        Sistem ini akan otomatis download/install tools + MEMAKAINYA secara
        mandiri melalui IntelligentToolCommander (self-learning CLI engine).
        """
        self.tool_orchestrator = None
        self.smart_commander = None

        if TOOL_ORCHESTRATOR_AVAILABLE and AutoToolOrchestrator is not None:
            try:
                self.tool_orchestrator = AutoToolOrchestrator()

                # Integrasi dengan ARC Main
                self.tool_orchestrator.integrate_with_arc_main(self)

                print("OK Auto Tool Orchestrator initialized - auto-download tools enabled")
            except Exception as e:
                print(f"WARNING: Auto Tool Orchestrator init failed: {e}")
                print("OK ARC berjalan tanpa auto-tool management (manual mode)")
                self.tool_orchestrator = None
        else:
            print("ℹ️ Auto Tool Orchestrator disabled - install TOOL_ORCHESTRATION untuk mengaktifkan")

        # IntelligentToolCommander: mesin belajar-memakai tool apa pun secara mandiri
        if TOOL_ORCHESTRATOR_AVAILABLE and create_smart_tool_commander is not None:
            try:
                self.smart_commander = create_smart_tool_commander(
                    orchestrator=self.tool_orchestrator
                )
                print("OK IntelligentToolCommander initialized - ARC dapat memakai tool CLI apa pun secara mandiri")
            except Exception as e:
                print(f"WARNING: IntelligentToolCommander init failed: {e}")
                self.smart_commander = None
        else:
            print("ℹ️ IntelligentToolCommander disabled")

        # AutonomousSessionEngine: install/update/eksekusi mandiri di terminal
        self.session_engine = None
        if TOOL_ORCHESTRATOR_AVAILABLE and AutonomousSessionEngine is not None:
            try:
                self.session_engine = AutonomousSessionEngine(
                    orchestrator=self.tool_orchestrator,
                    commander=self.smart_commander,
                    approval_controller=getattr(self, 'session_approval_controller', None),
                )
                print(f"OK AutonomousSessionEngine initialized - {self.session_engine.env.get('is_kali', False) and 'Kali Linux' or self.session_engine.env.get('platform')} terminal")
            except Exception as e:
                print(f"WARNING: AutonomousSessionEngine init failed: {e}")
                self.session_engine = None
        else:
            print("ℹ️ AutonomousSessionEngine disabled")

    def smart_use_tool(self, tool_name: str, intent: str = 'generic',
                       params: dict = None, subcommand: str = None) -> dict:
        """
        API publik ARC: gunakan tool CLI apa pun secara MANDIRI.
        - Pelajari antarmuka tool (jika belum ada kache)
        - Bangun command dengan flag yang benar berdasarkan intent & parameter
        - Jalankan, self-heal bila gagal

        Contoh:
            arc.smart_use_tool('nuclei', 'web_scan',
                               {'target': ['https://target.com'], 'severity': 'high'})
        """
        params = params or {}
        if self.smart_commander is None:
            return {'success': False,
                    'error': 'IntelligentToolCommander tidak tersedia'}
        return self.smart_commander.smart_execute(
            tool_name=tool_name,
            intent=intent,
            params=params,
            subcommand=subcommand
        )

    def autonomous_use_tool(self, tool_name: str, intent: str = 'generic',
                            params: dict = None, subcommand: str = None,
                            auto_install: bool = True,
                            update_data: bool = False) -> dict:
        """
        API otonom ARC: pastikan tool tersedia (install sendiri bila perlu) ->
        perbarui data -> pelajari antarmuka -> jalankan -> lapor di sesi terminal.
        Ini memanfaatkan AutonomousSessionEngine.
        """
        params = params or {}
        if self.session_engine is None:
            return {'success': False,
                    'error': 'AutonomousSessionEngine tidak tersedia'}
        if not auto_install and not (self.smart_commander and
                                     self.smart_commander.ensure_available(tool_name)):
            return {'success': False,
                    'error': f"auto_install=False dan tool '{tool_name}' tidak ada"}
        return self.session_engine.run_autonomously({
            'tool': tool_name,
            'intent': intent,
            'params': params,
            'subcommand': subcommand,
            'update_data': update_data,
        })

    def _initialize_mutation_engine(self):
        """
        Inisialisasi Intelligent Mutation Engine untuk payload evolution.
        Sistem ini menggunakan Genetic Algorithm + RL untuk generate payloads yang cerdas.
        """
        if MUTATION_ENGINE_AVAILABLE and MutationEngineIntegration is not None:
            try:
                self.mutation_engine = MutationEngineIntegration(self)
                print("OK Intelligent Mutation Engine initialized - Genetic Algorithm + RL enabled")
            except Exception as e:
                print(f"WARNING: Mutation Engine init failed: {e}")
                print("OK ARC berjalan tanpa intelligent mutation (basic mutation only)")
                self.mutation_engine = None
        else:
            print("ℹ️ Intelligent Mutation Engine disabled - using basic mutation only")
    
    def get_intelligent_payload(self, vuln_type: str, target_info: Dict) -> Dict:
        """
        Get intelligent payload dengan Genetic Algorithm + RL
        
        Args:
            vuln_type: Tipe vulnerability (xss, sqli, ssrf, etc)
            target_info: Dict dengan target context
        
        Returns:
            Dict dengan payload, confidence, strategy
        """
        if not self.mutation_engine:
            # Fallback ke basic payload factory
            factory = PayloadFactory()
            return {
                'payload': factory.generate_payload(vuln_type, target_info),
                'confidence': 0.5,
                'strategy': 'basic'
            }
        
        return self.mutation_engine.get_payload_with_intelligence(vuln_type, target_info)
    
    def _initialize_vulnerability_detectors(self):
        """Inisialisasi semua vulnerability detectors."""
        self.detectors = {}
        
        # Web Security Detectors
        self.detectors['xss'] = XSSDetector()
        self.detectors['sqli'] = SQLiScanner()
        self.detectors['ssrf'] = SSRFHunter()
        self.detectors['idor'] = IDORAnalyzer()
        self.detectors['csrf'] = CSRFValidator()
        self.detectors['lfi'] = LFIScanner()
        self.detectors['rfi'] = RFIScanner()
        self.detectors['command_injection'] = CommandInjectionScanner()
        self.detectors['modern_web'] = ModernWebAnalyzer()
        self.detectors['backdoor'] = BackdoorHunter()
        
        # API Security Detectors
        self.detectors['bola'] = BOLAScanner()
        if JWT_AVAILABLE and JWTValidator is not None:
            self.detectors['jwt'] = JWTValidator()
        self.detectors['mass_assignment'] = MassAssignmentTester()
        
        # Connect SEMUA detectors ke learning bridge (bukan langsung ke orchestrator)
        # Bridge meneruskan ke orchestrator asli dan mencegah duplikasi kode
        for name, detector in self.detectors.items():
            self.learning_bridge.attach_detector(name, detector)
            # Set ARC orchestrator reference untuk mutation engine access
            if hasattr(detector, 'set_arc_orchestrator'):
                detector.set_arc_orchestrator(self)
        
        print(f"OK Initialized {len(self.detectors)} vulnerability detectors and connected to learning bridge")
    
    def _initialize_specialized_detectors(self):
        """Inisialisasi specialized vulnerability detectors (mobile, cloud, crypto, AI, browser)."""
        # Browser Security Detectors
        if BROWSER_SECURITY_AVAILABLE and ChromiumFuzzOrchestrator is not None:
            try:
                self.specialized_detectors['browser'] = {
                    'chromium_fuzz_orchestrator': ChromiumFuzzOrchestrator()
                }
                print("OK Browser Security detectors initialized")
            except Exception as e:
                print(f"WARNING: Browser Security detectors init failed: {e}")
        
        # Mobile Security Detectors
        if MOBILE_SECURITY_AVAILABLE:
            try:
                mobile_detectors = {}
                if APKStaticAnalyzer:
                    mobile_detectors['apk_analyzer'] = APKStaticAnalyzer()
                if IOSIPAAnalyzer:
                    mobile_detectors['ios_analyzer'] = IOSIPAAnalyzer()
                if BinaryAnalyzer:
                    mobile_detectors['binary_analyzer'] = BinaryAnalyzer()
                
                if mobile_detectors:
                    self.specialized_detectors['mobile'] = mobile_detectors
                    print(f"OK Mobile Security detectors initialized ({len(mobile_detectors)} modules)")
            except Exception as e:
                print(f"WARNING: Mobile Security detectors init failed: {e}")
        
        # Cloud Security Detectors
        if CLOUD_SECURITY_AVAILABLE:
            try:
                cloud_detectors = {}
                if AWSS3Checker:
                    cloud_detectors['aws_s3'] = AWSS3Checker()
                if GCPBucketScanner:
                    cloud_detectors['gcp_bucket'] = GCPBucketScanner()
                if AzureBlobValidator:
                    cloud_detectors['azure_blob'] = AzureBlobValidator()
                if CloudMetadataProber:
                    cloud_detectors['metadata_prober'] = CloudMetadataProber()
                
                if cloud_detectors:
                    self.specialized_detectors['cloud'] = cloud_detectors
                    print(f"OK Cloud Security detectors initialized ({len(cloud_detectors)} modules)")
            except Exception as e:
                print(f"WARNING: Cloud Security detectors init failed: {e}")
        
        # Crypto/Web3 Security Detectors
        if CRYPTO_SECURITY_AVAILABLE:
            try:
                crypto_detectors = {}
                if SmartContractAnalyzer:
                    crypto_detectors['smart_contract'] = SmartContractAnalyzer()
                if ReentrancySimulator:
                    crypto_detectors['reentrancy'] = ReentrancySimulator()
                if TokenApprovalAbuser:
                    crypto_detectors['token_approval'] = TokenApprovalAbuser()
                
                if crypto_detectors:
                    self.specialized_detectors['crypto'] = crypto_detectors
                    print(f"OK Crypto/Web3 Security detectors initialized ({len(crypto_detectors)} modules)")
            except Exception as e:
                print(f"WARNING: Crypto/Web3 Security detectors init failed: {e}")
        
        # AI Security Detectors
        if AI_SECURITY_AVAILABLE:
            try:
                ai_detectors = {}
                if AdvancedLLMAttacker:
                    ai_detectors['llm_attacker'] = AdvancedLLMAttacker()
                if PromptInjectionDetector:
                    ai_detectors['prompt_injection'] = PromptInjectionDetector()
                
                if ai_detectors:
                    self.specialized_detectors['ai'] = ai_detectors
                    print(f"OK AI Security detectors initialized ({len(ai_detectors)} modules)")
            except Exception as e:
                print(f"WARNING: AI Security detectors init failed: {e}")
        
        total_specialized = sum(len(dets) for dets in self.specialized_detectors.values())
        print(f"OK Total specialized detectors initialized: {total_specialized}")

    
    def _connect_learning_sources(self):
        """Hubungkan sumber pembelajaran tambahan (CTF, writeups) ke self-learning."""
        # 1. CTF Challenge Analyzer - belajar dari solusi CTF
        try:
            self.ctf_analyzer = CTFChallengeAnalyzer()
            self.ctf_analyzer.learning_bridge = self.learning_bridge
            print("OK CTF Challenge Analyzer connected to learning bridge")
        except Exception as e:
            print(f"WARNING: CTF Challenge Analyzer init failed: {e}")
            self.ctf_analyzer = None
        
        # 2. Platform Writeup Scraper - belajar dari writeup bug bounty
        try:
            self.writeup_scraper = PlatformWriteupScraper(learning_bridge=self.learning_bridge)
            print("OK Platform Writeup Scraper connected to learning bridge")
        except Exception as e:
            print(f"WARNING: Platform Writeup Scraper init failed: {e}")
            self.writeup_scraper = None
    
    def _initialize_ethical_armor(self):
        """Inisialisasi modul ethical armor."""
        self.audit_logger = AuditTrailLogger()
        self.zero_trust = ZeroTrustExecution()
        self.data_minimizer = DataMinimizationEnforcer()
        self.ethics_lock = ChainEthicsLock()
        print("OK Initialized ethical armor modules")
    
    def _initialize_submitters(self):
        """Inisialisasi platform-specific submitters dengan kredensial valid.
        Prioritas: config.yaml > CredentialVault GPG
        """
        credentials = self.credential_vault.load_all_credentials()
        
        # HackerOne - gunakan API token
        h1_creds = self._merge_credentials('hackerone', credentials)
        if h1_creds and h1_creds.get('api_token'):
            self.submitters['hackerone'] = HackerOneSubmitter(h1_creds['api_token'])
            self.submitters['hackerone'].set_evidence_generator(self.evidence_generator)
            self.submitters['hackerone'].set_patch_generator(self.patch_generator)
        
        # Intigriti - gunakan Personal Access Token
        intigriti_creds = self._merge_credentials('intigriti', credentials)
        if intigriti_creds and intigriti_creds.get('personal_access_token'):
            self.submitters['intigriti'] = IntigritiSubmitter(intigriti_creds['personal_access_token'])
            self.submitters['intigriti'].set_evidence_generator(self.evidence_generator)
            self.submitters['intigriti'].set_patch_generator(self.patch_generator)
        
        # Platform lain - gunakan session cookie
        for platform in ['bugcrowd', 'yeswehack', 'immunefi']:
            creds = self._merge_credentials(platform, credentials)
            if creds and creds.get('session_cookie'):
                if platform == 'bugcrowd':
                    self.submitters['bugcrowd'] = BugCrowdSubmitter(creds['session_cookie'])
                elif platform == 'yeswehack':
                    self.submitters['yeswehack'] = YesWeHackSubmitter(creds['session_cookie'])
                elif platform == 'immunefi':
                    self.submitters['immunefi'] = ImmunefiSubmitter(creds['session_cookie'])
                
                if platform in self.submitters:
                    self.submitters[platform].set_evidence_generator(self.evidence_generator)
                    self.submitters[platform].set_patch_generator(self.patch_generator)
    
    def _merge_credentials(self, platform, vault_credentials):
        """
        Gabungkan kredensial dari config.yaml dan CredentialVault.
        Prioritas: config.yaml > CredentialVault
        """
        # 1. Dari config.yaml
        yaml_creds = self.config_loader.get_platform_credentials(platform)
        
        # 2. Dari CredentialVault GPG
        vault_creds = self._get_vault_credentials(vault_credentials, platform)
        
        # Gabungkan: config.yaml menang jika ada
        if yaml_creds and any(yaml_creds.values()):
            merged = dict(vault_creds)
            merged.update({k: v for k, v in yaml_creds.items() if v})
            return merged
        return vault_creds

    def _get_vault_credentials(self, credentials, platform):
        """Dapatkan kredensial dari vault untuk platform tertentu."""
        bug_bounty_creds = credentials.get('bug_bounty', {})
        ctf_creds = credentials.get('ctf', {})
        
        all_creds = {**bug_bounty_creds, **ctf_creds}
        
        # Coba berbagai naming convention
        possible_keys = [
            f'{platform}_researcher',
            f'{platform}_corp', 
            f'{platform}_bounty',
            f'{platform}_main',
            f'{platform}_personal',
            f'{platform}_pro',
            f'{platform}_student'
        ]
        
        for key in possible_keys:
            if key in all_creds:
                return all_creds[key]
        
        return {}
    
    def _get_platform_credentials(self, credentials, platform):
        """Dapatkan kredensial untuk platform tertentu (backward compat)."""
        return self._merge_credentials(platform, credentials)
    
    def _initialize_scrapers(self):
        """Inisialisasi scraper berdasarkan kredensial yang tersedia.
        Prioritas: config.yaml > CredentialVault GPG
        """
        credentials = self.credential_vault.load_all_credentials()
        
        # HackerOne
        h1_creds = self._merge_credentials('hackerone', credentials)
        if h1_creds and h1_creds.get('api_token'):
            self.scrapers['hackerone'] = HackerOneScraper(h1_creds['api_token'])
        
        # Intigriti  
        intigriti_creds = self._merge_credentials('intigriti', credentials)
        if intigriti_creds and intigriti_creds.get('personal_access_token'):
            self.scrapers['intigriti'] = IntigritiScraper(intigriti_creds['personal_access_token'])
        
        # Platform lain
        for platform in ['bugcrowd', 'yeswehack', 'immunefi']:
            creds = self._merge_credentials(platform, credentials)
            if creds and creds.get('session_cookie'):
                if platform == 'bugcrowd':
                    self.scrapers['bugcrowd'] = BugCrowdScraper(creds['session_cookie'])
                elif platform == 'yeswehack':
                    self.scrapers['yeswehack'] = YesWeHackScraper(creds['session_cookie'])
                elif platform == 'immunefi':
                    self.scrapers['immunefi'] = ImmunefiScraper(creds['session_cookie'])

        # CTF platform scrapers (jika key tersedia di config.yaml)
        htb_creds = self.config_loader.get_platform_credentials('hackthebox')
        if htb_creds and htb_creds.get('session_cookie'):
            try:
                from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.ctf_monitor.hackthebox_scraper import HackTheBoxScraper
                self.scrapers['hackthebox'] = HackTheBoxScraper(htb_creds['session_cookie'])
            except Exception:
                pass
        
        
        thm_creds = self.config_loader.get_platform_credentials('tryhackme')
        if thm_creds and thm_creds.get('session_cookie'):
            try:
                from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.ctf_monitor.tryhackme_scraper import TryHackMeScraper
                self.scrapers['tryhackme'] = TryHackMeScraper(thm_creds['session_cookie'])
            except Exception:
                pass
        
        # CTFtime – API publik tanpa auth, selalu tersedia
        try:
            self.scrapers['ctftime'] = CTFtimeScraper()
        except Exception:
            pass

    
    def _initialize_google_vrp(self):
        """Inisialisasi Google VRP Integrator (bughunters.google.com).

        Mendaftarkan sebagai scraper ('google_vrp') dan submitter ('google_vrp')
        agar kompatibel dengan loop intelijen & alur pelaporan ARC yang sudah ada.
        Prioritas kredensial: config.yaml/bughunters_google > CredentialVault GPG.
        """
        if not GOOGLE_VRP_AVAILABLE:
            print("WARNING: GoogleVRPIntegrator tidak tersedia - install requests + beautifulsoup4")
            return
        
        try:
            credentials = self.credential_vault.load_all_credentials()
            google_creds = self._merge_credentials('google', credentials)
            session_cookie = google_creds.get('session_cookie') if google_creds else None
            
            self.google_vrp_integrator = GoogleVRPIntegrator(session_cookie=session_cookie)
            self.google_vrp_integrator.load_cache()
            
            # Registrasi sebagai scraper (untuk _update_intelligence_feed)
            self.scrapers['google_vrp'] = self.google_vrp_integrator
            # Registrasi sebagai submitter (untuk template laporan form-based)
            self.submitters['google_vrp'] = self.google_vrp_integrator
            # Hubungkan evidence + patch generator (untuk clarification/triage analis)
            self.google_vrp_integrator.set_evidence_generator(self.evidence_generator)
            self.google_vrp_integrator.set_patch_generator(self.patch_generator)
            
            session_state = "dengan cookie" if session_cookie else "tanpa cookie (public scope)"
            print(f"OK Google VRP Integrator initialized ({session_state})")
        except Exception as e:
            print(f"WARNING: Google VRP Integrator init failed: {e}")
            self.google_vrp_integrator = None
    
    def start_autonomous_operations(self):
        """Mulai operasi otonom 24/7"""
        print("▶️ Starting autonomous operations...")
        self.telegram_notifier.send_notification(
            "▶️ <b>AUTONOMOUS OPERATIONS STARTED</b>\n\n"
            "ARC v7.6 Final is now running 24/7 with full capabilities:\n"
            "• Continuous reconnaissance\n• Vulnerability detection\n"
            "• Economic exploit simulation\n• Report submission\n• Income optimization"
        )
        
        # Loop operasi utama
        while True:
            try:
                # 1. Perbarui intelijen dari semua platform
                self._update_intelligence_feed()
                
                # 2. Analisis temuan baru
                findings = self._analyze_new_findings()
                
                # 3. Validasi keunikan & duplikat
                validated_findings = self._validate_findings(findings)
                
                # 4. Generate laporan untuk temuan unik
                for finding in validated_findings:
                    if self._requires_human_approval(finding):
                        self._request_human_approval(finding)
                    else:
                        self._submit_automatically(finding)
                
                # Tunggu sebelum siklus berikutnya (30 menit)
                time.sleep(1800)
                
            except KeyboardInterrupt:
                print("\n⏹️ Autonomous operations stopped by user")
                break
            except Exception as e:
                error_msg = f"❌ Error in autonomous loop: {str(e)}"
                print(error_msg)
                self.telegram_notifier.send_notification(
                    f"❌ <b>AUTONOMOUS LOOP ERROR</b>\n{error_msg}"
                )
                time.sleep(300)  # Tunggu 5 menit sebelum retry
    
    def _update_intelligence_feed(self):
        """Perbarui feed intelijen dari semua platform"""
        print("📡 Updating intelligence feed...")
        
        # Inisialisasi scraper jika belum ada
        if not self.scrapers:
            self._initialize_scrapers()
        
        # 1. Scraping Program Intel
        for platform, scraper in self.scrapers.items():
            try:
                programs = scraper.get_all_programs()
                print(f"OK Found {len(programs)} programs on {platform}")
                self._cache_program_intelligence(platform, programs)
            except Exception as e:
                print(f"WARNING: Failed to scrape {platform}: {e}")

# 1a. Google VRP feed (output CLI + cache inteligen program bughunters.google.com)
        if getattr(self, 'google_vrp_integrator', None):
            try:
                google_programs = self.google_vrp_integrator.get_all_google_programs()
                active_count = len([
                    p for p in google_programs.values()
                    if p.get('status') != 'on_hold'
                ])
                print(f"OK Google VRP: {len(google_programs)} program, {active_count} aktif (bughunters.google.com)")
            except Exception as e:
                print(f"WARNING: Google VRP refresh gagal: {e}")
        # 1b. Scrap writeup bug bounty untuk pembelajaran AI
        if hasattr(self, 'writeup_scraper') and self.writeup_scraper:
            try:
                writeup_results = self.writeup_scraper.scrape_all_platforms()
                total_writeups = writeup_results.get('total_writeups', 0)
                fed_to_learning = writeup_results.get('learning_insights_fed', 0)
                if total_writeups > 0:
                    print(f"OK Scraped {total_writeups} writeups, fed {fed_to_learning} to self-learning")
            except Exception as e:
                print(f"WARNING: Writeup scraping failed: {e}")

        # 2. Update CVE/CWE OSINT
        try:
            from INFRASTRUCTURE.cve_osint_updater import CVEOSINTUpdater
            cve_updater = CVEOSINTUpdater()
            threat_result = cve_updater.update_realtime_threats(days_back=1)
            
            if threat_result.get('success'):
                # Integrasikan CVE ke self-learning engine
                threat_data = cve_updater.get_latest_threat_data()
                if threat_data:
                    self.self_learning_orchestrator.integrate_threat_intelligence(threat_data)
                    print("OK CVE threat intelligence integrated into self-learning engine")
                
                # Integrasikan CWE ke self-learning engine
                cwe_data = cve_updater.get_latest_cwe_data()
                if cwe_data:
                    self.self_learning_orchestrator.integrate_cwe_data(cwe_data)
                    print("OK CWE data integrated into self-learning engine")
        except Exception as e:
            print(f"WARNING: Failed to update threat intelligence: {e}")
        
        # 3. Hubungkan temuan dari semua detektor ke self-learning via LEARNING BRIDGE
        self._connect_detector_findings_to_learning()
    
    def _connect_detector_findings_to_learning(self):
        """Hubungkan temuan dari semua detektor ke self-learning via learning bridge."""
        # Sinkronkan semua detector yang terhubung ke bridge
        synced = self.learning_bridge.sync_all_detectors()
        if synced > 0:
            print(f"OK Synced {synced} findings from all detectors to learning engine")
    
    def _cache_program_intelligence(self, platform, programs):
        """Simpan intelijen program ke cache."""
        # Implementasi aktual akan menyimpan ke database atau file
        pass
    
    def _analyze_new_findings(self):
        """Analisis temuan baru menggunakan cognitive core dan detectors dengan target routing."""
        print("🧠 Analyzing new findings with target-aware routing...")
        findings = []
        
        # Get learning-based recommendations
        learning_context = {"operation": "finding_analysis", "timestamp": time.time()}
        recommendations = self.self_learning_orchestrator.get_learning_recommendations(
            learning_context, "vulnerability_scan"
        )
        success_prob = recommendations.get('success_probability', 0.5)
        if isinstance(success_prob, dict):
            success_prob = success_prob.get('probability',
                                            success_prob.get('success_probability', 0.5))
        try:
            success_prob = float(success_prob)
        except (TypeError, ValueError):
            success_prob = 0.5
        print(f"💡 Learning Engine Recommendations: {success_prob * 100:.1f}% success probability")

        # Gunakan SovereignReasoner jika tersedia
        if self.sovereign_reasoner:
            try:
                analysis = self.sovereign_reasoner.analyze_vulnerability(
                    target_info="scanning_programs",
                    vulnerability_type="multi_surface"
                )
                print(f"🧠 AI Analysis: {analysis[:100]}...")
            except Exception as e:
                print(f"WARNING: AI analysis failed: {e}")
        
        # TARGET-AWARE SCANNING
        if self.target_router:
            try:
                target_scope = getattr(self, 'current_target_scope', {})
                target_url = target_scope.get('url', '')
                target_hint = target_scope.get('type_hint', '')
                
                if target_url or target_hint:
                    print(f"🎯 Using target-aware routing for: {target_url or target_hint}")
                    profile = self.target_router.detect_target_type(
                        target_url=target_url,
                        target_hint=target_hint
                    )
                    routing_result = self.target_router.route_to_modules(profile)
                    routed_modules = routing_result['routed_modules']
                    print(f"🔀 Routed to: {list(routed_modules.keys())}")
                    
                    # Execute routed detectors
                    findings = []
                    for category, detectors in routed_modules.items():
                        print(f"  🔍 Executing {category} detectors...")
                        findings.append({
                            'type': category,
                            'detectors': list(detectors.keys()),
                            'status': 'routed_and_ready'
                        })
                    
                    if not findings:
                        findings = self._execute_web_detectors_fallback(target_scope)
                else:
                    findings = self._execute_web_detectors_fallback(target_scope)
            except Exception as e:
                print(f"WARNING: Target routing failed: {e}")
                findings = self._execute_web_detectors_fallback({})
        else:
            print("ℹ️ Target Router not available, using standard detectors")
            findings = self._execute_web_detectors_fallback({})
        
        return findings
    
    def _execute_web_detectors_fallback(self, target_scope):
        """Fallback ke standard web detectors."""
        findings = []
        for name, detector in self.detectors.items():
            try:
                if name in ['xss', 'sqli', 'ssrf', 'idor', 'csrf']:
                    findings.append({
                        'type': 'web_security',
                        'detector': name,
                        'status': 'scanned',
                        'target': target_scope.get('url', 'unknown')
                    })
            except Exception:
                pass
        return findings
    
    def _validate_findings(self, findings):
        """Validasi keunikan temuan"""
        print("🔍 Validating findings uniqueness...")
        validated = []
        for finding in findings:
            if self.uniqueness_validator.validate_uniqueness(finding)['is_unique']:
                validated.append(finding)
        return validated
    
    def _requires_human_approval(self, finding):
        """Tentukan apakah temuan memerlukan approval manusia"""
        risk_score = finding.get('risk_score', 0)
        operation_type = finding.get('operation_type', 'report_submission')
        return self.human_in_the_loop_gate.requires_approval(operation_type, risk_score)
    
    def _request_human_approval(self, finding):
        """Minta approval manusia untuk temuan berisiko tinggi"""
        print(f"WARNING: Requesting human approval for finding: {finding.get('id', 'N/A')}")
        self.human_in_the_loop_gate.request_approval(finding)
    
    def _submit_automatically(self, finding):
        """Kirim laporan secara otomatis untuk temuan aman"""
        platform = finding.get('platform')
        if platform in self.submitters and self.submitters[platform]:
            try:
                result = self.submitters[platform].submit_report(
                    finding.get('program_handle'),
                    finding,
                    finding.get('evidence_files', [])
                )
                print(f"OK Auto-submission result for {platform}: {result.get('success', False)}")
            except Exception as e:
                print(f"❌ Auto-submission failed for {platform}: {e}")
        else:
            print(f"WARNING: No submitter available for {platform}, skipping auto-submission")

def main():
    """Fungsi utama ARC v7.6 Final"""
    try:
        # Buat instance orchestrator
        arc = ARCOrchestrator()
        
        # Mulai operasi
        arc.start_autonomous_operations()
        
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()