# Azure Deployment Guide - Multi-Agent Timesheet System

## 🎯 **Overview**

This guide deploys the **Unified Multi-Agent Conversation System** to Azure Container Apps.

**Current Deployment:**
- **Container App:** `unified-temporal-worker` (Port 8003)
- **Image:** `secureagentreg2ai.azurecr.io/multi-agent-system:latest`
  - Tagged with timestamp: `1.0.0-YYYYMMDD-HHMMSS` (e.g., `1.0.0-20251201-185138`)
- **URL:** https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io

**System Components:**
- 🤖 **4 AI Agents:** Planner, Timesheet, Branding, Quality
- ⏰ **Temporal Workflows:** Daily reminders, conversation orchestration
- 📧 **Multi-Channel:** SMS, WhatsApp, Email support
- 🔧 **51 Harvest Tools:** Complete timesheet management
- 📊 **Opik Tracking:** LLM observability and monitoring

## 🏗️ **Infrastructure**

- **Resource Group:** `rg-secure-timesheet-agent`
- **Container Registry:** `secureagentreg2ai.azurecr.io`
- **Key Vault:** `kv-secure-agent-2ai`
- **Environment:** `secure-timesheet-env`
- **Location:** `australiaeast`
- **Temporal Server:** `temporal-dev-server` (internal)

## 📋 **Prerequisites**

1. **Azure CLI** installed and logged in (`az login`)
2. **Docker** with buildx support
3. **Access to Azure subscription** with Container Apps enabled
4. **API Keys:**
   - OpenRouter API key (for LLM)
   - Harvest API tokens (per user)
   - Twilio credentials (SMS/WhatsApp)
   - Supabase project (get your project ID from Supabase dashboard)
   - Gmail credentials (email sending & polling)

## 🚀 **Deployment Steps**

### **Step 1: Set Up Azure Key Vault Secrets**

Add all required secrets to Key Vault:

```bash
# LLM Configuration
az keyvault secret set --vault-name kv-secure-agent-2ai --name "OPENROUTER-API-KEY" --value "your_openrouter_key"
az keyvault secret set --vault-name kv-secure-agent-2ai --name "OPENAI-API-KEY" --value "your_openai_key"

# Harvest API (per user)
az keyvault secret set --vault-name kv-secure-agent-2ai --name "HARVEST-ACCESS-TOKEN" --value "your_harvest_token"
az keyvault secret set --vault-name kv-secure-agent-2ai --name "HARVEST-ACCOUNT-ID" --value "your_account_id"

# Additional users (if needed)
az keyvault secret set --vault-name kv-secure-agent-2ai --name "HARVEST-ACCESS-TOKEN-USER2" --value "your_harvest_token_user2"
az keyvault secret set --vault-name kv-secure-agent-2ai --name "HARVEST-ACCOUNT-ID-USER2" --value "your_account_id_user2"

# Twilio (SMS/WhatsApp)
az keyvault secret set --vault-name kv-secure-agent-2ai --name "TWILIO-ACCOUNT-SID" --value "your_sid"
az keyvault secret set --vault-name kv-secure-agent-2ai --name "TWILIO-AUTH-TOKEN" --value "your_token"
az keyvault secret set --vault-name kv-secure-agent-2ai --name "TWILIO-PHONE-NUMBER" --value "+1234567890"

# Gmail (Email Sending & Polling)
az keyvault secret set --vault-name kv-secure-agent-2ai --name "GMAIL-USER" --value "your@gmail.com"
az keyvault secret set --vault-name kv-secure-agent-2ai --name "GMAIL-PASSWORD" --value "your_app_password"

# Supabase
az keyvault secret set --vault-name kv-secure-agent-2ai --name "SUPABASE-KEY" --value "your_supabase_key"

# User Phone Numbers
az keyvault secret set --vault-name kv-secure-agent-2ai --name "USER-PHONE-NUMBER" --value "+61412345678"

# Additional users (if needed)
az keyvault secret set --vault-name kv-secure-agent-2ai --name "USER-PHONE-NUMBER-USER2" --value "+61412345679"
```

### **Step 2: Build and Push Docker Image**

```bash
# Login to Azure Container Registry
az acr login --name secureagentreg2ai

# Build the Docker image with timestamp tag
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker build -t secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-$TIMESTAMP .

# Tag as latest
docker tag secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-$TIMESTAMP \
  secureagentreg2ai.azurecr.io/multi-agent-system:latest

# Push both tags
docker push secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-$TIMESTAMP
docker push secureagentreg2ai.azurecr.io/multi-agent-system:latest

echo "Image pushed: multi-agent-system:1.0.0-$TIMESTAMP"
```

### **Step 3: Deploy/Update Container App**

**For first-time deployment:**
```bash
az containerapp create \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --environment secure-timesheet-env \
  --image secureagentreg2ai.azurecr.io/multi-agent-system:latest \
  --target-port 8003 \
  --ingress external \
  --registry-server secureagentreg2ai.azurecr.io \
  --cpu 1.0 --memory 2Gi \
  --min-replicas 1 --max-replicas 1 \
  --system-assigned \
  --env-vars \
    AZURE_KEY_VAULT_URL=https://kv-secure-agent-2ai.vault.azure.net/ \
    TEMPORAL_HOST=temporal-dev-server:7233 \
    TEMPORAL_NAMESPACE=default \
    SUPABASE_URL=https://<your-project-id>.supabase.co \
    USE_OPENROUTER=true \
    OPIK_ENABLED=true \
    PORT=8003
```

**For updates (recommended):**
```bash
# Update with new image
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --image secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-$TIMESTAMP
```

### **Step 4: Configure Key Vault Access**

```bash
# Get the managed identity principal ID
PRINCIPAL_ID=$(az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query identity.principalId -o tsv)

# Grant Key Vault access
az keyvault set-policy \
  --name kv-secure-agent-2ai \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

### **Step 5: Verify Deployment**

```bash
# Health check
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health

# System info
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/
```

## 🔧 **Container Configuration**

### **Unified Temporal Worker**
- **Name:** `unified-temporal-worker`
- **Port:** 8003
- **CPU:** 1.0 cores
- **Memory:** 2Gi
- **Replicas:** 1 (fixed)
- **Note:** Auto-scaling can be enabled by increasing max-replicas
- **Image:** `secureagentreg2ai.azurecr.io/multi-agent-system:latest`
  - Also tagged with timestamp: `1.0.0-YYYYMMDD-HHMMSS` (e.g., `1.0.0-20251201-185138`)

**Features:**
- ✅ **4 AI Agents:** Planner, Timesheet, Branding, Quality
- ✅ **Temporal Workflows:** Daily reminders, conversation orchestration
- ✅ **Multi-Channel Support:** SMS, WhatsApp, Email
- ✅ **51 Harvest Tools:** Complete timesheet API integration
- ✅ **LLM Integration:** OpenRouter/OpenAI with caching
- ✅ **Opik Tracking:** Full observability
- ✅ **Gmail Polling:** Automatic email monitoring (30s interval)
- ✅ **Rate Limiting:** Per-tenant and per-user limits
- ✅ **Circuit Breaker:** Automatic failure recovery

## 🌐 **API Endpoints**

### **System Endpoints:**
```
GET  /                              # System information & health
GET  /health                        # Detailed health check
```

### **Webhook Endpoints:**
```
POST /webhook/sms                   # Twilio SMS webhook
POST /webhook/whatsapp              # Twilio WhatsApp webhook
POST /webhook/email                 # Email webhook
```

### **Temporal Workflow Endpoints:**
```
POST /trigger-reminder/{user_id}    # Manual reminder for specific user
POST /trigger-daily-reminders       # Batch reminders for all users
POST /cleanup-old-workflows         # Cleanup old Temporal workflows
```

### **Governance Endpoints:**
```
GET  /governance/metrics            # Current governance metrics
GET  /governance/dashboard          # Governance dashboard data
GET  /governance/safety-report      # Comprehensive safety report
GET  /governance/actions            # Recent governance actions (limit param)
```

### **Testing Endpoints:**
```
POST /test/conversation             # Test conversation flow
GET  /test/harvest                  # Test Harvest API connection
```

## 🔑 **Environment Variables**

### **Required Environment Variables:**
```bash
# Azure
AZURE_KEY_VAULT_URL=https://kv-secure-agent-2ai.vault.azure.net/

# Temporal
TEMPORAL_HOST=temporal-dev-server:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TLS_ENABLED=false

# Supabase
SUPABASE_URL=https://<your-project-id>.supabase.co
# Example: https://czcrfhfioxypxavwwdji.supabase.co

# LLM
USE_OPENROUTER=true
OPENROUTER_MODEL=gpt-oss-20b

# Observability
OPIK_ENABLED=true
OPIK_PROJECT_NAME=unified-temporal-worker

# Server
PORT=8003
HTTP2_TRANSPORT=true
USE_DIRECT_INTERNAL_CALLS=true
```

### **Secrets (from Key Vault):**
All sensitive credentials are stored in Azure Key Vault and accessed via managed identity:
- `OPENROUTER-API-KEY`
- `OPENAI-API-KEY`
- `HARVEST-ACCESS-TOKEN`
- `HARVEST-ACCOUNT-ID`
- `HARVEST-ACCESS-TOKEN-USER2` (if multi-user)
- `HARVEST-ACCOUNT-ID-USER2` (if multi-user)
- `TWILIO-ACCOUNT-SID`
- `TWILIO-AUTH-TOKEN`
- `TWILIO-PHONE-NUMBER`
- `GMAIL-USER`
- `GMAIL-PASSWORD`
- `SUPABASE-KEY`
- `USER-PHONE-NUMBER`
- `USER-PHONE-NUMBER-USER2` (if multi-user)
- `OPIK-API-KEY`
- `OPIK-WORKSPACE`
- `OPIK-PROJECT`

## 🔐 **Security Features**

- **Non-root containers** for security
- **Managed identity** for Key Vault access
- **All secrets** stored in Azure Key Vault
- **HTTPS ingress** enabled
- **Auto-scaling** based on demand

## 🧪 **Testing**

### **Test System Health:**
```bash
BASE_URL="https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"

# Health check
curl $BASE_URL/health

# System information
curl $BASE_URL/

# Temporal status
curl $BASE_URL/temporal/status
```

### **Test Conversation Flow:**
```bash
# Test SMS conversation
curl -X POST $BASE_URL/test/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "message": "How many hours did I log this week?",
    "channel": "SMS"
  }'

# Test WhatsApp conversation
curl -X POST $BASE_URL/webhook/whatsapp \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+61412345678&Body=Check my timesheet"
```

### **Test Manual Reminder:**
```bash
# Trigger reminder for a user
curl -X POST "$BASE_URL/trigger-reminder?user_name=User1"
```

## 🔧 **Temporal Server**

**Current Setup:**
- **Server:** `temporal-dev-server` (Azure Container App)
- **Host:** `temporal-dev-server:7233` (internal)
- **Namespace:** `default`
- **TLS:** Disabled (internal communication)
- **Transport:** HTTP/2 with gRPC

**Architecture:**
```
[unified-temporal-worker] --HTTP/2--> [temporal-dev-server:7233]
                                            |
                                            v
                                    [PostgreSQL DB]
```

**Note:** The Temporal server is already deployed and running in the same Azure Container Apps environment.

## 📊 **Monitoring**

### **Application Monitoring:**
- ✅ **Health Checks:** Every 30 seconds
- ✅ **Application Logs:** Azure Container Apps
- ✅ **Metrics:** Azure Monitor
- ✅ **Opik Tracing:** https://www.comet.com/opik/ds2ai/projects/
- ✅ **LLM Observability:** Token usage, costs, latency
- ✅ **Gmail Polling:** Every 30 seconds

### **View Logs:**
```bash
# Real-time logs
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --follow

# Recent logs (last 100 lines)
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 100
```

### **Monitor Metrics:**
```bash
# View container metrics
az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.template.containers[0].resources"

# View revision history
az containerapp revision list \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "[].{Name:name, Created:properties.createdTime, Active:properties.active}"
```

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **1. LLM 402 Payment Required**
```bash
# Check OpenRouter API key and credits
az containerapp show --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.template.containers[0].env[?name=='OPENROUTER_API_KEY']"

# Update API key
az containerapp update --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --set-env-vars OPENROUTER_API_KEY="new-key"
```

#### **2. Circuit Breaker Open**
```bash
# Wait 60 seconds for automatic recovery
# Or restart the container
az containerapp revision restart \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent
```

#### **3. Key Vault Access Denied**
```bash
# Verify managed identity
PRINCIPAL_ID=$(az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query identity.principalId -o tsv)

echo "Principal ID: $PRINCIPAL_ID"

# Re-grant access
az keyvault set-policy \
  --name kv-secure-agent-2ai \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

#### **4. Temporal Connection Failed**
```bash
# Check Temporal server status
az containerapp show --name temporal-dev-server \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.runningStatus"

# Check connection from worker
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/temporal/status
```

#### **5. Gmail Polling Not Working**
```bash
# Check Gmail credentials in Key Vault
az keyvault secret show --vault-name kv-secure-agent-2ai --name GMAIL-USER
az keyvault secret show --vault-name kv-secure-agent-2ai --name GMAIL-PASSWORD

# Check logs for Gmail errors
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 100 | grep -i gmail
```

### **Useful Commands:**

```bash
# View logs
az containerapp logs show --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --follow

# Restart container
az containerapp revision restart --name unified-temporal-worker --resource-group rg-secure-timesheet-agent

# Scale container
az containerapp update --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --min-replicas 2 --max-replicas 5

# Update environment variable
az containerapp update --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --set-env-vars KEY=VALUE

# View current configuration
az containerapp show --name unified-temporal-worker --resource-group rg-secure-timesheet-agent
```

## ✅ **Success Criteria**

Deployment is successful when:
- ✅ Health endpoint returns 200 OK with system info
- ✅ Key Vault secrets are accessible via managed identity
- ✅ Temporal connection is established (check `/temporal/status`)
- ✅ Supabase database is connected
- ✅ All 4 agents are initialized (Planner, Timesheet, Branding, Quality)
- ✅ LLM calls are working (no 402 errors)
- ✅ Opik tracking is enabled and logging
- ✅ Gmail polling is running (check logs)
- ✅ Webhook endpoints respond correctly
- ✅ Circuit breaker is closed

## 📊 **Post-Deployment Verification**

### **1. Check System Health:**
```bash
curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health | jq
```

**Expected Response:**
```json
{
  "status": "healthy",
  "temporal": "✅ Connected",
  "supabase": "✅ Connected",
  "opik": "✅ Enabled",
  "agents": {
    "planner": "✅ Ready",
    "timesheet": "✅ Ready",
    "branding": "✅ Ready",
    "quality": "✅ Ready"
  },
  "llm": {
    "provider": "openrouter",
    "circuit_breaker": "closed"
  }
}
```

### **2. Test Conversation Flow:**
```bash
# Send test message
curl -X POST https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/test/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "How many hours did I log this week?",
    "channel": "SMS"
  }'
```

### **3. Verify Opik Tracking:**
1. Go to https://www.comet.com/opik/ds2ai/projects/
2. Look for project: `unified-temporal-worker`
3. Verify traces are being logged
4. Check token usage and costs

### **4. Monitor Logs:**
```bash
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --follow
```

Look for:
- ✅ "Opik Tracking: Enabled"
- ✅ "Temporal client connected"
- ✅ "Gmail polling cycle starting"
- ✅ "All agents initialized"

## 🎯 **Next Steps**

After successful deployment:

1. **Add OpenRouter Credits**
   - Go to https://openrouter.ai/settings/credits
   - Add at least $5 for testing

2. **Configure Twilio Webhooks**
   - SMS: `https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms`
   - WhatsApp: `https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/whatsapp`

3. **Test Real Conversations**
   - Send SMS to Twilio number
   - Send WhatsApp message
   - Send email to monitored Gmail account

4. **Set Up Monitoring Alerts**
   - Configure Azure Monitor alerts
   - Set up Opik alerts for high costs
   - Monitor circuit breaker status

5. **Configure Auto-Scaling**
   ```bash
   az containerapp update \
     --name unified-temporal-worker \
     --resource-group rg-secure-timesheet-agent \
     --min-replicas 1 \
     --max-replicas 5
   ```

6. **Set Up CI/CD Pipeline**
   - Create GitHub Actions workflow
   - Automate Docker build and push
   - Automate container app updates

## 📦 **Quick Deployment Script**

Save this as `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Login to Azure
az acr login --name secureagentreg2ai

# Build and push
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE="secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-$TIMESTAMP"

echo "📦 Building image: $IMAGE"
docker build -t $IMAGE .
docker tag $IMAGE secureagentreg2ai.azurecr.io/multi-agent-system:latest

echo "⬆️ Pushing image..."
docker push $IMAGE
docker push secureagentreg2ai.azurecr.io/multi-agent-system:latest

echo "🔄 Updating container app..."
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --image $IMAGE

echo "✅ Deployment complete!"
echo "🔗 URL: https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"
echo "📊 Health: https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health"
```

Make it executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

## 📞 **Support**

If you encounter issues:

1. **Check Logs:**
   ```bash
   az containerapp logs show --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --follow
   ```

2. **Verify Key Vault Access:**
   ```bash
   az keyvault show --name kv-secure-agent-2ai --query "properties.accessPolicies"
   ```

3. **Test Network Connectivity:**
   ```bash
   curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health
   ```

4. **Review Temporal Status:**
   ```bash
   curl https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/temporal/status
   ```

5. **Check Opik Dashboard:**
   - https://www.comet.com/opik/ds2ai/projects/

---

**🎉 Your Unified Multi-Agent System is now deployed and ready for production use!**

**System URL:** https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io

**Features:**
- ✅ 4 AI Agents working together
- ✅ Multi-channel support (SMS, WhatsApp, Email)
- ✅ 51 Harvest API tools
- ✅ Temporal workflows for automation
- ✅ Full observability with Opik
- ✅ Production-ready with auto-scaling

🚀 **Happy deploying!**
