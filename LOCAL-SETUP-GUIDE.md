# Local Setup Guide - Multi-Agent Timesheet System

## 🎯 **Overview**

This guide helps you set up the **Unified Multi-Agent Conversation System** on a new computer for local development and testing.

**System Components:**
- 🤖 **4 AI Agents:** Planner, Timesheet, Branding, Quality
- ⏰ **Temporal Workflows:** Daily reminders, conversation orchestration
- 📧 **Multi-Channel:** SMS, WhatsApp, Email support
- 🔧 **51 Harvest Tools:** Complete timesheet management
- 📊 **Opik Tracking:** LLM observability

---

## 📋 **Prerequisites**

### **1. System Requirements**
- **OS:** macOS, Linux, or Windows (WSL2)
- **Python:** 3.11 or later
- **Docker:** Latest version (for Temporal server)
- **Git:** For cloning the repository
- **Memory:** At least 4GB RAM
- **Disk Space:** At least 2GB free

### **2. Required Accounts & API Keys**

You'll need accounts and API keys for:

| Service | Purpose | Sign Up Link |
|---------|---------|--------------|
| **OpenRouter** | LLM API | https://openrouter.ai |
| **Harvest** | Timesheet API | https://id.getharvest.com |
| **Twilio** | SMS/WhatsApp | https://www.twilio.com |
| **Supabase** | Database | https://supabase.com |
| **Gmail** | Email sending & polling | https://gmail.com |
| **Opik/Comet** | LLM tracking | https://www.comet.com/opik |

---

## 🚀 **Step-by-Step Setup**

### **Step 1: Install Python 3.11+**

#### **macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3.11 --version
```

#### **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
python3.11 --version
```

#### **Windows (WSL2):**
```bash
# Install WSL2 first, then follow Linux instructions
wsl --install
```

---

### **Step 2: Install Docker**

#### **macOS:**
```bash
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
# Or use Homebrew
brew install --cask docker
```

#### **Linux:**
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### **Windows:**
```bash
# Download Docker Desktop for Windows
# https://www.docker.com/products/docker-desktop
```

---

### **Step 3: Clone the Repository**

```bash
# Clone the repository (replace with your actual repository URL)
git clone <YOUR-REPOSITORY-URL>
cd multi_Agent_Conversation_System

# Example:
# git clone https://github.com/your-org/multi_Agent_Conversation_System.git

# Or if you already have it, pull latest changes
git pull origin main
```

---

### **Step 4: Set Up Python Virtual Environment**

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate

# Windows (WSL2):
source .venv/bin/activate

# Verify activation (should show .venv in path)
which python
```

---

### **Step 5: Install Python Dependencies**

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|temporalio|openai|twilio"
```

**Expected packages:**
- `fastapi==0.104.1`
- `temporalio==1.5.0`
- `openai>=1.6.1`
- `twilio==8.10.0`
- `supabase==2.0.3`
- `opik==0.1.0`

---

### **Step 6: Set Up Temporal Server (Local)**

#### **Option 1: Using Docker (Recommended)**

```bash
# Start Temporal server in Docker
docker run -d \
  --name temporal-dev \
  -p 7233:7233 \
  -p 8233:8233 \
  temporalio/auto-setup:latest

# Verify it's running
docker ps | grep temporal

# Check logs
docker logs temporal-dev
```

#### **Option 2: Using Temporal CLI**

```bash
# Install Temporal CLI
brew install temporal

# Start development server
temporal server start-dev
```

**Temporal UI:** http://localhost:8233

---

### **Step 7: Configure Environment Variables**

Create a `.env` file in the project root:

```bash
# Copy the example file (provided in repository)
cp .env.example .env

# Edit with your credentials
nano .env
# Or use your preferred editor: code .env, vim .env, etc.
```

**Required `.env` configuration:**

```bash
# ===== LLM Configuration =====
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=gpt-oss-20b
USE_OPENROUTER=true

# Alternative: Direct OpenAI
# OPENAI_API_KEY=sk-your-key-here
# USE_OPENROUTER=false

# ===== Temporal Configuration =====
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TLS_ENABLED=false

# ===== Supabase Configuration =====
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Example:
# SUPABASE_URL=https://czcrfhfioxypxavwwdji.supabase.co

# ===== Harvest API (per user) =====
HARVEST_ACCESS_TOKEN=your-harvest-token
HARVEST_ACCOUNT_ID=your-account-id

# Additional users (if needed)
# HARVEST_ACCESS_TOKEN_USER2=your-harvest-token-user2
# HARVEST_ACCOUNT_ID_USER2=your-account-id-user2

# ===== Twilio (SMS/WhatsApp) =====
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# ===== Gmail (Email Sending & Polling) =====
GMAIL_USER=your@gmail.com
GMAIL_PASSWORD=your-app-password

# ===== User Configuration =====
USER_PHONE_NUMBER=+61412345678
USER_NAME=John Doe

# Additional users (if needed)
# USER_PHONE_NUMBER_USER2=+61412345679
# USER2_NAME=Jane Doe

# ===== Observability =====
OPIK_ENABLED=true
OPIK_PROJECT_NAME=local-development
OPIK_API_KEY=your-opik-key

# ===== Server Configuration =====
PORT=8003
LOG_LEVEL=INFO
```

---

### **Step 8: Set Up Supabase Database**

#### **1. Create Supabase Project**
- Go to https://supabase.com
- Create a new project
- Note your project URL and anon key

#### **2. Run Database Migrations**

```bash
# Install Supabase CLI
brew install supabase/tap/supabase

# Login to Supabase
supabase login

# Link to your project (replace with your project ID)
supabase link --project-ref <your-project-id>

# Example:
# supabase link --project-ref czcrfhfioxypxavwwdji

# Run migrations (if any)
supabase db push
```

#### **3. Create Required Tables**

Execute this SQL in Supabase SQL Editor:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  full_name TEXT,
  phone_number TEXT,
  harvest_account_id TEXT,
  harvest_access_token TEXT,
  harvest_user_id INTEGER,
  timezone TEXT DEFAULT 'Australia/Sydney',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  platform TEXT NOT NULL,  -- 'sms', 'email', 'whatsapp'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversation context table (message history)
CREATE TABLE IF NOT EXISTS conversation_context (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL,
  user_id UUID NOT NULL,
  content TEXT NOT NULL,
  message_type TEXT NOT NULL,  -- 'INBOUND', 'OUTBOUND'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_conversation_id ON conversation_context(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_user_id ON conversation_context(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_created_at ON conversation_context(created_at);
```

---

### **Step 9: Test the Setup**

#### **1. Run Tests**

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/unit/test_planner.py -v
pytest tests/integration/test_agent_coordination.py -v

# Run with coverage
pytest tests/ --cov --cov-report=html
```

#### **2. Start the Server**

```bash
# Activate virtual environment (if not already)
source .venv/bin/activate

# Start the server
python -m uvicorn unified_server:app --host 0.0.0.0 --port 8003 --reload
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     🚀 Unified Temporal Worker initialized
INFO:     ✅ Temporal client connected
INFO:     ✅ All agents initialized
INFO:     📧 Gmail polling started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8003
```

#### **3. Test Endpoints**

Open a new terminal and test:

```bash
# Health check
curl http://localhost:8003/health | jq

# System info
curl http://localhost:8003/ | jq

# Temporal status
curl http://localhost:8003/temporal/status | jq

# Test conversation
curl -X POST http://localhost:8003/test/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "How many hours did I log this week?",
    "channel": "SMS"
  }' | jq
```

---

## 🔧 **Development Workflow**

### **Daily Development**

```bash
# 1. Start Temporal server (if using Docker)
docker start temporal-dev

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Start the development server
python -m uvicorn unified_server:app --host 0.0.0.0 --port 8003 --reload

# 4. In another terminal, watch logs
tail -f logs/app.log

# 5. Run tests when making changes
pytest tests/ -v
```

### **Code Changes**

```bash
# Make your changes
nano agents/planner.py

# Run tests
pytest tests/unit/test_planner.py -v

# Check code style
black agents/
flake8 agents/

# Commit changes
git add .
git commit -m "Update planner agent"
git push origin main
```

---

## 🧪 **Testing**

### **Run All Tests**

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### **Run Specific Tests**

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_planner.py -v

# Specific test function
pytest tests/unit/test_planner.py::test_analyze_request -v
```

### **Test with Real APIs**

```bash
# Test Harvest API connection
python test_harvest_token.py

# Test Twilio SMS
python -c "
from twilio.rest import Client
client = Client('your_sid', 'your_token')
message = client.messages.create(
    body='Test from local setup',
    from_='+1234567890',
    to='+61412345678'
)
print(f'Message SID: {message.sid}')
"
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **1. Python Version Mismatch**

```bash
# Check Python version
python --version

# If wrong version, use python3.11 explicitly
python3.11 -m venv .venv
source .venv/bin/activate
python --version  # Should show 3.11.x
```

#### **2. Temporal Connection Failed**

```bash
# Check if Temporal is running
docker ps | grep temporal

# If not running, start it
docker start temporal-dev

# Check logs
docker logs temporal-dev

# Test connection
curl http://localhost:8233
```

#### **3. Module Import Errors**

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check if virtual environment is activated
which python  # Should show .venv path
```

#### **4. Port Already in Use**

```bash
# Find process using port 8003
lsof -i :8003

# Kill the process
kill -9 <PID>

# Or use a different port
python -m uvicorn unified_server:app --port 8004
```

#### **5. LLM 402 Payment Required**

```bash
# Check OpenRouter credits
# Go to https://openrouter.ai/settings/credits

# Or switch to a free model
# Edit .env:
OPENROUTER_MODEL=google/gemma-2-9b-it:free
```

#### **6. Database Connection Failed**

```bash
# Check Supabase URL and key in .env
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python -c "
from supabase import create_client
client = create_client('your_url', 'your_key')
print('Connected!')
"
```

---

## 📚 **Project Structure**

```
multi_Agent_Conversation_System/
├── agents/                    # AI Agents
│   ├── planner.py            # Planner agent
│   ├── timesheet.py          # Timesheet agent
│   ├── branding.py           # Branding agent
│   ├── quality.py            # Quality agent
│   ├── base.py               # Base agent class
│   └── models.py             # Pydantic models
├── llm/                       # LLM Integration
│   ├── client.py             # LLM client
│   ├── config.py             # Configuration
│   ├── cache.py              # Response caching
│   ├── rate_limiter.py       # Rate limiting
│   ├── error_handler.py      # Error handling
│   └── opik_tracker.py       # Opik tracking
├── tests/                     # Tests
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test fixtures
├── unified_server.py          # Main FastAPI server
├── unified_workflows.py       # Temporal workflows
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── .env.example              # Environment template
└── README.md                  # Project documentation
```

---

## 🎯 **Next Steps**

After successful local setup:

1. **Explore the Code**
   - Read through `agents/planner.py`
   - Understand the workflow in `unified_workflows.py`
   - Check the API endpoints in `unified_server.py`

2. **Make Your First Change**
   - Modify an agent's prompt
   - Add a new endpoint
   - Create a new test

3. **Test Thoroughly**
   - Run all tests
   - Test with real APIs
   - Check code coverage

4. **Deploy to Azure**
   - Follow `AZURE-DEPLOYMENT-GUIDE.md`
   - Build Docker image
   - Deploy to Azure Container Apps

---

## 📞 **Support**

If you encounter issues:

1. **Check Logs:**
   ```bash
   tail -f logs/app.log
   ```

2. **Run Diagnostics:**
   ```bash
   python -c "import sys; print(sys.version)"
   docker --version
   pip list
   ```

3. **Test Individual Components:**
   ```bash
   pytest tests/unit/test_planner.py -v -s
   ```

4. **Check Environment:**
   ```bash
   env | grep -E "OPENROUTER|TEMPORAL|SUPABASE"
   ```

---

## ✅ **Success Checklist**

- [ ] Python 3.11+ installed
- [ ] Docker installed and running
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Temporal server running
- [ ] `.env` file configured
- [ ] Supabase database set up
- [ ] Tests passing
- [ ] Server starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] Test conversation works

---

**🎉 Your local development environment is ready!**

**Start the server:**
```bash
source .venv/bin/activate
python -m uvicorn unified_server:app --host 0.0.0.0 --port 8003 --reload
```

**Access the system:**
- **API:** http://localhost:8003
- **Health:** http://localhost:8003/health
- **Temporal UI:** http://localhost:8233

🚀 **Happy coding!**
