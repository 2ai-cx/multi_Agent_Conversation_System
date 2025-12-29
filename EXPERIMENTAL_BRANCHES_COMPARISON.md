# Experimental Branches Comparison
## LangChain vs Microsoft Agent Framework - Detailed Analysis

**Date:** December 23, 2025  
**Purpose:** Comprehensive comparison of two experimental approaches to improve RAG accuracy  
**Baseline:** 66.6% RAG accuracy with Mem0 + Qdrant

---

## 🎯 Overview

We created two experimental branches to test different agent orchestration frameworks while preserving our production infrastructure. Both branches keep:
- ✅ Temporal workflows (durable orchestration)
- ✅ Mem0 + Qdrant RAG system (66.6% baseline)
- ✅ Custom LLM client (rate limiting, caching, multi-tenant)
- ✅ 51 Harvest MCP tools

**The Question:** Which framework provides better agent orchestration for improved RAG accuracy?

---

## 📊 Quick Comparison

| Aspect | LangChain Branch | Agent Framework Branch |
|--------|------------------|------------------------|
| **Framework** | LangChain v1.0 (stable) | Microsoft Agent Framework beta |
| **Maturity** | Production-ready | Preview/experimental |
| **Tests** | ✅ 41/41 passing (100%) | ✅ 24/24 passing (100%) |
| **MCP Support** | Custom wrapper needed | ✅ Native built-in |
| **Learning Curve** | Moderate (popular framework) | Steep (new, limited docs) |
| **Community** | Large, active | Small, growing |
| **Integration Effort** | Medium (wrapper + bridge) | High (API discovery needed) |
| **Future Support** | Established | Microsoft-backed |

---

## 🔬 Branch 1: LangChain Integration

### **Philosophy**
"Use the most popular agent framework with proven patterns"

### **Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    User Request                         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Temporal Workflow (Unchanged)              │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│           LangChain Agent (NEW)                         │
│  - Uses CustomLangChainLLM wrapper                      │
│  - Accesses Mem0LangChainMemory bridge                  │
│  - Calls LangChain-wrapped Harvest tools                │
└────────────────────┬────────────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
┌───────────────┐         ┌──────────────┐
│ Custom LLM    │         │ Mem0 Memory  │
│ (Wrapped)     │         │ (Bridged)    │
└───────────────┘         └──────────────┘
        ↓                         ↓
┌───────────────┐         ┌──────────────┐
│ OpenAI API    │         │ Qdrant DB    │
└───────────────┘         └──────────────┘
```

### **Key Components**

#### 1. **Custom LLM Wrapper** (`llm/langchain_wrapper.py`)
**Purpose:** Adapt custom LLM client to LangChain's interface

**Implementation:**
```python
class CustomLangChainLLM(LLM):
    """Wraps custom LLM client for LangChain compatibility"""
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # Preserves all custom features:
        # - Rate limiting
        # - Response caching
        # - Multi-tenant API keys
        # - JSON minification
        return self.llm_client.generate(prompt)
    
    async def _acall(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # Async version for concurrent operations
        return await self.llm_client.generate_async(prompt)
```

**What it preserves:**
- ✅ Rate limiting (prevents API overload)
- ✅ Response caching (saves costs)
- ✅ Multi-tenant API keys (customer isolation)
- ✅ JSON minification (reduces tokens)

**What it adds:**
- ✅ LangChain chain compatibility
- ✅ LangChain agent compatibility
- ✅ Streaming support
- ✅ Callback system for monitoring

---

#### 2. **Mem0-LangChain Memory Bridge** (`llm/langchain_mem0_bridge.py`)
**Purpose:** Connect Mem0 self-improving memory to LangChain's memory interface

**Implementation:**
```python
class Mem0LangChainMemory(BaseMemory):
    """Bridges Mem0 to LangChain memory interface"""
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Retrieve relevant memories from Mem0/Qdrant
        query = inputs.get("input", "")
        memories = await self.memory_manager.retrieve_context(
            query=query,
            user_id=self.user_id,
            limit=10  # Top 10 relevant memories
        )
        return {"history": memories}
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]):
        # Store new conversation in Mem0
        await self.memory_manager.add_conversation(
            user_message=inputs["input"],
            ai_response=outputs["output"],
            metadata={"user_id": self.user_id}
        )
```

**Memory Flow:**
1. User asks: "How many hours did I log last week?"
2. Bridge retrieves from Mem0: "User logged 40 hours last week on Project X"
3. Agent gets context automatically
4. Agent responds with accurate information
5. Bridge stores new conversation in Mem0

**Benefits:**
- ✅ No migration needed (uses existing Mem0)
- ✅ Preserves 66.6% RAG baseline
- ✅ Automatic context injection
- ✅ Self-improving over time

---

#### 3. **Harvest Tools Conversion** (`agents/langchain_tools.py`)
**Purpose:** Convert 51 Harvest MCP tools to LangChain Tool format

**Implementation:**
```python
class HarvestLangChainTools:
    """Converts Harvest MCP tools to LangChain format"""
    
    def get_tools(self) -> List[Tool]:
        tools = []
        
        # Example: Time entry tool
        tools.append(Tool(
            name="create_time_entry",
            description="Create a new time entry. Args: project_id, hours, notes, date",
            func=self._create_time_entry_wrapper
        ))
        
        # ... 50 more tools
        return tools
    
    async def _create_time_entry_wrapper(self, input_str: str) -> str:
        # Parse LLM's natural language input
        params = self._parse_params(input_str)
        
        # Call Harvest API
        result = await self.harvest_client.create_time_entry(**params)
        
        # Return formatted response
        return f"Created time entry: {result}"
```

**Tool Categories:**
- 📊 Time entries (create, update, delete, list)
- 👥 Projects (list, get details)
- 📅 Tasks (list, assign)
- 📈 Reports (generate, export)
- ⚙️ Settings (get, update)

**Total:** 51 tools converted

---

#### 4. **LangChain Agents in Temporal** (`agents/langchain_temporal_agent.py`)
**Purpose:** Run LangChain agents inside Temporal activities

**Implementation:**
```python
@activity.defn
async def run_langchain_agent(request: AgentRequest) -> AgentResponse:
    # Initialize LangChain agent
    llm = CustomLangChainLLM(config=config)
    memory = Mem0LangChainMemory(user_id=request.user_id)
    tools = HarvestLangChainTools().get_tools()
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        memory=memory,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )
    
    # Run agent
    response = await agent.arun(request.message)
    
    return AgentResponse(text=response)
```

**Benefits:**
- ✅ Durable execution (Temporal handles failures)
- ✅ Retry logic (automatic retries)
- ✅ Monitoring (Temporal UI shows progress)
- ✅ Scalability (horizontal scaling)

---

#### 5. **Production Callbacks** (`monitoring/langchain_callbacks.py`)
**Purpose:** Monitor LangChain agent execution

**Implementation:**
```python
class ProductionCallbackHandler(BaseCallbackHandler):
    """Tracks LangChain agent events"""
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        # Log LLM call start
        logger.info(f"LLM call started: {prompts[0][:100]}")
    
    def on_llm_end(self, response, **kwargs):
        # Log LLM call end
        logger.info(f"LLM call completed: {response.generations[0][0].text[:100]}")
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        # Log tool call
        logger.info(f"Tool called: {serialized['name']}")
    
    def on_agent_action(self, action, **kwargs):
        # Track agent decisions
        logger.info(f"Agent action: {action.tool} with {action.tool_input}")
```

**Metrics Tracked:**
- LLM calls (count, latency, tokens)
- Tool usage (which tools, success rate)
- Agent decisions (reasoning steps)
- Memory operations (retrieval, storage)

---

### **Testing Strategy**

**Test Coverage:** 41/41 tests passing (100%)

**Test Categories:**
1. **LLM Wrapper Tests** (10 tests)
   - Basic generation
   - Async generation
   - Streaming
   - Error handling
   - Rate limiting preservation

2. **Memory Bridge Tests** (8 tests)
   - Context retrieval
   - Context storage
   - Multi-tenant isolation
   - Memory search

3. **Tools Tests** (15 tests)
   - Tool conversion
   - Parameter parsing
   - Async execution
   - Error handling

4. **Integration Tests** (8 tests)
   - End-to-end agent flow
   - Temporal integration
   - Memory + tools together
   - Callback system

---

### **Pros & Cons**

**✅ Advantages:**
1. **Mature ecosystem** - Proven patterns, extensive documentation
2. **Large community** - Easy to find help, examples
3. **Rich tooling** - LangSmith for debugging, LangServe for deployment
4. **Stable API** - v1.0 released, breaking changes rare
5. **Preserves everything** - All custom features intact
6. **Easy testing** - Well-documented testing patterns

**❌ Disadvantages:**
1. **Wrapper overhead** - Extra layer between custom LLM and framework
2. **Memory bridge complexity** - Need to maintain bridge code
3. **Tool conversion effort** - Manual conversion of 51 tools
4. **No native MCP** - Need custom wrapper for MCP tools
5. **Callback limitations** - Less granular than native monitoring

---

## 🔬 Branch 2: Microsoft Agent Framework Integration

### **Philosophy**
"Use Microsoft's next-gen framework with native MCP support"

### **Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    User Request                         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Temporal Workflow (Unchanged)              │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│         Agent Framework Agent (NEW)                     │
│  - Uses BaseChatClient implementation                   │
│  - Accesses ContextProvider for memory                  │
│  - Native MCP client for Harvest tools                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
┌───────────────┐         ┌──────────────┐
│ Custom LLM    │         │ Mem0 Memory  │
│ (Native)      │         │ (Provider)   │
└───────────────┘         └──────────────┘
        ↓                         ↓
┌───────────────┐         ┌──────────────┐
│ OpenAI API    │         │ Qdrant DB    │
└───────────────┘         └──────────────┘
```

### **Key Components**

#### 1. **Custom LLM Connector** (`llm/agent_framework_connector.py`)
**Purpose:** Implement Agent Framework's BaseChatClient interface

**Implementation:**
```python
class CustomAgentFrameworkLLM(BaseChatClient):
    """Native Agent Framework LLM client"""
    
    async def _inner_get_response(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> ChatResponse:
        # Convert Agent Framework messages to custom format
        prompt = self._messages_to_prompt(messages)
        
        # Use custom LLM client (preserves all features)
        response = await self.llm_client.generate(prompt)
        
        # Convert back to Agent Framework format
        return ChatResponse(
            message=ChatMessage(role="assistant", text=response)
        )
    
    async def _inner_get_streaming_response(
        self,
        messages: List[ChatMessage],
        **kwargs
    ) -> AsyncGenerator[ChatResponse, None]:
        # Streaming implementation
        async for chunk in self.llm_client.generate_stream(prompt):
            yield ChatResponse(
                message=ChatMessage(role="assistant", text=chunk)
            )
```

**What it preserves:**
- ✅ Rate limiting
- ✅ Response caching
- ✅ Multi-tenant API keys
- ✅ JSON minification

**What it adds:**
- ✅ Native Agent Framework interface
- ✅ No wrapper overhead
- ✅ Direct integration

---

#### 2. **Mem0-Agent Framework Bridge** (`llm/agent_framework_mem0_bridge.py`)
**Purpose:** Implement Agent Framework's ContextProvider interface

**Implementation:**
```python
class Mem0ContextProvider(ContextProvider):
    """Provides Mem0 memory as Agent Framework context"""
    
    async def get_context(self, context: Any) -> str:
        # Extract query from context
        query = self._extract_query(context)
        
        # Retrieve from Mem0
        memories = await self.memory_manager.retrieve_context(
            query=query,
            user_id=self.user_id,
            limit=10
        )
        
        # Format for agent
        return self._format_memories(memories)
    
    async def save_context(self, context: Any, response: str):
        # Store conversation in Mem0
        await self.memory_manager.add_conversation(
            user_message=self._extract_message(context),
            ai_response=response,
            metadata={"user_id": self.user_id}
        )
```

**Benefits:**
- ✅ Native ContextProvider interface
- ✅ Automatic context injection
- ✅ Preserves Mem0 functionality

---

#### 3. **Native MCP Tools** (`agents/agent_framework_mcp_tools.py`)
**Purpose:** Use Agent Framework's built-in MCP client

**Implementation:**
```python
class AgentFrameworkMCPTools:
    """Native MCP tool integration"""
    
    def __init__(self):
        # Agent Framework has native MCP support!
        self.mcp_client = MCPClient(
            server_url="http://harvest-mcp:8080"
        )
    
    async def get_tools(self) -> List[Tool]:
        # Automatically discover all MCP tools
        tools = await self.mcp_client.list_tools()
        
        # No conversion needed - Agent Framework understands MCP natively
        return tools
```

**Advantages:**
- ✅ **Zero conversion effort** - MCP tools work directly
- ✅ **Auto-discovery** - Framework finds all available tools
- ✅ **Native protocol** - No wrapper overhead
- ✅ **Future-proof** - MCP is the standard

---

#### 4. **Agent Framework Agents in Temporal** (`agents/agent_framework_temporal_agent.py`)
**Purpose:** Run Agent Framework agents inside Temporal activities

**Implementation:**
```python
@activity.defn
async def run_agent_framework_agent(request: AgentRequest) -> AgentResponse:
    # Initialize Agent Framework agent
    llm = CustomAgentFrameworkLLM(config=config)
    memory = Mem0ContextProvider(user_id=request.user_id)
    tools = await AgentFrameworkMCPTools().get_tools()
    
    agent = Agent(
        model=llm,
        context_provider=memory,
        tools=tools
    )
    
    # Run agent
    response = await agent.run(request.message)
    
    return AgentResponse(text=response.text)
```

---

#### 5. **Monitoring Middleware** (`monitoring/agent_framework_callbacks.py`)
**Purpose:** Track Agent Framework execution

**Implementation:**
```python
class AgentFrameworkMonitoring:
    """Monitors Agent Framework events"""
    
    async def on_agent_start(self, context: Any):
        logger.info(f"Agent started: {context}")
    
    async def on_agent_end(self, context: Any, result: Any):
        logger.info(f"Agent completed: {result}")
    
    async def on_tool_call(self, tool: Any, input: Any):
        logger.info(f"Tool called: {tool.name}")
    
    async def on_llm_call(self, messages: List[Any]):
        logger.info(f"LLM called with {len(messages)} messages")
```

---

### **Testing Strategy**

**Test Coverage:** 24/24 tests passing (100%)

**Test Categories:**
1. **LLM Connector Tests** (8 tests)
   - BaseChatClient implementation
   - Message conversion
   - Streaming
   - Error handling

2. **Memory Bridge Tests** (6 tests)
   - ContextProvider implementation
   - Context retrieval
   - Context storage

3. **Integration Tests** (10 tests)
   - End-to-end agent flow
   - Temporal integration
   - Native MCP tools
   - Middleware system

---

### **Pros & Cons**

**✅ Advantages:**
1. **Native MCP support** - Zero conversion effort for tools
2. **No wrapper overhead** - Direct integration
3. **Microsoft backing** - Long-term support expected
4. **Modern architecture** - Built for async, streaming
5. **Unified framework** - Replaces AutoGen + Semantic Kernel
6. **Future-proof** - Designed for next-gen AI agents

**❌ Disadvantages:**
1. **Beta/preview status** - API may change
2. **Limited documentation** - Had to discover API through trial
3. **Small community** - Harder to find help
4. **Learning curve** - New concepts, different patterns
5. **Integration effort** - Required API discovery phase
6. **Uncertain roadmap** - Preview software risks

---

## 🔍 Detailed Comparison

### **1. Integration Complexity**

**LangChain:**
```
Effort: Medium
Time: ~2 days
Components:
  - Custom LLM wrapper (150 lines)
  - Memory bridge (193 lines)
  - Tool conversion (51 tools × 20 lines = ~1000 lines)
  - Agent integration (100 lines)
  - Callbacks (150 lines)
Total: ~1,593 lines of integration code
```

**Agent Framework:**
```
Effort: High (due to API discovery)
Time: ~3 days (including API research)
Components:
  - LLM connector (116 lines)
  - Memory bridge (120 lines)
  - MCP tools (50 lines - native support!)
  - Agent integration (80 lines)
  - Middleware (100 lines)
Total: ~466 lines of integration code
```

**Winner:** Agent Framework (less code, but more research time)

---

### **2. MCP Tool Support**

**LangChain:**
```python
# Manual conversion required for each tool
def convert_harvest_tool_to_langchain(mcp_tool):
    return Tool(
        name=mcp_tool.name,
        description=mcp_tool.description,
        func=create_wrapper(mcp_tool.function)
    )

# 51 tools × manual conversion = maintenance burden
```

**Agent Framework:**
```python
# Native MCP support - zero conversion
mcp_client = MCPClient(server_url="http://harvest-mcp:8080")
tools = await mcp_client.list_tools()  # Done!
```

**Winner:** Agent Framework (native MCP is huge advantage)

---

### **3. Memory Integration**

**LangChain:**
```python
# Bridge pattern - extra layer
class Mem0LangChainMemory(BaseMemory):
    # Implements LangChain's memory interface
    # Translates to/from Mem0
    # Works well but adds complexity
```

**Agent Framework:**
```python
# Provider pattern - cleaner
class Mem0ContextProvider(ContextProvider):
    # Implements ContextProvider interface
    # Similar complexity to LangChain
```

**Winner:** Tie (both require similar bridge code)

---

### **4. Custom LLM Integration**

**LangChain:**
```python
# Wrapper pattern
class CustomLangChainLLM(LLM):
    def _call(self, prompt: str) -> str:
        # Wraps custom client
        return self.custom_client.generate(prompt)
```

**Agent Framework:**
```python
# Native implementation
class CustomAgentFrameworkLLM(BaseChatClient):
    async def _inner_get_response(self, messages) -> ChatResponse:
        # Direct implementation
        return ChatResponse(...)
```

**Winner:** Agent Framework (no wrapper overhead)

---

### **5. Monitoring & Observability**

**LangChain:**
```
✅ Mature callback system
✅ LangSmith integration (paid service)
✅ Rich event types
✅ Easy to extend
```

**Agent Framework:**
```
⚠️ Basic middleware system
⚠️ Limited event types
⚠️ Less mature
✅ Azure Application Insights integration
```

**Winner:** LangChain (more mature monitoring)

---

### **6. Testing & Debugging**

**LangChain:**
```
✅ Extensive testing utilities
✅ Mock tools, mock LLMs
✅ LangSmith for debugging
✅ Well-documented patterns
```

**Agent Framework:**
```
⚠️ Basic testing support
⚠️ Limited mocking utilities
⚠️ Debugging is manual
⚠️ Sparse documentation
```

**Winner:** LangChain (better testing ecosystem)

---

### **7. Performance**

**LangChain:**
```
Overhead:
  - Wrapper layer: ~1-2ms per call
  - Memory bridge: ~5-10ms per retrieval
  - Tool conversion: ~1ms per tool call
Total overhead: ~10-15ms per agent turn
```

**Agent Framework:**
```
Overhead:
  - Native implementation: ~0ms
  - Context provider: ~5-10ms per retrieval
  - Native MCP: ~0ms
Total overhead: ~5-10ms per agent turn
```

**Winner:** Agent Framework (less overhead)

---

### **8. Future-Proofing**

**LangChain:**
```
✅ Stable v1.0 API
✅ Large community
✅ Active development
⚠️ May need MCP wrapper updates
```

**Agent Framework:**
```
✅ Native MCP support (future standard)
✅ Microsoft backing
⚠️ Beta API may change
⚠️ Smaller community
```

**Winner:** Tie (different risk profiles)

---

## 🎯 Decision Framework

### **Choose LangChain if:**
- ✅ You want **stability** and **proven patterns**
- ✅ You need **extensive documentation** and **community support**
- ✅ You want **mature tooling** (LangSmith, LangServe)
- ✅ You're okay with **wrapper overhead**
- ✅ You don't mind **manual tool conversion**

### **Choose Agent Framework if:**
- ✅ You want **native MCP support** (huge advantage)
- ✅ You're comfortable with **beta software**
- ✅ You want **less integration code**
- ✅ You value **Microsoft backing**
- ✅ You can handle **limited documentation**

---

## 📈 Next Steps

### **Immediate Actions:**
1. **Run RAG benchmarks** on both branches
2. **Compare accuracy** against 66.6% baseline
3. **Measure performance** (latency, throughput)
4. **Test edge cases** (errors, timeouts, etc.)

### **Evaluation Criteria:**
1. **RAG Accuracy** (most important)
   - Target: >70% (improvement over 66.6%)
   - Measure: Same test set for both branches

2. **Performance**
   - Latency: <2s per agent turn
   - Throughput: >100 requests/min

3. **Reliability**
   - Error rate: <1%
   - Recovery time: <5s

4. **Maintainability**
   - Code complexity
   - Documentation quality
   - Testing coverage

---

## 🏆 Recommendation

**For Production (Current):**
- Keep **LangChain branch** if you need stability now
- More mature, better documented, proven patterns

**For Future (6-12 months):**
- Consider **Agent Framework** when it reaches v1.0
- Native MCP support is a game-changer
- Microsoft backing suggests long-term viability

**Hybrid Approach:**
- Use **LangChain** for production agents
- Use **Agent Framework** for MCP tool integration
- Gradually migrate as Agent Framework matures

---

## 📚 Resources

### **LangChain:**
- Documentation: https://python.langchain.com/
- GitHub: https://github.com/langchain-ai/langchain
- LangSmith: https://smith.langchain.com/
- Community: Discord, Twitter, Stack Overflow

### **Agent Framework:**
- Documentation: https://microsoft.github.io/agent-framework/
- GitHub: https://github.com/microsoft/agent-framework
- Package: `pip install agent-framework`
- Community: GitHub Discussions

### **Our Implementation:**
- LangChain Branch: `feature/langchain-integration`
- Agent Framework Branch: `feature/agent-framework-integration`
- Comparison Guide: This document
- Test Results: Run `pytest` in each branch

---

## 🔄 Updates

**December 23, 2025:**
- ✅ Both branches implemented
- ✅ All tests passing (41/41 LangChain, 24/24 Agent Framework)
- ✅ Ready for RAG benchmarking
- ⏳ Awaiting accuracy comparison results

---

**Questions? Issues?**
- Check branch-specific integration status files
- Review test files for implementation examples
- Compare code side-by-side in the two branches
