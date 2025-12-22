# 🚀 Multi-Agent System - Deployment Guide

**Current Status**: ✅ **DEPLOYED AND RUNNING**

---

## 📊 Current Deployment

### Live System
- **URL**: `https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io`
- **Health**: ✅ Healthy
- **Version**: `1.0.0-20251125-085810`
- **Deployed**: Nov 24, 2025 21:58 UTC

### Azure Resources
- **Resource Group**: `rg-secure-timesheet-agent`
- **Container App**: `unified-temporal-worker`
- **Container Registry**: `secureagentreg2ai.azurecr.io`
- **Environment**: `secure-timesheet-env`
- **Key Vault**: `kv-secure-agent-2ai`

---

## 🔄 Future Deployments - Quick Reference

### Option 1: Automated Deployment (Recommended)

**When to use**: Regular updates, bug fixes, new features

```bash
# 1. Make your code changes
# 2. Commit to git (optional but recommended)
git add .
git commit -m "Description of changes"

# 3. Run automated deployment
./deploy_configured.sh

# That's it! The script will:
# - Build Docker image
# - Push to Azure Container Registry
# - Deploy to Container App
# - Test health endpoint
# - Show logs
```

**Time**: ~5-7 minutes

---

### Option 2: Manual Deployment (Advanced)

**When to use**: Custom configurations, troubleshooting

#### Step 1: Build Docker Image
```bash
# Build for linux/amd64 (Azure requirement)
docker build --platform linux/amd64 \
  -t secureagentreg2ai.azurecr.io/multi-agent-system:v1.0.1 \
  -t secureagentreg2ai.azurecr.io/multi-agent-system:latest \
  .
```

#### Step 2: Push to Registry
```bash
# Login to ACR
az acr login --name secureagentreg2ai

# Push image
docker push secureagentreg2ai.azurecr.io/multi-agent-system:v1.0.1
docker push secureagentreg2ai.azurecr.io/multi-agent-system:latest
```

#### Step 3: Deploy to Container App
```bash
# Update container app
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --image secureagentreg2ai.azurecr.io/multi-agent-system:v1.0.1
```

#### Step 4: Verify Deployment
```bash
# Check health
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health

# Check logs
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --follow
```

---

## 🎯 Next Steps After Deployment

### 1. Update Twilio Webhooks ⚠️ IMPORTANT

You need to update your Twilio webhooks to point to the new deployment:

#### SMS Webhook
1. Go to: https://console.twilio.com/
2. Navigate to: Phone Numbers → Manage → Active Numbers
3. Click your phone number
4. Under "Messaging Configuration":
   - **A MESSAGE COMES IN**: 
   ```
   https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms
   ```
   - Method: `POST`
5. Click **Save**

#### WhatsApp Webhook
1. Go to: https://console.twilio.com/
2. Navigate to: Messaging → Try it out → Send a WhatsApp message
3. Under "Sandbox Settings":
   - **WHEN A MESSAGE COMES IN**:
   ```
   https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/whatsapp
   ```
   - Method: `POST`
4. Click **Save**

---

### 2. Test the System 🧪

#### Test SMS
Send an SMS to your Twilio number:
```
Check my timesheet
```

**Expected Response** (7-10 seconds):
- ✅ Plain text (no markdown)
- ✅ Timesheet data from Harvest
- ✅ User-friendly formatting
- ✅ Under 1600 characters

#### Test WhatsApp
Send a WhatsApp message to your Twilio sandbox:
```
join [your-sandbox-code]
```
Then:
```
Check my timesheet
```

#### Test Email
Send an email to your configured Gmail address with:
```
Subject: Timesheet Query
Body: Check my timesheet for this week
```

---

### 3. Monitor the System 📊

#### Check Logs
```bash
# Real-time logs
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --follow

# Last 50 lines
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 50
```

#### Monitor Workflows
- **Temporal Cloud**: https://cloud.temporal.io
  - View workflow executions
  - Check for errors
  - Monitor performance

#### Monitor Costs
- **Opik Dashboard**: https://www.comet.com/opik
  - Track LLM API calls
  - Monitor costs per conversation
  - View response quality

#### Azure Monitoring
```bash
# Check container app status
az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "{Status:properties.provisioningState, Health:properties.runningStatus}"

# Check revisions
az containerapp revision list \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "[].{Name:name, Active:properties.active, Traffic:properties.trafficWeight}"
```

---

## 🔧 Common Deployment Scenarios

### Scenario 1: Quick Bug Fix

```bash
# 1. Fix the bug in your code
# 2. Deploy
./deploy_configured.sh

# 3. Verify fix
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health

# 4. Test with real message
# Send SMS: "Check my timesheet"
```

---

### Scenario 2: Add New Feature

```bash
# 1. Implement feature
# 2. Test locally
./run_local_test.sh

# 3. Deploy to production
./deploy_configured.sh

# 4. Monitor for issues
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --follow
```

---

### Scenario 3: Update Dependencies

```bash
# 1. Update requirements.txt
# 2. Test locally
pip install -r requirements.txt
./run_local_test.sh

# 3. Deploy
./deploy_configured.sh

# 4. Verify all services work
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health
```

---

### Scenario 4: Rollback to Previous Version

```bash
# 1. List available images
az acr repository show-tags \
  --name secureagentreg2ai \
  --repository multi-agent-system \
  --orderby time_desc

# 2. Deploy previous version
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --image secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-20251125-085810

# 3. Verify
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health
```

---

## 🛡️ Best Practices

### Before Deploying
- [ ] Test locally with `./run_local_test.sh`
- [ ] Run unit tests: `pytest tests/unit/ -v`
- [ ] Check for syntax errors
- [ ] Review changes in git diff
- [ ] Update version number (optional)

### During Deployment
- [ ] Monitor deployment logs
- [ ] Wait for health check to pass
- [ ] Check for errors in logs
- [ ] Verify all secrets loaded

### After Deployment
- [ ] Test with real SMS/WhatsApp/Email
- [ ] Monitor Temporal workflows
- [ ] Check Opik for LLM costs
- [ ] Verify no errors in logs for 10 minutes
- [ ] Update documentation if needed

---

## 🚨 Troubleshooting

### Deployment Fails

**Check Docker build**:
```bash
docker build --platform linux/amd64 -t test .
```

**Check Azure login**:
```bash
az account show
```

**Check ACR access**:
```bash
az acr login --name secureagentreg2ai
```

### Health Check Fails

**Check logs**:
```bash
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 100
```

**Common issues**:
- Missing secrets in Key Vault
- Temporal connection failed
- Supabase connection failed
- LLM client initialization failed

### No Response to Messages

**Check Twilio webhooks**:
- Verify webhook URLs are correct
- Check webhook logs in Twilio console
- Ensure webhooks are using POST method

**Check application logs**:
```bash
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --follow
```

**Test webhook directly**:
```bash
curl -X POST https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms \
  -d "From=+1234567890" \
  -d "Body=Check my timesheet" \
  -d "MessageSid=test123"
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Code changes tested locally
- [ ] Unit tests passing
- [ ] Dependencies updated in requirements.txt
- [ ] Environment variables verified in Key Vault
- [ ] Git commit created (optional)

### Deployment
- [ ] Run `./deploy_configured.sh`
- [ ] Docker image built successfully
- [ ] Image pushed to ACR
- [ ] Container app updated
- [ ] Health check passed

### Post-Deployment
- [ ] Twilio webhooks updated
- [ ] Test SMS sent and received
- [ ] Test WhatsApp sent and received
- [ ] Test Email sent and received
- [ ] Temporal workflows executing
- [ ] Opik tracking working
- [ ] No errors in logs for 10 minutes

### Monitoring (First 24 Hours)
- [ ] Check logs every hour
- [ ] Monitor Temporal workflows
- [ ] Track LLM costs in Opik
- [ ] Verify response quality
- [ ] Check for any errors

---

## 🎯 Quick Commands Reference

```bash
# Deploy
./deploy_configured.sh

# Check health
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health

# View logs
az containerapp logs show --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --follow

# Check status
az containerapp show --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --query "properties.runningStatus"

# List revisions
az containerapp revision list --name unified-temporal-worker --resource-group rg-secure-timesheet-agent -o table

# List images
az acr repository show-tags --name secureagentreg2ai --repository multi-agent-system --orderby time_desc

# Restart app
az containerapp revision restart --name unified-temporal-worker --resource-group rg-secure-timesheet-agent

# Scale app
az containerapp update --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --min-replicas 1 --max-replicas 5
```

---

## 📚 Additional Resources

- **Temporal Cloud**: https://cloud.temporal.io
- **Opik Dashboard**: https://www.comet.com/opik
- **Twilio Console**: https://console.twilio.com
- **Azure Portal**: https://portal.azure.com
- **Local Testing Guide**: `LOCAL_TESTING.md`
- **Deployment Checklist**: `FINAL_CHECKLIST.md`

---

## ✅ Current Status Summary

**Deployment**: ✅ Live and Healthy  
**Health Check**: ✅ Passing  
**Temporal**: ✅ Connected  
**Supabase**: ✅ Connected  
**LLM Client**: ✅ Initialized  
**Key Vault**: ✅ Connected  
**Webhooks**: ⚠️ Need to be updated (see Step 1 above)  

**Next Action**: Update Twilio webhooks and test with real messages!

---

**Last Updated**: November 25, 2025  
**Version**: 1.0.0-20251125-085810  
**Status**: Production Ready 🚀
