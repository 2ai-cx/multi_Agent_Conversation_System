# Goose-Assisted Local Setup Guide

## 🤖 **For Goose AI Agent**

This guide is optimized for Goose AI to automatically set up the Multi-Agent Timesheet System on a new computer.

---

## 📋 **Prerequisites Check**

**Goose, please verify these are installed:**

```bash
# Check Python version (need 3.11+)
python3.11 --version || python3 --version

# Check Docker
docker --version

# Check Git
git --version

# Check if project exists
ls -la multi_Agent_Conversation_System 2>/dev/null || echo "Project not found"
```

---

## 🚀 **Step 1: System Dependencies**

### **Task: Install Python 3.11 (if needed)**

**Goose, run this based on OS:**

```bash
# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  brew install python@3.11
fi

# Linux (Ubuntu/Debian)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  sudo apt update
  sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi

# Verify
python3.11 --version
```

### **Task: Install Docker (if needed)**

**Goose, check if Docker is running:**

```bash
docker ps 2>/dev/null || echo "Docker not running or not installed"
```

**If Docker not installed:**
- macOS: `brew install --cask docker`
- Linux: `curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh`

---

## 📦 **Step 2: Clone or Update Repository**

**Goose, execute:**

```bash
# If project doesn't exist, clone it
if [ ! -d "multi_Agent_Conversation_System" ]; then
  git clone https://github.com/your-org/multi_Agent_Conversation_System.git
  cd multi_Agent_Conversation_System
else
  cd multi_Agent_Conversation_System
  git pull origin main
fi

# Show current directory
pwd
ls -la
```

---

## 🐍 **Step 3: Python Virtual Environment**

**Goose, create and activate virtual environment:**

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate it
source .venv/bin/activate

# Verify activation
which python
python --version

# Upgrade pip
pip install --upgrade pip
```

---

## 📚 **Step 4: Install Dependencies**

**Goose, install all Python packages:**

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify key packages
pip list | grep -E "fastapi|temporalio|openai|twilio|supabase|opik"

# Show installation summary
echo "✅ Dependencies installed successfully"
pip list | wc -l
```

---

## 🐳 **Step 5: Start Temporal Server**

**Goose, start Temporal in Docker:**

```bash
# Check if temporal-dev already exists
if docker ps -a | grep -q temporal-dev; then
  echo "Temporal container exists, starting it..."
  docker start temporal-dev
else
  echo "Creating new Temporal container..."
  docker run -d \
    --name temporal-dev \
    -p 7233:7233 \
    -p 8233:8233 \
    temporalio/auto-setup:latest
fi

# Wait for it to be ready
sleep 10

# Verify it's running
docker ps | grep temporal-dev

# Check logs
docker logs temporal-dev --tail 20

echo "✅ Temporal server running on:"
echo "   - gRPC: localhost:7233"
echo "   - UI: http://localhost:8233"
```

---

## ⚙️ **Step 6: Create Environment Configuration**

**Goose, create .env file with placeholders:**

```bash
cat > .env << 'EOF'
# ===== LLM Configuration =====
OPENROUTER_API_KEY=REPLACE_WITH_YOUR_KEY
OPENROUTER_MODEL=gpt-oss-20b
USE_OPENROUTER=true

# ===== Temporal Configuration =====
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TLS_ENABLED=false

# ===== Supabase Configuration =====
SUPABASE_URL=https://czcrfhfioxypxavwwdji.supabase.co
SUPABASE_KEY=REPLACE_WITH_YOUR_KEY

# ===== Harvest API =====
HARVEST_ACCESS_TOKEN_USER1=REPLACE_WITH_YOUR_TOKEN
HARVEST_ACCOUNT_ID_USER1=REPLACE_WITH_YOUR_ACCOUNT_ID

# ===== Twilio (SMS/WhatsApp) =====
TWILIO_ACCOUNT_SID=REPLACE_WITH_YOUR_SID
TWILIO_AUTH_TOKEN=REPLACE_WITH_YOUR_TOKEN
TWILIO_PHONE_NUMBER=REPLACE_WITH_YOUR_NUMBER

# ===== SendGrid (Email) =====
SENDGRID_API_KEY=REPLACE_WITH_YOUR_KEY
SENDGRID_FROM_EMAIL=REPLACE_WITH_YOUR_EMAIL

# ===== Gmail (Email Polling) =====
GMAIL_USER=REPLACE_WITH_YOUR_EMAIL
GMAIL_PASSWORD=REPLACE_WITH_YOUR_APP_PASSWORD

# ===== User Configuration =====
USER1_PHONE=REPLACE_WITH_PHONE
USER1_NAME=Test User

# ===== Observability =====
OPIK_ENABLED=true
OPIK_PROJECT_NAME=local-development
OPIK_API_KEY=REPLACE_WITH_YOUR_KEY

# ===== Server Configuration =====
PORT=8003
LOG_LEVEL=INFO
EOF

echo "✅ .env file created"
echo "⚠️  IMPORTANT: User must update .env with real API keys"
cat .env
```

---

## 🗄️ **Step 7: Set Up Supabase Database**

**Goose, create SQL setup script:**

```bash
cat > setup_database.sql << 'EOF'
-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id TEXT NOT NULL,
  message TEXT NOT NULL,
  response TEXT,
  channel TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

-- User context table
CREATE TABLE IF NOT EXISTS user_context (
  user_id TEXT PRIMARY KEY,
  name TEXT,
  phone TEXT,
  email TEXT,
  harvest_token TEXT,
  harvest_account_id TEXT,
  preferences JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

-- Insert test user
INSERT INTO user_context (user_id, name, phone, email)
VALUES ('test-user', 'Test User', '+61412345678', 'test@example.com')
ON CONFLICT (user_id) DO NOTHING;
EOF

echo "✅ Database setup script created: setup_database.sql"
echo "📝 User must run this in Supabase SQL Editor"
cat setup_database.sql
```

---

## 🧪 **Step 8: Run Tests**

**Goose, verify installation with tests:**

```bash
# Activate virtual environment (if not already)
source .venv/bin/activate

# Run unit tests only (don't need real API keys)
pytest tests/unit/ -v --tb=short

# Show test summary
echo "✅ Unit tests completed"
```

---

## 🚀 **Step 9: Start the Server**

**Goose, create a startup script:**

```bash
cat > start_server.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting Multi-Agent Timesheet System..."

# Activate virtual environment
source .venv/bin/activate

# Check if Temporal is running
if ! docker ps | grep -q temporal-dev; then
  echo "⚠️  Starting Temporal server..."
  docker start temporal-dev
  sleep 5
fi

# Start the server
echo "🌐 Starting FastAPI server on http://localhost:8003"
python -m uvicorn unified_server:app --host 0.0.0.0 --port 8003 --reload
EOF

chmod +x start_server.sh

echo "✅ Startup script created: start_server.sh"
echo "📝 User can run: ./start_server.sh"
```

---

## ✅ **Step 10: Verification**

**Goose, create a verification script:**

```bash
cat > verify_setup.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying setup..."

# Check Python
echo "1. Python version:"
python --version

# Check dependencies
echo "2. Key packages installed:"
pip list | grep -E "fastapi|temporalio|openai" | head -3

# Check Docker
echo "3. Temporal server:"
docker ps | grep temporal-dev || echo "❌ Temporal not running"

# Check .env file
echo "4. Environment file:"
if [ -f .env ]; then
  echo "✅ .env exists"
  grep -c "REPLACE_WITH" .env && echo "⚠️  Found placeholder values - need to update"
else
  echo "❌ .env not found"
fi

# Check database script
echo "5. Database setup:"
[ -f setup_database.sql ] && echo "✅ SQL script ready" || echo "❌ SQL script missing"

echo ""
echo "📋 Setup Status:"
echo "  ✅ Python environment"
echo "  ✅ Dependencies installed"
echo "  ✅ Temporal server"
echo "  ⚠️  API keys need configuration"
echo "  ⚠️  Database needs setup in Supabase"
EOF

chmod +x verify_setup.sh
./verify_setup.sh
```

---

## 📝 **Step 11: Create User Instructions**

**Goose, generate final instructions for user:**

```bash
cat > SETUP_COMPLETE.md << 'EOF'
# ✅ Local Setup Complete!

## What's Been Done:

1. ✅ Python 3.11 virtual environment created
2. ✅ All dependencies installed
3. ✅ Temporal server running in Docker
4. ✅ .env configuration file created
5. ✅ Database setup script created
6. ✅ Startup scripts created

## What You Need to Do:

### 1. Update API Keys in .env

Edit the `.env` file and replace all `REPLACE_WITH_YOUR_*` values:

```bash
nano .env
```

**Required keys:**
- OpenRouter API key (https://openrouter.ai)
- Supabase key (https://supabase.com)
- Harvest token (https://id.getharvest.com)
- Twilio credentials (https://www.twilio.com)
- SendGrid key (https://sendgrid.com)
- Gmail app password (https://myaccount.google.com/apppasswords)

### 2. Set Up Supabase Database

1. Go to https://supabase.com
2. Open your project SQL Editor
3. Copy and paste content from `setup_database.sql`
4. Run the SQL script

### 3. Start the Server

```bash
./start_server.sh
```

### 4. Test the System

Open a new terminal:

```bash
# Health check
curl http://localhost:8003/health | jq

# System info
curl http://localhost:8003/ | jq

# Test conversation
curl -X POST http://localhost:8003/test/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "How many hours did I log this week?",
    "channel": "SMS"
  }' | jq
```

## Useful Commands:

```bash
# Start server
./start_server.sh

# Verify setup
./verify_setup.sh

# Run tests
source .venv/bin/activate
pytest tests/ -v

# View Temporal UI
open http://localhost:8233

# Stop Temporal
docker stop temporal-dev

# View logs
tail -f logs/app.log
```

## Troubleshooting:

**Port 8003 already in use:**
```bash
lsof -i :8003
kill -9 <PID>
```

**Temporal not responding:**
```bash
docker restart temporal-dev
docker logs temporal-dev
```

**Import errors:**
```bash
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## Next Steps:

1. Deploy to Azure: See `AZURE-DEPLOYMENT-GUIDE.md`
2. Run full test suite: `pytest tests/ --cov`
3. Explore the code: Start with `agents/planner.py`

🎉 **Your local development environment is ready!**
EOF

cat SETUP_COMPLETE.md
```

---

## 🎯 **Summary for Goose**

**Goose, you have completed:**

1. ✅ Verified system dependencies
2. ✅ Created Python virtual environment
3. ✅ Installed all Python packages
4. ✅ Started Temporal server in Docker
5. ✅ Created .env configuration file
6. ✅ Created database setup script
7. ✅ Created startup and verification scripts
8. ✅ Generated user instructions

**User must complete manually:**
- Update API keys in `.env` file
- Run SQL script in Supabase
- Test the system

**Files created:**
- `.env` - Environment configuration
- `setup_database.sql` - Database schema
- `start_server.sh` - Server startup script
- `verify_setup.sh` - Setup verification script
- `SETUP_COMPLETE.md` - User instructions

---

## 🤖 **Goose Execution Order**

**Copy this prompt to Goose:**

```
Please set up the Multi-Agent Timesheet System on this computer by following these steps in order:

1. Run Step 1: Check and install Python 3.11
2. Run Step 2: Clone or update the repository
3. Run Step 3: Create Python virtual environment
4. Run Step 4: Install all dependencies
5. Run Step 5: Start Temporal server in Docker
6. Run Step 6: Create .env configuration file
7. Run Step 7: Create database setup script
8. Run Step 8: Run unit tests to verify installation
9. Run Step 9: Create startup script
10. Run Step 10: Run verification script
11. Run Step 11: Generate user instructions

After completing all steps, show me the contents of SETUP_COMPLETE.md
```

---

**🚀 Ready for Goose automation!**
