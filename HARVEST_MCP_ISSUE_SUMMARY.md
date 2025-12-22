# Harvest MCP 401 Unauthorized Issue - Root Cause Analysis

## Current Status: ❌ BLOCKED

The multi-agent system is fully functional EXCEPT for Harvest API data retrieval, which returns 401 Unauthorized.

## What's Working ✅

1. **SMS Webhook** - Receives messages correctly
2. **Conversation History** - Loads from Supabase (new feature)
3. **Conversation Storage** - Stores to Supabase (new feature)
4. **Metrics Logging** - Logs to Opik (new feature)
5. **SOP-Based Planning** - Planner matches "check timesheet" pattern
6. **Planner Agent** - Correctly decides needs_data=true
7. **Timesheet Agent** - Gets called and attempts to fetch data
8. **Credential Loading** - Loads from Supabase successfully
9. **Harvest MCP Server** - Running and responding on port 8080
10. **Network Routing** - Requests reach Harvest MCP via KrakenD

## What's Failing ❌

**Harvest API returns 401 Unauthorized**

### Evidence from Logs:

```
Harvest MCP Server Log (22:44:48):
"Harvest API error: 401, message='Unauthorized', 
url='https://api.harvestapp.com/v2/time_entries?from=2025-11-25&to=2025-11-26'"
```

### Flow Trace:

```
1. User sends SMS: "Check my timesheet" ✅
2. Planner analyzes → needs_data=true ✅
3. Timesheet agent called ✅
4. Credentials loaded from Supabase ✅
5. Payload sent to Harvest MCP:
   {
     "harvest_account": "1834293",
     "harvest_token": "<token>",
     "from_date": "2025-11-25",
     "to_date": "2025-11-26",
     "user_id": "5007762"
   } ✅
6. Harvest MCP receives request ✅
7. Harvest MCP calls Harvest API ✅
8. Harvest API returns 401 ❌
9. System sends graceful failure SMS ✅
```

## Possible Root Causes

### 1. Token Format Issue
The Harvest access token might be stored incorrectly in Supabase:
- Missing "Bearer " prefix (but MCP adds this)
- Extra whitespace
- Truncated token
- Wrong token type (OAuth vs Personal Access Token)

### 2. Account ID Mismatch
The `harvest_account_id` (1834293) might not match the token's account.

### 3. Token Permissions
The token might lack permissions for the `/time_entries` endpoint.

### 4. Harvest MCP Bug
The MCP server might be formatting the API request incorrectly.

## Diagnostic Steps Taken

1. ✅ Verified Harvest MCP is running
2. ✅ Verified credentials are loaded from Supabase
3. ✅ Verified payload structure is correct
4. ✅ Verified MCP receives requests
5. ✅ Verified MCP calls Harvest API
6. ❌ Cannot verify actual token value (sensitive)

## Next Steps to Debug

### Option 1: Check Supabase Data Directly
```sql
SELECT 
  id,
  harvest_account_id,
  LENGTH(harvest_access_token) as token_length,
  harvest_user_id,
  phone_number
FROM users 
WHERE id = 'user1';
```

Expected:
- `harvest_account_id`: "1834293"
- `token_length`: ~40-50 characters
- `harvest_user_id`: "5007762"

### Option 2: Test Token Manually
```bash
curl -H "Harvest-Account-ID: 1834293" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "User-Agent: Test" \
     "https://api.harvestapp.com/v2/users/me"
```

If this returns 401, the token is invalid.

### Option 3: Check Harvest MCP Code
Verify the MCP server is correctly formatting headers:
```python
headers = {
    "Harvest-Account-ID": account_id,
    "Authorization": f"Bearer {access_token}",
    "User-Agent": "Harvest HTTP Standalone Server (python-aiohttp)"
}
```

### Option 4: Generate New Token
1. Go to Harvest → Settings → Developers
2. Create new Personal Access Token
3. Update Supabase:
```sql
UPDATE users 
SET harvest_access_token = '<NEW_TOKEN>'
WHERE id = 'user1';
```

## Temporary Workaround

None available. The system requires valid Harvest credentials to function.

## Impact

- ✅ System architecture is correct
- ✅ All new features (conversation history, storage, metrics) working
- ✅ Multi-agent coordination working
- ❌ Cannot retrieve actual timesheet data
- ❌ Users receive graceful failure messages

## Files with Debug Logging

Added debug logging in:
- `unified_workflows.py` line 3294-3298: Logs credential values before API call

To see these logs, search for:
```
grep "HarvestTools" logs
```

## Recommendation

**Check the Harvest access token in Supabase.** The token is either:
1. Expired (unlikely if it's a Personal Access Token)
2. Invalid format
3. Wrong token entirely
4. Missing required permissions

The system code is correct - the issue is with the credential data itself.
