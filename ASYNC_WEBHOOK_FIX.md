# Fix for HTTP 502 Error - Async Webhook Pattern

## The Problem

**Error 11200 from Twilio: Bad Gateway (HTTP 502)**

Your workflow takes 15-20 seconds to complete, but Azure Container Apps is timing out before that and returning 502 to Twilio.

## Twilio's Recommendation (from their docs)

> "If synchronously processing a webhook requires significant time, we recommend that you simply acknowledge the event by quickly responding with an empty 202 (Accepted) and then processing the message on your own timeline. Replies to inbound message events can be done at any time by making a call to the REST API."

## The Solution

Implement async webhook pattern:

1. **Webhook receives request** → Return 200 OK immediately (< 1 second)
2. **Workflow processes in background** → Takes 15-20 seconds
3. **Workflow sends SMS via Twilio API** → When complete

## Implementation Steps

### Step 1: Install Twilio SDK
```bash
pip install twilio
```

Add to `requirements.txt`:
```
twilio>=8.0.0
```

### Step 2: Add Twilio credentials to Azure Key Vault
```bash
az keyvault secret set --vault-name kv-secure-agent-2ai --name TWILIO-ACCOUNT-SID --value "your_account_sid"
az keyvault secret set --vault-name kv-secure-agent-2ai --name TWILIO-AUTH-TOKEN --value "your_auth_token"
az keyvault secret set --vault-name kv-secure-agent-2ai --name TWILIO-PHONE-NUMBER --value "+61488886084"
```

### Step 3: Create SMS sending activity

Add to `unified_workflows.py`:

```python
from twilio.rest import Client
import os

@activity.defn(name="send_sms_via_twilio")
async def send_sms_via_twilio(to_number: str, message: str) -> Dict[str, Any]:
    """Send SMS via Twilio API"""
    logger = activity.logger
    logger.info(f"📤 Sending SMS to {to_number}")
    
    try:
        # Get Twilio credentials from environment
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER', '+61488886084')
        
        if not account_sid or not auth_token:
            logger.error("❌ Twilio credentials not found")
            return {"success": False, "error": "Missing credentials"}
        
        # Send SMS
        client = Client(account_sid, auth_token)
        sms = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        logger.info(f"✅ SMS sent successfully: {sms.sid}")
        return {
            "success": True,
            "message_sid": sms.sid,
            "status": sms.status
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send SMS: {e}")
        return {"success": False, "error": str(e)}
```

### Step 4: Update workflow to send SMS at the end

In `MultiAgentConversationWorkflow.run()`, add before the return statement:

```python
# Step 9: Send SMS via Twilio API (async pattern)
if channel == "sms" and user_context.get("from"):
    to_number = user_context["from"]
    workflow.logger.info(f"📤 Sending SMS to {to_number}")
    
    try:
        sms_result = await workflow.execute_activity(
            send_sms_via_twilio,
            args=[to_number, final_response],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
            )
        )
        
        if sms_result["success"]:
            workflow.logger.info(f"✅ SMS sent: {sms_result['message_sid']}")
        else:
            workflow.logger.error(f"❌ SMS failed: {sms_result.get('error')}")
            
    except Exception as e:
        workflow.logger.error(f"❌ Failed to send SMS: {e}")

# Step 10: Return result
workflow.logger.info(f"✅ Multi-agent workflow complete: {request_id}")
```

### Step 5: Update webhook to return immediately

In `unified_server.py`, change the webhook handler:

```python
# Start workflow (don't wait)
result = await server.temporal_client.start_workflow(
    MultiAgentConversationWorkflow.run,
    args=[...],
    id=workflow_id,
    task_queue="timesheet-reminders"
)

logger.info(f"✅ Workflow started: {workflow_id}")
logger.info(f"📤 Returning 200 OK - SMS will be sent when workflow completes")

# Return empty response immediately (< 1 second)
return Response(
    content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
    media_type="text/xml; charset=utf-8"
)
```

### Step 6: Register activity in worker

In `unified_server.py`, add to activity list:

```python
activities=[
    # ... existing activities ...
    send_sms_via_twilio,  # NEW: Send SMS via Twilio API
]
```

### Step 7: Deploy

```bash
./deploy_configured.sh
```

## Benefits

1. ✅ **No more 502 errors** - Webhook returns in < 1 second
2. ✅ **Twilio gets 200 OK** - No timeout issues
3. ✅ **SMS still sent** - Via Twilio API when workflow completes
4. ✅ **Proper async pattern** - Recommended by Twilio
5. ✅ **Retry logic** - If SMS fails, workflow retries

## Testing

1. Send SMS to +61488886084
2. Check Twilio Debugger - should see 200 OK (not 502)
3. Wait 15-20 seconds
4. Receive SMS response on your phone

## Alternative: Quick Fix (Not Recommended)

If you don't want to implement async pattern, you could try to make the workflow faster:

1. Reduce LLM timeout
2. Use faster LLM model
3. Cache LLM responses
4. Parallelize agent calls

But this is fragile - if workflow ever takes > 30 seconds, you'll get 502 again.

**Async pattern is the proper solution.**
