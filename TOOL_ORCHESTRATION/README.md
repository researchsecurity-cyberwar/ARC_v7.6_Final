# ARC Auto Tool Orchestrator v7.6 Final

Sistem orkestrasi tool otomatis yang cerdas, adaptif, dan self-healing untuk ARC.

## Fitur Utama

1. **Auto-Detection & Auto-Install**: Deteksi tool yang dibutuhkan, auto-download dari GitHub
2. **Multi-Platform Support**: Go, Python, GitHub repos
3. **Self-Healing Installation**: Retry dengan strategi pemulihan
4. **Sandbox Testing**: Test tool di environment terisolasi
5. **Dependency Resolution**: Auto-resolve untuk Python/Go/Node/Rust
6. **Kali Linux Optimized**: Error handling robust untuk Kali

## Quick Start

```python
from TOOL_ORCHESTRATION.INTELLIGENT_TOOL_MANAGER import AutoToolOrchestrator

orchestrator = AutoToolOrchestrator()
result = orchestrator.ensure_tool_available('nuclei', 'web_scan')
```

## Tool Registry

- **subdomain_enum**: amass, subfinder, assetfinder
- **port_scan**: naabu, masscan, nmap
- **web_scan**: nuclei, dalfox, ffuf
- **wayback**: gau, waybackurls
- **http_probe**: httpx
- **sql_injection**: sqlmap
- **smart_contract**: slither

## Integration

Auto-terintegrasi dengan arc_main.py untuk auto-tool management.

## Status

✅ Production Ready for Kali Linux
✅ Auto-download system functional
✅ Self-healing installation active
✅ Integration complete
