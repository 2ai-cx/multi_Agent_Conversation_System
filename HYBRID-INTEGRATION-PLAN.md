# Hybrid Integration Plan: Keep Custom + Add LangChain

**Date:** December 10, 2025  
**Objective:** Add LangChain RAG, Memory, and Tool Registry while preserving ALL current features

---

## 🎯 Strategy: ADDITIVE, NOT REPLACEMENT

**Core Principle:** We ADD new capabilities WITHOUT changing existing code

- ✅ **Keep** all 522 lines of `llm/client.py`
- ✅ **Keep** all custom features (minification, rate limiting, caching, tenant keys)
- ➕ **Add** new methods alongside existing ones
- ➕ **Add** new files for RAG and tools
- ➕ **Opt-in** - features disabled by default

---

## 📊 Current System Inventory

### Core Files (KEEP ALL - NO CHANGES)
```
llm/client.py (522 lines)          ✅ KEEP - Add new methods only
llm/config.py (338 lines)          ✅ KEEP - Add new config fields
llm/json_minifier.py (313 lines)   ✅ KEEP - No changes
llm/rate_limiter.py (290 lines)    ✅ KEEP - No changes
llm/cache.py (287 lines)           ✅ KEEP - No changes
llm/tenant_key_manager.py (333)    ✅ KEEP - No changes
llm/opik_tracker.py (342 lines)    ✅ KEEP - Minor additions
llm/error_handler.py (293 lines)   ✅ KEEP - No changes
```

### Agent Files (MINIMAL CHANGES)
```
agents/planner.py (670 lines)      ✅ KEEP - Change 3 method calls
agents/timesheet.py (15KB)         ✅ KEEP - No changes
agents/branding.py (14KB)          ✅ KEEP - Change 1 method call
agents/quality.py (9KB)            ✅ KEEP - Change 1 method call
```

### Workflow Files (ADD NEW FUNCTION)
```
unified_workflows.py (3806 lines)  ✅ KEEP - Add tool registry function
unified_server.py (1519 lines)     ✅ KEEP - No changes
```

---

## 🏗️ New Files to Create

```
llm/
├── memory.py                      ➕ NEW (300 lines)
├── embeddings.py                  ➕ NEW (100 lines)

agents/tools/
├── __init__.py                    ➕ NEW (10 lines)
├── registry.py                    ➕ NEW (400 lines)
├── credentials.py                 ➕ NEW (150 lines)
├── gmail.py                       ➕ NEW (100 lines)
├── slack.py                       ➕ NEW (100 lines)
└── calendar.py                    ➕ NEW (100 lines)
```

**Total New Code:** ~1,260 lines  
**Modified Existing Code:** ~50 lines (method call changes)  
**Preserved Existing Code:** ~7,000+ lines (100%)

---

## 📝 Implementation Steps

### Phase 1: Memory (RAG) - Days 1-3

#### Step 1.1: Add Config Fields
**File:** `llm/config.py`  
**Action:** Add 15 new fields at end of class

```python
# ➕ ADD at end of LLMConfig class
rag_enabled: bool = Field(default=False)
vector_db_provider: str = Field(default="pinecone")
pinecone_api_key: Optional[str] = Field(default=None)
pinecone_index_name: str = Field(default="timesheet-memory")
embeddings_provider: str = Field(default="openai")
embeddings_model: str = Field(default="text-embedding-3-small")
memory_retrieval_k: int = Field(default=5)
memory_retrieval_method: str = Field(default="mmr")
```

#### Step 1.2: Create Memory Manager
**File:** `llm/memory.py` (NEW)  
**Purpose:** Manage vector store and retrieval

**Key Methods:**
- `__init__(tenant_id, config)` - Initialize with tenant isolation
- `add_conversation(user_msg, ai_msg, metadata)` - Store in vector DB
- `retrieve_context(query, k=5)` - Semantic search
- `get_stats()` - Memory statistics

#### Step 1.3: Create Embeddings Wrapper
**File:** `llm/embeddings.py` (NEW)  
**Purpose:** Unified embeddings interface

**Supports:**
- OpenAI (text-embedding-3-small)
- Cohere (embed-english-v3.0)
- HuggingFace (sentence-transformers)

#### Step 1.4: Extend LLMClient
**File:** `llm/client.py`  
**Action:** Add 3 new methods (don't change existing)

```python
# ➕ ADD to __init__
self._memory_managers = {}  # Cache per tenant

# ➕ ADD new property
def get_memory_manager(self, tenant_id: str):
    """Get or create memory for tenant"""
    if tenant_id not in self._memory_managers:
        from llm.memory import LLMMemoryManager
        self._memory_managers[tenant_id] = LLMMemoryManager(tenant_id, self.config)
    return self._memory_managers[tenant_id]

# ➕ ADD new method (existing chat_completion unchanged)
async def chat_completion_with_memory(
    self, messages, tenant_id, user_id, use_memory=True, **kwargs
):
    """Chat with RAG - calls existing chat_completion internally"""
    if not self.config.rag_enabled or not use_memory:
        return await self.chat_completion(messages, tenant_id, user_id, **kwargs)
    
    memory = self.get_memory_manager(tenant_id)
    context = await memory.retrieve_context(messages[-1]["content"])
    
    if context:
        messages = [{"role": "system", "content": f"Context:\n{context}"}] + messages
    
    response = await self.chat_completion(messages, tenant_id, user_id, **kwargs)
    
    await memory.add_conversation(messages[-1]["content"], response.content, {...})
    
    return response
```

#### Step 1.5: Update Agents
**Files:** `agents/planner.py`, `agents/branding.py`, `agents/quality.py`  
**Action:** Change method calls (5 locations total)

**Before:**
```python
response = await self.llm_client.chat_completion(messages, ...)
```

**After:**
```python
response = await self.llm_client.chat_completion_with_memory(
    messages, 
    tenant_id=user_context.get("tenant_id", "default"),
    user_id=user_context.get("user_id"),
    use_memory=True
)
```

**Changes:**
- `planner.py`: 3 method calls (analyze_request, compose_response, refine_response)
- `branding.py`: 1 method call (format_response)
- `quality.py`: 1 method call (validate_response)

---

### Phase 2: Tool Registry - Days 4-7

#### Step 2.1: Create Tool Registry
**File:** `agents/tools/registry.py` (NEW)  
**Purpose:** Unified tool management

**Key Methods:**
- `register_tool(tool, category, metadata)` - Register any tool
- `register_harvest_tools()` - Register existing 51 tools
- `register_langchain_tools(category)` - Register Gmail/Slack/Calendar
- `get_tool(name)` - Get tool by name
- `get_tools_by_category(category)` - Filter by category
- `execute_tool(name, args)` - Execute with tracking

#### Step 2.2: Create Credential Manager
**File:** `agents/tools/credentials.py` (NEW)  
**Purpose:** Encrypted credential storage

**Key Methods:**
- `store_credentials(tenant_id, user_id, tool_name, creds)` - Encrypt & store
- `get_credentials(tenant_id, user_id, tool_name)` - Decrypt & retrieve
- `delete_credentials(...)` - Remove credentials

**Database:**
```sql
CREATE TABLE tool_credentials (
  id UUID PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  credentials TEXT NOT NULL,  -- Encrypted
  UNIQUE(tenant_id, user_id, tool_name)
);
```

#### Step 2.3: Create Tool Wrappers
**Files:** `agents/tools/gmail.py`, `slack.py`, `calendar.py` (NEW)  
**Purpose:** LangChain tool integrations

**Gmail Tools:**
- `GmailSendMessage` - Send email
- `GmailSearch` - Search emails
- `GmailGetMessage` - Read email

**Slack Tools:**
- `SlackSendMessage` - Send message
- `SlackGetChannel` - Get channel info

**Calendar Tools:**
- `GoogleCalendarCreateEvent` - Create event
- `GoogleCalendarGetEvents` - List events

#### Step 2.4: Integrate with Workflows
**File:** `unified_workflows.py`  
**Action:** Add new function (keep existing `create_harvest_tools`)

```python
# ➕ ADD new function (don't change existing)
def create_unified_tool_registry(user_id: str, tenant_id: str):
    """Create registry with all tools"""
    from agents.tools.registry import ToolRegistry
    
    registry = ToolRegistry(tenant_id, user_id)
    
    # Register existing Harvest tools
    registry.register_harvest_tools()
    
    # Register LangChain tools (if enabled)
    if registry.config.tool_registry_enabled:
        registry.register_langchain_tools("gmail", user_id)
        registry.register_langchain_tools("slack", user_id)
        registry.register_langchain_tools("calendar", user_id)
    
    return registry

# ➕ ADD new activity
@activity.defn
async def execute_tool_from_registry(tenant_id, user_id, tool_name, tool_args):
    """Execute tool from registry"""
    registry = create_unified_tool_registry(user_id, tenant_id)
    return await registry.execute_tool(tool_name, tool_args)
```

---

## 🔧 Configuration

### Environment Variables

**Add to `.env`:**
```bash
# RAG Configuration
RAG_ENABLED=false                              # Feature flag
VECTOR_DB_PROVIDER=pinecone                    # pinecone, weaviate, qdrant
PINECONE_API_KEY=your-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=timesheet-memory
EMBEDDINGS_PROVIDER=openai
EMBEDDINGS_MODEL=text-embedding-3-small
MEMORY_RETRIEVAL_K=5
MEMORY_RETRIEVAL_METHOD=mmr

# Tool Registry
TOOL_REGISTRY_ENABLED=false                    # Feature flag
TOOL_REGISTRY_CACHE_TTL=3600

# Encryption
TOOL_CREDENTIALS_ENCRYPTION_KEY=your-fernet-key
```

### Dependencies

**Add to `requirements.txt`:**
```txt
# Vector Database
pinecone-client==2.2.4
langchain-pinecone==0.0.1

# LangChain Tools
langchain-community==0.0.10
google-auth==2.23.0
google-api-python-client==2.100.0
slack-sdk==3.23.0

# Encryption
cryptography==41.0.5
```

---

## ✅ Testing Strategy

### Phase 1 Tests: Memory

**Test 1: Memory Storage**
```python
# Store conversation
await memory.add_conversation(
    user_message="I prefer Project Alpha",
    ai_response="Noted.",
    metadata={"user_id": "test-user"}
)

# Verify stored
context = await memory.retrieve_context("favorite project")
assert "Project Alpha" in str(context)
```

**Test 2: Memory Retrieval**
```python
# First conversation
response1 = await client.chat_completion_with_memory(
    messages=[{"role": "user", "content": "I work on Project Alpha"}],
    tenant_id="test-tenant",
    user_id="test-user"
)

# Second conversation (should recall)
response2 = await client.chat_completion_with_memory(
    messages=[{"role": "user", "content": "What project do I work on?"}],
    tenant_id="test-tenant",
    user_id="test-user"
)

assert "Alpha" in response2.content
```

**Test 3: Multi-Tenant Isolation**
```python
# Tenant 1 stores data
await memory1.add_conversation("Secret data", "OK", {})

# Tenant 2 cannot retrieve
context = await memory2.retrieve_context("secret")
assert len(context) == 0
```

### Phase 2 Tests: Tools

**Test 4: Tool Registration**
```python
registry = ToolRegistry("tenant-1", "user-1")
registry.register_harvest_tools()

tools = registry.get_all_tools()
assert len(tools) == 51

harvest_tools = registry.get_tools_by_category("harvest")
assert len(harvest_tools) == 51
```

**Test 5: Tool Execution**
```python
result = await registry.execute_tool(
    "check_my_timesheet",
    {"date_range": "this_week"}
)

assert result["success"] == True
assert "hours" in result["result"]
```

---

## 🚀 Deployment Plan

### Step 1: Staging Deployment (Week 2)

1. Deploy with feature flags OFF
2. Verify existing functionality unchanged
3. Enable RAG for test tenant
4. Monitor memory usage and latency
5. Enable tool registry for test tenant
6. Verify tool execution

### Step 2: Production Rollout (Week 3)

**Day 1-2: Gradual Rollout**
- Enable RAG for 10% of tenants
- Monitor metrics:
  - Memory retrieval latency (<100ms target)
  - LLM call latency (should increase <200ms)
  - Memory storage success rate (>99%)
  - Cost per request (should decrease with better context)

**Day 3-4: Scale Up**
- Enable RAG for 50% of tenants
- Enable tool registry for 10% of tenants
- Monitor tool execution success rate

**Day 5: Full Rollout**
- Enable RAG for all tenants
- Enable tool registry for all tenants
- Monitor overall system health

### Step 3: Monitoring

**Key Metrics:**
```python
# Memory metrics
- memory_retrieval_latency_ms
- memory_storage_latency_ms
- memory_hit_rate
- memory_storage_size_mb

# Tool metrics
- tool_execution_count_by_category
- tool_execution_latency_ms
- tool_execution_success_rate
- tool_execution_error_rate

# Overall metrics
- llm_call_latency_with_memory_ms
- llm_call_latency_without_memory_ms
- cost_per_request_with_memory_usd
- cost_per_request_without_memory_usd
```

---

## 📊 Success Criteria

### Memory (RAG)
- ✅ Memory retrieval latency <100ms (p95)
- ✅ Memory storage success rate >99%
- ✅ Context relevance score >0.8
- ✅ User satisfaction +10%
- ✅ Zero impact on existing features

### Tool Registry
- ✅ Tool execution success rate >95%
- ✅ Tool discovery time <10ms
- ✅ Credential retrieval <50ms
- ✅ Support 100+ tools
- ✅ Zero impact on existing Harvest tools

### Overall
- ✅ All existing features working
- ✅ No performance degradation
- ✅ No cost increase (should decrease)
- ✅ Backward compatible
- ✅ Can disable features via flags

---

## 🔄 Rollback Plan

### If Memory Issues
1. Set `RAG_ENABLED=false` in environment
2. Restart services
3. System reverts to existing behavior
4. Zero data loss (Supabase unchanged)

### If Tool Registry Issues
1. Set `TOOL_REGISTRY_ENABLED=false`
2. Restart services
3. System uses existing `create_harvest_tools`
4. Zero impact on Harvest functionality

### If Critical Issues
1. Revert to previous deployment
2. All new code is additive
3. Existing code unchanged
4. Full rollback in <5 minutes

---

## 📁 File Change Summary

### Modified Files (5 files, ~50 lines changed)
```
llm/config.py                  +15 lines (new config fields)
llm/client.py                  +30 lines (new methods)
agents/planner.py              +3 lines (method call changes)
agents/branding.py             +1 line (method call change)
agents/quality.py              +1 line (method call change)
```

### New Files (9 files, ~1,260 lines)
```
llm/memory.py                  300 lines
llm/embeddings.py              100 lines
agents/tools/__init__.py       10 lines
agents/tools/registry.py       400 lines
agents/tools/credentials.py    150 lines
agents/tools/gmail.py          100 lines
agents/tools/slack.py          100 lines
agents/tools/calendar.py       100 lines
```

### Unchanged Files (10+ files, ~7,000+ lines)
```
llm/json_minifier.py           ✅ No changes
llm/rate_limiter.py            ✅ No changes
llm/cache.py                   ✅ No changes
llm/tenant_key_manager.py      ✅ No changes
llm/error_handler.py           ✅ No changes
agents/timesheet.py            ✅ No changes
unified_server.py              ✅ No changes
... all other files ...        ✅ No changes
```

---

## 🎯 Next Steps

1. **Review this plan** - Confirm approach
2. **Set up Pinecone** - Create index
3. **Create new files** - Start with memory.py
4. **Test memory** - Verify RAG works
5. **Update agents** - Add memory calls
6. **Create tool registry** - Build infrastructure
7. **Add LangChain tools** - Gmail, Slack, Calendar
8. **Test end-to-end** - Full workflow
9. **Deploy to staging** - Feature flags OFF
10. **Gradual rollout** - Enable for test tenants

**Timeline:** 2-3 weeks  
**Risk:** Low (additive, feature-flagged)  
**Benefit:** High (RAG + 100+ tools)

---

**Ready to start implementation?** 🚀
