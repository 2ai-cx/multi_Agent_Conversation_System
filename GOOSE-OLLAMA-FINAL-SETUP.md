# 🦢 Goose + Ollama Configuration Guide (Official Method)

## 🔍 **Issue Identified**

Based on official Goose documentation, the 404 error occurs because:

1. **Tool Calling Required**: Goose needs models with tool calling support
2. **gpt-oss:20b**: May not support tool calling (causing 404 errors)
3. **Configuration Method**: Desktop UI might not properly configure Ollama

## ✅ **Official Solution: Use CLI Configuration**

### **Step 1: Check Available Models**

First, check which Ollama models support tool calling:

```bash
# List your models
ollama list

# Check if gpt-oss:20b supports tools
curl -s http://localhost:11434/api/show -d '{"name":"gpt-oss:20b"}' | grep -i tool
```

### **Step 2: Configure Goose via CLI**

Open a terminal and run:

```bash
goose configure
```

You'll see:

```
┌ goose-configure
│◆ What would you like to configure?
│ ● Configure Providers (Change provider or update credentials)
│ ○ Toggle Extensions
│ ○ Add Extension
└
```

### **Step 3: Select Ollama Provider**

Choose **Ollama**:

```
┌ goose-configure
│◇ What would you like to configure?
│ Configure Providers
│◆ Which model provider should we use?
│ ○ Anthropic
│ ○ Databricks
│ ○ Google Gemini
│ ○ Groq
│ ● Ollama (Local open source models)
│ ○ OpenAI
│ ○ OpenRouter
└
```

### **Step 4: Enter Ollama Host**

When prompted for `OLLAMA_HOST`, enter:

```
http://localhost:11434
```

**Important:** Include `http://` prefix!

```
┌ goose-configure
│◇ Which model provider should we use?
│ Ollama
│◆ Provider Ollama requires OLLAMA_HOST, please enter a value
│ http://localhost:11434
└
```

### **Step 5: Enter Model Name**

Enter your model:

```
gpt-oss:20b
```

```
┌ goose-configure
│◇ Provider Ollama requires OLLAMA_HOST, please enter a value
│ http://localhost:11434
│◇ Enter a model from that provider:
│ gpt-oss:20b
│◇ Welcome! You're all set to explore and utilize my capabilities!
└ Configuration saved successfully
```

---

## 🔧 **If gpt-oss:20b Doesn't Support Tool Calling**

### **Option 1: Use a Tool-Calling Model**

Download a model that supports tool calling:

```bash
# Recommended: Qwen 2.5 (supports tool calling)
ollama pull qwen2.5

# Or: Llama 3.2 (supports tool calling)
ollama pull llama3.2

# Or: Custom DeepSeek-R1 for Goose
ollama pull michaelneale/deepseek-r1-goose
```

Then configure Goose with one of these models instead.

### **Option 2: Disable Extensions for gpt-oss:20b**

If you want to use `gpt-oss:20b` without tool calling:

```bash
goose configure
```

Choose **Toggle Extensions** and disable all extensions.

**Note:** Without extensions, Goose can only do chat completion, not execute commands or read files.

---

## 🧪 **Test Your Configuration**

After configuration, test it:

```bash
# Start goose
goose session start

# Try a simple prompt
> Hello, what model are you using?
```

If it works, you should get a response from your local Ollama model!

---

## 📋 **Recommended Models for Goose**

Based on official docs, these models work well with Goose:

| Model | Size | Tool Calling | Speed | Quality |
|-------|------|--------------|-------|---------|
| **qwen2.5** | 7B | ✅ Yes | Fast | Good |
| **llama3.2** | 3B | ✅ Yes | Very Fast | Decent |
| **michaelneale/deepseek-r1-goose** | 70B | ✅ Yes | Slow | Excellent |
| **gpt-oss:20b** | 20B | ❓ Unknown | Medium | Good |

---

## 🎯 **Quick Setup Commands**

### **For qwen2.5 (Recommended):**

```bash
# Pull model
ollama pull qwen2.5

# Configure Goose
goose configure
# Choose: Ollama
# Host: http://localhost:11434
# Model: qwen2.5

# Test
goose session start
```

### **For gpt-oss:20b (If Tool Calling Works):**

```bash
# Configure Goose
goose configure
# Choose: Ollama
# Host: http://localhost:11434
# Model: gpt-oss:20b

# Test
goose session start
```

---

## 🔍 **Verify Tool Calling Support**

To check if `gpt-oss:20b` supports tool calling:

```bash
# Get model info
curl -s http://localhost:11434/api/show -d '{"name":"gpt-oss:20b"}' | python3 -m json.tool

# Look for "tools" or "function_calling" in the output
```

Or test directly:

```bash
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:20b",
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "calculate",
          "description": "Perform calculation",
          "parameters": {
            "type": "object",
            "properties": {
              "expression": {"type": "string"}
            }
          }
        }
      }
    ]
  }' | python3 -m json.tool
```

If you get a valid response with `tool_calls`, it supports tools!

---

## 🚀 **Next Steps**

1. **Run `goose configure`** in terminal (not Desktop UI)
2. **Choose Ollama** as provider
3. **Enter `http://localhost:11434`** as host
4. **Enter `gpt-oss:20b`** as model
5. **Test with `goose session start`**

If you still get 404 errors, switch to `qwen2.5` which definitely supports tool calling.

---

## 💡 **Why CLI Configuration Works Better**

The Desktop UI might not properly save Ollama configuration. The CLI:
- ✅ Saves to correct config location
- ✅ Tests the connection immediately
- ✅ Shows clear error messages
- ✅ Properly handles Ollama-specific settings

---

**🎯 Try running `goose configure` in your terminal now!**
