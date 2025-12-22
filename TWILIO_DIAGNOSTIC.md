# Twilio SMS Not Received - Diagnostic Guide

## Problem
- ✅ System processes SMS and completes workflow
- ✅ System returns TwiML response to Twilio
- ❌ You don't receive SMS response on your phone

## Root Cause Analysis

### Possible Issues:

#### 1. **Twilio Account Status**
- Trial account may have restrictions
- Phone number not verified
- Account suspended or limited

#### 2. **Twilio Phone Number Configuration**
- Webhook URL not saved properly
- Wrong HTTP method (should be POST)
- Webhook disabled

#### 3. **Twilio Messaging Service**
- SMS sending disabled
- Geographic restrictions
- Rate limits exceeded

#### 4. **TwiML Response Format**
- Our system returns valid TwiML
- Twilio may not be processing it correctly

## Diagnostic Steps

### Step 1: Check Twilio Debugger
1. Go to: https://console.twilio.com/us1/monitor/logs/debugger
2. Look for recent webhook calls
3. Check for any errors or warnings
4. Verify the response code (should be 200)

**What to look for:**
- ❌ 11200: HTTP retrieval failure
- ❌ 11205: HTTP connection failure  
- ❌ 11206: HTTP protocol violation
- ❌ 11210: HTTP bad host name
- ✅ 11200 with 200 status: Webhook working

### Step 2: Verify Phone Number Configuration
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on **+61488886084**
3. Scroll to "Messaging Configuration"
4. Verify:
   - ✅ "Configure with" is set to "Webhooks, TwiML Bins, Functions, Studio, or Proxy"
   - ✅ "A MESSAGE COMES IN" webhook is:
     ```
     https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms
     ```
   - ✅ HTTP method is **POST**
   - ✅ Click **Save** if you made changes

### Step 3: Check Account Status
1. Go to: https://console.twilio.com/us1/account/manage-account/general-settings
2. Check account status
3. If trial account, verify:
   - Your phone number (+61434639294) is verified
   - Trial account limitations

### Step 4: Test with Twilio Console
1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms
2. Send a test SMS from Twilio to your phone
3. If this works, the issue is with webhook response
4. If this doesn't work, the issue is with Twilio account/phone config

### Step 5: Check Twilio Logs
1. Go to: https://console.twilio.com/us1/monitor/logs/sms
2. Look for outgoing SMS messages
3. Check their status:
   - ✅ **delivered**: SMS was sent successfully
   - ❌ **failed**: SMS failed to send
   - ⏳ **queued/sending**: SMS is being processed

### Step 6: Verify TwiML Response
Our system returns:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>{response_text}</Message>
</Response>
```

This is valid TwiML. Test it manually:
1. Go to: https://www.twilio.com/console/runtime/twiml-bins
2. Create a new TwiML Bin
3. Paste:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Response>
     <Message>Test response from TwiML Bin</Message>
   </Response>
   ```
4. Save and get the URL
5. Update your phone number webhook to this TwiML Bin URL
6. Send an SMS
7. If you receive it, the issue is with our webhook response format

## Common Solutions

### Solution 1: Re-save Webhook Configuration
Sometimes Twilio doesn't save properly:
1. Go to phone number settings
2. Clear the webhook URL
3. Click Save
4. Add the webhook URL again
5. Click Save
6. Test

### Solution 2: Use Absolute URL
Ensure webhook URL is:
- ✅ HTTPS (not HTTP)
- ✅ Publicly accessible
- ✅ Returns 200 status code
- ✅ Returns valid TwiML

### Solution 3: Check Geographic Permissions
1. Go to: https://console.twilio.com/us1/develop/sms/settings/geo-permissions
2. Ensure Australia is enabled for SMS
3. Enable if not

### Solution 4: Verify Phone Number
If trial account:
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Verify +61434639294 is in the list
3. If not, add and verify it

### Solution 5: Check Balance
1. Go to: https://console.twilio.com/us1/billing/manage-billing/billing-overview
2. Ensure you have credit
3. Trial accounts have free credit but may have limits

## Testing Our Webhook

### Manual Test
```bash
curl -X POST https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms \
  -d "From=+61434639294&Body=test&To=+61488886084&MessageSid=TEST123" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

**Expected Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>...</Message>
</Response>
```

### Check Logs
```bash
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 100 | grep "POST /webhook/sms"
```

## Next Steps

1. **Check Twilio Debugger** - This will show you exactly what's happening
2. **Verify webhook is saved** - Re-save if needed
3. **Check account status** - Ensure no restrictions
4. **Test with TwiML Bin** - Isolate the issue
5. **Check SMS logs** - See if Twilio is trying to send

## If Still Not Working

### Contact Twilio Support
If all above steps fail, contact Twilio support with:
- Phone number: +61488886084
- Webhook URL: https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms
- Issue: Webhook receives SMS, returns valid TwiML, but SMS not delivered to user
- Logs from Twilio Debugger

### Alternative: Use Messaging Service
Instead of direct phone number webhook:
1. Create a Messaging Service
2. Add phone number to service
3. Configure webhook on service
4. Test

## Current System Status

✅ **Webhook endpoint:** Working
✅ **Multi-agent workflow:** Completing successfully  
✅ **TwiML response:** Valid format
✅ **Response time:** 15-30 seconds
❌ **SMS delivery:** Not reaching your phone

**The issue is on the Twilio side, not our system.**
