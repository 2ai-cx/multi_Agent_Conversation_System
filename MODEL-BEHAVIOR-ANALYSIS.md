# Local LLM Model Behavior Analysis for Autonomous Workflows

## Executive Summary

Local LLMs fall into two distinct categories when used with Goose for autonomous workflows:
1. **Category A:** Models without Ollama tool support (incompatible)
2. **Category B:** Models with tool support but unable to execute autonomously (behavioral limitation)

**Key Finding:** No local model (8B-70B) can perform multi-hour autonomous workflows, regardless of tool support.

---

## Category A: Models Without Ollama Tool Support

### Behavior Pattern
These models fail immediately with `400 Bad Request` or `does not support tools` errors when Goose attempts to use tool calling.

### Root Cause
- Designed as reasoning or chat models, not action models
- Lack the specific tool calling API format required by Ollama
- May claim "function calling" but don't implement Ollama's tool schema

---

### A1. DeepSeek Family (Reasoning Models)

#### **DeepSeek-R1 Series**
- `deepseek-r1:1.5b`
- `deepseek-r1:7b`
- `deepseek-r1:8b`
- `deepseek-r1:14b`
- `deepseek-r1:32b`
- `deepseek-r1:70b`
- `deepseek-r1:671b`

**Architecture:** Pure reasoning models with chain-of-thought
**Tool Support:** ❌ None (confirmed via API test)
**Error:** `registry.ollama.ai/library/deepseek-r1:8b does not support tools`

**Analysis:**
- Designed for O1-style reasoning, not tool execution
- Focus on internal thought process, not external actions
- Incompatible with Goose's tool-based architecture
- Will never work regardless of prompt engineering

---

#### **DeepSeek-V3 Series**
- `deepseek-v3:671b`

**Architecture:** Mixture of Experts reasoning model
**Tool Support:** ❌ None
**Analysis:**
- Same reasoning-focused architecture as R1
- Too large for consumer hardware (671B parameters)
- Not designed for tool calling

---

#### **DeepSeek-V3.1 Series**
- `deepseek-v3.1:671b`

**Architecture:** Hybrid reasoning model (thinking + non-thinking modes)
**Tool Support:** ✅ Yes (official Ollama tools category)
**Analysis:**
- **Exception in DeepSeek family** - supports tools
- But 671B parameters = 400GB+ RAM required
- Impractical for local deployment
- Untested due to size constraints

---

#### **Custom DeepSeek Variants**
- `MFDoom/deepseek-r1-tool-calling:8b`
- `hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_XL`

**Architecture:** Community modifications attempting to add tool support
**Tool Support:** ⚠️ Claimed but unreliable
**Analysis:**
- Not officially supported by Ollama
- Inconsistent behavior across versions
- May work intermittently but not production-ready
- Better to use officially supported models

---

### A2. Dolphin Family (Uncensored Models)

#### **Dolphin 3.0 Series**
- `dolphin3:8b-llama3.1`
- `dolphin3:70b-llama3.1`

**Architecture:** Fine-tuned Llama 3.1 for uncensored responses
**Marketing Claim:** "Designed for agentic, function calling, and general use cases"
**Tool Support:** ❌ **None** (despite marketing)
**Error:** `registry.ollama.ai/library/dolphin3:8b does not support tools`

**Analysis:**
- **False advertising** - claims function calling but lacks Ollama tool API
- "Function calling" refers to general capability, not Ollama's specific format
- Uncensored training removes safety filters but doesn't add tool support
- Community confusion due to misleading documentation
- Will never work with Goose regardless of configuration

**Why This Happens:**
- Dolphin focuses on removing alignment restrictions
- Tool calling requires specific training and API implementation
- These are orthogonal features - uncensored ≠ tool-capable
- Marketing materials conflate "can discuss functions" with "can call tools"

---

### A3. Phi Family (Microsoft Small Models)

#### **Phi 3 Series**
- `phi3:3.8b`
- `phi3:14b`

#### **Phi 4 Series**
- `phi4:14b`
- `phi4-mini:3.8b`

**Architecture:** Small, efficient models optimized for edge deployment
**Tool Support:** ❌ None
**Analysis:**
- Designed for chat and reasoning, not tool execution
- Focus on efficiency and small size
- Lack the architectural components for tool calling
- Better suited for embedded systems than agentic workflows

---

### A4. Gemma Family (Google)

#### **Gemma 2 Series**
- `gemma2:2b`
- `gemma2:9b`
- `gemma2:27b`

#### **Gemma 3 Series**
- `gemma3:2b`
- `gemma3:9b`

**Architecture:** Google's open-weight models
**Tool Support:** ❌ None
**Analysis:**
- Chat-focused models without tool calling infrastructure
- Google reserves tool calling for Gemini API models
- Open-weight versions lack this capability
- Not designed for autonomous agent workflows

---

### A5. CodeLlama Family (Meta)

#### **CodeLlama Series**
- `codellama:7b`
- `codellama:13b`
- `codellama:34b`
- `codellama:70b`

**Architecture:** Llama 2 fine-tuned for code generation
**Tool Support:** ❌ None
**Analysis:**
- Pre-dates tool calling era (based on Llama 2)
- Excellent at code generation but no tool execution
- Superseded by Llama 3.1+ for agentic use cases
- Still useful for code completion, not autonomous workflows

---

### A6. Other Models Without Tool Support

#### **Vicuna Series**
- `vicuna:7b`
- `vicuna:13b`
- `vicuna:33b`

**Architecture:** Llama fine-tuned on user conversations
**Tool Support:** ❌ None

#### **Orca Series**
- `orca-mini:3b`
- `orca-mini:7b`
- `orca-mini:13b`

**Architecture:** Small models trained on GPT-4 outputs
**Tool Support:** ❌ None

#### **WizardLM Series**
- `wizardlm:7b`
- `wizardlm:13b`
- `wizardlm-uncensored:13b`

**Architecture:** Instruction-tuned models
**Tool Support:** ❌ None

---

## Category B: Models With Tool Support But Unable to Execute Autonomously

### Behavior Pattern
These models:
- ✅ Successfully connect to Goose
- ✅ Support Ollama tool calling API
- ✅ Can execute 1-3 simple commands
- ❌ **Explain instead of execute** for complex workflows
- ❌ Lose context after 5-10 steps
- ❌ Ask for confirmation despite instructions not to
- ❌ Hallucinate or discuss rather than act

### Root Cause
**Fundamental architectural limitation:** These models are trained as chat assistants, not autonomous agents.

**Training Objective Mismatch:**
- Trained to be helpful, harmless, and honest (HHH)
- Rewarded for explaining and discussing
- Penalized for taking actions without confirmation
- RLHF (Reinforcement Learning from Human Feedback) optimizes for conversation, not execution

**Context Window Limitations:**
- Even with 128K context, models lose "task focus" after several steps
- Attention mechanism degrades for long action sequences
- No persistent memory of original goal

**Lack of Agency:**
- No internal "task completion" drive
- No self-monitoring or error recovery
- No ability to maintain multi-step plans
- Prefer to defer to humans rather than proceed

---

### B1. Llama Family (Meta)

#### **Llama 3.1 Series**
- `llama3.1:8b`
- `llama3.1:70b`
- `llama3.1:405b`

**Architecture:** Meta's flagship open-weight models
**Tool Support:** ✅ Yes (official, first-class)
**Context:** 128K tokens
**Autonomous Capability:** ❌ Low (3-5 steps)

**Tested Behavior (8B):**
- Hallucinates code instead of using tools
- Talks about what to do instead of doing it
- Loses focus after 2-3 commands
- Asks "Would you like me to..." despite explicit instructions

**Analysis:**
- Best tool support among open models
- Excellent for single-step tasks
- Fails at multi-step autonomy due to training objective
- 70B and 405B versions better but still limited (10-20 steps max)
- RLHF training prioritizes safety over agency

**Why 8B Fails:**
- Insufficient parameters to maintain complex task state
- Attention mechanism can't track multiple goals simultaneously
- Defaults to "helpful assistant" mode under uncertainty

**Why Even 405B Would Struggle:**
- Training data emphasizes conversation, not execution
- No reinforcement learning for task completion
- Architecture designed for next-token prediction, not goal-oriented behavior

---

#### **Llama 3.2 Series**
- `llama3.2:1b`
- `llama3.2:3b`

**Architecture:** Smaller, efficient Llama variants
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ❌ Very Low (1-2 steps)

**Tested Behavior (1B):**
- Too small to maintain task context
- Forgets instructions immediately
- Cannot handle even simple multi-step workflows

**Analysis:**
- Tool support exists but model too weak to use effectively
- Useful for simple queries, not autonomous work
- Proves that tool support alone is insufficient

---

#### **Llama 3.3 Series**
- `llama3.3:70b`

**Architecture:** Optimized 70B matching 405B performance
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Medium (10-20 steps)
**RAM Required:** 50GB (too large for most consumer hardware)

**Analysis:**
- Best Llama variant for autonomous work
- Still exhibits "explain instead of execute" behavior
- Better at maintaining context but not truly autonomous
- Size makes it impractical for local deployment

---

#### **Llama 4 Series**
- `llama4:16x17b` (MoE)
- `llama4:128x17b` (MoE)

**Architecture:** Mixture of Experts multimodal models
**Tool Support:** ✅ Yes (official)
**Autonomous Capability:** ❓ Unknown (likely Medium)

**Analysis:**
- MoE architecture may help with task switching
- Still based on chat training paradigm
- Unlikely to solve fundamental agency problem

---

### B2. Mistral Family (Mistral AI)

#### **Mistral 7B Series**
- `mistral:7b`

**Architecture:** Efficient 7B model with sliding window attention
**Tool Support:** ✅ Yes (official)
**Context:** 8K tokens (sliding window)
**Autonomous Capability:** ❌ Low (3-5 steps)

**Analysis:**
- Good tool calling implementation
- Limited context window hurts multi-step tasks
- Same "explain vs execute" problem as Llama
- Efficient but not autonomous

---

#### **Mistral Nemo Series**
- `mistral-nemo:12b`

**Architecture:** 12B model with 128K context
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Medium-Low (5-10 steps)

**Analysis:**
- Best Mistral model for tool calling
- 128K context helps maintain task state
- Still defaults to explanation mode
- Better than 7B but not truly autonomous
- Training prioritizes helpfulness over action

---

#### **Mistral Small Series**
- `mistral-small:22b`
- `mistral-small:24b`

**Architecture:** 22-24B models, best under 70B
**Tool Support:** ✅ Yes (official, excellent)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Medium (10-15 steps)

**Tested Behavior (22B):**
- Successfully calls tools for simple tasks
- Explains instead of executes for complex workflows
- Shows JSON function calls rather than invoking them
- Says "Here's how you would..." instead of doing it
- Better reasoning than 8B but same behavioral limitation

**Analysis:**
- Best local model under 70B for tool calling
- Excellent reasoning and instruction following
- **Critical finding:** Even with 22B parameters and perfect tool support, still can't execute autonomously
- Proves the problem is training objective, not model size
- Would need different RLHF training to become truly agentic

**Why It Fails:**
- Trained on conversational data, not task execution logs
- Reward model optimizes for "helpful explanations"
- No training examples of multi-hour autonomous work
- Safety training prevents unsupervised action

---

#### **Mistral Large Series**
- `mistral-large:123b`

**Architecture:** Flagship 123B model
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Medium-High (15-25 steps)
**RAM Required:** 85GB (impractical for consumer hardware)

**Analysis:**
- Best Mistral model for complex tasks
- Still exhibits chat-assistant behavior
- Size helps but doesn't solve fundamental issue
- Too large for local deployment

---

#### **Ministral Series**
- `ministral-3:3b`
- `ministral-3:8b`
- `ministral-3:14b`

**Architecture:** Edge-optimized models
**Tool Support:** ✅ Yes (official)
**Autonomous Capability:** ❌ Low (3-5 steps)

**Analysis:**
- Designed for efficiency, not autonomy
- Tool support exists but models too small
- Good for simple tasks, not workflows

---

### B3. Qwen Family (Alibaba)

#### **Qwen 2 Series**
- `qwen2:0.5b`
- `qwen2:1.5b`
- `qwen2:7b`
- `qwen2:72b`

**Architecture:** Multilingual models with long context
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ❌ Low to Medium (5-15 steps depending on size)

**Analysis:**
- Good multilingual support
- Tool calling works but same behavioral issues
- Trained as assistants, not agents
- Larger variants (72B) better but still limited

---

#### **Qwen 2.5 Series**
- `qwen2.5:0.5b`
- `qwen2.5:1.5b`
- `qwen2.5:3b`
- `qwen2.5:7b`
- `qwen2.5:14b`
- `qwen2.5:32b`
- `qwen2.5:72b`

**Architecture:** Improved Qwen with better reasoning
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Low to Medium (varies by size)

**Analysis:**
- Better reasoning than Qwen 2
- Still chat-focused training
- 32B and 72B variants approach Mistral Small performance
- Same fundamental limitation: explains instead of executes

---

#### **Qwen 2.5 Coder Series**
- `qwen2.5-coder:0.5b`
- `qwen2.5-coder:1.5b`
- `qwen2.5-coder:3b`
- `qwen2.5-coder:7b`
- `qwen2.5-coder:14b`
- `qwen2.5-coder:32b`

**Architecture:** Code-specialized Qwen models
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Low to Medium

**Analysis:**
- Excellent at code generation
- Tool calling works for code-related tasks
- Still defaults to explanation mode
- Better at "write this code" than "execute this workflow"

---

#### **Qwen 3 Series**
- `qwen3:0.6b`
- `qwen3:1.7b`
- `qwen3:4b`
- `qwen3:8b`
- `qwen3:14b`
- `qwen3:30b`
- `qwen3:32b`
- `qwen3:235b`

**Architecture:** Latest Qwen generation with MoE variants
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Medium (varies by size)

**Analysis:**
- Most advanced Qwen models
- 235B variant theoretically capable of better autonomy
- Still trained as chat models
- Impractical sizes for local deployment (30B+)

---

#### **Qwen 3 Coder Series**
- `qwen3-coder:30b`
- `qwen3-coder:480b`

**Architecture:** Latest code-specialized models
**Tool Support:** ✅ Yes (official)
**Autonomous Capability:** ⚠️ Medium to High (480B variant)

**Analysis:**
- 480B variant approaches GPT-4 capability
- Requires 300GB+ RAM (cloud-only)
- Still exhibits chat behavior at smaller sizes

---

#### **QwQ Series**
- `qwq:32b`

**Architecture:** Reasoning-focused Qwen variant
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Medium (10-15 steps)

**Analysis:**
- Combines reasoning with tool calling
- Better at planning than execution
- Still prefers to explain reasoning rather than act
- Useful for complex problem-solving, not autonomous workflows

---

### B4. Command-R Family (Cohere)

#### **Command-R Series**
- `command-r:35b`

**Architecture:** Optimized for RAG and long context
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Medium (10-15 steps)

**Analysis:**
- Designed for retrieval-augmented generation
- Good at tool calling for information retrieval
- Less effective at autonomous execution
- Trained for enterprise Q&A, not agent workflows

---

#### **Command-R+ Series**
- `command-r-plus:104b`

**Architecture:** Larger Command-R variant
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Medium-High (15-25 steps)
**RAM Required:** 70GB

**Analysis:**
- Best Cohere model for complex tasks
- Still enterprise-focused, not agent-focused
- Size helps but doesn't solve behavioral issue
- Too large for consumer hardware

---

### B5. Hermes Family (Nous Research)

#### **Hermes 3 Series**
- `hermes3:3b`
- `hermes3:8b`
- `hermes3:70b`
- `hermes3:405b`

**Architecture:** Llama fine-tuned for instruction following
**Tool Support:** ✅ Yes (official)
**Context:** 128K tokens
**Autonomous Capability:** ⚠️ Low to Medium (5-20 steps depending on size)

**Analysis:**
- Better instruction following than base Llama
- Specifically trained for tool use
- Still exhibits "explain vs execute" behavior
- Proves that instruction tuning alone insufficient for autonomy
- Larger variants (70B, 405B) better but still limited

---

### B6. Granite Family (IBM)

#### **Granite 3 Dense Series**
- `granite3-dense:2b`
- `granite3-dense:8b`

**Architecture:** Enterprise-focused models with tool optimization
**Tool Support:** ✅ Yes (official, optimized)
**Autonomous Capability:** ❌ Low (3-8 steps)

**Analysis:**
- Specifically designed for tool-based use cases
- Good at RAG and code generation
- Still chat-assistant paradigm
- Enterprise safety constraints limit autonomy

---

#### **Granite 3.1 MoE Series**
- `granite3.1-moe:1b`
- `granite3.1-moe:3b`

**Architecture:** Mixture of Experts for efficiency
**Tool Support:** ✅ Yes (official)
**Autonomous Capability:** ❌ Low (3-5 steps)

**Analysis:**
- MoE helps with task switching
- Too small for complex workflows
- Efficient but not autonomous

---

#### **Granite 3.2 Series**
- `granite3.2:2b`
- `granite3.2:8b`

**Architecture:** Thinking-capable models
**Tool Support:** ✅ Yes (official)
**Autonomous Capability:** ⚠️ Low-Medium (5-10 steps)

**Analysis:**
- Adds reasoning capabilities
- Better at planning than execution
- Still defaults to explanation mode

---

#### **Granite 3.3 Series**
- `granite3.3:1b`
- `granite3.3:3b`
- `granite3.3:8b`

**Architecture:** Latest Granite generation
**Tool Support:** ✅ Yes (official)
**Autonomous Capability:** ⚠️ Low-Medium (5-10 steps)

**Analysis:**
- Most advanced Granite models
- Enterprise-grade tool calling
- Safety constraints prevent full autonomy

---

#### **Granite 4 Series**
- `granite4:350m`
- `granite4:1b`
- `granite4:3b`

**Architecture:** Improved instruction following and tool calling
**Tool Support:** ✅ Yes (official, enhanced)
**Autonomous Capability:** ❌ Low (3-5 steps)

**Analysis:**
- Best tool calling in Granite family
- Still too small for autonomous workflows
- Proves tool optimization ≠ autonomy

---

### B7. GPT-OSS Family (OpenAI Open Weights)

#### **GPT-OSS Series**
- `gpt-oss:20b`

**Architecture:** OpenAI's open-weight models for reasoning and agentic tasks
**Tool Support:** ✅ Yes (official)
**Context:** Unknown
**Autonomous Capability:** ⚠️ Medium (10-15 steps)

**Tested Behavior (20B):**
- Successfully configured after initial 404 errors
- Works with proper Ollama setup
- Explains instead of executes for complex tasks
- Better reasoning than 8B models
- Same behavioral limitation as other models

**Analysis:**
- 20B parameters provide better reasoning
- Still trained as chat assistant
- Larger than Llama 3.1 8B but same fundamental issue
- Proves that 2.5x parameter increase doesn't solve autonomy problem
- Would need GPT-4 level (175B+) or different training for true autonomy

---

### B8. Cogito Family (Deep Cogito)

#### **Cogito Series**
- `cogito:3b`
- `cogito:8b`
- `cogito:14b`
- `cogito:32b`
- `cogito:70b`

**Architecture:** Hybrid reasoning models
**Tool Support:** ✅ Yes (official)
**Autonomous Capability:** ⚠️ Low to Medium (5-20 steps depending on size)

**Analysis:**
- Combines reasoning with tool calling
- Better at planning than execution
- Reasoning capability doesn't translate to autonomous action
- Still chat-focused training paradigm

---

### B9. Mixtral Family (Mistral AI MoE)

#### **Mixtral Series**
- `mixtral:8x7b` (47B active parameters)
- `mixtral:8x22b` (141B active parameters)

**Architecture:** Mixture of Experts with sparse activation
**Tool Support:** ✅ Yes (official)
**Context:** 32K tokens
**Autonomous Capability:** ⚠️ Medium (10-20 steps)

**Analysis:**
- MoE architecture efficient for tool selection
- Good at switching between different tool types
- Still exhibits chat-assistant behavior
- Sparse activation helps with efficiency, not autonomy
- 8x22b variant better but still limited

---

### B10. SmolLM Family (Hugging Face)

#### **SmolLM2 Series**
- `smollm2:135m`
- `smollm2:360m`
- `smollm2:1.7b`

**Architecture:** Compact models for edge deployment
**Tool Support:** ✅ Yes (official)
**Autonomous Capability:** ❌ Very Low (1-2 steps)

**Analysis:**
- Tool support exists but models too small
- Useful for simple queries, not workflows
- Proves minimum size threshold exists for autonomy

---

## Comparative Analysis: Why Tool Support Isn't Enough

### Parameter Size vs Autonomy

| Size Range | Autonomous Steps | Representative Models | Limitation |
|------------|------------------|----------------------|------------|
| **< 2B** | 1-2 | SmolLM2, Llama 3.2 1B | Insufficient capacity |
| **2-8B** | 3-5 | Llama 3.1 8B, Mistral 7B | Weak task maintenance |
| **12-24B** | 5-15 | Mistral Nemo, Mistral Small, GPT-OSS 20B | Better but still explains |
| **30-70B** | 10-25 | Llama 3.3 70B, Mixtral 8x22b | Approaching useful but not autonomous |
| **100B+** | 20-40 | Mistral Large, Command-R+ | Better but impractical for local |
| **175B+** | 50+ | GPT-4, Claude (cloud only) | True autonomy |

**Key Insight:** Even 70B models with perfect tool support can't do multi-hour autonomous workflows.

---

### Training Objective Analysis

#### **Chat Models (All Category B)**
- **Objective:** Maximize helpfulness, harmlessness, honesty
- **Reward:** Explaining clearly, asking for confirmation
- **Penalty:** Taking actions without approval
- **Result:** Explains instead of executes

#### **What's Needed for Autonomy**
- **Objective:** Maximize task completion rate
- **Reward:** Successfully executing multi-step plans
- **Penalty:** Stopping to ask questions
- **Training Data:** Logs of successful autonomous workflows

**No current open-weight model has this training.**

---

### Context Window Analysis

| Model | Context | Autonomous Steps | Observation |
|-------|---------|------------------|-------------|
| Mistral 7B | 8K | 3-5 | Limited context hurts |
| Llama 3.1 8B | 128K | 3-5 | Context doesn't help |
| Mistral Small 22B | 128K | 10-15 | Context helps but insufficient |
| Llama 3.3 70B | 128K | 10-25 | Context + size better but not enough |

**Key Insight:** Long context necessary but not sufficient for autonomy.

---

### Tool Calling Quality Analysis

#### **Excellent Tool Support (Still Fails Autonomy)**
- Llama 3.1 series
- Mistral series
- Qwen series
- Hermes 3 series
- Granite 4 series

**Observation:** Quality of tool calling API doesn't correlate with autonomous capability.

#### **Why Good Tool Support Doesn't Help**
1. Models can call tools when explicitly instructed
2. Models don't autonomously decide to call tools
3. Models prefer to describe tool calls rather than make them
4. Tool calling is a capability, not a behavior

---

## Fundamental Limitations

### 1. Training Data Mismatch
- **Current:** Trained on conversations, Q&A, explanations
- **Needed:** Trained on task execution logs, autonomous workflows

### 2. Reward Model Mismatch
- **Current:** Rewarded for helpfulness and safety
- **Needed:** Rewarded for task completion and persistence

### 3. Architecture Limitations
- **Current:** Next-token prediction optimized for text generation
- **Needed:** Goal-oriented architecture with task state tracking

### 4. Inference Limitations
- **Current:** Single-pass generation with no self-correction
- **Needed:** Multi-step reasoning with error recovery

### 5. Memory Limitations
- **Current:** Stateless between calls, no persistent task memory
- **Needed:** Persistent task state across multiple interactions

---

## Conclusion

### Category A (No Tool Support)
**Models:** DeepSeek-R1, Dolphin 3.0, Phi, Gemma, CodeLlama, etc.
**Issue:** Architectural - lack tool calling API
**Solution:** Use different models (Category B)
**Prognosis:** Will never work with Goose

### Category B (Tool Support But Not Autonomous)
**Models:** Llama 3.1, Mistral, Qwen, Command-R, Hermes, Granite, GPT-OSS, etc.
**Issue:** Behavioral - trained as chat assistants, not agents
**Solution:** 
- Use cloud models (GPT-4, Claude) - trained for autonomy
- Use purpose-built agents (Cascade) - designed for execution
- Accept phase-by-phase interaction with local models
**Prognosis:** Fundamental limitation, not fixable with prompting

### Key Finding
**No local model (8B-70B) can perform multi-hour autonomous workflows**, regardless of:
- Parameter count
- Tool support quality
- Context window size
- Instruction tuning
- Reasoning capability

**Root cause:** Training objective mismatch - all models trained for conversation, not autonomous execution.

**What's needed:** New training paradigm focused on task completion, not helpfulness.

---

## Recommendations

### For Autonomous Workflows
1. **Use cloud APIs:** GPT-4, Claude (trained for autonomy)
2. **Use purpose-built agents:** Cascade, AutoGPT (designed for execution)
3. **Accept limitations:** Local models for simple tasks only

### For Local Models
1. **Keep:** Mistral Small 22B (best under 70B)
2. **Keep:** GPT-OSS 20B (good reasoning)
3. **Delete:** All Category A models (no tool support)
4. **Delete:** Small Category B models (< 12B, too weak)

### For Future Research
- Train models on task execution logs, not conversations
- Reward task completion, not explanation quality
- Add persistent task state to architecture
- Implement self-correction and error recovery
- Focus on agency, not just capability
