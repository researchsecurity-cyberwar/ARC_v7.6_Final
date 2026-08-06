# ARC v7.6 Final - Kali Linux Deployment Guide

## 🎯 Overview
This guide will walk you through deploying ARC v7.6 Final on Kali Linux for autonomous bug bounty hunting operations.

## ✅ Prerequisites

### System Requirements
- **OS**: Kali Linux 2024.x (recommended) or Ubuntu 20.04+
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 10GB free space
- **Python**: 3.9 or higher

### Required Tools
The following tools will be installed automatically or manually:

## 📦 Installation Steps

### 1. Install Python Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Create virtual environment (recommended)
python3 -m venv arc_env
source arc_env/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Install External CLI Tools

```bash
# Install Go tools
sudo apt install golang-go -y

# Install reconnaissance tools
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/lc/gau@latest
go install github.com/projectdiscovery/dalfox/v2/cmd/dalfox@latest
go install github.com/ffuf/ffuf/v2@latest

# Install nuclei
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Install other tools via apt
sudo apt install nuclei sqlmap amass -y

# Install Playwright browsers
playwright install chromium
```

### 3. Configure ARC

```bash
# Create config directory
mkdir -p ~/.arc

# Create config.yaml
nano ~/.arc/config.yaml
```

**Example config.yaml:**
```yaml
# Telegram Bot Configuration
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"

# Bug Bounty Platforms
bug_bounty:
  hackerone_main:
    api_token: "YOUR_H1_API_TOKEN"
  
  intigriti_personal:
    personal_access_token: "YOUR_INTIGRITI_TOKEN"
  
  bugcrowd_main:
    session_cookie: "YOUR_BUGCROWD_SESSION"
  
  yeswehack_main:
    session_cookie: "YOUR_YWH_SESSION"
  
  immunefi_main:
    session_cookie: "YOUR_IMMUNEFI_SESSION"

# Optional: AI Reasoning
llama_cpp:
  model_path: "/path/to/llama/model.bin"
  n_ctx: 2048
  n_threads: 4
```

### 4. Verify Installation

```bash
# Test imports
python import_test.py

# Expected output:
# Arc Main Imports: 40 passed, 0 failed
# Full Project Import Test: 296 passed, 0 failed
```

### 5. Run ARC

```bash
# Activate virtual environment (if using)
source arc_env/bin/activate

# Start ARC
python arc_main.py
```

## 🔧 Configuration Details

### Telegram Bot Setup

1. Create a bot via @BotFather on Telegram:
   ```
   /newbot
   ```
   Save the `bot_token` provided.

2. Get your `chat_id`:
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Copy the `chat.id` from the response

### Platform Credentials

#### HackerOne
1. Go to https://hackerone.com/settings/api_token
2. Generate a new API token
3. Add to config.yaml under `bug_bounty.hackerone_main.api_token`

#### Intigriti
1. Go to https://www.intigriti.com/settings/apitokens
2. Create a personal access token
3. Add to config.yaml under `bug_bounty.intigriti_personal.personal_access_token`

#### Bugcrowd
1. Login to https://bugcrowd.com
2. Open DevTools → Application → Cookies
3. Copy `_bugcrowd_session` cookie value
4. Add to config.yaml under `bug_bounty.bugcrowd_main.session_cookie`

#### YesWeHack
1. Login to https://yeswehack.com
2. Open DevTools → Application → Cookies
3. Copy session cookie
4. Add to config.yaml under `bug_bounty.yeswehack_main.session_cookie`

#### Immunefi
1. Login to https://immunefi.com
2. Open DevTools → Application → Cookies
3. Copy `sessionid` cookie
4. Add to config.yaml under `bug_bounty.immunefi_main.session_cookie`

## 🚀 Running ARC

### Basic Usage
```bash
python arc_main.py
```

### With Virtual Environment
```bash
source arc_env/bin/activate
python arc_main.py
```

### With AI Reasoning (Optional)
```bash
# Requires llama-cpp-python installation
pip install llama-cpp-python

# Download a model (example: Llama 2 7B)
wget https://huggingface.co/TheBloke/Llama-2-7B-chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_0.bin

# Update config.yaml with model_path
```

## 📊 Monitoring

### Telegram Notifications
ARC will send you notifications via Telegram for:
- ✅ Initialization status
- ⚠️ Session expirations
- 🔍 New findings
- ✅ Auto-submissions
- ❌ Errors

### Logs
Logs are stored in:
- `~/.arc/logs/` (if configured)
- Console output (real-time)

## ⚠️ Important Notes

### Legal & Ethical
1. **Only test authorized targets**
2. Respect program scope
3. Follow responsible disclosure
4. ARC includes ethical guardrails - do not disable them

### Kali Linux Specific
- ARC is designed for Kali Linux but works on other distros
- Some CLI tools may need manual installation on non-Kali systems
- Tor integration works best on Kali Linux

### Troubleshooting

#### Import Errors
```bash
# If imports fail, ensure you're in the ARC directory
cd /path/to/ARC_v7.6_Final
python import_test.py
```

#### Permission Issues
```bash
# Make scripts executable
chmod +x arc_main.py
chmod +x import_test.py
chmod +x deep_analysis.py
```

#### Missing Dependencies
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

## 🎯 Target Selection

You determine the target by configuring:
1. Platform credentials in `~/.arc/config.yaml`
2. Program scopes via platform interfaces
3. ARC scans programs you have access to

ARC will:
1. Monitor your authorized programs
2. Look for new targets
3. Apply vulnerability detectors
4. Generate reports
5. Submit via platform submitters

## 📈 Performance Tips

1. **Use Virtual Environment**: Isolates dependencies
2. **Increase RAM**: 8GB+ recommended for AI features
3. **Fast Network**: Essential for reconnaissance tools
4. **Tor**: Use for anonymity (configure in `~/.arc/config.yaml`)

## 🔄 Updates

To update ARC:
```bash
git pull origin main
pip install --upgrade -r requirements.txt
```

## 📞 Support

For issues:
1. Check logs
2. Run `python deep_analysis.py` for diagnostics
3. Review `~/.arc/config.yaml` configuration
4. Ensure all CLI tools are installed

---

**Status**: ✅ Production Ready
**Version**: v7.6 Final
**Tested On**: Kali Linux 2024.x
**Modules**: 296/296 passing
**Imports**: 40/40 passing