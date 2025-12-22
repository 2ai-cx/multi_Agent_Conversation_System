# 🧪 Local Testing Guide - Multi-Agent System

Complete guide for testing the multi-agent conversation system locally.

---

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **Temporal CLI** installed (for local Temporal server)
3. **OpenRouter API key** (free tier available) OR OpenAI API key
4. **Supabase account** (for database)
5. **Twilio account** (for SMS/WhatsApp testing) - Optional for unit tests

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and fill in your values (minimum required):
# - OPENROUTER_API_KEY (or OPENAI_API_KEY)
# - SUPABASE_URL
# - SUPABASE_KEY
# - HARVEST_ACCESS_TOKEN
# - HARVEST_ACCOUNT_ID
```

**Minimum .env for testing**:
```bash
# LLM
USE_OPENROUTER=true
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free

# Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=xxxxx

# Harvest
HARVEST_ACCESS_TOKEN=xxxxx
HARVEST_ACCOUNT_ID=xxxxx

# Temporal (local)
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# Disable optional features for testing
OPIK_ENABLED=false
CACHE_ENABLED=true
REDIS_ENABLED=false
```

### Step 3: Start Temporal Dev Server

```bash
# In a separate terminal
temporal server start-dev

# This starts:
# - Temporal server on localhost:7233
# - Temporal UI on http://localhost:8233
```

### Step 4: Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_planner.py -v

# Run with coverage
pytest tests/ --cov=agents --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Step 5: Start the Server

```bash
# Start the unified server
python unified_server.py

# Server will start on http://localhost:8003
# Check logs for:
# ✅ Temporal client initialized
# ✅ LLM client initialized
# ✅ Temporal worker started
```

---

## 🧪 Testing Options

### Option A: Unit Tests (No External Services)

Test individual agents without Temporal or external APIs.

```bash
# Test Planner Agent
pytest tests/unit/test_planner.py -v

# Test Timesheet Agent
pytest tests/unit/test_timesheet.py -v

# Test Branding Agent
pytest tests/unit/test_branding.py -v

# Test Quality Agent
pytest tests/unit/test_quality.py -v
```

**What's tested**:
- ✅ Agent logic
- ✅ LLM prompt construction
- ✅ Response parsing
- ✅ Error handling
- ✅ Mocked LLM responses (no API calls)

---

### Option B: Integration Tests (Temporal Required)

Test complete multi-agent workflow with Temporal.

```bash
# Make sure Temporal is running first!
temporal server start-dev

# Run integration tests
pytest tests/integration/test_agent_coordination.py -v
```

**What's tested**:
- ✅ Complete workflow execution
- ✅ Agent coordination
- ✅ Refinement loop
- ✅ Graceful failure
- ✅ Performance (<10s)
- ✅ Mocked LLM and Harvest (no real API calls)

---

### Option C: Manual Testing via Webhook

Test the complete system with real webhooks.

#### Setup ngrok (for Twilio webhooks)

```bash
# Install ngrok
brew install ngrok  # On Mac
# Or download from https://ngrok.com/

# Start ngrok
ngrok http 8003

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

#### Configure Twilio Webhook

1. Go to Twilio Console → Phone Numbers
2. Select your phone number
3. Set SMS webhook to: `https://abc123.ngrok.io/webhook/sms`
4. Set WhatsApp webhook to: `https://abc123.ngrok.io/webhook/whatsapp`
5. Save

#### Send Test SMS

```bash
# Send SMS to your Twilio number
# Message: "Check my timesheet"

# Watch server logs for:
# 📱 SMS received from +1234567890: Check my timesheet
# 🤖 Using Multi-Agent Conversation System
# 🤖 Starting MultiAgentConversationWorkflow
# 📋 Step 1: Planner analyzing request
# 📊 Step 2: Timesheet extracting data
# ✍️ Step 3: Planner composing response
# 🎨 Step 4: Branding formatting for SMS
# ✅ Step 5: Quality validating response
# ✅ Multi-agent workflow complete
# 📤 Sending response via SMS
```

---

### Option D: Direct Workflow Testing (Python Script)

Test the workflow directly without webhooks.

Create `test_workflow_direct.py`:

```python
import asyncio
from temporalio.client import Client
from unified_workflows import MultiAgentConversationWorkflow

async def test_workflow():
    # Connect to local Temporal
    client = await Client.connect("localhost:7233")
    
    # Start workflow
    result = await client.execute_workflow(
        MultiAgentConversationWorkflow.run,
        args=[
            "Check my timesheet",  # user_message
            "sms",                 # channel
            "user1",               # user_id
            "test-123",            # conversation_id
            [],                    # conversation_history
            {"from": "+1234567890"}  # user_context
        ],
        id=f"test-workflow-{int(time.time())}",
        task_queue="timesheet-reminders"
    )
    
    print("✅ Workflow completed!")
    print(f"Response: {result['final_response']}")
    print(f"Validation passed: {result['validation_passed']}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
```

Run it:
```bash
python test_workflow_direct.py
```

---

## 🔍 Debugging Tips

### 1. Check Temporal UI

Visit http://localhost:8233 to see:
- Workflow executions
- Activity logs
- Errors and retries
- Execution history

### 2. Enable Verbose Logging

```bash
# In .env
LOG_LEVEL=DEBUG

# Restart server
python unified_server.py
```

### 3. Test Individual Agents

```python
# test_agent.py
import asyncio
from llm.client import get_llm_client
from agents.planner import PlannerAgent

async def test_planner():
    llm_client = get_llm_client()
    agent = PlannerAgent(llm_client)
    
    result = await agent.analyze_request(
        request_id="test-123",
        user_message="Check my timesheet",
        channel="sms",
        conversation_history=[],
        user_context={"from": "+1234567890"}
    )
    
    print(result)

asyncio.run(test_planner())
```

### 4. Check LLM Calls

```bash
# Enable LLM logging in .env
LOG_PROMPTS=true
LOG_RESPONSES=true

# You'll see:
# LLM request: {...}
# LLM response: {...}
```

### 5. Monitor Costs (if Opik enabled)

```bash
# In .env
OPIK_ENABLED=true
OPIK_API_KEY=xxxxx

# Visit Opik dashboard to see:
# - All LLM calls
# - Costs per call
# - Token usage
# - Latency
```

---

## 📊 Expected Test Results

### Unit Tests
```
tests/unit/test_planner.py::test_analyze_request ✅ PASSED
tests/unit/test_planner.py::test_compose_response ✅ PASSED
tests/unit/test_planner.py::test_refine_response ✅ PASSED
tests/unit/test_timesheet.py::test_extract_hours ✅ PASSED
tests/unit/test_branding.py::test_format_sms ✅ PASSED
tests/unit/test_quality.py::test_validate_response ✅ PASSED

Total: 20 tests, 20 passed ✅
```

### Integration Tests
```
tests/integration/test_agent_coordination.py::test_complete_workflow ✅ PASSED (7.2s)
tests/integration/test_agent_coordination.py::test_refinement_loop ✅ PASSED (9.1s)
tests/integration/test_agent_coordination.py::test_graceful_failure ✅ PASSED (3.5s)
tests/integration/test_agent_coordination.py::test_performance ✅ PASSED (8.9s)

Total: 4 tests, 4 passed ✅
All under 10s target ✅
```

### Manual SMS Test
```
Input: "Check my timesheet"
Expected Output: "Hi [Name]! You've logged X out of Y hours this week. [Details]"
Time: ~7-10 seconds
Format: Plain text, no markdown, <1600 chars
```

---

## 🐛 Common Issues

### Issue 1: "Temporal client not available"

**Solution**:
```bash
# Make sure Temporal is running
temporal server start-dev

# Check connection
temporal workflow list
```

### Issue 2: "LLM Client not initialized"

**Solution**:
```bash
# Check .env has LLM credentials
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Or use OpenAI
OPENAI_API_KEY=sk-xxxxx
```

### Issue 3: "Supabase client not initialized"

**Solution**:
```bash
# Check .env has Supabase credentials
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=xxxxx
```

### Issue 4: "No module named 'agents'"

**Solution**:
```bash
# Make sure you're in the project root
cd /path/to/multi_Agent_Conversation_System

# Run from project root
python unified_server.py
```

### Issue 5: Tests fail with "Mock not working"

**Solution**:
```bash
# Install pytest-mock
pip install pytest-mock

# Re-run tests
pytest tests/ -v
```

---

## 📝 Test Checklist

Before deploying, verify:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Manual SMS test works
- [ ] Response is properly formatted for SMS (no markdown)
- [ ] Response is under 1600 characters
- [ ] Quality validation works
- [ ] Refinement loop works (test with bad response)
- [ ] Graceful failure works (test with error)
- [ ] Performance is <10s end-to-end
- [ ] Temporal UI shows successful workflows
- [ ] Logs show all agent steps
- [ ] No errors in console

---

## 🎯 Next Steps

Once local testing passes:

1. **Deploy to staging** with real Temporal Cloud
2. **Test with real users** (small group)
3. **Monitor metrics** (Opik dashboard)
4. **Gradual rollout** to production
5. **Monitor and iterate**

---

## 📚 Additional Resources

- **Temporal Docs**: https://docs.temporal.io/
- **OpenRouter**: https://openrouter.ai/
- **Supabase**: https://supabase.com/docs
- **Twilio**: https://www.twilio.com/docs

---

## 🆘 Need Help?

1. Check logs: `tail -f server.log`
2. Check Temporal UI: http://localhost:8233
3. Check test output: `pytest tests/ -v -s`
4. Enable debug logging: `LOG_LEVEL=DEBUG`

Good luck with testing! 🚀
