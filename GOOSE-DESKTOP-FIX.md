# 🔧 Goose Desktop 400 Error - Debug & Fix

## 🐛 **Problem Found:**

Goose Desktop was getting **400 Bad Request** from Ollama API because:
1. Config file had issues with URL format
2. Moderator was set to model name instead of valid option
3. Desktop daemon (`goosed`) was using cached config

## ✅ **Fixes Applied:**

### **1. Fixed config.yaml**
```yaml
OLLAMA_HOST: http://localhost:11434/  # Added trailing slash
OLLAMA_TIMEOUT: '600'
GOOSE_PROVIDER: ollama
GOOSE_MODEL: deepseek-r1:8b
```

### **2. Fixed profiles.yaml**
```yaml
default:
  provider: ollama
  processor: deepseek-r1:8b
  accelerator: deepseek-r1:8b
  moderator: passive  # Changed from deepseek-r1:8b to passive
```

### **3. Killed Goose Desktop**
```bash
killall Goose
```

---

## 🚀 **To Test Goose Desktop:**

1. **Relaunch Goose Desktop**
   ```bash
   open -a Goose
   ```

2. **Wait 5 seconds** for daemon to start

3. **Open your project** in Goose Desktop

4. **Try this prompt:**
   ```
   Read tests/e2e/test_complete_conversation_flow.py and count the test methods.
   ```

5. **Expected:** Should work without 400 error!

---

## 📊 **Verification:**

### **Check if it's working:**
```bash
# Monitor logs in real-time
tail -f ~/Library/Application\ Support/Goose/logs/main.log
```

### **Look for:**
- ✅ No "400 Bad Request" errors
- ✅ "Provider request succeeded" messages
- ✅ Model responses appearing

---

## 🔍 **If Still Getting 400 Error:**

### **Debug Steps:**

1. **Check Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```
   Should return list of models.

2. **Test Ollama API directly:**
   ```bash
   curl -X POST http://localhost:11434/api/generate \
     -d '{"model": "deepseek-r1:8b", "prompt": "hi", "stream": false}'
   ```
   Should return a response.

3. **Check Goose config is loaded:**
   ```bash
   cat ~/.config/goose/config.yaml | grep GOOSE
   ```
   Should show: `GOOSE_MODEL: deepseek-r1:8b`

4. **Check goosed processes:**
   ```bash
   ps aux | grep goosed
   ```
   Should show 2 processes running.

5. **Check logs for specific error:**
   ```bash
   grep "400\|error" ~/Library/Application\ Support/Goose/logs/main.log | tail -10
   ```

---

## 🎯 **Root Cause Analysis:**

### **Why 400 Error Happened:**

1. **URL Format Issue:**
   - Goose adds `/v1` to Ollama host
   - Without trailing slash: `http://localhost:11434v1/` ❌
   - With trailing slash: `http://localhost:11434/v1/` ✅

2. **Moderator Config:**
   - Moderator must be: `passive`, `summarize`, `truncate`, or `synopsis`
   - Cannot be a model name like `deepseek-r1:8b`

3. **Cached Config:**
   - Goose Desktop daemon caches config
   - Must restart app to reload

---

## 📝 **Working Configuration:**

### **~/.config/goose/config.yaml:**
```yaml
extensions:
  developer:
    enabled: true
  # ... other extensions ...

OLLAMA_HOST: http://localhost:11434/
OLLAMA_TIMEOUT: '600'
GOOSE_PROVIDER: ollama
GOOSE_MODEL: deepseek-r1:8b
```

### **~/.config/goose/profiles.yaml:**
```yaml
default:
  provider: ollama
  processor: deepseek-r1:8b
  accelerator: deepseek-r1:8b
  moderator: passive
```

---

## ✅ **Success Criteria:**

- [ ] Goose Desktop launches without errors
- [ ] Can send prompts without 400 error
- [ ] Model responds (DeepSeek-R1 8B)
- [ ] No "Request failed" in logs
- [ ] Responses appear in chat

---

## 🆚 **Goose CLI vs Desktop:**

| Feature | CLI | Desktop |
|---------|-----|---------|
| **Status** | ✅ Working | ⚠️ Testing |
| **Config** | Environment vars | config.yaml |
| **Restart needed** | No | Yes |
| **Debugging** | Easy | Harder (logs) |
| **Recommended** | ✅ Yes | After fix |

---

## 💡 **Alternative: Use CLI**

If Desktop still doesn't work, use CLI:

```bash
cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System

GOOSE_PROVIDER=ollama GOOSE_MODEL=deepseek-r1:8b OLLAMA_HOST=http://localhost:11434/ goose session start
```

**CLI is confirmed working!** ✅

---

## 📞 **Next Steps:**

1. ✅ Relaunch Goose Desktop
2. ✅ Test with simple prompt
3. ✅ Check logs if error persists
4. ✅ Report back results!

---

**Goose Desktop should work now!** 🎉
