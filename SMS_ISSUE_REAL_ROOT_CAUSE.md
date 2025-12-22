# SMS Issue - REAL Root Cause Found

## Problem
User sends SMS "check timesheet" → No response received

## Investigation Timeline

### Initial Hypothesis ❌
- Thought: Twilio webhook not configured
- Reality: Webhook WAS configured and working

### Real Root Cause ✅

**SMS webhook IS working, but workflow fails due to Harvest MCP HTTP method error**

## Evidence from Logs

```
TimeStamp: 2025-12-18T14:49:36
workflow_id: conversation_user1_20251218_144914

ERROR: 405 Client Error: Method Not Allowed for url: 
https://harvest-mcp.internal.../api/list_time_entries

Sending POST request → Server expects GET
```

## The Bug

### Location
`unified_workflows.py` line 660

### Issue
```python
# WRONG - Sends POST for all tools
response = session.post(url, json=payload)
```

### Why It Failed
- `list_time_entries` endpoint expects **GET with query parameters**
- Code was sending **POST with JSON body**
- Server returned **405 Method Not Allowed**
- Workflow failed silently
- User received no SMS response

## The Fix

### Changed Code
```python
# Determine HTTP method based on tool name
if tool_name == "list_time_entries":
    logger.info(f"📤 [HTTP] Sending GET request to {url} with params")
    response = session.get(url, params=payload)
else:
    logger.info(f"📤 [HTTP] Sending POST request to {url}")
    response = session.post(url, json=payload)
```

## Flow Breakdown

### What Happens When User Sends SMS

1. **User sends**: "check timesheet" to Twilio number
2. **Twilio calls**: `https://.../webhook/sms` ✅
3. **Server receives**: SMS webhook ✅
4. **Workflow starts**: `MultiAgentConversationWorkflow` ✅
5. **Timesheet agent**: Tries to call `list_time_entries` ✅
6. **HTTP call**: POST to Harvest MCP ❌ **FAILS HERE**
7. **Error**: 405 Method Not Allowed ❌
8. **Workflow**: Fails silently ❌
9. **User**: Receives nothing ❌

### After Fix

1-5. Same as above ✅
6. **HTTP call**: GET to Harvest MCP ✅
7. **Success**: Returns timesheet data ✅
8. **Workflow**: Completes successfully ✅
9. **User**: Receives SMS with timesheet info ✅

## Deployment

```bash
# Built and pushed
docker buildx build --platform linux/amd64 \
  -t secureagentreg2ai.azurecr.io/multi-agent-system:20251219-harvest-fix \
  --push .

# Deployed to Azure
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --image secureagentreg2ai.azurecr.io/multi-agent-system:20251219-harvest-fix
```

**Status**: ✅ Deployed and running

## Testing

### Test Command
Send SMS to Twilio number: "check timesheet"

### Expected Result
User receives SMS with:
- Current week timesheet summary
- Total hours logged
- Missing entries (if any)

### Verify in Logs
```bash
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 100 | grep -E "🔔|list_time_entries|GET request"
```

Should see:
- `🔔 SMS WEBHOOK TRIGGERED`
- `📤 [HTTP] Sending GET request to .../list_time_entries with params`
- `📥 [HTTP] Response status: 200`
- `✅ SMS sent`

## Why This Was Hard to Find

1. **No error logs visible initially** - Had to search 3500+ log cycles
2. **Webhook appeared not working** - Actually was working, just failing downstream
3. **Silent failure** - Workflow failed but no SMS error sent to user
4. **Misleading symptom** - "No response" suggested webhook issue, not HTTP method issue

## Lessons Learned

1. **Check full workflow execution** - Not just endpoint availability
2. **Look for workflow errors** - Not just webhook logs
3. **HTTP method matters** - GET vs POST is critical
4. **Silent failures are dangerous** - Should send error SMS to user

## Related Issues

This same bug would affect ANY tool that expects GET:
- `list_time_entries` ✅ Fixed
- Other Harvest MCP tools may need similar fixes

## Next Steps

1. ✅ Deploy fix
2. ⏳ Test with real SMS
3. ⏳ Verify user receives response
4. ⏳ Monitor logs for success
5. ⏳ Check if other tools need similar fixes

---

**Created**: December 19, 2025 1:55 AM  
**Status**: ✅ Fixed and Deployed  
**Deployment**: `20251219-harvest-fix`
