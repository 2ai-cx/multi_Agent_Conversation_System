# 🎯 Best Ollama Models for Goose Autonomous Tasks

## Research Summary - December 2025

Based on comprehensive research, here are the **TOP 3 models** for autonomous agent tasks with Goose:

---

## 🥇 **RECOMMENDED: Download These 3 Models**

### **1. Llama 3.1 8B-Instruct** ⭐⭐⭐⭐⭐
**Best Overall for Goose Autonomous Tasks**

```bash
ollama pull llama3.1:8b-instruct
```

**Specs:**
- Size: 8B parameters (~5GB download)
- RAM: 8GB+ required
- Speed: Fast
- Tool Calling: ✅ Excellent

**Why This Model:**
- ✅ **Best function/tool calling support**
- ✅ **Excellent at following multi-step instructions**
- ✅ **Strong error handling and recovery**
- ✅ **Wide community support**
- ✅ **Officially supported by Ollama for tools**
- ✅ **Good balance of size vs capability**

**Perfect For:**
- Multi-step workflows
- Autonomous task execution
- Tool calling (file operations, command execution)
- Error recovery
- Sequential task processing

---

### **2. Qwen2.5 7B-Instruct** ⭐⭐⭐⭐⭐
**Best for Coding and Technical Tasks**

```bash
ollama pull qwen2.5:7b-instruct
```

**Specs:**
- Size: 7B parameters (~4.7GB download)
- RAM: 7GB+ required
- Speed: Very Fast
- Tool Calling: ✅ Excellent

**Why This Model:**
- ✅ **Exceptional at understanding code**
- ✅ **Great for test generation**
- ✅ **Fast inference speed**
- ✅ **Reliable tool calling**
- ✅ **Good at following structured instructions**
- ✅ **Smaller than Llama 3.1**

**Perfect For:**
- Test file generation
- Code editing tasks
- Technical documentation
- API integration
- Development workflows

---

### **3. Mistral 7B-Instruct v0.3** ⭐⭐⭐⭐
**Best for Speed and Efficiency**

```bash
ollama pull mistral:7b-instruct-v0.3
```

**Specs:**
- Size: 7B parameters (~4.1GB download)
- RAM: 7GB+ required
- Speed: Very Fast
- Tool Calling: ✅ Good

**Why This Model:**
- ✅ **Fastest inference speed**
- ✅ **Memory efficient**
- ✅ **Good tool calling support**
- ✅ **Reliable for simple tasks**
- ✅ **Low latency**

**Perfect For:**
- Real-time applications
- High-throughput tasks
- Resource-constrained environments
- Simple repetitive tasks

---

## 📊 **Comparison Table**

| Model | Size | Speed | Tool Calling | Best For | Download |
|-------|------|-------|--------------|----------|----------|
| **Llama 3.1 8B** | 5GB | Fast | ⭐⭐⭐⭐⭐ | **Autonomous workflows** | `llama3.1:8b-instruct` |
| **Qwen2.5 7B** | 4.7GB | Very Fast | ⭐⭐⭐⭐⭐ | **Code/test generation** | `qwen2.5:7b-instruct` |
| **Mistral 7B** | 4.1GB | Very Fast | ⭐⭐⭐⭐ | **Speed/efficiency** | `mistral:7b-instruct-v0.3` |
| ~~gpt-oss:20b~~ | 13GB | Slow | ⭐ | ❌ **Failed** | ❌ Not recommended |

---

## 🚀 **Quick Start: Download All 3**

Run these commands to download all recommended models:

```bash
# Download all 3 models (takes ~15-20 minutes)
ollama pull llama3.1:8b-instruct
ollama pull qwen2.5:7b-instruct
ollama pull mistral:7b-instruct-v0.3

# Verify downloads
ollama list
```

**Total Download Size:** ~14GB  
**Total RAM Required:** 8GB (one model at a time)

---

## 🎯 **Which Model to Use When?**

### **Use Llama 3.1 8B for:**
- ✅ Complex multi-step workflows
- ✅ Autonomous task execution (like our 50-task batch)
- ✅ Tasks requiring reasoning
- ✅ Error recovery scenarios
- ✅ General-purpose agent work

### **Use Qwen2.5 7B for:**
- ✅ Test file generation
- ✅ Code editing and refactoring
- ✅ Technical documentation
- ✅ API integration tasks
- ✅ Python/JavaScript work

### **Use Mistral 7B for:**
- ✅ Simple repetitive tasks
- ✅ Fast response requirements
- ✅ Low-latency applications
- ✅ Resource-constrained scenarios

---

## ⚙️ **Configure Goose with New Model**

After downloading, configure Goose to use the new model:

### **Option 1: Update config file**
Edit `~/.config/goose/config.yaml`:
```yaml
GOOSE_PROVIDER: ollama
GOOSE_MODEL: llama3.1:8b-instruct  # or qwen2.5:7b-instruct
OLLAMA_HOST: http://localhost:11434
```

### **Option 2: Update profiles**
Edit `~/.config/goose/profiles.yaml`:
```yaml
default:
  provider: ollama
  processor: llama3.1:8b-instruct
  accelerator: llama3.1:8b-instruct
  moderator: llama3.1:8b-instruct
```

---

## 🧪 **Test the New Model**

After configuring, test with a simple task:

```
Test prompt for Goose:

Read tests/e2e/test_complete_conversation_flow.py and tell me:
1. How many test methods are there?
2. What errors do you see?
3. List the line numbers that need fixing.

Do this now.
```

**Expected behavior with good model:**
- ✅ Reads the file
- ✅ Counts tests accurately
- ✅ Identifies specific errors
- ✅ Lists exact line numbers
- ✅ Doesn't ask unnecessary questions

---

## 📈 **Why These Are Better Than gpt-oss:20b**

| Feature | gpt-oss:20b | Llama 3.1 8B | Qwen2.5 7B |
|---------|-------------|--------------|------------|
| **Tool Calling** | ❌ Poor | ✅ Excellent | ✅ Excellent |
| **Following Instructions** | ❌ Weak | ✅ Strong | ✅ Strong |
| **Multi-step Tasks** | ❌ Fails | ✅ Works | ✅ Works |
| **Code Understanding** | ⚠️ Basic | ✅ Good | ✅ Excellent |
| **Speed** | 🐌 Slow | ⚡ Fast | ⚡ Very Fast |
| **Size** | 13GB | 5GB | 4.7GB |
| **Autonomous Work** | ❌ No | ✅ Yes | ✅ Yes |

---

## 🎓 **Official Support**

All 3 recommended models are **officially supported** by Ollama for tool calling:

- [Llama 3.1](https://ollama.com/library/llama3.1) - Official Ollama library
- [Qwen2.5](https://ollama.com/library/qwen2.5) - Official Ollama library
- [Mistral](https://ollama.com/library/mistral) - Official Ollama library

Source: [Ollama Tool Support Blog](https://ollama.com/blog/tool-support)

---

## 💡 **Advanced: Try Larger Models (If You Have RAM)**

If you have **32GB+ RAM**, consider these powerhouse models:

### **Llama 3.1 70B-Instruct** (Best Quality)
```bash
ollama pull llama3.1:70b-instruct
```
- Size: ~40GB
- RAM: 64GB+ required
- Quality: ⭐⭐⭐⭐⭐ (Best possible)
- Speed: Slower

### **Qwen2.5 32B-Instruct** (Best for Code)
```bash
ollama pull qwen2.5:32b-instruct
```
- Size: ~20GB
- RAM: 32GB+ required
- Quality: ⭐⭐⭐⭐⭐
- Speed: Medium

---

## 🔄 **Migration Plan**

### **Step 1: Download New Models**
```bash
ollama pull llama3.1:8b-instruct
ollama pull qwen2.5:7b-instruct
```

### **Step 2: Update Goose Config**
```bash
# Backup current config
cp ~/.config/goose/config.yaml ~/.config/goose/config.yaml.backup

# Edit config to use llama3.1:8b-instruct
nano ~/.config/goose/config.yaml
```

### **Step 3: Restart Goose**
- Quit Goose Desktop (Cmd+Q)
- Relaunch Goose Desktop

### **Step 4: Test**
Give Goose a simple task and verify it works better

### **Step 5: Run Batch Tasks**
Try the 50-task batch workflow again with new model

---

## 📝 **Expected Improvements**

With Llama 3.1 8B or Qwen2.5 7B, you should see:

✅ **Better understanding** of complex instructions  
✅ **Actual autonomous execution** (not stopping after each task)  
✅ **Proper tool calling** (file operations, commands)  
✅ **Error recovery** (fixes mistakes and continues)  
✅ **Faster responses** (smaller, optimized models)  
✅ **More reliable** (officially supported for tools)  

---

## 🎯 **Final Recommendation**

**Download all 3 models and test each:**

1. **Start with Llama 3.1 8B** - Best overall
2. **Try Qwen2.5 7B** - Best for code/tests
3. **Fall back to Mistral 7B** - If you need speed

**Then run the 50-task batch workflow** and see which performs best for your specific use case.

---

## 📞 **Next Steps**

1. Run the download commands above
2. Update Goose configuration
3. Restart Goose
4. Test with simple task
5. Run full 50-task batch workflow
6. Report results!

---

**Ready to download? Run:**
```bash
ollama pull llama3.1:8b-instruct && \
ollama pull qwen2.5:7b-instruct && \
ollama pull mistral:7b-instruct-v0.3
```

This will download all 3 models (~15-20 minutes). ⏱️
