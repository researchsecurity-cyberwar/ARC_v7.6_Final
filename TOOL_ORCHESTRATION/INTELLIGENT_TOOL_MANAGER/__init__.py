"""
ARC Intelligent Tool Manager Package
Sistem manajemen tool otomatis yang cerdas dan adaptif.

Fitur:
- Auto-download tools dari GitHub
- Dependency resolution otomatis
- Self-healing installation
- Sandbox testing
- CLI tool adaptation
- Template validation
- Human approval workflow

Komponen:
- GitHubToolInstaller: Download dan build tools dari GitHub
- DependencyResolver: Resolve dependencies (Python/Go/Node/Rust)
- SelfHealingInstaller: Retry dengan strategi pemulihan
- CLIToolAdapter: Adaptasi tool CLI untuk ARC
- AutoToolOrchestrator: Orkestrator utama (MAIN BRAIN)
- SandboxIntegrator: Test tools di environment terisolasi
- TemplateValidator: Validasi keamanan template
- HumanApprovalNotifier: Notifikasi persetujuan manusia
"""

from .github_tool_installer import GitHubToolInstaller
from .dependency_resolver import DependencyResolver
from .self_healing_installer import SelfHealingInstaller
from .cli_tool_adapter import CLIToolAdapter
from .auto_tool_orchestrator import AutoToolOrchestrator, ensure_security_tools

# Import dari auto_integration_engine
from .auto_integration_engine.sandbox_integrator import SandboxIntegrator
from .auto_integration_engine.template_validator import TemplateValidator
from .auto_integration_engine.human_approval_notifier import HumanApprovalNotifier
from .auto_integration_engine.tool_discovery_watcher import ToolDiscoveryWatcher

__version__ = '7.6.0'
__all__ = [
    'GitHubToolInstaller',
    'DependencyResolver',
    'SelfHealingInstaller',
    'CLIToolAdapter',
    'AutoToolOrchestrator',
    'ensure_security_tools',
    'SandboxIntegrator',
    'TemplateValidator',
    'HumanApprovalNotifier',
    'ToolDiscoveryWatcher'
]
