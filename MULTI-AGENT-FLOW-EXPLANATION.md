# Multi-Agent Conversation Flow - Step-by-Step Explanation
## Complete SMS Conversation Journey

**Date:** December 9, 2025  
**Example:** User sends "Check my timesheet" via SMS  
**System:** 4-Agent Multi-Agent Architecture

---

## 🎯 **Overview**

This document explains **exactly what happens** when a user sends an SMS message to the timesheet assistant, from the moment they hit "send" to when they receive a response.

**Total Steps:** 11 main steps  
**Total Participants:** 11 components  
**Average Time:** 3-5 seconds  
**LLM Calls:** 7-13 (depending on validation results)

---

## 📱 **The Journey Begins: User Sends SMS**

### **Step 0: User Action**

```
User's Phone
├── User types: "Check my timesheet"
├── User presses Send
└── SMS sent to Twilio phone number (+61...)
```

**What happens:**
- User's phone sends SMS to your Twilio number
- Twilio receives the message
- Twilio immediately sends a webhook to your server

**Data at this point:**
```json
{
  "From": "+61412345678",
  "To": "+61987654321",
  "Body": "Check my timesheet",
  "MessageSid": "SM1234567890abcdef",
  "AccountSid": "AC...",
  "NumMedia": "0"
}
```

---

## 🌐 **Step 1: Twilio Webhook → Server**

### **What Happens:**

Twilio makes an HTTP POST request to your server:

```http
POST https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms
Content-Type: application/x-www-form-urlencoded

From=+61412345678&To=+61987654321&Body=Check+my+timesheet&MessageSid=SM1234...
```

**Server receives webhook:**

```python
# unified_server.py - Line ~150
@api.post("/webhook/sms")
async def handle_sms_webhook(request: Request):
    form_data = await request.form()
    
    from_number = form_data.get("From")      # "+61412345678"
    message_body = form_data.get("Body")     # "Check my timesheet"
    sms_sid = form_data.get("MessageSid")    # "SM1234..."
```

**Time elapsed:** ~100ms

---

## 🔍 **Step 2: Lookup User in Database**

### **What Happens:**

Server queries Supabase to find the user by phone number:

```python
# Query users table
user_data = supabase_client.table("users") \
    .select("id, full_name, phone_number, harvest_account_id, harvest_access_token, timezone") \
    .eq("phone_number", from_number) \
    .single() \
    .execute()
```

**Database returns:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "John Smith",
  "phone_number": "+61412345678",
  "harvest_account_id": "1234567",
  "harvest_access_token": "Bearer abc123...",
  "timezone": "Australia/Sydney"
}
```

**Why this matters:**
- We need the user's ID to track conversations
- We need Harvest credentials to access their timesheet
- We need timezone for date calculations

**Time elapsed:** ~200ms (database query)

---

## 🚀 **Step 3: Start Temporal Workflow**

### **What Happens:**

Server starts a Temporal workflow (asynchronous, durable execution):

```python
# Start workflow
workflow_handle = await temporal_client.start_workflow(
    MultiAgentConversationWorkflow.run,
    args=[
        user_message="Check my timesheet",
        channel="sms",
        user_id="550e8400-e29b-41d4-a716-446655440000",
        conversation_id="sms_SM1234...",
        conversation_history=[],  # Loaded later
        user_context={
            "from": "+61412345678",
            "credentials": {
                "harvest_account": "1234567",
                "harvest_token": "Bearer abc123...",
                "timezone": "Australia/Sydney"
            }
        }
    ],
    id=f"conversation-sms_SM1234...",
    task_queue="unified-task-queue"
)
```

**Server immediately returns 200 OK to Twilio:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>
```

**Why this matters:**
- Twilio webhook must respond within 15 seconds
- Workflow runs asynchronously (can take longer)
- Temporal ensures workflow completes even if server crashes

**Time elapsed:** ~50ms (workflow start is fast)

---

## 🔄 **WORKFLOW BEGINS: Multi-Agent Orchestration**

From here, everything happens inside the Temporal workflow...

---

## 📦 **STEP 0: Enrich User Context**

### **What Happens:**

Workflow ensures it has all necessary user data:

```python
# Check if credentials are already provided
if not user_context.get("credentials"):
    # Fetch from database
    credentials_result = await workflow.execute_activity(
        get_user_credentials_activity,
        args=[user_id],
        start_to_close_timeout=timedelta(seconds=2)
    )
    user_context["credentials"] = credentials_result

# Add current date (deterministic - uses workflow.now())
user_context["current_date"] = workflow.now().strftime("%Y-%m-%d")  # "2025-12-09"

# Ensure timezone is set
if not user_context.get("timezone"):
    user_context["timezone"] = "UTC"
```

**User context now contains:**
```json
{
  "from": "+61412345678",
  "credentials": {
    "harvest_account": "1234567",
    "harvest_token": "Bearer abc123...",
    "harvest_user_id": 9876543,
    "timezone": "Australia/Sydney"
  },
  "current_date": "2025-12-09",
  "timezone": "Australia/Sydney"
}
```

**Why this matters:**
- Agents need credentials to call Harvest API
- Current date is needed for "this week", "today", etc.
- Timezone ensures correct date calculations

**Time elapsed:** ~100ms (if credentials already provided, 0ms)

---

## 🎯 **STEP 1: Planner Analyzes Request**

### **What Happens:**

Workflow calls Planner Agent to analyze the user's request:

```python
plan_result = await workflow.execute_activity(
    planner_analyze_activity,
    args=[request_id, user_message, channel, conversation_history, user_context],
    start_to_close_timeout=timedelta(seconds=5)
)
```

**Inside Planner Agent:**

#### **A. Check for SOP Match**

Planner first checks if this matches a Standard Operating Procedure:

```python
# agents/planner.py
sops = {
    "check_timesheet": {
        "triggers": ["check timesheet", "my timesheet", "hours logged", ...],
        "needs_data": True,
        "message_to_timesheet": "Execute list_time_entries tool: ...",
        "criteria": [...]
    },
    ...
}

# Check if user message matches any SOP trigger
for sop_name, sop in sops.items():
    for trigger in sop["triggers"]:
        if trigger.lower() in user_message.lower():
            # MATCH! Use this SOP
            return {
                "needs_data": sop["needs_data"],
                "message_to_timesheet": sop["message_to_timesheet"],
                "criteria": sop["criteria"]
            }
```

**For "Check my timesheet":**
- ✅ Matches `check_timesheet` SOP
- ✅ Uses predefined message and criteria
- ✅ **No LLM call needed** (saves time and cost!)

**SOP provides:**
```json
{
  "needs_data": true,
  "message_to_timesheet": "Execute list_time_entries tool:\n\nINPUT FORMAT:\n- tool: list_time_entries\n- from_date: Start of current week (Monday)\n- to_date: Today\n- user_id: Current user's ID\n\nOUTPUT FORMAT:\nReturn complete Harvest API response with all entries.",
  "criteria": [
    {
      "id": "data_completeness",
      "description": "Response includes all timesheet entries OR provides a summary if many entries OR clearly states if there are no entries",
      "expected": "For 1-5 entries: list all with details. For 6+ entries: provide summary. For 0 entries: explicitly state 'no entries'"
    },
    {
      "id": "time_period_clarity",
      "description": "Response clearly states the time period covered",
      "expected": "Date range is mentioned (e.g., 'Dec 4-9' or 'this week')"
    },
    {
      "id": "sms_format",
      "description": "Response is formatted appropriately for SMS",
      "expected": "Concise, clear, and easy to read on mobile"
    }
  ]
}
```

#### **B. If No SOP Match (Alternative Path)**

If the message didn't match any SOP, Planner would use LLM:

```python
prompt = f"""You are a Planner Agent coordinating a multi-agent team.

User's request: "Check my timesheet"
Channel: sms

Available agents:
- Timesheet Agent: Can retrieve data from Harvest API (51 tools available)
- Branding Agent: Can format responses for different channels
- Quality Agent: Can validate response quality

Your task:
1. Analyze the user's request
2. Decide if you need data from the Timesheet Agent
3. If yes, write a clear, specific message to the Timesheet Agent
4. Create quality validation criteria

Return JSON:
{
    "needs_data": true/false,
    "message_to_timesheet": "...",
    "criteria": [...]
}
"""

llm_response = await self.llm_client.generate(prompt)
```

**Planner returns to Workflow:**
```json
{
  "execution_plan": {
    "request_id": "abc-123",
    "needs_data": true,
    "message_to_timesheet": "Execute list_time_entries tool: ...",
    "user_message": "Check my timesheet",
    "channel": "sms"
  },
  "scorecard": {
    "request_id": "abc-123",
    "criteria": [
      {"id": "data_completeness", "description": "...", "expected": "..."},
      {"id": "time_period_clarity", "description": "...", "expected": "..."},
      {"id": "sms_format", "description": "...", "expected": "..."}
    ]
  }
}
```

**Why this matters:**
- Planner decides if we need to call Harvest API
- Planner creates quality criteria upfront
- SOPs make common queries faster and cheaper

**Time elapsed:** ~0ms (SOP match) or ~800ms (LLM call)

---

## 📊 **STEP 2: Timesheet Agent Extracts Data**

### **What Happens:**

Since `needs_data = true`, Workflow routes Planner's message to Timesheet Agent:

```python
if execution_plan.get("needs_data"):
    planner_message = execution_plan.get("message_to_timesheet")
    
    timesheet_result = await workflow.execute_activity(
        timesheet_execute_activity,
        args=[request_id, planner_message, user_context],
        start_to_close_timeout=timedelta(seconds=10)
    )
```

**Inside Timesheet Agent:**

#### **A. LLM Decides Which Tool to Call**

Timesheet Agent receives Planner's natural language instruction:

```
"Execute list_time_entries tool:

INPUT FORMAT:
- tool: list_time_entries
- from_date: Start of current week (Monday)
- to_date: Today
- user_id: Current user's ID

OUTPUT FORMAT:
Return complete Harvest API response with all entries."
```

Timesheet Agent uses LLM to parse this:

```python
prompt = f"""You are a Timesheet Tool Execution Specialist with access to ALL 51 Harvest API tools.

PLANNER'S INSTRUCTION:
"{planner_message}"

CONTEXT:
- User's timezone: Australia/Sydney
- Today's date: 2025-12-09

COMPLETE HARVEST API TOOL CATALOG (51 tools):

TIME ENTRIES (7 tools):
- list_time_entries(from_date, to_date, user_id=None) - List entries in date range
- get_time_entry(time_entry_id) - Get specific entry
- create_time_entry(project_id, task_id, spent_date, hours, notes=None) - Create entry
...

[Full catalog of 51 tools]

Your task:
1. Understand what the Planner is asking for
2. Decide which tool to call
3. Extract parameters from the instruction

Return JSON:
{
    "tool_name": "list_time_entries",
    "tool_args": {
        "from_date": "2025-12-02",  // Monday of current week
        "to_date": "2025-12-09",    // Today
        "user_id": 9876543
    }
}
"""

llm_response = await self.llm_client.generate(prompt)
```

**LLM returns:**
```json
{
  "tool_name": "list_time_entries",
  "tool_args": {
    "from_date": "2025-12-02",
    "to_date": "2025-12-09",
    "user_id": 9876543
  }
}
```

#### **B. Execute Tool via Harvest MCP**

Timesheet Agent finds the tool and executes it:

```python
# Find tool by name
for tool in self.harvest_tools:
    if tool.name == "list_time_entries":
        # Execute tool
        result = await tool.ainvoke({
            "from_date": "2025-12-02",
            "to_date": "2025-12-09",
            "user_id": 9876543
        })
```

**Tool makes HTTP call to Harvest MCP:**

```http
POST http://harvest-mcp.internal.../api/list_time_entries
Content-Type: application/json

{
  "harvest_account": "1234567",
  "harvest_token": "Bearer abc123...",
  "from_date": "2025-12-02",
  "to_date": "2025-12-09",
  "user_id": 9876543
}
```

**Harvest MCP returns:**
```json
{
  "time_entries": [
    {
      "id": 111,
      "spent_date": "2025-12-02",
      "hours": 8.0,
      "project": {"id": 456, "name": "Alpha Project"},
      "task": {"id": 789, "name": "Development"},
      "notes": "Worked on authentication module"
    },
    {
      "id": 222,
      "spent_date": "2025-12-03",
      "hours": 7.5,
      "project": {"id": 456, "name": "Alpha Project"},
      "task": {"id": 789, "name": "Development"},
      "notes": "Bug fixes"
    },
    {
      "id": 333,
      "spent_date": "2025-12-04",
      "hours": 8.0,
      "project": {"id": 457, "name": "Beta Project"},
      "task": {"id": 790, "name": "Design"},
      "notes": "UI mockups"
    },
    {
      "id": 444,
      "spent_date": "2025-12-05",
      "hours": 6.0,
      "project": {"id": 456, "name": "Alpha Project"},
      "task": {"id": 789, "name": "Development"},
      "notes": "Code review"
    },
    {
      "id": 555,
      "spent_date": "2025-12-09",
      "hours": 5.5,
      "project": {"id": 457, "name": "Beta Project"},
      "task": {"id": 790, "name": "Design"},
      "notes": "Client feedback implementation"
    }
  ],
  "total_hours": 35.0,
  "week_start": "2025-12-02",
  "week_end": "2025-12-09"
}
```

**Timesheet Agent returns to Workflow:**
```json
{
  "success": true,
  "data": {
    "harvest_response": {
      "time_entries": [...],
      "total_hours": 35.0,
      "week_start": "2025-12-02",
      "week_end": "2025-12-09"
    },
    "query_parameters": {
      "from_date": "2025-12-02",
      "to_date": "2025-12-09",
      "user_id": 9876543
    },
    "tool_used": "list_time_entries"
  }
}
```

**Why this matters:**
- LLM dynamically chooses the right tool (no hardcoded logic)
- Harvest MCP handles API authentication and rate limiting
- Structured data is returned for Planner to use

**Time elapsed:** ~1200ms (LLM call ~800ms + MCP call ~400ms)

---

## ✍️ **STEP 3: Planner Composes Response**

### **What Happens:**

Workflow sends the Harvest data back to Planner to compose a response:

```python
compose_result = await workflow.execute_activity(
    planner_compose_activity,
    args=[request_id, user_message, timesheet_data, conversation_history, user_context],
    start_to_close_timeout=timedelta(seconds=5)
)
```

**Inside Planner Agent:**

Planner uses LLM to compose a natural language response from the data:

```python
# Extract harvest response
harvest_response = timesheet_data.get("harvest_response")

prompt = f"""You are composing a response to a user's timesheet query.

USER ASKED:
"Check my timesheet"

HARVEST DATA:
{json.dumps(harvest_response, indent=2)}

CONTEXT:
- User's name: John Smith
- Timezone: Australia/Sydney
- Channel: SMS (keep it concise)

Your task:
Compose a helpful, accurate response using this data.

Guidelines:
- Be specific about dates, hours, and projects
- Use natural language (not JSON)
- Be concise for SMS
- Include all important details

Example good response:
"You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5h (Development)
- Beta Project: 13.5h (Design)

Great work! 💪"
"""

llm_response = await self.llm_client.generate(prompt)
```

**LLM returns:**
```
"You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5 hours (Development, code review)
- Beta Project: 13.5 hours (Design, UI work)

You're on track! Keep it up! 💪"
```

**Planner returns to Workflow:**
```json
{
  "response": "You logged 35 hours this week (Dec 2-9):\n- Alpha Project: 21.5 hours (Development, code review)\n- Beta Project: 13.5 hours (Design, UI work)\n\nYou're on track! Keep it up! 💪"
}
```

**Why this matters:**
- LLM composes natural, contextual responses
- Data is transformed into user-friendly format
- Response is tailored to the user's question

**Time elapsed:** ~900ms (LLM call)

---

## 🎨 **STEP 4: Branding Agent Formats for Channel**

### **What Happens:**

Workflow sends the response to Branding Agent for channel-specific formatting:

```python
branding_result = await workflow.execute_activity(
    branding_format_activity,
    args=[request_id, response, channel, user_context],
    start_to_close_timeout=timedelta(seconds=5)
)
```

**Inside Branding Agent:**

Branding Agent uses LLM to format for SMS:

```python
prompt = f"""You are a Branding Specialist formatting responses for different communication channels.

Response to format:
"You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5 hours (Development, code review)
- Beta Project: 13.5 hours (Design, UI work)

You're on track! Keep it up! 💪"

Channel: sms

Channel requirements and constraints:
- SMS: Plain text only, max 1600 characters, no markdown, be concise and clear

Brand voice: Professional but friendly, clear and helpful

Your task:
1. Format the response appropriately for SMS
2. Apply the brand voice
3. Ensure it meets channel constraints (length, formatting)
4. If too long, intelligently truncate or split

Return JSON:
{
    "formatted_content": "the formatted response text",
    "is_split": false,
    "parts": []
}
"""

llm_response = await self.llm_client.generate(prompt)
```

**LLM returns:**
```json
{
  "formatted_content": "You logged 35 hours this week (Dec 2-9):\n- Alpha Project: 21.5h (Development, code review)\n- Beta Project: 13.5h (Design, UI work)\n\nYou're on track! Keep it up! 💪",
  "is_split": false,
  "parts": []
}
```

**Changes made:**
- ✅ "hours" → "h" (more concise for SMS)
- ✅ Kept emoji (appropriate for SMS)
- ✅ No markdown formatting
- ✅ Under 1600 characters (160 characters)

**Branding Agent returns to Workflow:**
```json
{
  "formatted_response": {
    "content": "You logged 35 hours this week (Dec 2-9):\n- Alpha Project: 21.5h (Development, code review)\n- Beta Project: 13.5h (Design, UI work)\n\nYou're on track! Keep it up! 💪",
    "is_split": false,
    "parts": [],
    "channel": "sms"
  }
}
```

**Why this matters:**
- Consistent formatting across all channels
- Respects channel constraints (length, markdown support)
- Applies brand voice

**Time elapsed:** ~700ms (LLM call)

---

## ✅ **STEP 5: Quality Agent Validates**

### **What Happens:**

Workflow sends the formatted response to Quality Agent for validation:

```python
validation_result = await workflow.execute_activity(
    quality_validate_activity,
    args=[request_id, formatted_response["content"], scorecard, channel, user_message],
    start_to_close_timeout=timedelta(seconds=2)
)
```

**Inside Quality Agent:**

Quality Agent evaluates each criterion from the scorecard:

#### **Criterion 1: data_completeness**

```python
criterion = {
    "id": "data_completeness",
    "description": "Response includes all timesheet entries OR provides a summary if many entries OR clearly states if there are no entries",
    "expected": "For 1-5 entries: list all with details. For 6+ entries: provide summary. For 0 entries: explicitly state 'no entries'"
}

prompt = f"""You are a Quality Assurance Specialist.

CRITERION TO EVALUATE:
ID: data_completeness
Description: {criterion["description"]}
Expected: {criterion["expected"]}

RESPONSE TO VALIDATE:
"You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5h (Development, code review)
- Beta Project: 13.5h (Design, UI work)

You're on track! Keep it up! 💪"

CONTEXT:
- Channel: sms
- Original question: "Check my timesheet"
- Number of entries: 5

Your task:
Evaluate if the response meets this criterion.

Return JSON:
{{
    "passed": true/false,
    "feedback": "specific feedback if failed"
}}
"""

llm_response = await self.llm_client.generate(prompt)
```

**LLM returns:**
```json
{
  "passed": true,
  "feedback": ""
}
```

**Reasoning:** Response provides a summary (5 entries grouped by project), which is appropriate.

#### **Criterion 2: time_period_clarity**

```python
criterion = {
    "id": "time_period_clarity",
    "description": "Response clearly states the time period covered",
    "expected": "Date range is mentioned (e.g., 'Dec 4-9' or 'this week')"
}

# Same LLM evaluation process...
```

**LLM returns:**
```json
{
  "passed": true,
  "feedback": ""
}
```

**Reasoning:** Response clearly states "this week (Dec 2-9)".

#### **Criterion 3: sms_format**

```python
criterion = {
    "id": "sms_format",
    "description": "Response is formatted appropriately for SMS",
    "expected": "Concise, clear, and easy to read on mobile"
}

# Same LLM evaluation process...
```

**LLM returns:**
```json
{
  "passed": true,
  "feedback": ""
}
```

**Reasoning:** Response is concise, uses abbreviations, and is easy to read.

#### **Overall Validation Result**

```python
overall_passed = all([
    criterion1.passed,  # True
    criterion2.passed,  # True
    criterion3.passed   # True
])
# overall_passed = True
```

**Quality Agent returns to Workflow:**
```json
{
  "validation_result": {
    "passed": true,
    "scorecard_id": "abc-123",
    "failed_criteria_ids": []
  },
  "failed_criteria": []
}
```

**Why this matters:**
- Automated quality assurance
- Catches issues before sending to user
- Provides specific feedback for improvement

**Time elapsed:** ~600ms (3 LLM calls, one per criterion)

---

## 🔄 **STEP 6: Refinement Loop (If Validation Failed)**

### **What Happens (Alternative Path):**

If validation had failed, Workflow would trigger refinement:

```python
if not validation["passed"]:
    # Get failed criteria
    failed_criteria = validation_result.get("failed_criteria", [])
    
    # Refine response
    refine_result = await workflow.execute_activity(
        planner_refine_activity,
        args=[request_id, response, failed_criteria, 1],
        start_to_close_timeout=timedelta(seconds=5)
    )
    
    refined_response = refine_result["refined_response"]
    
    # Reformat
    rebranding_result = await workflow.execute_activity(
        branding_format_activity,
        args=[request_id, refined_response, channel, user_context],
        start_to_close_timeout=timedelta(seconds=5)
    )
    
    formatted_response = rebranding_result["formatted_response"]
    
    # Revalidate
    revalidation_result = await workflow.execute_activity(
        quality_validate_activity,
        args=[request_id, formatted_response["content"], scorecard, channel, user_message],
        start_to_close_timeout=timedelta(seconds=2)
    )
    
    validation = revalidation_result["validation_result"]
```

**Example Refinement:**

If `data_completeness` failed because response didn't mention all projects:

**Planner receives:**
```json
{
  "failed_criteria": [
    {
      "id": "data_completeness",
      "description": "Response includes all timesheet entries...",
      "expected": "For 1-5 entries: list all with details...",
      "feedback": "Response only mentions 2 projects but user has entries in 3 projects"
    }
  ]
}
```

**Planner refines:**
```python
prompt = f"""You are refining a response that failed quality validation.

ORIGINAL RESPONSE:
"{original_response}"

FAILED CRITERIA:
{json.dumps(failed_criteria, indent=2)}

Your task:
Refine the response to fix the issues mentioned in the failed criteria.

Return the refined response.
"""

refined = await self.llm_client.generate(prompt)
```

**Refined response:**
```
"You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5h (Development, code review)
- Beta Project: 13.5h (Design, UI work)
- Gamma Project: 0h (no entries)

You're on track! Keep it up! 💪"
```

**Then:** Reformat → Revalidate → If still fails → Graceful failure

**In our example:** Validation passed, so we skip this step.

**Time elapsed:** ~0ms (skipped)

---

## 🚨 **STEP 7: Graceful Failure (If Still Failed)**

### **What Happens (Alternative Path):**

If validation still failed after refinement, Workflow would compose a graceful failure:

```python
if not validation["passed"]:
    failure_result = await workflow.execute_activity(
        planner_graceful_failure_activity,
        args=[request_id, user_message, "validation_failed", channel],
        start_to_close_timeout=timedelta(seconds=3)
    )
    
    final_response = failure_result["failure_message"]
```

**Planner composes graceful failure:**
```python
prompt = f"""You are composing a graceful failure message.

USER ASKED:
"Check my timesheet"

FAILURE REASON:
validation_failed (response quality did not meet standards)

CHANNEL:
sms

Your task:
Compose a helpful, apologetic message that:
1. Acknowledges the issue
2. Doesn't expose technical details
3. Suggests what the user can do
4. Maintains brand voice

Return the failure message.
"""

failure_message = await self.llm_client.generate(prompt)
```

**Example graceful failure:**
```
"I apologize, but I'm having trouble processing your timesheet request right now. Please try again in a moment, or contact support if the issue persists."
```

**Quality validates graceful failure:**
- Ensures it's helpful
- Ensures it doesn't expose errors
- Ensures it's appropriate for channel

**In our example:** Validation passed, so we skip this step.

**Time elapsed:** ~0ms (skipped)

---

## 📤 **STEP 8: Send Response via Twilio**

### **What Happens:**

Workflow sends the final response via SMS:

```python
to_number = user_context["from"]  # "+61412345678"
final_response = formatted_response["content"]

sms_result = await workflow.execute_activity(
    send_sms_response_activity,
    args=[to_number, final_response, request_id],
    start_to_close_timeout=timedelta(seconds=10),
    retry_policy=RetryPolicy(
        maximum_attempts=3,
        initial_interval=timedelta(seconds=1),
        maximum_interval=timedelta(seconds=10)
    )
)
```

**Inside send_sms_response_activity:**

```python
from twilio.rest import Client

# Get Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
from_number = os.getenv('TWILIO_PHONE_NUMBER')

# Create Twilio client
client = Client(account_sid, auth_token)

# Send SMS
sms_message = client.messages.create(
    body=final_response,
    from_=from_number,  # "+61987654321"
    to=to_number        # "+61412345678"
)
```

**Twilio API call:**
```http
POST https://api.twilio.com/2010-04-01/Accounts/AC.../Messages.json
Authorization: Basic [base64(account_sid:auth_token)]
Content-Type: application/x-www-form-urlencoded

From=+61987654321&To=+61412345678&Body=You+logged+35+hours...
```

**Twilio returns:**
```json
{
  "sid": "SM9876543210fedcba",
  "status": "queued",
  "to": "+61412345678",
  "from": "+61987654321",
  "body": "You logged 35 hours this week (Dec 2-9):\n- Alpha Project: 21.5h (Development, code review)\n- Beta Project: 13.5h (Design, UI work)\n\nYou're on track! Keep it up! 💪",
  "date_created": "2025-12-09T12:34:56Z"
}
```

**Activity returns to Workflow:**
```json
{
  "success": true,
  "message_sid": "SM9876543210fedcba",
  "status": "queued"
}
```

**User receives SMS on their phone:**
```
You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5h (Development, code review)
- Beta Project: 13.5h (Design, UI work)

You're on track! Keep it up! 💪
```

**Why this matters:**
- Twilio handles SMS delivery
- Retry policy ensures delivery even if Twilio is temporarily down
- Message SID allows tracking delivery status

**Time elapsed:** ~500ms (Twilio API call)

---

## 💾 **STEP 9: Store Conversation in Database**

### **What Happens:**

Workflow stores both the user's message and the response in Supabase:

```python
store_result = await workflow.execute_activity(
    store_conversation,
    args=[user_id, user_message, final_response, channel, conversation_id, user_context],
    start_to_close_timeout=timedelta(seconds=5),
    retry_policy=RetryPolicy(maximum_attempts=2)
)
```

**Inside store_conversation activity:**

#### **A. Store INBOUND message (user's message)**

```python
inbound_data = {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "platform": "SMS",
    "message_type": "INBOUND",
    "content": "Check my timesheet",
    "metadata": {"conversation_id": "sms_SM1234..."},
    "sms_sid": "SM1234...",
    "phone_number": "+61412345678"
}

supabase_client.table("conversation_context").insert(inbound_data).execute()
```

**Database record created:**
```sql
INSERT INTO conversation_context (
    id, user_id, platform, message_type, content, metadata, sms_sid, phone_number, created_at
) VALUES (
    'uuid-1',
    '550e8400-e29b-41d4-a716-446655440000',
    'SMS',
    'INBOUND',
    'Check my timesheet',
    '{"conversation_id": "sms_SM1234..."}',
    'SM1234...',
    '+61412345678',
    '2025-12-09 12:34:56'
);
```

#### **B. Store OUTBOUND message (assistant's response)**

```python
outbound_data = {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "platform": "SMS",
    "message_type": "OUTBOUND",
    "content": "You logged 35 hours this week (Dec 2-9):\n- Alpha Project: 21.5h (Development, code review)\n- Beta Project: 13.5h (Design, UI work)\n\nYou're on track! Keep it up! 💪",
    "metadata": {
        "conversation_id": "sms_SM1234...",
        "validation_passed": true,
        "refinement_attempted": false
    },
    "sms_sid": "SM9876543210fedcba",
    "phone_number": "+61412345678"
}

supabase_client.table("conversation_context").insert(outbound_data).execute()
```

**Database record created:**
```sql
INSERT INTO conversation_context (
    id, user_id, platform, message_type, content, metadata, sms_sid, phone_number, created_at
) VALUES (
    'uuid-2',
    '550e8400-e29b-41d4-a716-446655440000',
    'SMS',
    'OUTBOUND',
    'You logged 35 hours this week...',
    '{"conversation_id": "sms_SM1234...", "validation_passed": true, "refinement_attempted": false}',
    'SM9876543210fedcba',
    '+61412345678',
    '2025-12-09 12:34:57'
);
```

**Activity returns to Workflow:**
```json
{
  "status": "success",
  "records_stored": 2
}
```

**Why this matters:**
- Conversation history enables context-aware responses
- Audit trail for debugging and analytics
- Cross-platform conversation tracking

**Time elapsed:** ~300ms (2 database inserts)

---

## 📊 **STEP 10: Log Metrics**

### **What Happens:**

Workflow logs conversation metrics for monitoring:

```python
await workflow.execute_activity(
    log_conversation_metrics,
    args=[channel, len(user_message), len(final_response)],
    start_to_close_timeout=timedelta(seconds=5)
)
```

**Inside log_conversation_metrics activity:**

```python
metrics = {
    "channel": "sms",
    "message_length": 18,  # "Check my timesheet"
    "response_length": 160,
    "timestamp": datetime.utcnow().isoformat()
}

# Log to monitoring system (e.g., CloudWatch, Datadog, etc.)
logger.info(f"📊 Conversation metrics: {json.dumps(metrics)}")
```

**Metrics logged:**
```json
{
  "channel": "sms",
  "message_length": 18,
  "response_length": 160,
  "timestamp": "2025-12-09T01:34:57Z"
}
```

**Why this matters:**
- Monitor conversation volume
- Track response lengths (important for SMS costs)
- Identify trends and patterns

**Time elapsed:** ~50ms (logging)

---

## ✅ **STEP 11: Return Result**

### **What Happens:**

Workflow returns the final result:

```python
return {
    "request_id": "abc-123",
    "final_response": "You logged 35 hours this week (Dec 2-9):\n- Alpha Project: 21.5h (Development, code review)\n- Beta Project: 13.5h (Design, UI work)\n\nYou're on track! Keep it up! 💪",
    "validation_passed": true,
    "refinement_attempted": false,
    "graceful_failure": false,
    "metadata": {
        "channel": "sms",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "conversation_id": "sms_SM1234..."
    }
}
```

**Workflow completes successfully.**

**Temporal UI shows:**
- ✅ Workflow status: Completed
- ✅ Duration: ~4.5 seconds
- ✅ Activities: 10 activities executed
- ✅ Result: Success

**Time elapsed:** ~0ms (return is instant)

---

## 🎉 **Journey Complete!**

### **Total Time Breakdown:**

| Step | Component | Time | LLM Calls |
|------|-----------|------|-----------|
| 0 | User sends SMS | ~100ms | 0 |
| 1 | Twilio webhook | ~100ms | 0 |
| 2 | Database lookup | ~200ms | 0 |
| 3 | Start workflow | ~50ms | 0 |
| **Workflow Step 0** | Enrich context | ~100ms | 0 |
| **Workflow Step 1** | Planner analyze | ~0ms (SOP) | 0 (SOP match) |
| **Workflow Step 2** | Timesheet execute | ~1200ms | 1 |
| **Workflow Step 3** | Planner compose | ~900ms | 1 |
| **Workflow Step 4** | Branding format | ~700ms | 1 |
| **Workflow Step 5** | Quality validate | ~600ms | 3 |
| **Workflow Step 6** | Refinement | ~0ms (skipped) | 0 |
| **Workflow Step 7** | Graceful failure | ~0ms (skipped) | 0 |
| **Workflow Step 8** | Send SMS | ~500ms | 0 |
| **Workflow Step 9** | Store conversation | ~300ms | 0 |
| **Workflow Step 10** | Log metrics | ~50ms | 0 |
| **Workflow Step 11** | Return result | ~0ms | 0 |
| **TOTAL** | | **~4.8 seconds** | **6 LLM calls** |

---

## 📈 **What User Experiences:**

```
[12:34:56] User: "Check my timesheet" → Send

[12:34:56 - 12:35:01] ... (4.8 seconds of processing)

[12:35:01] Assistant: "You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5h (Development, code review)
- Beta Project: 13.5h (Design, UI work)

You're on track! Keep it up! 💪"
```

**User perception:** ~5 seconds from send to receive (acceptable for SMS)

---

## 🔍 **Behind the Scenes:**

### **What Happened:**

1. ✅ **11 participants** worked together
2. ✅ **11 workflow steps** executed
3. ✅ **6 LLM calls** made decisions
4. ✅ **1 Harvest API call** retrieved data
5. ✅ **2 database queries** (lookup + store)
6. ✅ **1 SMS sent** via Twilio
7. ✅ **Quality validated** before sending
8. ✅ **Conversation stored** for future context

### **What Made It Possible:**

- 🤖 **4 specialized agents** (Planner, Timesheet, Branding, Quality)
- 🔄 **Temporal workflow** (reliability, durability, observability)
- 🧠 **Centralized LLM client** (rate limiting, caching, tracing)
- 📊 **Harvest MCP** (API abstraction)
- 💾 **Supabase** (user data, conversation history)
- 📱 **Twilio** (SMS delivery)

### **What Ensures Quality:**

- ✅ **SOPs** for common queries (faster, cheaper, consistent)
- ✅ **Scorecard validation** (automated QA)
- ✅ **Refinement loop** (self-improving)
- ✅ **Graceful failures** (better UX)
- ✅ **Channel formatting** (consistent branding)
- ✅ **Conversation history** (context-aware)

---

## 🎯 **Key Takeaways:**

### **1. Multi-Agent = Better Quality**

Each agent has **one job** and does it well:
- Planner: Decide what to do
- Timesheet: Get the data
- Branding: Format for channel
- Quality: Validate before sending

### **2. LLM-Driven = More Flexible**

No hardcoded logic:
- Planner decides if data is needed
- Timesheet chooses which tool to call
- Branding formats appropriately
- Quality validates against criteria

### **3. Validation = Guaranteed Quality**

Every response is validated before sending:
- Scorecard defines quality criteria
- Quality agent evaluates each criterion
- Refinement loop fixes issues
- Graceful failures if still not good enough

### **4. Temporal = Reliability**

Workflow ensures completion:
- Automatic retries on failures
- Durable execution (survives crashes)
- Timeout protection
- Full observability

### **5. Context = Better Responses**

System uses context at every step:
- User credentials for API calls
- Conversation history for context
- Timezone for date calculations
- Channel for formatting

---

## 🚀 **What's Next?**

This same flow works for:
- ✅ **Email** (different formatting, same agents)
- ✅ **WhatsApp** (different formatting, same agents)
- ✅ **Teams** (different formatting, same agents)

The multi-agent architecture makes it easy to:
- 🔧 **Add new agents** (e.g., Translation Agent)
- 📊 **Add new tools** (e.g., Jira integration)
- 🎨 **Update branding** (just change config files)
- ✅ **Add new criteria** (just update scorecards)

**Your system is production-ready and built to scale!** 🎉

---

## 📚 **Related Documents:**

- **Architecture Overview:** `MULTI-AGENT-SYSTEM-ANALYSIS.md`
- **Sequence Diagram:** `MULTI-AGENT-SYSTEM-ANALYSIS.md` (lines 181-449)
- **LLM Client Analysis:** `LLM-CLIENT-INTEGRATION-ANALYSIS.md`
- **Deployment Guide:** `AZURE-DEPLOYMENT-GUIDE.md`
- **Local Setup:** `LOCAL-SETUP-GUIDE.md`
