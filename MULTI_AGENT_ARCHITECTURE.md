# Multi-Agent Conversation System Architecture

**Version:** 2.0.0  
**Date:** November 25, 2025  
**Status:** Active

---

## 🎯 System Overview

The multi-agent conversation system replaces the legacy single-agent architecture with a coordinated team of specialized agents that work together to provide high-quality, channel-specific responses.

### Key Principles

1. **Separation of Concerns**: Each agent has a single, well-defined responsibility
2. **Structured Data Flow**: Agents pass structured data (dicts), not formatted strings
3. **Quality First**: Every response is validated before sending
4. **Channel-Aware**: Responses are formatted specifically for SMS, Email, or WhatsApp

---

## 🤖 Agent Roles

### 1. **Planner Agent** (`agents/planner.py`)
**Role**: Orchestrator and strategist

**Responsibilities:**
- Analyze user requests and create execution plans
- Generate quality scorecards (validation criteria)
- Compose responses from timesheet data
- Refine responses based on quality feedback

**Input:** User message, conversation history, user context  
**Output:** Execution plan (JSON), scorecard (JSON), composed response (text)

**Key Methods:**
- `analyze_request()` → Returns execution plan + scorecard
- `compose_response()` → Returns draft response
- `refine_response()` → Returns improved response

---

### 2. **Timesheet Agent** (`agents/timesheet.py`)
**Role**: Data extraction specialist

**Responsibilities:**
- Extract timesheet data from Harvest API
- Handle API errors gracefully
- Return structured data (not formatted strings)
- Use user-specific credentials and timezone

**Input:** Query type, parameters, user credentials  
**Output:** Structured data dict with hours, projects, entries

**Key Methods:**
- `extract_timesheet_data()` → Returns structured data dict

**Data Structure:**
```python
{
    "data": {
        "hours_logged": 32.5,
        "hours_target": 40,
        "percentage": 81.25,
        "time_entries": [...]
    },
    "metadata": {
        "tools_used": ["check_my_timesheet"],
        "api_calls": 1
    },
    "success": True,
    "error": None
}
```

---

### 3. **Branding Agent** (`agents/branding.py`)
**Role**: Channel-specific formatter

**Responsibilities:**
- Format responses for specific channels (SMS/Email/WhatsApp)
- Apply brand voice and tone
- Handle message splitting for length limits
- Remove/add markdown based on channel

**Input:** Response text, channel, brand spec  
**Output:** Formatted response with channel-specific styling

**Channel Rules:**
- **SMS**: Plain text, no markdown, max 1600 chars, split at sentence boundaries
- **Email**: Full markdown, headers, tables, bold, links
- **WhatsApp**: Limited markdown (bold, italic), no tables

**Key Methods:**
- `format_response()` → Returns formatted response dict

---

### 4. **Quality Agent** (`agents/quality.py`)
**Role**: Quality validator

**Responsibilities:**
- Validate responses against scorecard criteria
- Provide specific feedback for failures
- Approve or reject responses
- Log validation failures for debugging

**Input:** Response, scorecard, original question  
**Output:** Validation result with pass/fail + feedback

**Key Methods:**
- `validate_response()` → Returns validation result dict

**Validation Criteria Examples:**
- "Response answers the user's question"
- "Response is formatted correctly for SMS (plain text)"
- "Response length is under 1600 characters"

---

## 🔄 Multi-Agent Workflow

### Workflow: `MultiAgentConversationWorkflow`

```
User Message (SMS/Email/WhatsApp)
         ↓
┌────────────────────────────────────────┐
│ Step 1: Planner Analyzes Request      │
│  - Creates execution plan              │
│  - Generates quality scorecard         │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ Step 2: Timesheet Agent Extracts Data │
│  - Calls Harvest MCP directly          │
│  - Returns structured data             │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ Step 3: Planner Composes Response     │
│  - Uses timesheet data                 │
│  - Creates natural language response   │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ Step 4: Branding Agent Formats        │
│  - Applies channel-specific formatting │
│  - Handles length limits               │
└────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ Step 5: Quality Agent Validates       │
│  - Checks against scorecard            │
│  - Pass → Send | Fail → Refine         │
└────────────────────────────────────────┘
         ↓
    ┌─────────┐
    │ Pass?   │
    └─────────┘
      │     │
     Yes    No (max 1 refinement)
      │     │
      │     ↓
      │  ┌────────────────────────────────┐
      │  │ Step 6: Planner Refines        │
      │  │  - Uses quality feedback       │
      │  │  - Creates improved response   │
      │  └────────────────────────────────┘
      │     │
      │     ↓
      │  ┌────────────────────────────────┐
      │  │ Reformat & Revalidate          │
      │  │  - Steps 4 & 5 again           │
      │  └────────────────────────────────┘
      │     │
      └─────┴──→ Send Response
```

---

## 🔧 Technical Implementation

### Harvest MCP Integration

**Problem with Legacy System:**
- LangChain tools returned **formatted strings** for direct user consumption
- Multi-agent system needs **structured data** to pass between agents

**Solution:**
- Created `HarvestMCPWrapper` class that calls Harvest MCP directly
- Returns structured dicts instead of formatted strings
- Bypasses LangChain tool layer entirely

**Example:**
```python
# Legacy (single-agent): Returns formatted string
result = await check_my_timesheet("this_week")
# → "You've logged 32/40 hours this week..."

# Multi-agent: Returns structured data
result = await harvest_tools.check_my_timesheet("this_week")
# → {"hours_logged": 32, "hours_target": 40, ...}
```

### Activity Structure

Each agent operation is a Temporal activity:

```python
@activity.defn
async def planner_analyze_activity(
    request_id: str,
    user_message: str,
    channel: str,
    conversation_history: List[Dict],
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Activity: Planner analyzes request"""
    llm_client = get_llm_client()
    planner = PlannerAgent(llm_client)
    return await planner.analyze_request(...)
```

**Benefits:**
- Automatic retries on failure
- Timeout protection
- Distributed execution
- Observable in Temporal UI

---

## 📊 Data Flow

### Input: User Message
```python
{
    "user_message": "Check my timesheet",
    "channel": "sms",
    "user_id": "user1",
    "conversation_history": [...],
    "user_context": {
        "harvest_account_id": "...",
        "harvest_access_token": "...",
        "timezone": "Australia/Sydney"
    }
}
```

### Step 1: Planner Analysis
```python
{
    "execution_plan": {
        "request_id": "abc123",
        "steps": [
            {"agent": "timesheet", "action": "extract_hours"},
            {"agent": "planner", "action": "compose_response"}
        ],
        "requires_timesheet_data": True
    },
    "scorecard": {
        "request_id": "abc123",
        "criteria": [
            {
                "id": "answers_question",
                "description": "Response answers user's question",
                "expected": "Response contains timesheet information"
            },
            {
                "id": "correct_format",
                "description": "Response is plain text for SMS",
                "expected": "No markdown, under 1600 chars"
            }
        ]
    }
}
```

### Step 2: Timesheet Extraction
```python
{
    "data": {
        "hours_logged": 32.5,
        "hours_target": 40,
        "percentage": 81.25,
        "time_entries": [
            {"project": "Alpha", "hours": 8, "date": "2025-11-24"},
            ...
        ]
    },
    "success": True
}
```

### Step 3: Planner Composition
```python
{
    "response": "You've logged 32.5 out of 40 hours this week (81%). You're on track! Keep up the good work."
}
```

### Step 4: Branding Format
```python
{
    "formatted_response": {
        "content": "You've logged 32.5 out of 40 hours this week (81%). You're on track! Keep up the good work.",
        "is_split": False,
        "channel": "sms"
    }
}
```

### Step 5: Quality Validation
```python
{
    "validation_result": {
        "passed": True,
        "scorecard_id": "abc123",
        "failed_criteria_ids": []
    },
    "failed_criteria": []
}
```

---

## 🚫 What's Deprecated

### Legacy Single-Agent System (REMOVED)

**Removed Components:**
- ❌ `ConversationWorkflow` - Replaced by `MultiAgentConversationWorkflow`
- ❌ `CrossPlatformRoutingWorkflow` - No longer needed
- ❌ `generate_ai_response_with_langchain` - Replaced by agent activities
- ❌ `format_check_timesheet_message()` - Replaced by Branding Agent

**Still Used (for timesheet reminders only):**
- ✅ `TimesheetReminderWorkflow` - Daily reminders (not conversations)
- ✅ `create_harvest_tools()` - Used by reminder workflow only
- ✅ LangChain tools - Used by reminder workflow only

**Key Difference:**
- **Reminders**: Use formatted strings (direct to user)
- **Conversations**: Use structured data (agent-to-agent)

---

## ✅ Benefits of Multi-Agent System

### 1. **Quality Control**
- Every response validated before sending
- Automatic refinement for poor responses
- Detailed failure logging

### 2. **Channel-Specific Formatting**
- SMS: Plain text, concise
- Email: Rich markdown, detailed
- WhatsApp: Limited markdown

### 3. **Maintainability**
- Each agent has single responsibility
- Easy to test individual agents
- Clear data contracts between agents

### 4. **Extensibility**
- Easy to add new agents (e.g., Project Agent, Client Agent)
- Easy to add new channels
- Easy to add new quality criteria

### 5. **Observability**
- Each agent step visible in Temporal UI
- Detailed logging at each stage
- Easy to debug failures

---

## 🔮 Future Enhancements

### Planned Agents
1. **Project Agent** - Manage projects, assignments, budgets
2. **Client Agent** - Handle client information, contacts
3. **Expense Agent** - Track and manage expenses
4. **Invoice Agent** - Create and manage invoices

### Planned Features
1. **Agent Collaboration** - Agents can request help from other agents
2. **Long-term Memory** - Conversation summarization and recall
3. **Proactive Suggestions** - Agents suggest actions based on patterns
4. **Multi-turn Planning** - Complex tasks broken into multiple steps

---

## 📚 Key Files

### Agent Implementations
- `agents/base.py` - Base agent class
- `agents/planner.py` - Planner agent
- `agents/timesheet.py` - Timesheet agent
- `agents/branding.py` - Branding agent
- `agents/quality.py` - Quality agent
- `agents/models.py` - Pydantic models for data contracts

### Workflows
- `unified_workflows.py` - Multi-agent workflow and activities

### Server
- `unified_server.py` - FastAPI server, webhook handlers

### Infrastructure
- `llm/` - Centralized LLM client
- `deploy_configured.sh` - Deployment script
- `DEPLOYMENT_GUIDE.md` - Deployment instructions

---

## 🎓 Key Learnings

### Architecture Decisions

1. **Structured Data > Formatted Strings**
   - Agents pass structured dicts, not formatted text
   - Formatting happens at the end (Branding Agent)
   - Enables validation and refinement

2. **Direct MCP Calls > LangChain Tools**
   - Multi-agent needs structured data
   - LangChain tools return formatted strings
   - Created `HarvestMCPWrapper` for direct calls

3. **Quality First**
   - Validation before sending
   - Automatic refinement (1 attempt)
   - Graceful failure messages

4. **Channel-Specific Everything**
   - Different formatting rules per channel
   - Different length limits
   - Different markdown support

---

## 🚀 Deployment

The multi-agent system is deployed to Azure Container Apps:

- **URL**: `https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io`
- **Webhooks**: 
  - SMS: `/webhook/sms`
  - WhatsApp: `/webhook/whatsapp`
  - Email: `/webhook/email`

See `DEPLOYMENT_GUIDE.md` for full deployment instructions.

---

## 📞 Support

For issues or questions:
1. Check Temporal UI for workflow execution details
2. Check Azure Container Apps logs
3. Review agent-specific logs for detailed errors
4. Consult this architecture document for design decisions
