# Tool Selection Strategies - Learnings from Goose

## Overview

Based on investigation of Goose (Block's AI agent) and the MCP ecosystem, here are the proven strategies for handling large tool catalogs (40-50+ tools).

---

## The Problem

### Our Current Situation
- **51 Harvest API tools** available
- **All 51 tools passed to LLM** on every request
- **Exceeds recommended 25-tool limit** (Goose recommendation)
- **Wastes tokens** (~50k tokens just for tool schemas!)
- **Confuses LLM** - too many irrelevant options

### Industry Evidence
- **Goose**: Recommends max 25 tools
- **Claude Code**: Unfiltered MCP servers consume ~50k tokens
- **MCP Filter**: Achieved 72% token reduction through filtering
- **GitHub MCP**: Has 40 tools - considered "very large"

---

## Solution 1: Static Allowlist (Configuration-Based)

### What It Is
Pre-define which tools are relevant for each query type using configuration.

### How Goose Does It
```yaml
# User configuration file
extensions:
  github:
    enabled_tools:
      - create_issue
      - list_pull_requests
      - get_repository
    disabled_tools:
      - create_repository
      - delete_repository
```

### How We Can Implement It

#### Option A: In Planner SOPs
```python
# agents/planner.py
sops = {
    "last_entry": {
        "triggers": ["last entry", "most recent entry"],
        "needs_data": True,
        "relevant_tools": ["list_time_entries"],  # Only 1 tool needed!
        "tool_call": {
            "tool": "list_time_entries",
            "parameters": {...}
        }
    },
    "check_timesheet": {
        "triggers": ["check timesheet", "my timesheet"],
        "needs_data": True,
        "relevant_tools": ["list_time_entries"],  # Only 1 tool needed!
        "tool_call": {
            "tool": "list_time_entries",
            "parameters": {...}
        }
    },
    "create_entry": {
        "triggers": ["log time", "create entry"],
        "needs_data": True,
        "relevant_tools": [
            "create_time_entry",
            "list_projects",
            "list_tasks"
        ],  # 3 tools needed
        "tool_call": {
            "tool": "create_time_entry",
            "parameters": {...}
        }
    }
}
```

#### Option B: MCP Filter Proxy (External)
```bash
# Wrap Harvest MCP server with filter
mcp-filter run \
  -t stdio \
  --stdio-command "harvest-mcp-server" \
  -a "list_time_entries,create_time_entry,list_projects"
  
# Result: Only 3 tools exposed instead of 51!
```

### Pros & Cons

✅ **Pros:**
- Simple to implement
- Explicit control
- No ML/vector search needed
- Works immediately
- Easy to debug

❌ **Cons:**
- Manual configuration
- Requires updating when adding new query types
- Less flexible than dynamic approaches

### Token Savings
- **Before**: 51 tools × ~100 tokens/tool = ~5,100 tokens
- **After**: 3 tools × ~100 tokens/tool = ~300 tokens
- **Savings**: ~4,800 tokens (94% reduction!)

---

## Solution 2: Vector-Based Tool Router (Dynamic)

### What It Is
Use semantic search to find relevant tools based on user query.

### How Goose Does It
```yaml
# goose config
tool_selection_strategy: vector  # Instead of "default"
```

**Architecture:**
1. Index all tool descriptions using embeddings
2. When user asks a question, embed the query
3. Vector search finds top-K most relevant tools
4. Only pass those K tools to LLM

### How We Can Implement It

```python
# tool_router.py
import numpy as np
from sentence_transformers import SentenceTransformer

class ToolRouter:
    def __init__(self, tools: List[Dict]):
        self.tools = tools
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Build index
        self.tool_descriptions = [
            f"{t['name']}: {t['description']}" 
            for t in tools
        ]
        self.tool_embeddings = self.model.encode(self.tool_descriptions)
    
    def select_tools(
        self, 
        user_query: str, 
        max_tools: int = 5
    ) -> List[str]:
        """
        Select most relevant tools using vector similarity
        
        Args:
            user_query: User's question
            max_tools: Maximum number of tools to return
        
        Returns:
            List of tool names
        """
        # Embed query
        query_embedding = self.model.encode([user_query])[0]
        
        # Calculate cosine similarity
        similarities = np.dot(
            self.tool_embeddings, 
            query_embedding
        ) / (
            np.linalg.norm(self.tool_embeddings, axis=1) * 
            np.linalg.norm(query_embedding)
        )
        
        # Get top-K
        top_indices = np.argsort(similarities)[-max_tools:][::-1]
        
        return [self.tools[i]['name'] for i in top_indices]


# Usage in Planner
router = ToolRouter(harvest_tools)
relevant_tools = router.select_tools(
    "When was my last entry", 
    max_tools=3
)
# Returns: ["list_time_entries", "get_current_user"]
```

### Pros & Cons

✅ **Pros:**
- Fully automatic
- Adapts to new queries
- Scales to 100+ tools
- No manual configuration

❌ **Cons:**
- Requires embedding model
- More complex
- Slight latency overhead (~50-100ms)
- May select wrong tools occasionally

### Token Savings
- **Before**: 51 tools = ~5,100 tokens
- **After**: 5 tools = ~500 tokens
- **Savings**: ~4,600 tokens (90% reduction)

---

## Solution 3: Tag-Based Filtering (Hybrid)

### What It Is
Tag tools by category, then filter by tags relevant to query.

### Proposed by MCP Community
```python
# Tag tools when registering
@mcp.tool(tags=["read", "timesheet"])
def list_time_entries(...):
    pass

@mcp.tool(tags=["write", "timesheet"])
def create_time_entry(...):
    pass

@mcp.tool(tags=["read", "project"])
def list_projects(...):
    pass

# Filter by tags
tools = mcp.list_tools(tags=["read", "timesheet"])
# Returns only: list_time_entries
```

### How We Can Implement It

```python
# Categorize Harvest tools
TOOL_CATEGORIES = {
    "timesheet_read": [
        "list_time_entries",
        "get_time_entry",
        "list_time_entries_for_user"
    ],
    "timesheet_write": [
        "create_time_entry",
        "update_time_entry",
        "delete_time_entry"
    ],
    "project_read": [
        "list_projects",
        "get_project",
        "list_project_assignments"
    ],
    "task_read": [
        "list_tasks",
        "get_task"
    ],
    "user_read": [
        "get_current_user",
        "list_users"
    ]
}

# In Planner SOP
sops = {
    "last_entry": {
        "tool_categories": ["timesheet_read"],  # Uses 3 tools
        ...
    },
    "create_entry": {
        "tool_categories": ["timesheet_write", "project_read", "task_read"],  # Uses 8 tools
        ...
    }
}

# Filter tools
def get_tools_for_categories(categories: List[str]) -> List[str]:
    tools = []
    for cat in categories:
        tools.extend(TOOL_CATEGORIES.get(cat, []))
    return list(set(tools))  # Deduplicate
```

### Pros & Cons

✅ **Pros:**
- Balance between manual and automatic
- Flexible grouping
- Easy to understand
- Can combine categories

❌ **Cons:**
- Requires initial categorization
- Categories may overlap
- Still needs some maintenance

### Token Savings
- **Before**: 51 tools = ~5,100 tokens
- **After**: 3-8 tools per query = ~300-800 tokens
- **Savings**: ~4,300-4,800 tokens (85-94% reduction)

---

## Real-World Evidence

### MCP Filter Results
**Before filtering:**
```
MCP tools: 50.1k tokens (25% of context)
Free space: 88k (44%)
```

**After filtering:**
```
MCP tools: 13.7k tokens (6.9% of context)
Free space: 120k (60%)
```

**Result:** 72% token reduction, +32k context gained

### Goose Recommendations
- **Max 25 tools** recommended
- **Vector search** for 40+ tools
- **Configuration filtering** for simpler cases
- **GitHub MCP** (40 tools) considered "very large"

---

## Recommended Implementation for Our System

### Phase 1: Static Allowlist (Immediate - This Week)

**Why:** Simplest, highest impact, no dependencies

```python
# agents/planner.py
sops = {
    "last_entry": {
        "relevant_tools": ["list_time_entries"],  # 1 tool
        ...
    },
    "check_timesheet": {
        "relevant_tools": ["list_time_entries"],  # 1 tool
        ...
    },
    "weekly_summary": {
        "relevant_tools": ["list_time_entries", "list_projects"],  # 2 tools
        ...
    },
    "create_entry": {
        "relevant_tools": [
            "create_time_entry",
            "list_projects",
            "list_tasks",
            "get_current_user"
        ],  # 4 tools
        ...
    }
}

# unified_workflows.py
async def timesheet_execute_activity(
    request_id: str,
    tool_call_spec: Dict,
    user_context: Dict,
    allowed_tools: List[str]  # NEW!
):
    timesheet = TimesheetAgent(
        credentials=credentials,
        timezone=timezone,
        allowed_tools=allowed_tools  # Filter tools
    )
    ...
```

**Expected Savings:**
- From 51 tools → 1-4 tools per query
- ~4,500-5,000 tokens saved per request
- ~$0.009-0.010 saved per request (at $0.50/1M tokens)
- At 1,000 requests/day: ~$9-10/day = ~$270-300/month

### Phase 2: Tag-Based Categories (Next Month)

**Why:** More flexible, easier to maintain

```python
TOOL_CATEGORIES = {
    "timesheet_read": [...],  # 8 tools
    "timesheet_write": [...],  # 6 tools
    "project_info": [...],  # 12 tools
    "user_info": [...],  # 5 tools
    "reporting": [...],  # 10 tools
}

# In SOPs
"last_entry": {
    "tool_categories": ["timesheet_read"],
    ...
}
```

### Phase 3: Vector Router (Future - If Needed)

**Why:** Only if we add many more MCP servers

```python
# Only implement if:
# - We add GitHub, Jira, Slack MCP servers
# - Total tools exceed 100
# - Static filtering becomes unmaintainable
```

---

## Implementation Example

### Before (Current)
```python
# agents/timesheet.py
prompt = f"""You have access to these 51 Harvest API tools:

1. list_time_entries(from_date, to_date, user_id=None)
2. get_time_entry(time_entry_id)
3. create_time_entry(project_id, task_id, spent_date, hours=None, notes=None)
... (48 more tools)

Execute the Planner's instruction: "{planner_message}"
"""
# Result: ~5,100 tokens just for tool descriptions!
```

### After (With Filtering)
```python
# unified_workflows.py
relevant_tools = sop.get("relevant_tools", [])  # e.g., ["list_time_entries"]

# agents/timesheet.py
def __init__(self, credentials, timezone, allowed_tools=None):
    self.allowed_tools = allowed_tools or []

prompt = f"""You have access to these tools:

{self._format_tools(self.allowed_tools)}  # Only 1-4 tools!

Execute this tool call: {tool_call_spec}
"""
# Result: ~100-400 tokens for tool descriptions
```

---

## Key Takeaways

1. ✅ **51 tools is too many** - Industry recommends max 25
2. ✅ **Static filtering works** - 72-94% token reduction proven
3. ✅ **Start simple** - Configuration-based filtering first
4. ✅ **Vector search later** - Only if we scale to 100+ tools
5. ✅ **Tag-based hybrid** - Good middle ground

### Immediate Action
Implement static allowlist in Planner SOPs:
- **"last entry"** → 1 tool (`list_time_entries`)
- **"check timesheet"** → 1 tool (`list_time_entries`)
- **"create entry"** → 4 tools (`create_time_entry`, `list_projects`, `list_tasks`, `get_current_user`)

**Expected Impact:**
- 90%+ token reduction for tool schemas
- $270-300/month cost savings
- Faster LLM responses (less context to process)
- Better tool selection accuracy

---

## References

- [Goose Tool Router Documentation](https://block.github.io/goose/docs/guides/tool-router/)
- [MCP Filter Proxy](https://github.com/pro-vi/mcp-filter)
- [MCP Python SDK - Tag-Based Filtering](https://github.com/modelcontextprotocol/python-sdk/issues/522)
- [Goose Issue #2927 - Tool Filtering](https://github.com/block/goose/issues/2927)
