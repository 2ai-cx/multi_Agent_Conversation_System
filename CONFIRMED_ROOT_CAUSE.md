# CONFIRMED Root Cause Analysis - SMS No Response Issue

**Date:** December 19, 2025 2:15 AM  
**Status:** ✅ CONFIRMED

---

## Executive Summary

**The SMS system is working correctly. The issue is invalid Harvest API credentials.**

---

## Investigation Timeline

### Initial Hypothesis ❌
- Thought: Twilio webhook not configured
- Reality: Webhook working perfectly

### Second Hypothesis ❌  
- Thought: HTTP method issue (POST vs GET)
- Reality: **I CAUSED THIS** by changing code to use GET

### Third Hypothesis ❌
- Thought: Harvest MCP internal endpoint broken
- Reality: Harvest MCP working, but credentials invalid

### CONFIRMED ROOT CAUSE ✅

**Harvest API credentials in Supabase are returning 401 Unauthorized from Harvest API**

---

## Evidence Chain

### 1. SMS Webhook ✅ WORKING
```
User sends SMS → Twilio calls webhook → Server receives → Workflow starts
```

### 2. Workflow Execution ✅ WORKING
```
Planner analyzes → Timesheet agent called → Harvest MCP called
```

### 3. Harvest MCP Server ✅ WORKING
```
Harvest MCP Logs (2025-12-18):
- POST /api/list_time_entries → 200 OK (MCP accepts request)
- Then calls Harvest API → 401 Unauthorized (Harvest rejects credentials)
```

### 4. Harvest API ❌ FAILING
```
ERROR: Harvest API error: 401, message='Unauthorized', 
url='https://api.harvestapp.com/v2/time_entries?from=2025-12-01&to=2025-12-02'
```

---

## What I Did Wrong

### My Mistake #1: Changed POST to GET
```python
# WRONG CODE I ADDED (lines 661-666):
if tool_name == "list_time_entries":
    response = session.get(url, params=payload)  # ❌ WRONG
else:
    response = session.post(url, json=payload)
```

**This caused 405 Method Not Allowed errors**

### My Mistake #2: Tried to force KrakenD
```python
# WRONG FIX:
use_direct_internal_env = os.getenv('USE_DIRECT_INTERNAL_CALLS', 'false')
```

**This didn't help because the real issue is credentials, not routing**

---

## Correct Understanding

### Harvest MCP Endpoints (from logs):
```
POST /api/get_current_user
POST /api/list_time_entries  ← ALWAYS POST, NOT GET
POST /api/create_time_entry
POST /api/list_projects
POST /api/list_tasks
```

### Request Flow:
```
1. unified_workflows.py → POST to Harvest MCP ✅
2. Harvest MCP → Validates request ✅
3. Harvest MCP → POST to Harvest API with credentials ✅
4. Harvest API → Returns 401 Unauthorized ❌
5. Harvest MCP → Returns 500 to our system ❌
6. Workflow → Fails ❌
7. User → No SMS response ❌
```

---

## The Real Problem

### Harvest API Credentials Invalid

**Location:** Supabase `users` table for `user1`

**Fields:**
- `harvest_account_id`: "1834293" 
- `harvest_access_token`: (invalid or expired)
- `harvest_user_id`: "5007762"

**Evidence:**
```
Harvest API error: 401, message='Unauthorized'
```

---

## Why User Gets No Response

1. Workflow starts successfully ✅
2. Planner decides needs data ✅
3. Timesheet agent calls Harvest MCP ✅
4. Harvest MCP calls Harvest API ❌ **401 Unauthorized**
5. Harvest MCP returns 500 error ❌
6. Workflow catches exception ❌
7. **No graceful failure SMS sent** ❌

---

## Solutions

### Immediate Fix: Update Harvest Credentials

1. **Generate new Harvest Personal Access Token**
   - Go to: https://id.getharvest.com/developers
   - Create new Personal Access Token
   - Copy token

2. **Update Supabase**
   ```sql
   UPDATE users 
   SET harvest_access_token = '<NEW_TOKEN>'
   WHERE id = 'user1';
   ```

3. **Test**
   ```bash
   curl -H "Harvest-Account-ID: 1834293" \
        -H "Authorization: Bearer <NEW_TOKEN>" \
        -H "User-Agent: Test" \
        "https://api.harvestapp.com/v2/users/me"
   ```
   Should return 200 OK with user data

### Code Fix: Revert My Wrong Changes

✅ **DONE** - Reverted GET/POST logic back to always POST

### Future Fix: Add Graceful Failure

The workflow should send an SMS when Harvest API fails:
```
"Sorry, I couldn't retrieve your timesheet data right now. Please try again later."
```

---

## Test After Credential Fix

1. Update Harvest token in Supabase
2. Send SMS: "check timesheet"
3. Expected: Receive SMS with timesheet data

---

## Files Modified

### ✅ Fixed:
- `unified_workflows.py` line 659-660: Reverted to POST only

### ❌ Needs Revert:
- None - already fixed

---

## Lessons Learned

1. **Don't assume HTTP method** - Check server logs first
2. **405 errors mean wrong method** - I caused this by changing to GET
3. **401 errors mean bad credentials** - This is the real issue
4. **Check the full error chain** - Don't stop at first error
5. **Harvest MCP logs are critical** - They show the real Harvest API error

---

## Current Status

### What's Working ✅
- SMS webhook
- Twilio integration  
- Workflow orchestration
- Multi-agent system
- Harvest MCP server
- HTTP routing (both internal and KrakenD)

### What's Broken ❌
- Harvest API credentials (401 Unauthorized)
- No graceful failure message to user

### What's Fixed ✅
- Reverted wrong GET/POST logic
- Confirmed POST is correct method

---

## Next Action Required

**UPDATE HARVEST CREDENTIALS IN SUPABASE**

This is the ONLY remaining issue.

---

**Confirmed by:** Cascade AI  
**Verification:** Harvest MCP logs, test_harvest_mcp.py, curl tests  
**Confidence:** 100%
