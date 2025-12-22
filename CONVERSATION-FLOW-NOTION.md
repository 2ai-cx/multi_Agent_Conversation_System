# Multi-Agent Conversation Flow - Simple Explanation

How SMS Conversations Work (No Code!)

**Date:** December 9, 2025  
**Example:** User sends "Check my timesheet" via SMS  

---

# The Big Picture

When a user sends an SMS, **4 specialized AI agents** work together to create the perfect response:

1. **Planner Agent** - Decides what needs to be done
2. **Timesheet Agent** - Gets data from Harvest
3. **Branding Agent** - Formats for SMS
4. **Quality Agent** - Validates before sending

**Total time:** ~5 seconds from send to receive

---

# The Journey in 11 Steps

## Step 1: User Sends SMS

User's Phone: "Check my timesheet" → Send

SMS goes to Twilio phone number.

---

## Step 2: Twilio Receives & Forwards

Twilio receives SMS → Sends webhook to our server

Twilio immediately notifies our server with:
- User's phone number
- Message content
- Message ID

---

## Step 3: Find User in Database

Server looks up user by phone number → Gets credentials

Server finds:
- User ID
- Harvest account credentials
- Timezone (for date calculations)

---

## Step 4: Start Workflow

Server starts Temporal workflow → Returns 200 OK to Twilio

Workflow runs asynchronously (doesn't block Twilio).

---

# Multi-Agent Team Takes Over

From here, 4 agents work together inside the workflow...

---

## STEP 1: Planner Analyzes Request

**Planner Agent:** "Check my timesheet" → Analyzes → Creates plan

**What Planner does:**

**1. Checks Standard Operating Procedures (SOPs)**
- Does this match a common query?
- "Check my timesheet" → ✅ Matches `check_timesheet` SOP
- Uses pre-defined template (faster, no LLM needed!)

**2. Creates execution plan:**
- ✅ Needs data: YES
- ✅ Message to Timesheet Agent: "Get time entries for this week"
- ✅ Quality criteria: Data completeness, time period clarity, SMS format

**If no SOP match:** Planner uses AI to analyze and create plan

**Output:**

Execution Plan:
- Needs data: YES
- Message to Timesheet: "Get time entries for Dec 2-9"
- Quality criteria: [3 criteria defined]

**Time:** ~0ms (SOP match) or ~800ms (AI analysis)

---

## STEP 2: Timesheet Agent Gets Data

**Timesheet Agent:** Receives instruction → Chooses tool → Calls Harvest API

**What Timesheet does:**

**1. Receives natural language instruction from Planner:**
- "Get time entries for this week (Dec 2-9)"

**2. AI decides which tool to use:**
- 51 Harvest tools available
- AI chooses: `list_time_entries`
- AI extracts parameters: from_date="2025-12-02", to_date="2025-12-09"

**3. Calls Harvest API via MCP:**
- Sends request with user's credentials
- Gets back time entries

**Harvest returns:**

5 time entries found:
- Dec 2: Alpha Project, 8h, Development
- Dec 3: Alpha Project, 7.5h, Development
- Dec 4: Beta Project, 8h, Design
- Dec 5: Alpha Project, 6h, Code review
- Dec 9: Beta Project, 5.5h, Design

Total: 35 hours

**Output:**

Success: YES
Data: [5 time entries, 35 hours total]
Tool used: list_time_entries

**Time:** ~1200ms (AI tool selection + API call)

---

## STEP 3: Planner Composes Response

**Planner Agent:** Receives data → AI composes natural response

**What Planner does:**

1. Takes Harvest data
2. AI writes natural language response:
   - Summarizes 35 hours
   - Groups by project
   - Adds encouraging message

**Output:**

"You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5 hours (Development, code review)
- Beta Project: 13.5 hours (Design, UI work)

You're on track! Keep it up! 💪"

**Time:** ~900ms (AI composition)

---

## STEP 4: Branding Agent Formats for SMS

**Branding Agent:** Receives response → AI formats for SMS

**What Branding does:**

**1. Checks channel requirements:**
- SMS: Max 1600 characters, plain text, no markdown

**2. AI applies formatting:**
- Shortens "hours" → "h"
- Keeps emoji (appropriate for SMS)
- Ensures concise and clear

**Output:**

"You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5h (Development, code review)
- Beta Project: 13.5h (Design, UI work)

You're on track! Keep it up! 💪"

**Time:** ~700ms (AI formatting)

---

## STEP 5: Quality Agent Validates

**Quality Agent:** Receives formatted response → Validates against criteria

**What Quality does:**

Checks each criterion (using AI):

**Criterion 1: Data Completeness**
- Question: "Does response include all entries or provide appropriate summary?"
- Answer: ✅ PASS (5 entries grouped by project)

**Criterion 2: Time Period Clarity**
- Question: "Does response clearly state the time period?"
- Answer: ✅ PASS (mentions "this week (Dec 2-9)")

**Criterion 3: SMS Format**
- Question: "Is response formatted appropriately for SMS?"
- Answer: ✅ PASS (concise, clear, mobile-friendly)

**Overall Result:** ✅ **ALL CRITERIA PASSED**

**Output:**

Validation: PASSED
Failed criteria: None

**Time:** ~600ms (3 AI validations)

---

## STEP 6: Refinement Loop (If Needed)

**Quality Agent → Planner Agent:** If validation fails → Refine → Reformat → Revalidate

**What happens if validation fails:**

1. Quality tells Planner what's wrong
2. Planner refines the response
3. Branding reformats
4. Quality validates again
5. Max 1 refinement attempt

**In our example:** ✅ Validation passed, so **SKIP THIS STEP**

**Time:** ~0ms (skipped)

---

## STEP 7: Graceful Failure (If Still Failed)

**Planner Agent:** If still failed after refinement → Compose apologetic message

**What happens if validation still fails:**

Planner composes a graceful failure message:
- "I apologize, but I'm having trouble processing your timesheet request right now. Please try again in a moment."

**In our example:** ✅ Validation passed, so **SKIP THIS STEP**

**Time:** ~0ms (skipped)

---

## STEP 8: Send SMS via Twilio

**Server:** Sends final response via Twilio API

**What happens:**

1. Server calls Twilio API
2. Twilio sends SMS to user's phone
3. User receives message

**User receives:**

"You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5h (Development, code review)
- Beta Project: 13.5h (Design, UI work)

You're on track! Keep it up! 💪"

**Time:** ~500ms (Twilio API call)

---

## STEP 9: Store Conversation

**Database:** Stores user message + assistant response

**What's stored:**

**1. INBOUND message:**
- User: "Check my timesheet"
- Platform: SMS
- Timestamp: 2025-12-09 12:34:56

**2. OUTBOUND message:**
- Assistant: "You logged 35 hours..."
- Platform: SMS
- Timestamp: 2025-12-09 12:35:01
- Metadata: Validation passed, no refinement

**Why:** Enables conversation history for future context

**Time:** ~300ms (2 database inserts)

---

## STEP 10: Log Metrics

**System:** Logs conversation metrics for monitoring

**What's logged:**
- Channel: SMS
- Message length: 18 characters
- Response length: 160 characters
- Timestamp: 2025-12-09 12:35:01

**Why:** Monitor system performance and usage

**Time:** ~50ms (logging)

---

## STEP 11: Workflow Complete

**Workflow:** Returns result → Marks as complete

**Final result:**

✅ Success
✅ Response sent
✅ Validation passed
✅ No refinement needed
✅ Total time: 4.8 seconds

**Time:** ~0ms (instant return)

---

# Time Breakdown

| Step | What Happens | Time |
|------|--------------|------|
| 1-4 | User sends SMS → Workflow starts | ~450ms |
| Workflow Step 1 | Planner analyzes | ~0ms (SOP) |
| Workflow Step 2 | Timesheet gets data | ~1200ms |
| Workflow Step 3 | Planner composes | ~900ms |
| Workflow Step 4 | Branding formats | ~700ms |
| Workflow Step 5 | Quality validates | ~600ms |
| Workflow Step 6 | Refinement | ~0ms (skipped) |
| Workflow Step 7 | Graceful failure | ~0ms (skipped) |
| Workflow Step 8 | Send SMS | ~500ms |
| Workflow Step 9 | Store conversation | ~300ms |
| Workflow Step 10 | Log metrics | ~50ms |
| Workflow Step 11 | Complete | ~0ms |
| **TOTAL** | | **~4.7 seconds** |

---

# Why Multi-Agent?

## Single Agent (Old Way)

User → One AI → Response

**Problems:**
- ❌ No quality control
- ❌ No channel-specific formatting
- ❌ No refinement if response is bad
- ❌ Generic error messages

---

## Multi-Agent (Current Way)

User → Planner → Timesheet → Planner → Branding → Quality → User

(Timesheet connects to Harvest API, Quality can trigger Refinement if needed)

**Advantages:**
- ✅ **Separation of concerns** - Each agent has one job
- ✅ **Quality control** - Validated before sending
- ✅ **Automatic refinement** - Self-improving
- ✅ **Channel formatting** - SMS, Email, WhatsApp
- ✅ **Graceful failures** - Better error messages
- ✅ **Observability** - See what each agent did

---

# Alternative Paths

## Path 1: No Data Needed

User: "Hello"
↓
Planner: "No data needed, just conversational response"
↓
Planner composes → Branding formats → Quality validates → Send

**Skips:** Timesheet Agent (no API call needed)

---

## Path 2: Validation Fails

User: "Check my timesheet"
↓
[Steps 1-5 same as above]
↓
Quality: "❌ FAILED - Missing project details"
↓
Planner refines → Branding reformats → Quality revalidates
↓
Quality: "✅ PASSED"
↓
Send

**Extra steps:** Refinement loop (1 attempt)

---

## Path 3: Still Fails After Refinement

User: "Check my timesheet"
↓
[Steps 1-5 same as above]
↓
Quality: "❌ FAILED"
↓
Refinement attempt
↓
Quality: "❌ STILL FAILED"
↓
Planner: "I apologize, I'm having trouble..."
↓
Send graceful failure message

**Result:** User gets helpful error message (not technical error)

---

# Key Features

## 1. Standard Operating Procedures (SOPs)

Pre-defined templates for common queries:
- "Check my timesheet" → Use `check_timesheet` SOP
- "Log hours" → Use `log_hours` SOP
- "Weekly summary" → Use `weekly_summary` SOP

**Benefit:** Faster (no AI needed) + more consistent

---

## 2. AI-Driven Tool Selection

Timesheet Agent has 51 Harvest tools available:
- AI reads Planner's instruction
- AI chooses the right tool
- AI extracts parameters

**Benefit:** No hardcoded logic, handles novel queries

---

## 3. Scorecard Validation

Quality Agent checks every response:
- Each request gets custom quality criteria
- AI validates each criterion
- Must pass ALL criteria to send

**Benefit:** Guaranteed quality

---

## 4. Refinement Loop

If validation fails:
- Planner refines based on feedback
- Branding reformats
- Quality revalidates
- Max 1 attempt

**Benefit:** Self-improving responses

---

## 5. Graceful Failures

If still fails after refinement:
- Planner composes helpful error message
- Quality validates error message
- User gets contextual apology (not technical error)

**Benefit:** Better user experience

---

## 6. Conversation History

Every message is stored:
- Future requests use conversation context
- AI can reference previous messages
- Cross-platform tracking (SMS, Email, WhatsApp)

**Benefit:** Context-aware responses

---

# What User Experiences

## User's Perspective:

[12:34:56] User types: "Check my timesheet"
[12:34:56] User presses Send

... 5 seconds ...

[12:35:01] Assistant: "You logged 35 hours this week (Dec 2-9):
- Alpha Project: 21.5h (Development, code review)
- Beta Project: 13.5h (Design, UI work)

You're on track! Keep it up! 💪"

**User sees:** Simple question → Helpful answer in ~5 seconds

---

## Behind the Scenes:

✅ 11 steps executed
✅ 4 agents collaborated
✅ 6 AI decisions made
✅ 1 API call to Harvest
✅ 3 quality checks performed
✅ 2 database operations
✅ 1 SMS sent
✅ 100% quality guaranteed

**System did:** Complex orchestration, quality assurance, error handling

---

# Why This Matters

## For Users:
- ✅ Fast responses (~5 seconds)
- ✅ Accurate information (validated)
- ✅ Natural language (not robotic)
- ✅ Consistent quality
- ✅ Helpful error messages

## For Business:
- ✅ Scalable architecture
- ✅ Easy to maintain (each agent is separate)
- ✅ Easy to extend (add new agents or tools)
- ✅ Full observability (see what happened)
- ✅ Quality guaranteed (validation before sending)

## For Developers:
- ✅ Modular design (change one agent without affecting others)
- ✅ Testable (test each agent separately)
- ✅ Debuggable (see each step in Temporal UI)
- ✅ Reliable (Temporal handles retries and failures)

---

# Summary

**The multi-agent system is like a well-coordinated team:**

- **Planner** = Project Manager (decides what to do)
- **Timesheet** = Data Analyst (gets the data)
- **Branding** = Copywriter (makes it sound good)
- **Quality** = Editor (checks before publishing)

**Each agent is an expert at their job, and together they create perfect responses every time.**

**Total time:** ~5 seconds  
**Quality:** 100% validated  
**User experience:** Simple and helpful  

---

# Related Documents

- **Sequence Diagram:** `MULTI-AGENT-SYSTEM-ANALYSIS.md` (visual flow)
- **Technical Details:** `MULTI-AGENT-FLOW-EXPLANATION.md` (with code)
- **Architecture:** `MULTI-AGENT-SYSTEM-ANALYSIS.md` (full analysis)
