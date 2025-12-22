# Branch Strategy: LangChain vs Agent Kit Integration

**Date:** December 22, 2025  
**Objective:** Compare two different agent framework integrations while preserving main branch

---

## Branch Structure

```
main (current)
├── feature/langchain-integration (NEW)
└── feature/agentkit-integration (NEW)
```

### Branch Protection Strategy

**Main Branch:**
- ✅ Keep current hybrid approach (Custom LLM + Mem0 + LangChain Tools + Temporal)
- ✅ Production-ready and stable
- ✅ RAG benchmark: 66.6% pass rate
- ✅ No changes during experiment
- ✅ Ready to rollback anytime

**Experimental Branches:**
- 🧪 Test different integration patterns
- 🧪 Compare performance, complexity, maintainability
- 🧪 Benchmark against main branch
- 🧪 Merge winner back to main (or keep main if better)

---

## Branch 1: `feature/langchain-integration`

### Philosophy: "Full LangChain Ecosystem"

Embrace LangChain's opinionated patterns and rich ecosystem. Use LangChain's way of doing things.

### Unique Features to Implement

#### 1. **LangChain LLM Wrapper**
Replace direct OpenRouter calls with LangChain's LLM abstraction:

```python
# llm/langchain_client.py
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Any

class CustomLangChainLLM(LLM):
    """Wrap our custom LLM client as LangChain LLM"""
    
    custom_client: Any
    
    @property
    def _llm_type(self) -> str:
        return "custom_openrouter"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # Use our custom client but through LangChain interface
        return self.custom_client.generate(prompt, **kwargs)
```

**Benefits:**
- Access to LangChain callbacks and monitoring
- Compatible with all LangChain chains
- Streaming support via LangChain

---

#### 2. **LangChain RAG with LCEL (LangChain Expression Language)**

Replace Mem0 with LangChain's RAG patterns:

```python
# llm/langchain_rag.py
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate

# LangChain-style RAG chain
vectorstore = Qdrant(
    client=qdrant_client,
    collection_name="conversations",
    embeddings=OpenAIEmbeddings()
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# LCEL chain (LangChain's new syntax)
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Usage
response = rag_chain.invoke("where do I work?")
```

**Benefits:**
- Composable chains with `|` operator
- Built-in retry and fallback
- Automatic prompt management

---

#### 3. **LangChain Agents with ReAct Pattern**

Replace Temporal workflows with LangChain's agent patterns:

```python
# agents/langchain_agent.py
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool

# Define tools
harvest_tools = [
    Tool(
        name="get_time_entries",
        func=harvest_client.get_time_entries,
        description="Get time entries for a user"
    ),
    Tool(
        name="create_time_entry",
        func=harvest_client.create_time_entry,
        description="Create a new time entry"
    ),
    # ... 51 Harvest tools
]

# Create ReAct agent
agent = create_react_agent(
    llm=custom_langchain_llm,
    tools=harvest_tools,
    prompt=react_prompt
)

# Agent executor with memory
agent_executor = AgentExecutor(
    agent=agent,
    tools=harvest_tools,
    memory=ConversationBufferMemory(),
    verbose=True,
    max_iterations=5
)

# Usage
response = agent_executor.invoke({
    "input": "Log 8 hours for project X yesterday"
})
```

**Benefits:**
- Built-in reasoning traces
- Automatic tool selection
- Error handling and retries

---

#### 4. **LangChain Memory Management**

Use LangChain's conversation memory:

```python
# llm/langchain_memory.py
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory

# Short-term memory (conversation buffer)
conversation_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Long-term memory (vector store)
vector_memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    memory_key="context"
)

# Combined memory
from langchain.memory import CombinedMemory

memory = CombinedMemory(memories=[conversation_memory, vector_memory])
```

**Benefits:**
- Automatic conversation tracking
- Built-in memory summarization
- Easy integration with agents

---

#### 5. **LangChain Callbacks for Monitoring**

Add observability with LangChain callbacks:

```python
# monitoring/langchain_callbacks.py
from langchain.callbacks.base import BaseCallbackHandler

class CustomCallbackHandler(BaseCallbackHandler):
    """Track LLM calls, token usage, latency"""
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        logger.info(f"LLM started with {len(prompts)} prompts")
    
    def on_llm_end(self, response, **kwargs):
        logger.info(f"LLM finished: {response.llm_output}")
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        logger.info(f"Tool started: {serialized['name']}")
    
    def on_agent_action(self, action, **kwargs):
        logger.info(f"Agent action: {action.tool}")

# Usage
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[CustomCallbackHandler()]
)
```

**Benefits:**
- Detailed execution traces
- Token usage tracking
- Performance monitoring

---

#### 6. **LangChain Document Loaders**

Add document ingestion capabilities:

```python
# ingestion/langchain_loaders.py
from langchain.document_loaders import TextLoader, PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load and split documents
loader = TextLoader("company_policies.txt")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(documents)

# Store in vector database
vectorstore.add_documents(splits)
```

**Benefits:**
- Easy document ingestion
- Smart text splitting
- Multiple format support

---

### Architecture Changes for LangChain Branch

**File Structure:**
```
llm/
├── langchain_client.py       # NEW: LangChain LLM wrapper
├── langchain_rag.py          # NEW: LCEL RAG chains
├── langchain_memory.py       # NEW: LangChain memory
├── client.py                 # KEEP: Fallback to custom client
└── config.py                 # KEEP: Configuration

agents/
├── langchain_agent.py        # NEW: ReAct agent
├── langchain_tools.py        # NEW: Tool definitions
└── harvest_agent.py          # REMOVE: Replace with LangChain agent

workflows/
├── langchain_workflow.py     # NEW: Simplified workflow using agents
└── unified_workflows.py      # REMOVE: Replace with LangChain patterns

monitoring/
└── langchain_callbacks.py    # NEW: Observability
```

**Dependencies to Add:**
```txt
langchain==0.3.15
langchain-openai==0.3.0
langchain-community==0.3.15
langchain-qdrant==0.2.0
```

---

### Success Criteria for LangChain Branch

1. **RAG Performance:** ≥ 70% pass rate (better than main's 66.6%)
2. **Code Simplicity:** Fewer lines of code than main
3. **Maintainability:** Easier to understand for new developers
4. **Feature Richness:** More built-in features (streaming, callbacks, etc.)
5. **Ecosystem:** Easy to add new tools/integrations

---

## Branch 2: `feature/agentkit-integration`

### Philosophy: "Lightweight & Custom Control"

Minimal framework, maximum control. Keep custom architecture but add agent patterns.

### Unique Features to Implement

#### 1. **Agent Kit Core Integration**

Lightweight agent framework without heavy abstractions:

```python
# llm/agentkit_client.py
from agentkit import Agent, Tool, Context

class CustomAgentKitClient:
    """Minimal agent wrapper keeping custom LLM client"""
    
    def __init__(self, custom_client):
        self.llm = custom_client  # Keep our custom client as-is
        self.tools = []
    
    def add_tool(self, name: str, func: callable, description: str):
        """Register tools without heavy wrappers"""
        self.tools.append(Tool(
            name=name,
            func=func,
            description=description
        ))
    
    async def execute(self, prompt: str, context: Context) -> str:
        """Execute with tool calling"""
        # Agent Kit handles tool selection
        # But uses our custom LLM client directly
        return await self.llm.generate_with_tools(
            prompt=prompt,
            tools=self.tools,
            context=context
        )
```

**Benefits:**
- Keep custom client features (rate limiting, caching)
- Minimal abstraction overhead
- Full control over execution

---

#### 2. **Direct Mem0 Integration (Keep Current)**

Don't change RAG - Mem0 is already lightweight and good:

```python
# llm/memory.py (KEEP AS-IS)
# Agent Kit doesn't force memory patterns
# Keep Mem0 + Qdrant exactly as current main branch

class LLMMemoryManager:
    """Keep current Mem0 implementation"""
    # No changes needed
```

**Benefits:**
- Already working well
- Self-improving memory
- No migration needed

---

#### 3. **Agent Kit Tool Registry**

Simple tool registration without complex wrappers:

```python
# agents/agentkit_tools.py
from agentkit import ToolRegistry

registry = ToolRegistry()

# Register Harvest tools directly
@registry.tool(
    name="get_time_entries",
    description="Get time entries for a user"
)
async def get_time_entries(user_id: str, start_date: str, end_date: str):
    """Direct function - no wrapper needed"""
    return await harvest_client.get_time_entries(user_id, start_date, end_date)

# Register all 51 Harvest tools
@registry.tool(name="create_time_entry", description="...")
async def create_time_entry(project_id: str, hours: float, notes: str):
    return await harvest_client.create_time_entry(project_id, hours, notes)

# ... more tools
```

**Benefits:**
- Simple decorator pattern
- No abstraction layers
- Direct function calls

---

#### 4. **Agent Kit Multi-Agent Orchestration**

Lightweight multi-agent coordination:

```python
# agents/agentkit_orchestrator.py
from agentkit import Agent, Orchestrator

# Define specialized agents
harvest_agent = Agent(
    name="harvest_agent",
    llm=custom_client,
    tools=harvest_tools,
    system_prompt="You are a Harvest timesheet expert"
)

refinement_agent = Agent(
    name="refinement_agent",
    llm=custom_client,
    tools=[],
    system_prompt="You refine and improve responses"
)

quality_agent = Agent(
    name="quality_agent",
    llm=custom_client,
    tools=[],
    system_prompt="You validate response quality"
)

# Orchestrate agents (simpler than Temporal)
orchestrator = Orchestrator(agents=[
    harvest_agent,
    refinement_agent,
    quality_agent
])

# Execute workflow
result = await orchestrator.execute(
    input="Log 8 hours yesterday",
    workflow="sequential"  # or "parallel", "conditional"
)
```

**Benefits:**
- Simpler than Temporal workflows
- Built-in agent coordination
- Less infrastructure needed

---

#### 5. **Agent Kit Streaming**

Native streaming support:

```python
# llm/agentkit_streaming.py
from agentkit import StreamingAgent

agent = StreamingAgent(
    llm=custom_client,
    tools=tools
)

# Stream responses
async for chunk in agent.stream("What are my time entries?"):
    print(chunk, end="", flush=True)
```

**Benefits:**
- Real-time responses
- Better UX for long operations
- Native support (no custom implementation)

---

#### 6. **Agent Kit State Management**

Simple state tracking without external dependencies:

```python
# agents/agentkit_state.py
from agentkit import StateManager

# In-memory state (or Redis for production)
state = StateManager(backend="memory")

# Track conversation state
await state.set(f"user_{user_id}_context", {
    "last_query": "where do I work?",
    "last_response": "You work at Microsoft",
    "timestamp": datetime.now()
})

# Retrieve state
context = await state.get(f"user_{user_id}_context")
```

**Benefits:**
- No Temporal needed for state
- Simpler architecture
- Easy to understand

---

### Architecture Changes for Agent Kit Branch

**File Structure:**
```
llm/
├── agentkit_client.py        # NEW: Agent Kit wrapper
├── memory.py                 # KEEP: Mem0 (no changes)
├── client.py                 # KEEP: Custom LLM client
└── config.py                 # KEEP: Configuration

agents/
├── agentkit_orchestrator.py  # NEW: Multi-agent coordination
├── agentkit_tools.py         # NEW: Tool registry
├── harvest_agent.py          # MODIFY: Use Agent Kit
├── refinement_agent.py       # MODIFY: Use Agent Kit
├── quality_agent.py          # MODIFY: Use Agent Kit
└── notification_agent.py     # MODIFY: Use Agent Kit

workflows/
├── agentkit_workflow.py      # NEW: Simplified workflow
└── unified_workflows.py      # REMOVE: Replace with Agent Kit

state/
└── agentkit_state.py         # NEW: State management
```

**Dependencies to Add:**
```txt
agentkit==0.2.1
# Keep existing: mem0ai, qdrant-client, openai
```

---

### Success Criteria for Agent Kit Branch

1. **RAG Performance:** ≥ 66% pass rate (match or beat main)
2. **Code Simplicity:** Significantly fewer lines than main
3. **Performance:** Lower latency (less abstraction overhead)
4. **Maintainability:** Easy to debug and modify
5. **Custom Control:** Keep all custom features (rate limiting, caching, multi-tenant)

---

## Comparison Matrix

| Feature | Main Branch | LangChain Branch | Agent Kit Branch |
|---------|-------------|------------------|------------------|
| **LLM Client** | Custom | LangChain Wrapper | Custom (kept) |
| **RAG/Memory** | Mem0 + Qdrant | LangChain RAG | Mem0 + Qdrant (kept) |
| **Agent Pattern** | Custom | ReAct Agent | Agent Kit Agent |
| **Orchestration** | Temporal | LangChain Chains | Agent Kit Orchestrator |
| **Tools** | LangChain Tools | LangChain Tools | Agent Kit Tools |
| **Callbacks** | Custom | LangChain Callbacks | Agent Kit Events |
| **Streaming** | Custom | LangChain Streaming | Agent Kit Streaming |
| **State** | Temporal | LangChain Memory | Agent Kit State |
| **Dependencies** | Medium | Heavy | Light |
| **Abstraction** | Medium | High | Low |
| **Control** | High | Medium | Highest |
| **Ecosystem** | Mixed | Rich | Minimal |

---

## Implementation Plan

### Phase 1: Branch Setup (Day 1)

```bash
# Create branches from main
git checkout main
git pull origin main

# Create LangChain branch
git checkout -b feature/langchain-integration
git push -u origin feature/langchain-integration

# Create Agent Kit branch
git checkout main
git checkout -b feature/agentkit-integration
git push -u origin feature/agentkit-integration

# Protect main branch
# Set branch protection rules in GitHub/Azure DevOps
```

### Phase 2: LangChain Branch Implementation (Days 2-4)

**Day 2: Core Integration**
- [ ] Create `llm/langchain_client.py` - LLM wrapper
- [ ] Create `llm/langchain_rag.py` - LCEL RAG chains
- [ ] Update dependencies in `requirements.txt`
- [ ] Test basic LLM calls through LangChain

**Day 3: Agent & Tools**
- [ ] Create `agents/langchain_agent.py` - ReAct agent
- [ ] Convert 51 Harvest tools to LangChain Tool format
- [ ] Create `agents/langchain_tools.py` - Tool definitions
- [ ] Test tool calling through agent

**Day 4: Workflow & Memory**
- [ ] Create `workflows/langchain_workflow.py` - Replace Temporal
- [ ] Create `llm/langchain_memory.py` - Conversation memory
- [ ] Create `monitoring/langchain_callbacks.py` - Observability
- [ ] Run RAG benchmark on LangChain branch

### Phase 3: Agent Kit Branch Implementation (Days 5-7)

**Day 5: Core Integration**
- [ ] Create `llm/agentkit_client.py` - Lightweight wrapper
- [ ] Create `agents/agentkit_tools.py` - Tool registry
- [ ] Update dependencies in `requirements.txt`
- [ ] Test basic agent execution

**Day 6: Multi-Agent System**
- [ ] Create `agents/agentkit_orchestrator.py` - Coordination
- [ ] Modify existing agents to use Agent Kit
- [ ] Create `state/agentkit_state.py` - State management
- [ ] Test multi-agent workflows

**Day 7: Workflow & Testing**
- [ ] Create `workflows/agentkit_workflow.py` - Simplified workflow
- [ ] Add streaming support
- [ ] Run RAG benchmark on Agent Kit branch
- [ ] Performance testing

### Phase 4: Comparison & Decision (Days 8-9)

**Day 8: Benchmarking**
- [ ] Run RAG benchmark on all 3 branches
- [ ] Measure latency and performance
- [ ] Count lines of code
- [ ] Assess maintainability

**Day 9: Decision**
- [ ] Compare results against success criteria
- [ ] Team review and discussion
- [ ] Choose winning approach
- [ ] Plan merge strategy

---

## Benchmark Comparison Criteria

Run the same benchmark on all 3 branches:

```bash
# Main branch
git checkout main
./run_production_rag_benchmark.sh > results_main.txt

# LangChain branch
git checkout feature/langchain-integration
./run_production_rag_benchmark.sh > results_langchain.txt

# Agent Kit branch
git checkout feature/agentkit-integration
./run_production_rag_benchmark.sh > results_agentkit.txt

# Compare
python compare_benchmarks.py results_*.txt
```

### Metrics to Compare

1. **RAG Accuracy**
   - Pass rate
   - Precision
   - Recall

2. **Performance**
   - Average latency
   - Token usage
   - Memory consumption

3. **Code Quality**
   - Lines of code
   - Cyclomatic complexity
   - Test coverage

4. **Developer Experience**
   - Time to add new feature
   - Ease of debugging
   - Documentation quality

5. **Production Readiness**
   - Error handling
   - Monitoring capabilities
   - Scalability

---

## Rollback Strategy

If experiments fail, main branch is untouched:

```bash
# Always safe to return to main
git checkout main

# Delete experimental branches if needed
git branch -D feature/langchain-integration
git branch -D feature/agentkit-integration
```

**Main branch remains:**
- ✅ Production-ready
- ✅ RAG working (66.6% pass rate)
- ✅ All features functional
- ✅ No risk

---

## Decision Framework

After benchmarking, choose based on:

### Choose **LangChain** if:
- ✅ Pass rate > 75%
- ✅ Rich ecosystem is valuable
- ✅ Team wants standard patterns
- ✅ Need many integrations

### Choose **Agent Kit** if:
- ✅ Pass rate ≥ 66%
- ✅ Performance is critical
- ✅ Want maximum control
- ✅ Prefer lightweight solution

### Keep **Main** if:
- ✅ Neither branch beats main significantly
- ✅ Migration cost too high
- ✅ Current solution "good enough"
- ✅ Team prefers hybrid approach

---

## Next Steps

1. **Review this plan** - Confirm approach
2. **Create branches** - Set up git structure
3. **Start with LangChain** - Days 2-4
4. **Then Agent Kit** - Days 5-7
5. **Compare & decide** - Days 8-9

**Timeline:** ~2 weeks for complete comparison

**Risk:** Low (main branch protected)

**Reward:** Data-driven decision on best architecture

---

## Questions to Consider

Before starting:

1. **Team capacity:** Do we have 2 weeks for this experiment?
2. **Deployment:** Can we deploy experimental branches to test environments?
3. **Success threshold:** What pass rate makes a branch "better"?
4. **Feature parity:** Must experimental branches match all main features?
5. **Migration cost:** How much effort to migrate if we choose a new approach?

---

**Ready to proceed?** Let me know and I'll start creating the branches and implementing the first approach.
