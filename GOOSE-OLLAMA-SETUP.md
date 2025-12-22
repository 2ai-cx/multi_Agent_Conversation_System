# 🤖 Goose + Ollama Configuration Guide

## ✅ Verified Working Configuration

Your Ollama is running correctly with OpenAI-compatible API at:
- **Endpoint**: `http://localhost:11434/v1`
- **Model**: `gpt-oss:20b`
- **Status**: ✅ Working (tested successfully)

---

## 🔧 Configure Goose Desktop

### **Method 1: Goose Settings UI**

1. Open **Goose Desktop**
2. Go to **Settings** → **Model Configuration**
3. Configure as follows:

```
Provider: OpenAI Compatible / Custom
Base URL: http://localhost:11434/v1
Model: gpt-oss:20b
API Key: ollama
Temperature: 0.7
Max Tokens: 2000
```

### **Method 2: Environment Variables**

If Goose uses environment variables, set these before launching:

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_MODEL=gpt-oss:20b
```

Then restart Goose Desktop.

### **Method 3: Configuration File**

Some versions of Goose use a config file. Create or edit `~/.goose/config.yaml`:

```yaml
provider: openai
openai:
  api_base: http://localhost:11434/v1
  api_key: ollama
  model: gpt-oss:20b
  temperature: 0.7
  max_tokens: 2000
```

---

## 🧪 Test Your Configuration

### **Test 1: Simple Prompt**

In Goose, try:
```
Say hello and confirm you're using gpt-oss:20b
```

Expected response: Should get a response from your local model.

### **Test 2: File Operation**

```
List all Python files in the current directory
```

Expected: Should execute `ls *.py` or similar.

### **Test 3: Code Analysis**

```
Read tests/integration/test_agent_coordination.py and tell me how many tests are in it
```

Expected: Should read the file and count tests.

---

## 🐛 Troubleshooting

### **Error: 404 Not Found**

**Cause**: Goose is using wrong endpoint or model name

**Fix**:
1. Verify Ollama is running: `curl http://localhost:11434/v1/models`
2. Check model name exactly matches: `gpt-oss:20b` (case-sensitive)
3. Ensure base URL ends with `/v1` not `/api`

### **Error: Connection Refused**

**Cause**: Ollama server not running

**Fix**:
```bash
# Start Ollama (if not running)
ollama serve

# Or check if it's running
ps aux | grep ollama
```

### **Error: Model Not Found**

**Cause**: Model name mismatch

**Fix**:
```bash
# List available models
ollama list

# Use exact name from list
# Should be: gpt-oss:20b
```

### **Goose Still Using Cloud API**

**Cause**: Configuration not applied

**Fix**:
1. Completely quit Goose Desktop (Cmd+Q)
2. Relaunch Goose Desktop
3. Verify settings are saved
4. Try test prompt again

---

## 📊 Performance Expectations

With `gpt-oss:20b` on your local machine:

- **Speed**: ~10 seconds per response (varies by prompt length)
- **Quality**: Good for code analysis and test fixing
- **Cost**: $0 (completely free!)
- **Privacy**: All data stays local
- **Tokens**: Unlimited usage

---

## 🎯 Ready-to-Use Test Prompts

Once configured, try these prompts in Goose:

### **Phase 1: Fix Integration Tests**

```
I'm fixing tests for the Timesheet Multi-Agent System.

Current status: 3 integration tests failing in tests/integration/test_agent_coordination.py

Please:
1. Run: pytest tests/integration/test_agent_coordination.py -v
2. Analyze the failures
3. Fix the mock_llm_generate conditions to match actual agent prompts
4. Ensure JSON responses match Pydantic models
5. Test each fix

Success criteria: All integration tests pass
```

### **Phase 2: Eliminate Warnings**

```
Eliminate all Pydantic and datetime warnings in this project.

Tasks:
1. Migrate @validator to @field_validator in agents/models.py
2. Update Config to ConfigDict in llm/config.py  
3. Replace datetime.utcnow() with datetime.now(UTC)

Run pytest after each change to verify no breakage.

Success criteria: 0 warnings
```

### **Phase 3: Improve Coverage**

```
Improve test coverage from 70% to 80%+.

Steps:
1. Run: pytest --cov --cov-report=html
2. Identify low coverage modules
3. Add tests for error handling and edge cases
4. Focus on critical paths

Success criteria: Coverage >= 80%
```

---

## 💡 Tips for Using Goose with Ollama

1. **Be Patient**: Local models are slower than cloud APIs (~10s vs ~2s)
2. **Be Specific**: Give clear, detailed instructions
3. **Break Down Tasks**: Smaller tasks work better than large ones
4. **Verify Results**: Always check Goose's work
5. **Iterate**: If something doesn't work, refine your prompt

---

## 🚀 Next Steps

1. **Configure Goose** using Method 1 above
2. **Test** with simple prompt
3. **Run Phase 1** prompt to fix integration tests
4. **Monitor** Goose's progress
5. **Verify** results with `pytest`

---

**✅ Your Ollama is ready! Just need to configure Goose to use it.**

**Start here**: Configure Goose Settings with the values above, then try the Phase 1 prompt!
