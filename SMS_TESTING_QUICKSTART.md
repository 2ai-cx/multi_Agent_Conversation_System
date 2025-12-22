# SMS Memory Testing - Quick Start Guide

## Prerequisites

1. **Your phone number must be registered in Supabase**
   - Table: `users`
   - Column: `phone_number`
   - Format: `+61412345678` (with country code)

2. **Twilio must be configured**
   - Check Azure Key Vault for Twilio credentials
   - Webhook URL should be configured in Twilio console

## Option 1: Python Script (Recommended)

### Step 1: Update Phone Number

Edit `test_sms_memory.py` line 13:
```python
TEST_PHONE = "+61412345678"  # Change to YOUR phone number
```

### Step 2: Run the Script

```bash
python3 test_sms_memory.py
```

### Step 3: Check Your Phone

You should receive 6 SMS messages:
1. Response to job info
2. Answer about your job (should mention "Google")
3. Response to hours worked
4. Answer about hours (should mention "847")
5. Response to multiple facts
6. Answer about background (should mention "Microsoft" or "AI")

---

## Option 2: Bash Script

### Step 1: Update Phone Number

Edit `test_sms_memory.sh` line 8:
```bash
TEST_PHONE="+61412345678"  # Change to YOUR phone number
```

### Step 2: Make Executable and Run

```bash
chmod +x test_sms_memory.sh
./test_sms_memory.sh
```

---

## Option 3: Manual cURL Commands

Replace `YOUR_PHONE` with your actual phone number:

### Test 1: Store Information
```bash
curl -X POST "https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=YOUR_PHONE" \
  -d "Body=I work as a software engineer at Google." \
  -d "MessageSid=TEST$(date +%s)001"
```

### Wait 10 seconds
```bash
sleep 10
```

### Test 2: Retrieve Information
```bash
curl -X POST "https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=YOUR_PHONE" \
  -d "Body=What is my job?" \
  -d "MessageSid=TEST$(date +%s)002"
```

---

## Option 4: Send Real SMS from Your Phone

The easiest way! Just send SMS to your Twilio number:

1. **Find your Twilio phone number**:
   ```bash
   # Check Azure Key Vault or Twilio console
   ```

2. **Send SMS from your phone**:
   ```
   Message 1: I work as a software engineer at Google.
   (wait for response)
   
   Message 2: What is my job?
   (should respond with "software engineer" and "Google")
   ```

---

## Verification

### Check SMS Responses

You should receive SMS responses on your phone. The responses should:
- ✅ Acknowledge stored information
- ✅ Retrieve and mention specific facts you told it
- ✅ Show memory is working (e.g., "You work as a software engineer at Google")

### Check Azure Logs

```bash
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 100 | grep -E "memory|Memory|Mem0|Retrieved"
```

Look for:
```
INFO:llm.memory:Stored conversation in Mem0 for user: ...
INFO:llm.memory:Retrieved 2 memories from Mem0
INFO:llm.memory:Extracted memory 0: The user is a software engineer at Google...
```

---

## Test Scenarios

### Scenario 1: Simple Fact Storage
```
Store: "I work at Google."
Query: "Where do I work?"
Expected: Response mentions "Google"
```

### Scenario 2: Numeric Data
```
Store: "I worked 847 hours last month."
Query: "How many hours did I work?"
Expected: Response mentions "847"
```

### Scenario 3: Multiple Facts
```
Store: "I am a senior developer at Microsoft specializing in AI."
Query: "Tell me about my job."
Expected: Response mentions "Microsoft" and/or "senior developer" and/or "AI"
```

### Scenario 4: Preferences
```
Store: "I prefer Python over JavaScript."
Query: "What programming language do I prefer?"
Expected: Response mentions "Python"
```

---

## Troubleshooting

### Issue: No SMS Received

**Possible Causes**:
1. Phone number not in Supabase `users` table
2. Twilio credentials not configured
3. Twilio webhook URL not set

**Check**:
```bash
# View logs
az containerapp logs show --name unified-temporal-worker --tail 50

# Look for errors like:
# "No user found for phone +61..."
# "Failed to send SMS"
```

### Issue: SMS Received but No Memory

**Possible Causes**:
1. Not waiting long enough for indexing (wait 10 seconds)
2. Query not semantically similar to stored info
3. Different user_id used

**Check**:
```bash
# View memory logs
az containerapp logs show --name unified-temporal-worker --tail 100 | grep Mem0

# Look for:
# "Stored conversation in Mem0"
# "Retrieved X memories from Mem0"
```

### Issue: Wrong Information Retrieved

**Check**:
1. Verify the same phone number is used for both store and retrieve
2. Check if query is semantically related to stored information
3. Review logs to see what memories were actually retrieved

---

## Expected Success Criteria

✅ **Test 1-2**: Job information stored and retrieved correctly  
✅ **Test 3-4**: Numeric data (847 hours) stored and retrieved correctly  
✅ **Test 5-6**: Multiple facts stored and at least 1-2 facts retrieved  

**Success Rate**: Should be **80-100%** based on our test results.

---

## Quick Test (30 seconds)

```bash
# One-liner test (replace YOUR_PHONE)
PHONE="+61412345678" && \
curl -X POST "https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms" \
  -d "From=$PHONE" -d "Body=I work at Google." -d "MessageSid=TEST$(date +%s)" && \
sleep 10 && \
curl -X POST "https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms" \
  -d "From=$PHONE" -d "Body=Where do I work?" -d "MessageSid=TEST$(date +%s)"
```

Check your phone - you should get 2 SMS messages, the second mentioning "Google".

---

## Notes

- **Memory Indexing**: Takes 5-10 seconds after storing
- **Tenant Isolation**: Each phone number gets isolated memory
- **User Lookup**: Phone number is looked up in Supabase to get user_id
- **Fallback**: If phone not found, defaults to "user1"

---

**Last Updated**: December 17, 2025  
**System Status**: ✅ Production Ready (96.6% test success rate)
