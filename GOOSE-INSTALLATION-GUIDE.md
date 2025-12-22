# Goose Installation Guide

## 🎯 Overview

This guide helps you install **Goose AI** on your local machine. Goose is an AI-powered coding assistant that can execute commands, modify files, and automate development tasks.

**Official Documentation:** https://block.github.io/goose/

---

## 📋 Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **OS** | macOS, Linux, Windows (WSL2) | macOS or Linux |
| **Python** | 3.10+ | 3.11+ |
| **Memory** | 4GB RAM | 8GB+ RAM |
| **Disk Space** | 500MB | 1GB |

### Required Tools

```bash
# Check Python version
python3 --version  # Should be 3.10 or higher

# Check pip
pip3 --version

# Check pipx (recommended installer)
pipx --version
```

---

## 🚀 Installation Methods

### Method 1: Using pipx (Recommended)

**Why pipx?**
- ✅ Installs Goose in isolated environment
- ✅ Avoids dependency conflicts
- ✅ Easy to upgrade and uninstall
- ✅ Available globally

#### Step 1: Install pipx

**macOS:**
```bash
brew install pipx
pipx ensurepath
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```

**Linux (Fedora):**
```bash
sudo dnf install pipx
pipx ensurepath
```

**After installation, restart your terminal or run:**
```bash
source ~/.bashrc  # or ~/.zshrc for zsh
```

#### Step 2: Install Goose

```bash
# Install Goose
pipx install goose-ai

# Verify installation
goose --version

# Expected output:
# goose, version X.X.X
```

#### Step 3: Verify Goose is in PATH

```bash
which goose
# Should show: /Users/[username]/.local/bin/goose (macOS/Linux)
```

---

### Method 2: Using pip (Alternative)

**⚠️ Warning:** This installs Goose globally and may cause dependency conflicts.

```bash
# Install Goose
pip3 install goose-ai

# Verify installation
goose --version
```

**If `goose` command not found:**
```bash
# Add Python bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add to shell config for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc
```

---

### Method 3: Using uv (Fastest)

**uv** is a fast Python package installer.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Goose with uv
uv tool install goose-ai

# Verify installation
goose --version
```

---

## ⚙️ Configuration

### Step 1: Initial Configuration

```bash
# Run configuration wizard
goose configure
```

**The wizard will ask:**

1. **LLM Provider:** Choose your AI provider
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude)
   - OpenRouter (Multiple models)
   - Ollama (Local models)

2. **API Key:** Enter your API key for the chosen provider

3. **Model:** Select the model to use
   - GPT-4: Most capable, expensive
   - GPT-3.5: Fast, cheaper
   - Claude-3: Good balance
   - Local models: Free, requires Ollama

### Step 2: Manual Configuration (Alternative)

Create config file manually:

```bash
# Create config directory
mkdir -p ~/.config/goose

# Create config file
cat > ~/.config/goose/config.yaml << 'EOF'
# Goose Configuration

# LLM Provider (openai, anthropic, openrouter, ollama)
provider: openai

# API Key (get from provider)
api_key: your_api_key_here

# Model to use
model: gpt-4

# Optional: Temperature (0.0 - 1.0)
temperature: 0.7

# Optional: Max tokens
max_tokens: 4000

# Optional: Timeout (seconds)
timeout: 60
EOF
```

### Step 3: Get API Keys

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy and save it

**Anthropic:**
1. Go to https://console.anthropic.com/settings/keys
2. Create new API key
3. Copy and save it

**OpenRouter:**
1. Go to https://openrouter.ai/keys
2. Create new API key
3. Copy and save it

**Ollama (Local):**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull mistral

# Configure Goose to use Ollama
goose configure
# Select: ollama
# Model: mistral
```

---

## ✅ Verification

### Test 1: Check Installation

```bash
# Check version
goose --version

# Check help
goose --help

# Check config
cat ~/.config/goose/config.yaml
```

### Test 2: Run Simple Command

```bash
# Start Goose
goose

# Try a simple task
> "List files in current directory"

# Expected: Goose will run `ls` and show results
```

### Test 3: Test File Operations

```bash
# Start Goose
goose

# Create a test file
> "Create a file called test.txt with 'Hello from Goose'"

# Verify
> "Show me the contents of test.txt"

# Clean up
> "Delete test.txt"
```

---

## 🔧 Troubleshooting

### Issue 1: Command Not Found

**Problem:**
```bash
goose: command not found
```

**Solution:**
```bash
# Check if Goose is installed
pipx list | grep goose

# If installed, add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make permanent
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue 2: API Key Error

**Problem:**
```
Error: Invalid API key
```

**Solution:**
```bash
# Check config file
cat ~/.config/goose/config.yaml

# Reconfigure
goose configure

# Or manually edit
nano ~/.config/goose/config.yaml
```

### Issue 3: Python Version Error

**Problem:**
```
Error: Python 3.10+ required
```

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.11 (macOS)
brew install python@3.11

# Install Python 3.11 (Linux)
sudo apt install python3.11

# Use specific Python version
python3.11 -m pip install pipx
python3.11 -m pipx install goose-ai
```

### Issue 4: Permission Denied

**Problem:**
```
Error: Permission denied
```

**Solution:**
```bash
# Don't use sudo with pipx
# Instead, ensure user has write access
chmod +x ~/.local/bin

# Or reinstall without sudo
pipx uninstall goose-ai
pipx install goose-ai
```

### Issue 5: Dependency Conflicts

**Problem:**
```
Error: Conflicting dependencies
```

**Solution:**
```bash
# Uninstall and reinstall with pipx (isolated environment)
pip3 uninstall goose-ai
pipx install goose-ai

# Or use virtual environment
python3 -m venv goose-env
source goose-env/bin/activate
pip install goose-ai
```

---

## 🔄 Upgrading Goose

### Using pipx:
```bash
# Upgrade to latest version
pipx upgrade goose-ai

# Check new version
goose --version
```

### Using pip:
```bash
# Upgrade to latest version
pip3 install --upgrade goose-ai

# Check new version
goose --version
```

---

## 🗑️ Uninstalling Goose

### Using pipx:
```bash
# Uninstall Goose
pipx uninstall goose-ai

# Verify removal
goose --version  # Should show "command not found"
```

### Using pip:
```bash
# Uninstall Goose
pip3 uninstall goose-ai

# Verify removal
goose --version  # Should show "command not found"
```

### Remove Configuration:
```bash
# Remove config directory
rm -rf ~/.config/goose

# Remove cache (if exists)
rm -rf ~/.cache/goose
```

---

## 📚 Next Steps

After installing Goose, you can:

1. **Use Goose for Local Setup:**
   ```bash
   cd multi_Agent_Conversation_System
   goose
   > "Read GOOSE-LOCAL-SETUP.md and execute all steps"
   ```

2. **Use Goose for Azure Deployment:**
   ```bash
   cd multi_Agent_Conversation_System
   goose
   > "Read GOOSE-AZURE-DEPLOY.md and deploy to Azure"
   ```

3. **Explore Goose Capabilities:**
   - See `GOOSE-QUICK-START.md` for quick commands
   - See `GOOSE_INVESTIGATION.md` for advanced usage

---

## 🎓 Quick Reference

### Installation:
```bash
# Recommended
pipx install goose-ai

# Alternative
pip3 install goose-ai
```

### Configuration:
```bash
# Interactive
goose configure

# Manual
nano ~/.config/goose/config.yaml
```

### Usage:
```bash
# Start Goose
goose

# Exit Goose
> "exit" or Ctrl+D
```

### Upgrade:
```bash
pipx upgrade goose-ai
```

### Uninstall:
```bash
pipx uninstall goose-ai
```

---

## 🆘 Getting Help

### Official Resources:
- **Documentation:** https://block.github.io/goose/
- **GitHub:** https://github.com/block/goose
- **Discord:** https://discord.gg/goose-ai

### Common Commands:
```bash
# Help
goose --help

# Version
goose --version

# Configuration
goose configure

# Debug mode
goose --debug
```

---

## ✅ Installation Checklist

- [ ] Python 3.10+ installed
- [ ] pipx installed
- [ ] Goose installed (`pipx install goose-ai`)
- [ ] Goose in PATH (`which goose`)
- [ ] Configuration created (`goose configure`)
- [ ] API key set
- [ ] Test command successful
- [ ] Ready to use with project guides

---

**🎉 You're ready to use Goose!**

**Next:** See `GOOSE-QUICK-START.md` for how to use Goose with this project.
