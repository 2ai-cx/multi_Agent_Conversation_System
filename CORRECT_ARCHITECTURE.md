# Correct Multi-Agent Architecture

## ❌ What We Had (Wrong)

### Hardcoded Orchestration
```python
# Planner returns structured plan
{
    "requires_timesheet_data": true,
    "query_type": "hours_logged",
    "parameters": {"date_range": "this_week"}
}

# Workflow interprets the structure
if plan["requires_timesheet_data"]:
    result = await timesheet_agent.extract(
        query_type=plan["query_type"],
        parameters=plan["parameters"]
    )

# Timesheet Agent has hardcoded logic
if query_type == "hours_logged":
    return await self.harvest_tools.check_my_timesheet(...)
elif query_type == "projects":
    return await self.harvest_tools.list_my_projects(...)
```

**Problem:** We're defining HOW agents work instead of letting them decide!

---

## ✅ What It Should Be (Correct)

### Pure LLM-Driven Communication

```python
# ============================================
# STEP 1: Planner Analyzes Request
# ============================================
planner_prompt = """
You are a Planner Agent coordinating a team.

User asked: "Check my timesheet for last week"

Available agents:
- Timesheet Agent: Can retrieve data from Harvest API (51 tools available)
- Branding Agent: Can format responses for different channels
- Quality Agent: Can validate response quality

Your task:
1. Do you need data from another agent? If yes, write a message to that agent.
2. If no, you can compose the response directly.

Think step by step. Return JSON:
{
    "needs_help": true/false,
    "agent_to_contact": "timesheet" or null,
    "message_to_agent": "Your natural language request to the agent"
}
"""

planner_decision = await llm.generate(planner_prompt)
# LLM decides: {"needs_help": true, "agent_to_contact": "timesheet", 
#               "message_to_agent": "Get time entries for last week (Nov 18-24, 2025)"}

# ============================================
# STEP 2: Timesheet Agent Executes
# ============================================
timesheet_prompt = f"""
You are a Timesheet Data Specialist with access to Harvest API.

The Planner Agent sent you this message:
"{planner_decision['message_to_agent']}"

Available Harvest tools (you have 51 total):
- list_time_entries(from_date, to_date, user_id, harvest_account, harvest_token)
- list_projects(user_id, harvest_account, harvest_token)
- get_current_user(harvest_account, harvest_token)
- ... (48 more tools)

Your task:
1. Understand what the Planner needs
2. Decide which tool(s) to call
3. Call the tool(s) and return the data

Think step by step. Return JSON:
{{
    "tool_to_call": "tool_name",
    "parameters": {{"param": "value"}},
    "reasoning": "why this tool"
}}
"""

timesheet_decision = await llm.generate(timesheet_prompt)
# LLM decides: {"tool_to_call": "list_time_entries", 
#               "parameters": {"from_date": "2025-11-18", "to_date": "2025-11-24"}}

# Execute the tool
tool_func = getattr(harvest_tools, timesheet_decision['tool_to_call'])
data = await tool_func(**timesheet_decision['parameters'])

# ============================================
# STEP 3: Planner Composes Response
# ============================================
compose_prompt = f"""
You are a Planner Agent.

User asked: "Check my timesheet for last week"

You requested data from Timesheet Agent and received:
{json.dumps(data)}

Your task:
Compose a clear, helpful response to the user based on this data.
"""

response = await llm.generate(compose_prompt)
# LLM composes: "You logged 32 hours last week across 3 projects..."

# ============================================
# STEP 4: Branding Agent Formats
# ============================================
branding_prompt = f"""
You are a Branding Agent.

Response to format: "{response}"
Channel: SMS
Brand voice: Professional but friendly

Your task:
Format this response appropriately for SMS (160 char limit, clear, concise).
"""

formatted = await llm.generate(branding_prompt)

# ============================================
# STEP 5: Quality Agent Validates
# ============================================
quality_prompt = f"""
You are a Quality Agent.

Original question: "Check my timesheet for last week"
Proposed response: "{formatted}"

Validation criteria:
- Answers the question
- Factually accurate based on data
- Appropriate tone
- Correct length for channel

Does this response pass quality checks? Return JSON:
{{"passed": true/false, "issues": ["list of issues if any"]}}
"""

validation = await llm.generate(quality_prompt)
```

---

## Key Principles

### 1. No Hardcoded Structures
- ❌ No `query_type` enums
- ❌ No `requires_timesheet_data` flags
- ❌ No predefined `parameters` dicts
- ❌ No `if/elif` chains in agent code

### 2. Natural Language Communication
- ✅ Agents send messages to each other
- ✅ Each agent uses LLM to understand messages
- ✅ Each agent uses LLM to decide actions

### 3. Workflow is Just a Message Router
```python
@workflow.defn
class MultiAgentConversationWorkflow:
    async def run(self, user_message: str, user_context: dict):
        # Step 1: Planner analyzes
        planner_analysis = await execute_activity(
            planner_analyze,
            args=[user_message, user_context]
        )
        
        # Step 2: If Planner needs help, route to appropriate agent
        if planner_analysis['needs_help']:
            agent_name = planner_analysis['agent_to_contact']
            agent_message = planner_analysis['message_to_agent']
            
            agent_response = await execute_activity(
                f"{agent_name}_execute",
                args=[agent_message, user_context]
            )
        else:
            agent_response = None
        
        # Step 3: Planner composes
        response = await execute_activity(
            planner_compose,
            args=[user_message, agent_response, user_context]
        )
        
        # Step 4: Branding formats
        formatted = await execute_activity(
            branding_format,
            args=[response, user_context['channel']]
        )
        
        # Step 5: Quality validates
        validation = await execute_activity(
            quality_validate,
            args=[formatted, user_message]
        )
        
        if validation['passed']:
            return formatted
        else:
            # Refine once if needed
            refined = await execute_activity(
                planner_refine,
                args=[formatted, validation['issues']]
            )
            return refined
```

---

## What We Change

### In Planner Agent
- Remove: Structured execution plans
- Add: Natural language messages to other agents

### In Timesheet Agent
- Remove: `query_type` parameter
- Remove: `if query_type == "hours_logged"` logic
- Add: LLM-based tool selection

### In Workflow
- Remove: Interpreting structured plans
- Add: Simple message routing

### In All Agents
- Remove: Hardcoded logic
- Add: LLM prompts that make decisions

---

## Benefits

1. **Flexibility**: Add new query types without code changes
2. **Maintainability**: Only edit prompts, not code
3. **Intelligence**: Agents handle edge cases automatically
4. **Scalability**: Easy to add new agents or tools
5. **True Multi-Agent**: Agents actually collaborate, not follow scripts
