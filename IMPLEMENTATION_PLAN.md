# Implementation Plan: Remove All Hardcoded Logic

## Current Problems

1. **Planner Agent** returns structured data:
   - `requires_timesheet_data` flag
   - `steps` array with predefined actions
   - `query_type` and `parameters`

2. **Timesheet Agent** has hardcoded logic:
   - `if query_type == "hours_logged"`
   - `elif query_type == "projects"`
   - Predefined date parsing

3. **Workflow** interprets structured plans:
   - Checks `requires_timesheet_data` flag
   - Passes `query_type` and `parameters`
   - Hardcoded orchestration

## Solution: Pure LLM-Driven Agents

### Step 1: Simplify Planner Agent

**Remove:**
```python
{
    "requires_timesheet_data": true,
    "query_type": "hours_logged",
    "parameters": {"date_range": "this_week"}
}
```

**Replace with:**
```python
{
    "needs_data": true,
    "message_to_timesheet": "Get the user's time entries for last week (November 18-24, 2025)",
    "scorecard": [...]  # Keep quality criteria
}
```

### Step 2: Simplify Timesheet Agent

**Remove:**
```python
async def extract_timesheet_data(
    self, request_id, user_id, query_type, parameters, ...
):
    if query_type == "hours_logged":
        ...
    elif query_type == "projects":
        ...
```

**Replace with:**
```python
async def execute(self, request_id, planner_message, user_context):
    # Use LLM to understand Planner's message
    prompt = f"""
    Planner requested: "{planner_message}"
    Available tools: {list_of_51_harvest_tools}
    Which tool should you call and with what parameters?
    """
    decision = await llm.generate(prompt)
    
    # Execute the tool
    tool_func = getattr(self.harvest_tools, decision['tool'])
    result = await tool_func(**decision['params'])
    return result
```

### Step 3: Simplify Workflow

**Remove:**
```python
if execution_plan["requires_timesheet_data"]:
    result = await execute_activity(
        timesheet_extract_activity,
        args=[request_id, user_id, query_type, parameters, ...]
    )
```

**Replace with:**
```python
if planner_analysis["needs_data"]:
    result = await execute_activity(
        timesheet_execute_activity,
        args=[request_id, planner_analysis["message_to_timesheet"], user_context]
    )
```

## Files to Modify

1. `/agents/planner.py` - Remove structured plans, return natural language messages
2. `/agents/timesheet.py` - Remove hardcoded logic, add LLM-based tool selection
3. `/unified_workflows.py` - Simplify workflow to just route messages
4. `/agents/models.py` - Update ExecutionPlan model (or remove it)

## Testing

After changes, test with:
- "Check my timesheet" → Should work
- "Check my timesheet for last week" → Should work
- "Check my timesheet for December 2024" → Should work
- "Show me my projects" → Should work

All without code changes, just LLM understanding the request!
