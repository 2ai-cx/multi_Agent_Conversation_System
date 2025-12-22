# ✅ Goose + Ollama Configuration Complete

## 🎯 **Current Setup**

**Model:** `gpt-oss:20b` (20B parameters, 13 GB)  
**Provider:** Ollama (Local)  
**Host:** `http://localhost:11434`  
**Status:** ✅ Ready to use

---

## 📋 **Configuration Files**

### **1. Main Config:** `~/.config/goose/config.yaml`
```yaml
OLLAMA_HOST: http://localhost:11434
OLLAMA_TIMEOUT: '600'
GOOSE_PROVIDER: ollama
GOOSE_MODEL: gpt-oss:20b
```

### **2. Profiles:** `~/.config/goose/profiles.yaml`
```yaml
default:
  provider: ollama
  processor: gpt-oss:20b
  accelerator: gpt-oss:20b
  moderator: gpt-oss:20b
  
ollama:
  host: http://localhost:11434
  model: gpt-oss:20b
```

---

## 🚀 **How to Use**

### **Step 1: Restart Goose Desktop**
1. Quit Goose completely (Cmd+Q)
2. Relaunch Goose Desktop
3. Open your project directory

### **Step 2: Test Connection**
Send this test prompt:
```
Hello! Confirm you're using gpt-oss:20b model locally.
```

### **Step 3: Start Fixing Tests**
Once confirmed working, use this prompt:
```
I'm fixing integration tests in:
/Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System

Current status: 3 tests failing in tests/integration/test_agent_coordination.py

Please:
1. Run: pytest tests/integration/test_agent_coordination.py -v
2. Analyze the failures
3. Fix the mock_llm_generate conditions
4. Test each fix

Success: All 3 tests pass
```

---

## 🔍 **Verification Commands**

### **Check Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

### **Test gpt-oss:20b directly:**
```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:20b",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### **Check Goose config:**
```bash
cat ~/.config/goose/config.yaml | grep -A 3 OLLAMA
```

---

## ⚠️ **If You Get 404 Errors**

This means `gpt-oss:20b` might not support **tool calling** (required by Goose for extensions).

### **Option 1: Disable Extensions**
In Goose Desktop, disable all extensions to use chat-only mode.

### **Option 2: Check Tool Calling Support**
```bash
curl -s http://localhost:11434/api/show -d '{"name":"gpt-oss:20b"}' | grep -i tool
```

If no output, the model doesn't support tool calling.

---

## 💡 **Performance Expectations**

With `gpt-oss:20b` on your local machine:

- **Response Time:** ~10-15 seconds per request
- **Quality:** Good for code analysis and test fixing
- **Cost:** $0 (completely free!)
- **Privacy:** All data stays local
- **Tokens:** Unlimited usage

---

## 🎯 **Ready-to-Use Prompts**

### **Phase 1: Fix Integration Tests**
```
Fix the 3 failing integration tests in tests/integration/test_agent_coordination.py

Tests:
1. test_complete_workflow_success
2. test_workflow_with_refinement
3. test_workflow_with_graceful_failure

Update mock_llm_generate to match actual agent prompts.
Run each test after fixing.
```

### **Phase 2: Eliminate Warnings**
```
Eliminate all Pydantic and datetime warnings:

1. Migrate @validator to @field_validator in agents/models.py
2. Update Config to ConfigDict in llm/config.py
3. Replace datetime.utcnow() with datetime.now(UTC)

Run pytest after each change.
```

### **Phase 3: Improve Coverage**
```
Improve test coverage from 70% to 80%+:

1. Run: pytest --cov --cov-report=html
2. Identify low coverage modules
3. Add tests for error handling
4. Add edge case tests
```

---

## ✅ **Configuration Summary**

| Setting | Value |
|---------|-------|
| **Provider** | ollama |
| **Model** | gpt-oss:20b |
| **Host** | http://localhost:11434 |
| **Timeout** | 600 seconds |
| **Extensions** | Enabled (if tool calling works) |
| **Cost** | Free |
| **Privacy** | 100% local |

---

## 🚀 **Next Steps**

1. ✅ Configuration complete
2. 🔄 Restart Goose Desktop (Cmd+Q, then relaunch)
3. 🧪 Test with simple prompt
4. 🎯 Start fixing tests with Phase 1 prompt

---

**You're all set! Restart Goose Desktop and start testing!** 🦢
