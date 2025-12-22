# SMS Issue - Root Cause Analysis

## Problem Statement
User sends SMS "check timesheet" to Twilio phone number → **NO RESPONSE**

## Investigation Results

### ✅ What's Working
1. **Server is running** - Azure Container App is healthy
2. **Webhook endpoint exists** - `/webhook/sms` responds with 200 OK
3. **Manual test works** - `curl` to webhook returns proper XML response
4. **Credentials loaded** - Twilio credentials in Azure Key Vault
5. **Code is correct** - SMS webhook handler is properly implemented

### ❌ Root Cause Identified

**TWILIO IS NOT CALLING OUR WEBHOOK URL**

Evidence:
- No SMS webhook logs in Azure (checked 3500+ log cycles)
- Manual curl test triggers logs immediately
- Real SMS from user triggers NOTHING

## Why Twilio Isn't Calling Our Webhook

### Possible Causes:

#### 1. **Webhook URL Not Configured in Twilio Console** ⚠️ MOST LIKELY
- Twilio phone number must have webhook URL configured
- URL should be: `https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms`
- This is configured in Twilio Console → Phone Numbers → Your Number → Messaging Configuration

#### 2. **Wrong Twilio Phone Number**
- User might be texting a different number
- Need to verify: What number is user texting?
- What number is configured in Key Vault?

#### 3. **Twilio Account Issue**
- Account suspended/trial limitations
- Phone number not active
- Messaging not enabled

#### 4. **Webhook URL Typo in Twilio Console**
- Wrong domain
- HTTP instead of HTTPS
- Missing /webhook/sms path

## Verification Steps

### Step 1: Check Twilio Console Configuration

1. Log into Twilio Console: https://console.twilio.com
2. Go to: Phone Numbers → Manage → Active Numbers
3. Click on your phone number
4. Scroll to "Messaging Configuration"
5. Check "A MESSAGE COMES IN" webhook URL

**Expected:**
```
https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms
```

**Method:** POST

### Step 2: Check Twilio Phone Number

```bash
# Get phone number from Key Vault
az keyvault secret show \
  --vault-name kv-secure-agent-2ai \
  --name TWILIO-PHONE-NUMBER \
  --query "value" -o tsv
```

Verify this matches the number user is texting.

### Step 3: Test Twilio Webhook Delivery

In Twilio Console:
1. Go to your phone number settings
2. Find "Messaging Configuration"
3. Click "Test" button next to webhook URL
4. Check if Azure logs show the test message

### Step 4: Check Twilio Logs

In Twilio Console:
1. Go to Monitor → Logs → Messaging
2. Look for recent SMS from user
3. Check for webhook delivery errors

## Quick Fix

### Option 1: Configure Webhook in Twilio Console (RECOMMENDED)

1. Go to Twilio Console
2. Phone Numbers → Your Number
3. Set "A MESSAGE COMES IN" webhook to:
   ```
   https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms
   ```
4. Method: POST
5. Save

### Option 2: Use Twilio CLI

```bash
# Install Twilio CLI if not installed
npm install -g twilio-cli

# Login
twilio login

# List phone numbers
twilio phone-numbers:list

# Update webhook URL
twilio phone-numbers:update <PHONE_SID> \
  --sms-url="https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms" \
  --sms-method="POST"
```

## Test After Fix

1. Send SMS from your phone to Twilio number
2. Check Azure logs:
   ```bash
   az containerapp logs show \
     --name unified-temporal-worker \
     --resource-group rg-secure-timesheet-agent \
     --tail 50 | grep "🔔"
   ```
3. Should see: `🔔 SMS WEBHOOK TRIGGERED`

## Additional Debugging

If webhook is configured but still not working:

### Check Twilio Account Status
- Trial account limitations
- Account balance
- Phone number active status

### Check Network/Firewall
- Azure Container App allows inbound HTTPS
- No IP restrictions blocking Twilio

### Check Webhook Response
- Must return valid TwiML XML
- Currently returns: `<?xml version="1.0" encoding="UTF-8"?><Response></Response>`
- This is correct ✅

## Summary

**Root Cause:** Twilio webhook URL not configured or misconfigured in Twilio Console

**Solution:** Configure webhook URL in Twilio Console for the phone number

**Verification:** Send test SMS and check Azure logs for `🔔 SMS WEBHOOK TRIGGERED`

---

**Created:** December 19, 2025  
**Status:** Awaiting Twilio Console verification
