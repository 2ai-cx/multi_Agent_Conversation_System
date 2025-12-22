# Revised Branch Strategy: LangChain vs Microsoft Semantic Kernel

**Date:** December 22, 2025  
**Objective:** Compare LangChain and Microsoft Semantic Kernel (Agent Kit) while preserving main branch  
**Timeline:** Quality over speed - thorough implementation and testing

---

## User Requirements Confirmed

1. ✅ **Framework:** Microsoft Semantic Kernel (not generic "Agent Kit")
2. ✅ **Keep Temporal:** Maintain workflow orchestration for reliability
3. ✅ **Keep Mem0:** Maintain current RAG system (66.6% pass rate)
4. ✅ **Timeline:** Take time for quality implementation
5. ✅ **Goal:** Compare two approaches with comprehensive monitoring

---

## Branch Structure

```
main (current - PROTECTED)
├── feature/langchain-integration (NEW)
└── feature/semantic-kernel-integration (NEW)
```

### What Stays the Same (All Branches)

**Core Infrastructure (NO CHANGES):**
- ✅ **Temporal Workflows** - Durable execution, retry logic, reliability
- ✅ **Mem0 + Qdrant** - RAG system (already working at 66.6%)
- ✅ **Custom LLM Client** - Rate limiting, caching, multi-tenant keys
- ✅ **Azure Container Apps** - Deployment infrastructure
- ✅ **Twilio Integration** - SMS/WhatsApp webhooks
- ✅ **Harvest MCP** - 51 timesheet tools

**What Changes:**
- 🔄 **Agent orchestration layer** - How agents coordinate
- 🔄 **Tool calling patterns** - How tools are registered and invoked
- 🔄 **Prompt management** - How prompts are structured
- 🔄 **Monitoring/observability** - How we track execution

---

## Microsoft Semantic Kernel Overview

### What is Semantic Kernel?

**Microsoft's official agent framework** for building AI applications:
- Open source (MIT license)
- Cross-platform (Python, C#, Java)
- Enterprise-ready
- Native Azure integration
- Plugin architecture

### Key Features

1. **Kernel** - Central orchestration engine
2. **Plugins** - Reusable functions (like LangChain tools)
3. **Planners** - Automatic task decomposition
4. **Memory** - Built-in semantic memory (can use Qdrant)
5. **Connectors** - Native OpenAI, Azure OpenAI, etc.

### Why Consider It?

- ✅ Microsoft-backed (good for enterprise)
- ✅ Native Azure integration
- ✅ Lighter than LangChain
- ✅ Strong typing and structure
- ✅ Built-in planning capabilities

---

## Branch 1: `feature/langchain-integration`

### Philosophy: "Rich Ecosystem & Community"

Leverage LangChain's mature ecosystem while keeping core infrastructure.

### Architecture

```python
# High-level flow
Temporal Workflow
  └─> LangChain Agent (inside Temporal activity)
        ├─> Custom LLM Client (wrapped in LangChain interface)
        ├─> LangChain Tools (51 Harvest tools)
        ├─> Mem0 Memory (accessed via LangChain memory interface)
        └─> LangChain Callbacks (monitoring)
```

### Key Components

#### 1. **LangChain LLM Wrapper** (Keep Custom Client)

```python
# llm/langchain_wrapper.py
from langchain.llms.base import LLM
from llm.client import LLMClient

class CustomLangChainLLM(LLM):
    """Wrap our custom client to use LangChain features"""
    
    def __init__(self, custom_client: LLMClient):
        super().__init__()
        self.client = custom_client
    
    @property
    def _llm_type(self) -> str:
        return "custom_openrouter"
    
    def _call(self, prompt: str, stop=None, **kwargs) -> str:
        # Use our custom client (keeps rate limiting, caching)
        return self.client.generate(prompt, **kwargs)
    
    async def _acall(self, prompt: str, stop=None, **kwargs) -> str:
        return await self.client.generate_async(prompt, **kwargs)
```

**Benefits:**
- Keep custom features (rate limiting, multi-tenant, caching)
- Access LangChain ecosystem
- Streaming via LangChain

---

#### 2. **LangChain Agent in Temporal Activity**

```python
# agents/langchain_temporal_agent.py
from temporalio import activity
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory

@activity.defn
async def langchain_agent_activity(input_data: dict) -> dict:
    """LangChain agent running inside Temporal activity"""
    
    # Initialize LangChain components
    llm = CustomLangChainLLM(custom_client)
    
    # Use LangChain tools
    tools = [
        Tool(name="get_time_entries", func=harvest.get_time_entries),
        Tool(name="create_time_entry", func=harvest.create_time_entry),
        # ... 51 tools
    ]
    
    # Create ReAct agent
    agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)
    
    # Agent executor with callbacks
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=ConversationBufferMemory(),
        callbacks=[CustomCallback()],
        max_iterations=5
    )
    
    # Execute (inside Temporal activity - gets retry, timeout, etc.)
    result = await executor.ainvoke({"input": input_data["message"]})
    
    return result
```

**Benefits:**
- Temporal handles reliability (retries, timeouts)
- LangChain handles agent logic (tool selection, reasoning)
- Best of both worlds

---

#### 3. **Mem0 Integration with LangChain**

```python
# llm/langchain_mem0_bridge.py
from langchain.memory import BaseMemory
from llm.memory import LLMMemoryManager

class Mem0LangChainMemory(BaseMemory):
    """Bridge Mem0 to LangChain memory interface"""
    
    def __init__(self, mem0_manager: LLMMemoryManager):
        self.mem0 = mem0_manager
    
    @property
    def memory_variables(self) -> List[str]:
        return ["context", "chat_history"]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Retrieve from Mem0
        context = await self.mem0.retrieve_context(
            query=inputs.get("input", ""),
            k=10
        )
        return {"context": context}
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]):
        # Store in Mem0
        await self.mem0.add_conversation(
            user_message=inputs["input"],
            ai_response=outputs["output"]
        )
```

**Benefits:**
- Keep Mem0's self-improving memory
- Use LangChain's memory interface
- No migration needed

---

#### 4. **LangChain Callbacks for Monitoring**

```python
# monitoring/langchain_monitoring.py
from langchain.callbacks.base import BaseCallbackHandler
import logging

class ProductionCallbackHandler(BaseCallbackHandler):
    """Track execution for monitoring"""
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        logger.info(f"🤖 LLM started: {len(prompts)} prompts")
        # Track in Azure Application Insights
        track_metric("llm_calls", 1)
    
    def on_llm_end(self, response, **kwargs):
        tokens = response.llm_output.get("token_usage", {})
        logger.info(f"✅ LLM finished: {tokens}")
        track_metric("tokens_used", tokens.get("total_tokens", 0))
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "unknown")
        logger.info(f"🔧 Tool started: {tool_name}")
        track_metric(f"tool_{tool_name}", 1)
    
    def on_agent_action(self, action, **kwargs):
        logger.info(f"🎯 Agent action: {action.tool} - {action.tool_input}")
    
    def on_agent_finish(self, finish, **kwargs):
        logger.info(f"🏁 Agent finished: {finish.return_values}")
```

**Benefits:**
- Detailed execution traces
- Token usage tracking
- Tool usage analytics
- Easy Azure integration

---

### File Structure Changes

```
llm/
├── langchain_wrapper.py      # NEW: LangChain LLM wrapper
├── langchain_mem0_bridge.py  # NEW: Mem0 <-> LangChain bridge
├── client.py                 # KEEP: Custom LLM client
├── memory.py                 # KEEP: Mem0 manager
└── config.py                 # KEEP: Configuration

agents/
├── langchain_temporal_agent.py  # NEW: LangChain agent in Temporal
├── langchain_tools.py           # NEW: Tool definitions
├── harvest_agent.py             # MODIFY: Use LangChain
├── refinement_agent.py          # MODIFY: Use LangChain
├── quality_agent.py             # MODIFY: Use LangChain
└── notification_agent.py        # KEEP: No changes

workflows/
├── unified_workflows.py      # MODIFY: Call LangChain activities
└── (no new files)            # Keep Temporal workflows

monitoring/
└── langchain_monitoring.py   # NEW: Callbacks and tracking
```

### Dependencies to Add

```txt
# LangChain core
langchain==0.3.15
langchain-openai==0.3.0
langchain-community==0.3.15

# Keep existing
mem0ai==1.0.1
qdrant-client==1.16.1
temporalio==1.7.1
```

---

## Branch 2: `feature/semantic-kernel-integration`

### Philosophy: "Microsoft Native & Lightweight"

Use Microsoft's official agent framework with native Azure integration.

### Architecture

```python
# High-level flow
Temporal Workflow
  └─> Semantic Kernel Agent (inside Temporal activity)
        ├─> Custom LLM Client (via SK connector)
        ├─> SK Plugins (51 Harvest tools)
        ├─> Mem0 Memory (via SK memory connector)
        └─> SK Telemetry (monitoring)
```

### Key Components

#### 1. **Semantic Kernel with Custom LLM**

```python
# llm/semantic_kernel_connector.py
import semantic_kernel as sk
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from llm.client import LLMClient

class CustomSKConnector(ChatCompletionClientBase):
    """Connect our custom LLM client to Semantic Kernel"""
    
    def __init__(self, custom_client: LLMClient):
        self.client = custom_client
    
    async def complete_chat_async(
        self,
        messages: List[Dict[str, str]],
        settings: ChatRequestSettings
    ) -> str:
        # Convert SK messages to our format
        prompt = self._messages_to_prompt(messages)
        
        # Use our custom client (keeps all features)
        response = await self.client.generate_async(prompt)
        
        return response
    
    def _messages_to_prompt(self, messages: List[Dict]) -> str:
        # Convert SK message format to single prompt
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])
```

**Benefits:**
- Keep custom client features
- Use SK's planning and orchestration
- Native Azure telemetry

---

#### 2. **Semantic Kernel Plugins (Tools)**

```python
# agents/semantic_kernel_plugins.py
import semantic_kernel as sk
from semantic_kernel.skill_definition import sk_function

class HarvestPlugin:
    """Harvest tools as Semantic Kernel plugin"""
    
    @sk_function(
        description="Get time entries for a user",
        name="get_time_entries"
    )
    async def get_time_entries(
        self,
        user_id: str,
        start_date: str,
        end_date: str
    ) -> str:
        """Get time entries from Harvest"""
        result = await harvest_client.get_time_entries(user_id, start_date, end_date)
        return json.dumps(result)
    
    @sk_function(
        description="Create a new time entry",
        name="create_time_entry"
    )
    async def create_time_entry(
        self,
        project_id: str,
        hours: float,
        notes: str
    ) -> str:
        """Create time entry in Harvest"""
        result = await harvest_client.create_time_entry(project_id, hours, notes)
        return json.dumps(result)
    
    # ... 49 more functions (51 total)
```

**Benefits:**
- Clean decorator syntax
- Type hints and validation
- Automatic function discovery

---

#### 3. **Semantic Kernel Agent in Temporal**

```python
# agents/semantic_kernel_temporal_agent.py
from temporalio import activity
import semantic_kernel as sk
from semantic_kernel.planning import ActionPlanner

@activity.defn
async def semantic_kernel_agent_activity(input_data: dict) -> dict:
    """Semantic Kernel agent running inside Temporal activity"""
    
    # Initialize kernel
    kernel = sk.Kernel()
    
    # Add custom LLM connector
    kernel.add_chat_service(
        "custom_llm",
        CustomSKConnector(custom_client)
    )
    
    # Register plugins (tools)
    harvest_plugin = kernel.import_skill(HarvestPlugin(), "Harvest")
    
    # Create planner (automatic task decomposition)
    planner = ActionPlanner(kernel)
    
    # Plan and execute
    plan = await planner.create_plan_async(input_data["message"])
    result = await plan.invoke_async()
    
    return {"output": result.result}
```

**Benefits:**
- Automatic planning (no manual ReAct loop)
- Temporal handles reliability
- SK handles agent logic

---

#### 4. **Mem0 Integration with Semantic Kernel**

```python
# llm/semantic_kernel_mem0_bridge.py
import semantic_kernel as sk
from semantic_kernel.memory import MemoryStoreBase
from llm.memory import LLMMemoryManager

class Mem0SKMemory(MemoryStoreBase):
    """Bridge Mem0 to Semantic Kernel memory"""
    
    def __init__(self, mem0_manager: LLMMemoryManager):
        self.mem0 = mem0_manager
    
    async def get_async(
        self,
        collection: str,
        key: str,
        with_embedding: bool = False
    ) -> Optional[MemoryRecord]:
        # Retrieve from Mem0
        context = await self.mem0.retrieve_context(query=key, k=10)
        return self._to_memory_record(context)
    
    async def put_async(
        self,
        collection: str,
        key: str,
        record: MemoryRecord
    ):
        # Store in Mem0
        await self.mem0.add_conversation(
            user_message=record.text,
            ai_response="",
            metadata={"collection": collection}
        )
```

**Benefits:**
- Keep Mem0 functionality
- Use SK memory interface
- Seamless integration

---

#### 5. **Semantic Kernel Telemetry**

```python
# monitoring/semantic_kernel_monitoring.py
from semantic_kernel.kernel import Kernel
from semantic_kernel.orchestration.sk_context import SKContext
import logging

class SKMonitoring:
    """Monitor Semantic Kernel execution"""
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        # Hook into SK events
        kernel.on_function_invoked += self.on_function_invoked
        kernel.on_function_invoking += self.on_function_invoking
    
    def on_function_invoking(self, context: SKContext):
        func_name = context.function.name
        logger.info(f"🔧 SK Function starting: {func_name}")
        track_metric(f"sk_function_{func_name}_start", 1)
    
    def on_function_invoked(self, context: SKContext):
        func_name = context.function.name
        logger.info(f"✅ SK Function finished: {func_name}")
        track_metric(f"sk_function_{func_name}_complete", 1)
```

**Benefits:**
- Native SK telemetry
- Azure Application Insights integration
- Function-level tracking

---

### File Structure Changes

```
llm/
├── semantic_kernel_connector.py    # NEW: SK connector for custom LLM
├── semantic_kernel_mem0_bridge.py  # NEW: Mem0 <-> SK bridge
├── client.py                       # KEEP: Custom LLM client
├── memory.py                       # KEEP: Mem0 manager
└── config.py                       # KEEP: Configuration

agents/
├── semantic_kernel_temporal_agent.py  # NEW: SK agent in Temporal
├── semantic_kernel_plugins.py         # NEW: Plugin definitions
├── harvest_agent.py                   # MODIFY: Use SK
├── refinement_agent.py                # MODIFY: Use SK
├── quality_agent.py                   # MODIFY: Use SK
└── notification_agent.py              # KEEP: No changes

workflows/
├── unified_workflows.py            # MODIFY: Call SK activities
└── (no new files)                  # Keep Temporal workflows

monitoring/
└── semantic_kernel_monitoring.py   # NEW: SK telemetry
```

### Dependencies to Add

```txt
# Semantic Kernel
semantic-kernel==1.0.3

# Keep existing
mem0ai==1.0.1
qdrant-client==1.16.1
temporalio==1.7.1
```

---

## Comparison Matrix

| Feature | Main (Current) | LangChain Branch | Semantic Kernel Branch |
|---------|----------------|------------------|------------------------|
| **Framework** | Hybrid | LangChain | Microsoft SK |
| **LLM Client** | Custom | Custom (wrapped) | Custom (connector) |
| **RAG/Memory** | Mem0 + Qdrant | Mem0 + Qdrant | Mem0 + Qdrant |
| **Orchestration** | Temporal | Temporal | Temporal |
| **Agent Pattern** | Custom | ReAct | Action Planner |
| **Tools** | LangChain Tools | LangChain Tools | SK Plugins |
| **Monitoring** | Custom logs | LangChain Callbacks | SK Telemetry |
| **Dependencies** | Medium | Heavy | Light |
| **Ecosystem** | Mixed | Rich (Python) | Growing (Microsoft) |
| **Azure Integration** | Manual | Manual | Native |
| **Planning** | Manual | Manual (ReAct) | Automatic |
| **Type Safety** | Medium | Low | High |

---

## Monitoring & Comparison Strategy

### Metrics to Track (All Branches)

#### 1. **RAG Accuracy Metrics**
```python
# Run same benchmark on all branches
metrics = {
    "pass_rate": 0.0,           # % of queries that retrieve correctly
    "precision": 0.0,           # Relevant retrieved / Total retrieved
    "recall": 0.0,              # Relevant retrieved / Total relevant
    "keyword_accuracy": 0.0,    # % of expected keywords found
}
```

#### 2. **Performance Metrics**
```python
metrics = {
    "avg_latency_ms": 0.0,      # Average response time
    "p95_latency_ms": 0.0,      # 95th percentile latency
    "p99_latency_ms": 0.0,      # 99th percentile latency
    "tokens_per_request": 0.0,  # Average tokens used
    "memory_mb": 0.0,           # Memory consumption
}
```

#### 3. **Code Quality Metrics**
```python
metrics = {
    "lines_of_code": 0,         # Total LOC
    "cyclomatic_complexity": 0, # Code complexity
    "test_coverage": 0.0,       # % test coverage
    "num_dependencies": 0,      # Dependency count
}
```

#### 4. **Developer Experience Metrics**
```python
metrics = {
    "time_to_add_feature_hours": 0.0,  # How long to add new tool
    "debugging_difficulty": 0,          # 1-10 scale
    "documentation_quality": 0,         # 1-10 scale
    "learning_curve": 0,                # 1-10 scale (1=easy)
}
```

#### 5. **Production Readiness Metrics**
```python
metrics = {
    "error_rate": 0.0,          # % of failed requests
    "retry_success_rate": 0.0,  # % of retries that succeed
    "monitoring_coverage": 0.0, # % of code with monitoring
    "scalability_score": 0,     # 1-10 scale
}
```

---

### Monitoring Implementation

#### Azure Application Insights Integration

```python
# monitoring/azure_insights.py
from applicationinsights import TelemetryClient
from applicationinsights.channel import TelemetryChannel

class BranchMonitoring:
    """Track metrics for branch comparison"""
    
    def __init__(self, branch_name: str):
        self.branch = branch_name
        self.telemetry = TelemetryClient(instrumentation_key)
    
    def track_rag_query(
        self,
        query: str,
        retrieved_count: int,
        relevant_count: int,
        latency_ms: float,
        success: bool
    ):
        """Track RAG query metrics"""
        self.telemetry.track_event(
            "rag_query",
            properties={
                "branch": self.branch,
                "query": query[:100],
                "success": success
            },
            measurements={
                "retrieved_count": retrieved_count,
                "relevant_count": relevant_count,
                "latency_ms": latency_ms,
                "precision": relevant_count / retrieved_count if retrieved_count > 0 else 0
            }
        )
    
    def track_agent_execution(
        self,
        agent_name: str,
        duration_ms: float,
        tokens_used: int,
        success: bool,
        error: Optional[str] = None
    ):
        """Track agent execution metrics"""
        self.telemetry.track_event(
            "agent_execution",
            properties={
                "branch": self.branch,
                "agent": agent_name,
                "success": success,
                "error": error
            },
            measurements={
                "duration_ms": duration_ms,
                "tokens_used": tokens_used
            }
        )
```

---

### Comparison Dashboard

Create Azure Dashboard to compare branches side-by-side:

```kusto
// KQL Query for comparison
customEvents
| where name == "rag_query"
| extend branch = tostring(customDimensions.branch)
| summarize 
    pass_rate = avg(todouble(customDimensions.success)),
    avg_latency = avg(todouble(customMeasurements.latency_ms)),
    avg_precision = avg(todouble(customMeasurements.precision))
    by branch
| order by pass_rate desc
```

---

## Implementation Timeline (Realistic)

### Week 1-2: LangChain Branch
- **Days 1-2:** Setup branch, LangChain wrapper, basic integration
- **Days 3-5:** Convert agents to use LangChain
- **Days 6-8:** Convert 51 tools to LangChain format
- **Days 9-10:** Testing, debugging, monitoring setup
- **Days 11-12:** Run RAG benchmark, collect metrics
- **Days 13-14:** Buffer for issues

### Week 3-4: Semantic Kernel Branch
- **Days 15-16:** Setup branch, SK connector, basic integration
- **Days 17-19:** Convert agents to use SK
- **Days 20-22:** Convert 51 tools to SK plugins
- **Days 23-24:** Testing, debugging, monitoring setup
- **Days 25-26:** Run RAG benchmark, collect metrics
- **Days 27-28:** Buffer for issues

### Week 5: Comparison & Analysis
- **Days 29-30:** Collect all metrics from both branches
- **Days 31-32:** Analyze results, create comparison report
- **Day 33:** Team review and discussion
- **Day 34:** Decision and merge planning
- **Day 35:** Buffer day

**Total: 5 weeks (35 days)**

---

## Success Criteria

### LangChain Branch Wins If:
- ✅ RAG pass rate ≥ 75% (better than main's 66.6%)
- ✅ Rich ecosystem provides clear value
- ✅ Callbacks and monitoring are superior
- ✅ Community support accelerates development
- ✅ Code is more maintainable

### Semantic Kernel Branch Wins If:
- ✅ RAG pass rate ≥ 70% (better than main's 66.6%)
- ✅ Performance is significantly better (lower latency)
- ✅ Azure integration provides clear benefits
- ✅ Automatic planning works well
- ✅ Lighter dependencies and simpler code

### Keep Main If:
- ✅ Neither branch beats main by >10% on key metrics
- ✅ Migration cost outweighs benefits
- ✅ Current hybrid approach is optimal
- ✅ Team prefers current architecture

---

## Risk Mitigation

### Main Branch Protection
```bash
# Main branch is NEVER touched during experiment
git checkout main
# ... main stays frozen ...

# All work happens in feature branches
git checkout -b feature/langchain-integration
git checkout -b feature/semantic-kernel-integration
```

### Rollback Strategy
```bash
# If experiments fail, simply delete branches
git branch -D feature/langchain-integration
git branch -D feature/semantic-kernel-integration

# Main branch remains production-ready
git checkout main
```

### Deployment Strategy
- Deploy experimental branches to separate Azure Container Apps
- Run in parallel with production (main branch)
- Compare metrics in real-time
- No risk to production users

---

## Next Steps

1. **Create branches** - Set up git structure
2. **Start LangChain branch** - Weeks 1-2
3. **Start Semantic Kernel branch** - Weeks 3-4
4. **Compare and analyze** - Week 5
5. **Make decision** - Merge winner or keep main

**Ready to begin?** I can start by:
1. Creating both feature branches
2. Beginning LangChain integration implementation
3. Setting up monitoring infrastructure

What would you like me to start with?
