# All Goose-Compatible Models (Ollama Tool Support)

These models support Ollama's tool calling format and will work with Goose Desktop.

---

## ✅ Models You Already Have

| Model | Size | RAM | Status | Autonomous Capability |
|-------|------|-----|--------|----------------------|
| **llama3.1:latest** | 4.9GB | 6.2GB | ✅ Downloaded | ⚠️ Low-Medium |
| **gpt-oss:20b** | 13GB | 16GB | ✅ Downloaded | ⚠️ Medium |
| **llama3.2:latest** | 2.0GB | 3GB | ✅ Downloaded | ❌ Very Low (too small) |

---

## 🎯 Best Models for Autonomous Work (Recommended Downloads)

### **Small Models (8B-14B) - Fast, Efficient**

| Model | Size | RAM | Download Command | Best For |
|-------|------|-----|------------------|----------|
| **mistral-nemo** ⭐ | 7GB | 9GB | `ollama pull mistral-nemo` | **Best 12B for tools** |
| **hermes3:8b** | 4.9GB | 6.2GB | `ollama pull hermes3:8b` | Instruction following |
| **qwen2.5:14b** | 9GB | 11GB | `ollama pull qwen2.5:14b` | Long context (128K) |
| **qwen2.5-coder:14b** | 9GB | 11GB | `ollama pull qwen2.5-coder:14b` | Code generation |
| **mistral:7b** | 4.1GB | 5.5GB | `ollama pull mistral:7b` | General purpose |
| **qwen3:8b** | 4.9GB | 6.2GB | `ollama pull qwen3:8b` | Latest Qwen |
| **cogito:8b** | 4.9GB | 6.2GB | `ollama pull cogito:8b` | Hybrid reasoning |

### **Medium Models (20B-35B) - Better Reasoning**

| Model | Size | RAM | Download Command | Best For |
|-------|------|-----|------------------|----------|
| **mistral-small:22b** ⭐ | 13GB | 16GB | `ollama pull mistral-small:22b` | **Best under 70B** |
| **qwq:32b** | 19GB | 23GB | `ollama pull qwq:32b` | Reasoning tasks |
| **command-r:35b** | 20GB | 24GB | `ollama pull command-r:35b` | Long context, RAG |
| **cogito:32b** | 19GB | 23GB | `ollama pull cogito:32b` | Hybrid reasoning |

### **Large Models (70B+) - Best Performance (If you have RAM)**

| Model | Size | RAM | Download Command | Best For |
|-------|------|-----|------------------|----------|
| **llama3.3:70b** ⭐ | 40GB | 50GB | `ollama pull llama3.3:70b` | **Best 70B overall** |
| **hermes3:70b** | 40GB | 50GB | `ollama pull hermes3:70b` | Tool calling |
| **mistral-large:123b** | 70GB | 85GB | `ollama pull mistral-large:123b` | Flagship model |
| **command-r-plus:104b** | 59GB | 70GB | `ollama pull command-r-plus:104b` | Enterprise use |

---

## 📊 Complete List (All Tool-Supported Models)

### **Tiny Models (< 2B)**
- `smollm2:135m` - 135M parameters
- `smollm2:360m` - 360M parameters
- `granite4:350m` - 350M parameters
- `granite3.1-moe:1b` - 1B MoE
- `smollm2:1.7b` - 1.7B parameters
- `llama3.2:1b` - 1B parameters

### **Small Models (2B-8B)**
- `granite3.2:2b` - 2B thinking model
- `granite3-dense:2b` - 2B tool-optimized
- `qwen3:2b` - 2B Qwen
- `llama3.2:3b` - 3B Meta model
- `granite3.1-moe:3b` - 3B MoE
- `granite4:3b` - 3B tool-calling
- `hermes3:3b` - 3B Hermes
- `cogito:3b` - 3B reasoning
- `ministral-3:3b` - 3B edge model
- `qwen3:4b` - 4B Qwen
- `qwen2.5:7b` - 7B Qwen
- `qwen2.5-coder:7b` - 7B code model
- `qwen2:7b` - 7B Qwen v2
- `mistral:7b` - 7B Mistral
- `deepseek-r1:7b` ⚠️ - 7B reasoning (tool support added)
- `llama3.1:8b` - 8B Meta model
- `hermes3:8b` - 8B Hermes
- `qwen3:8b` - 8B Qwen
- `granite3-dense:8b` - 8B tool-optimized
- `granite3.2:8b` - 8B thinking
- `cogito:8b` - 8B reasoning
- `ministral-3:8b` - 8B edge
- `deepseek-r1:8b` ⚠️ - 8B reasoning

### **Medium Models (12B-32B)**
- `mistral-nemo:12b` ⭐ - 12B state-of-the-art
- `qwen2.5:14b` - 14B Qwen
- `qwen2.5-coder:14b` - 14B code
- `qwen3:14b` - 14B Qwen
- `cogito:14b` - 14B reasoning
- `ministral-3:14b` - 14B edge
- `deepseek-r1:14b` ⚠️ - 14B reasoning
- `gpt-oss:20b` - 20B OpenAI-style
- `mistral-small:22b` - 22B Mistral
- `mistral-small:24b` - 24B Mistral
- `qwen3:30b` - 30B Qwen
- `qwen3-coder:30b` - 30B code
- `qwq:32b` - 32B reasoning
- `qwen2.5:32b` - 32B Qwen
- `qwen2.5-coder:32b` - 32B code
- `qwen3:32b` - 32B Qwen
- `cogito:32b` - 32B reasoning
- `deepseek-r1:32b` ⚠️ - 32B reasoning
- `command-r:35b` - 35B Cohere

### **Large Models (70B+)**
- `llama3.1:70b` - 70B Meta
- `llama3.3:70b` ⭐ - 70B state-of-the-art
- `hermes3:70b` - 70B Hermes
- `cogito:70b` - 70B reasoning
- `qwen2.5:72b` - 72B Qwen
- `qwen2:72b` - 72B Qwen v2
- `deepseek-r1:70b` ⚠️ - 70B reasoning
- `command-r-plus:104b` - 104B enterprise
- `mistral-large:123b` - 123B flagship
- `llama4:128x17b` - 128 experts MoE
- `qwen3:235b` - 235B Qwen
- `llama3.1:405b` - 405B Meta
- `hermes3:405b` - 405B Hermes
- `qwen3-coder:480b` - 480B code
- `deepseek-r1:671b` ⚠️ - 671B reasoning
- `deepseek-v3.1:671b` ⚠️ - 671B hybrid

### **Mixture of Experts (MoE)**
- `mixtral:8x7b` - 8 experts × 7B
- `mixtral:8x22b` - 8 experts × 22B
- `llama4:16x17b` - 16 experts × 17B
- `llama4:128x17b` - 128 experts × 17B

---

## 🎯 My Top 5 Recommendations for Goose

### **1. Mistral Nemo 12B** ⭐⭐⭐⭐⭐
```bash
ollama pull mistral-nemo
```
**Why:** Best balance of size, speed, and tool-calling capability. 128K context.
**RAM:** 9GB
**Autonomous:** Medium-High (5-10 steps)

---

### **2. Mistral Small 22B** ⭐⭐⭐⭐⭐
```bash
ollama pull mistral-small:22b
```
**Why:** Best model under 70B. Excellent reasoning and tool use.
**RAM:** 16GB (you have 30GB free)
**Autonomous:** High (10-20 steps)

---

### **3. Hermes 3 8B** ⭐⭐⭐⭐
```bash
ollama pull hermes3:8b
```
**Why:** Optimized for instruction following and tool calling.
**RAM:** 6.2GB
**Autonomous:** Medium (5-8 steps)

---

### **4. Qwen 2.5 14B** ⭐⭐⭐⭐
```bash
ollama pull qwen2.5:14b
```
**Why:** 128K context, multilingual, good reasoning.
**RAM:** 11GB
**Autonomous:** Medium-High (8-12 steps)

---

### **5. Llama 3.3 70B** ⭐⭐⭐⭐⭐ (If you have RAM)
```bash
ollama pull llama3.3:70b
```
**Why:** Best 70B model, approaches 405B performance.
**RAM:** 50GB (you have 30GB - **won't fit**)
**Autonomous:** Very High (20-30 steps)

---

## ⚠️ Models That DON'T Support Ollama Tools

These models will give **400 Bad Request** in Goose:

- ❌ `dolphin3:8b` - Claims function calling but no Ollama tool support
- ❌ `phi4` - No tool support
- ❌ `phi3` - No tool support
- ❌ `gemma2` - No tool support
- ❌ `codellama` - No tool support
- ❌ Most custom/community models

---

## 🚀 Quick Start Guide

### **Step 1: Download Recommended Model**
```bash
# Best option for your RAM (30GB free)
ollama pull mistral-small:22b

# Or if you want faster/smaller
ollama pull mistral-nemo
```

### **Step 2: Configure Goose**
```bash
# Edit ~/.config/goose/config.yaml
GOOSE_MODEL: mistral-small:22b

# Edit ~/.config/goose/profiles.yaml
processor: mistral-small:22b
accelerator: mistral-small:22b
```

### **Step 3: Restart Goose Desktop**

### **Step 4: Test**
Paste this into Goose:
```
Create tests/api/test_simple.py with one test function that asserts True.
Then run pytest on it.
Do it now.
```

---

## 📊 Size vs Capability Chart

| Size | Autonomous Steps | Best Models | Your RAM OK? |
|------|-----------------|-------------|--------------|
| **1-3B** | 1-3 steps | smollm2, granite4 | ✅ Yes |
| **7-8B** | 3-5 steps | mistral, hermes3, qwen2.5 | ✅ Yes |
| **12-14B** | 5-10 steps | **mistral-nemo**, qwen2.5:14b | ✅ Yes |
| **20-32B** | 10-20 steps | **mistral-small**, qwq, command-r | ✅ Yes |
| **70B** | 20-30 steps | llama3.3, hermes3:70b | ❌ No (need 50GB) |
| **100B+** | 30-50 steps | mistral-large, command-r-plus | ❌ No (need 70GB+) |

---

## 💡 Realistic Expectations

### **With Mistral Nemo (12B):**
- ✅ Can handle 5-10 step workflows
- ✅ Good tool calling
- ✅ Better than Llama 3.1 8B
- ⚠️ Still may need phase-by-phase for 16+ steps

### **With Mistral Small (22B):**
- ✅ Can handle 10-20 step workflows
- ✅ Excellent tool calling
- ✅ Much better reasoning
- ⚠️ May handle full 16-step workflow with guidance

### **For True Multi-Hour Autonomy:**
- Need 70B+ models (won't fit in your RAM)
- Or use cloud APIs (GPT-4, Claude)
- Or use me (Cascade) - I can do it now

---

## 🎯 My Recommendation

**Download Mistral Small 22B:**
```bash
ollama pull mistral-small:22b
```

**Why:**
- ✅ Fits in your RAM (16GB < 30GB free)
- ✅ Best model under 70B
- ✅ 10-20 step autonomous capability
- ✅ Excellent tool calling
- ✅ May actually complete your 16-step workflow

**Then test with phase-by-phase approach first, then try full workflow.**

---

Want me to download and configure Mistral Small 22B for you?
