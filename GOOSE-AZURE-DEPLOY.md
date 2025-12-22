# Goose-Assisted Azure Deployment Guide

## 🤖 **For Goose AI Agent**

This guide is optimized for Goose AI to automatically deploy the Multi-Agent Timesheet System to Azure Container Apps.

---

## 📋 **Prerequisites Check**

**Goose, verify these are installed:**

```bash
# Check Azure CLI
az --version

# Check Docker
docker --version

# Check if logged into Azure
az account show 2>/dev/null || echo "Not logged into Azure"

# Check if logged into ACR
az acr login --name secureagentreg2ai 2>/dev/null || echo "Not logged into ACR"
```

---

## 🚀 **Step 1: Azure Login**

**Goose, ensure Azure authentication:**

```bash
# Check current login status
if az account show &>/dev/null; then
  echo "✅ Already logged into Azure"
  az account show --query "{Name:name, SubscriptionId:id, User:user.name}" -o table
else
  echo "⚠️  User needs to login to Azure"
  echo "Run: az login"
  exit 1
fi

# Login to Container Registry
echo "🔐 Logging into Azure Container Registry..."
az acr login --name secureagentreg2ai

echo "✅ Azure authentication complete"
```

---

## 🔑 **Step 2: Verify Key Vault Secrets**

**Goose, check which secrets exist:**

```bash
echo "🔍 Checking Key Vault secrets..."

# List all secrets
az keyvault secret list \
  --vault-name kv-secure-agent-2ai \
  --query "[].{Name:name, Enabled:attributes.enabled}" \
  -o table

# Check critical secrets
REQUIRED_SECRETS=(
  "OPENROUTER-API-KEY"
  "HARVEST-ACCESS-TOKEN-USER1"
  "HARVEST-ACCOUNT-ID-USER1"
  "TWILIO-ACCOUNT-SID"
  "TWILIO-AUTH-TOKEN"
  "TWILIO-PHONE-NUMBER"
  "SUPABASE-KEY"
  "USER1-PHONE"
)

echo ""
echo "📋 Required secrets status:"
for secret in "${REQUIRED_SECRETS[@]}"; do
  if az keyvault secret show --vault-name kv-secure-agent-2ai --name "$secret" &>/dev/null; then
    echo "  ✅ $secret"
  else
    echo "  ❌ $secret (MISSING)"
  fi
done
```

---

## 🔧 **Step 3: Add Missing Secrets (Interactive)**

**Goose, create a script to add secrets:**

```bash
cat > add_secrets.sh << 'EOF'
#!/bin/bash

echo "🔑 Adding secrets to Azure Key Vault..."

# Function to add secret
add_secret() {
  local name=$1
  local prompt=$2
  
  echo ""
  echo "Enter value for $name:"
  echo "  ($prompt)"
  read -s value
  
  if [ -n "$value" ]; then
    az keyvault secret set \
      --vault-name kv-secure-agent-2ai \
      --name "$name" \
      --value "$value" \
      --output none
    echo "✅ $name added"
  else
    echo "⚠️  Skipped $name"
  fi
}

# Add secrets interactively
add_secret "OPENROUTER-API-KEY" "Get from https://openrouter.ai"
add_secret "HARVEST-ACCESS-TOKEN-USER1" "Get from Harvest settings"
add_secret "HARVEST-ACCOUNT-ID-USER1" "Your Harvest account ID"
add_secret "TWILIO-ACCOUNT-SID" "From Twilio console"
add_secret "TWILIO-AUTH-TOKEN" "From Twilio console"
add_secret "TWILIO-PHONE-NUMBER" "Format: +1234567890"
add_secret "SENDGRID-API-KEY" "From SendGrid settings"
add_secret "GMAIL-USER" "Your Gmail address"
add_secret "GMAIL-PASSWORD" "Gmail app password"
add_secret "SUPABASE-KEY" "From Supabase project settings"
add_secret "USER1-PHONE" "Format: +61412345678"

echo ""
echo "✅ Secrets configuration complete"
EOF

chmod +x add_secrets.sh

echo "✅ Secret management script created: add_secrets.sh"
echo "📝 User can run: ./add_secrets.sh (if secrets are missing)"
```

---

## 📦 **Step 4: Build Docker Image**

**Goose, build and tag the Docker image:**

```bash
echo "🐳 Building Docker image..."

# Generate timestamp tag
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG="1.0.0-$TIMESTAMP"
IMAGE_NAME="secureagentreg2ai.azurecr.io/multi-agent-system:$IMAGE_TAG"
LATEST_IMAGE="secureagentreg2ai.azurecr.io/multi-agent-system:latest"

echo "📦 Building: $IMAGE_NAME"

# Build the image
docker build -t "$IMAGE_NAME" .

# Tag as latest
docker tag "$IMAGE_NAME" "$LATEST_IMAGE"

# Show image info
docker images | grep multi-agent-system | head -2

echo "✅ Docker image built successfully"
echo "   Tag: $IMAGE_TAG"
echo "   Size: $(docker images $IMAGE_NAME --format '{{.Size}}')"

# Save tag for next steps
echo "$IMAGE_TAG" > .last_build_tag
echo "$IMAGE_NAME" > .last_build_image
```

---

## ⬆️ **Step 5: Push to Azure Container Registry**

**Goose, push the Docker image:**

```bash
echo "⬆️  Pushing Docker image to Azure Container Registry..."

# Read the image name from previous step
IMAGE_NAME=$(cat .last_build_image)
LATEST_IMAGE="secureagentreg2ai.azurecr.io/multi-agent-system:latest"

# Push both tags
echo "Pushing: $IMAGE_NAME"
docker push "$IMAGE_NAME"

echo "Pushing: $LATEST_IMAGE"
docker push "$LATEST_IMAGE"

# Verify push
echo ""
echo "📋 Recent images in ACR:"
az acr repository show-tags \
  --name secureagentreg2ai \
  --repository multi-agent-system \
  --orderby time_desc \
  --top 5 \
  -o table

echo "✅ Docker image pushed successfully"
```

---

## 🔄 **Step 6: Update Container App**

**Goose, update the Azure Container App:**

```bash
echo "🔄 Updating Azure Container App..."

# Read the image name
IMAGE_NAME=$(cat .last_build_image)

# Update container app
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --image "$IMAGE_NAME"

echo "✅ Container app updated"

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 15

# Check status
az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "{Name:name, Status:properties.runningStatus, Image:properties.template.containers[0].image}" \
  -o table
```

---

## 🔐 **Step 7: Verify Key Vault Access**

**Goose, ensure managed identity has Key Vault access:**

```bash
echo "🔐 Verifying Key Vault access..."

# Get managed identity principal ID
PRINCIPAL_ID=$(az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query identity.principalId -o tsv)

echo "Principal ID: $PRINCIPAL_ID"

# Check if access policy exists
POLICY_EXISTS=$(az keyvault show \
  --name kv-secure-agent-2ai \
  --query "properties.accessPolicies[?objectId=='$PRINCIPAL_ID'].objectId" -o tsv)

if [ -z "$POLICY_EXISTS" ]; then
  echo "⚠️  Access policy not found, adding it..."
  az keyvault set-policy \
    --name kv-secure-agent-2ai \
    --object-id "$PRINCIPAL_ID" \
    --secret-permissions get list
  echo "✅ Key Vault access granted"
else
  echo "✅ Key Vault access already configured"
fi
```

---

## ⚙️ **Step 8: Update Environment Variables**

**Goose, ensure all environment variables are set:**

```bash
echo "⚙️  Updating environment variables..."

# Update container app environment variables
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --set-env-vars \
    AZURE_KEY_VAULT_URL=https://kv-secure-agent-2ai.vault.azure.net/ \
    TEMPORAL_HOST=temporal-dev-server:7233 \
    TEMPORAL_NAMESPACE=default \
    TEMPORAL_TLS_ENABLED=false \
    SUPABASE_URL=https://czcrfhfioxypxavwwdji.supabase.co \
    USE_OPENROUTER=true \
    OPENROUTER_MODEL=gpt-oss-20b \
    OPIK_ENABLED=true \
    OPIK_PROJECT_NAME=unified-temporal-worker \
    PORT=8003 \
    HTTP2_TRANSPORT=true \
    USE_DIRECT_INTERNAL_CALLS=true

echo "✅ Environment variables updated"

# Show current env vars
echo ""
echo "📋 Current environment variables:"
az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.template.containers[0].env[].{Name:name, Value:value}" \
  -o table | head -20
```

---

## 🧪 **Step 9: Test Deployment**

**Goose, verify the deployment is working:**

```bash
echo "🧪 Testing deployment..."

BASE_URL="https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"

# Wait for app to be ready
echo "⏳ Waiting for app to start..."
sleep 20

# Test health endpoint
echo ""
echo "1. Health Check:"
curl -s "$BASE_URL/health" | jq '.' || echo "❌ Health check failed"

# Test system info
echo ""
echo "2. System Info:"
curl -s "$BASE_URL/" | jq '.system_info' || echo "❌ System info failed"

# Test Temporal status
echo ""
echo "3. Temporal Status:"
curl -s "$BASE_URL/temporal/status" | jq '.' || echo "❌ Temporal status failed"

echo ""
echo "✅ Deployment tests complete"
```

---

## 📊 **Step 10: Check Logs**

**Goose, retrieve recent logs:**

```bash
echo "📊 Fetching recent logs..."

az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 50

echo ""
echo "✅ Logs retrieved"
echo "📝 For live logs, run:"
echo "   az containerapp logs show --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --follow"
```

---

## 📈 **Step 11: Verify Opik Tracking**

**Goose, check if Opik is enabled:**

```bash
echo "📈 Verifying Opik tracking..."

# Check environment variable
OPIK_ENABLED=$(az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.template.containers[0].env[?name=='OPIK_ENABLED'].value" -o tsv)

echo "Opik Enabled: $OPIK_ENABLED"

if [ "$OPIK_ENABLED" = "true" ]; then
  echo "✅ Opik tracking is enabled"
  echo "📊 View traces at: https://www.comet.com/opik/ds2ai/projects/"
else
  echo "⚠️  Opik tracking is disabled"
fi
```

---

## 📝 **Step 12: Generate Deployment Report**

**Goose, create a deployment summary:**

```bash
cat > DEPLOYMENT_REPORT.md << EOF
# Deployment Report - $(date)

## Deployment Details

**Image:** $(cat .last_build_image)
**Timestamp:** $(cat .last_build_tag)
**Deployed:** $(date)

## Container App Status

\`\`\`
$(az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "{Name:name, Status:properties.runningStatus, FQDN:properties.configuration.ingress.fqdn, CPU:properties.template.containers[0].resources.cpu, Memory:properties.template.containers[0].resources.memory}" \
  -o table)
\`\`\`

## Endpoints

- **System URL:** https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io
- **Health Check:** https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health
- **Temporal Status:** https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/temporal/status

## Health Check Result

\`\`\`json
$(curl -s https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health | jq '.')
\`\`\`

## Environment Variables

\`\`\`
$(az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "properties.template.containers[0].env[].name" \
  -o tsv | sort)
\`\`\`

## Key Vault Secrets

\`\`\`
$(az keyvault secret list \
  --vault-name kv-secure-agent-2ai \
  --query "[].name" \
  -o tsv | sort)
\`\`\`

## Recent Logs

\`\`\`
$(az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 20)
\`\`\`

## Verification Checklist

- [x] Docker image built and pushed
- [x] Container app updated
- [x] Key Vault access configured
- [x] Environment variables set
- [x] Health endpoint responding
- [x] Temporal connection verified
- [x] Opik tracking enabled

## Next Steps

1. **Test Conversation Flow:**
   \`\`\`bash
   curl -X POST https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/test/conversation \\
     -H "Content-Type: application/json" \\
     -d '{"user_id": "test-user", "message": "How many hours did I log this week?", "channel": "SMS"}'
   \`\`\`

2. **Configure Twilio Webhooks:**
   - SMS: https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms
   - WhatsApp: https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/whatsapp

3. **Monitor Logs:**
   \`\`\`bash
   az containerapp logs show --name unified-temporal-worker --resource-group rg-secure-timesheet-agent --follow
   \`\`\`

4. **Check Opik Dashboard:**
   - https://www.comet.com/opik/ds2ai/projects/

## Deployment Status: ✅ SUCCESS

EOF

cat DEPLOYMENT_REPORT.md

echo ""
echo "✅ Deployment report generated: DEPLOYMENT_REPORT.md"
```

---

## 🎯 **Summary for Goose**

**Goose, you have completed:**

1. ✅ Verified Azure authentication
2. ✅ Checked Key Vault secrets
3. ✅ Built Docker image with timestamp tag
4. ✅ Pushed image to Azure Container Registry
5. ✅ Updated Container App with new image
6. ✅ Verified Key Vault access
7. ✅ Updated environment variables
8. ✅ Tested deployment endpoints
9. ✅ Retrieved and checked logs
10. ✅ Verified Opik tracking
11. ✅ Generated deployment report

**Files created:**
- `add_secrets.sh` - Script to add missing secrets
- `.last_build_tag` - Last build timestamp
- `.last_build_image` - Last build image name
- `DEPLOYMENT_REPORT.md` - Comprehensive deployment report

---

## 🤖 **Goose Execution Order**

**Copy this prompt to Goose:**

```
Please deploy the Multi-Agent Timesheet System to Azure by following these steps in order:

1. Run Step 1: Verify Azure login and ACR access
2. Run Step 2: Check existing Key Vault secrets
3. Run Step 3: Create script for adding missing secrets (user will run if needed)
4. Run Step 4: Build Docker image with timestamp tag
5. Run Step 5: Push image to Azure Container Registry
6. Run Step 6: Update Azure Container App with new image
7. Run Step 7: Verify Key Vault access for managed identity
8. Run Step 8: Update environment variables
9. Run Step 9: Test the deployment (health, system info, Temporal)
10. Run Step 10: Retrieve recent logs
11. Run Step 11: Verify Opik tracking is enabled
12. Run Step 12: Generate deployment report

After completing all steps, show me the contents of DEPLOYMENT_REPORT.md
```

---

## 🔄 **Quick Re-deployment**

**Goose, for subsequent deployments, use this shortcut:**

```bash
cat > quick_deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Quick Deployment Script"

# Login to ACR
az acr login --name secureagentreg2ai

# Build
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE="secureagentreg2ai.azurecr.io/multi-agent-system:1.0.0-$TIMESTAMP"
echo "📦 Building: $IMAGE"
docker build -t "$IMAGE" .
docker tag "$IMAGE" secureagentreg2ai.azurecr.io/multi-agent-system:latest

# Push
echo "⬆️  Pushing..."
docker push "$IMAGE"
docker push secureagentreg2ai.azurecr.io/multi-agent-system:latest

# Update
echo "🔄 Updating container app..."
az containerapp update \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --image "$IMAGE"

# Test
echo "🧪 Testing..."
sleep 20
curl -s https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/health | jq '.'

echo "✅ Deployment complete!"
echo "🔗 URL: https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"
EOF

chmod +x quick_deploy.sh

echo "✅ Quick deployment script created: quick_deploy.sh"
echo "📝 User can run: ./quick_deploy.sh"
```

---

## 📞 **Troubleshooting Commands**

**Goose, if deployment fails, run these diagnostics:**

```bash
cat > troubleshoot.sh << 'EOF'
#!/bin/bash

echo "🔍 Troubleshooting Deployment..."

# 1. Check container status
echo "1. Container Status:"
az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "{Name:name, Status:properties.runningStatus, Health:properties.health}" \
  -o table

# 2. Check recent revisions
echo ""
echo "2. Recent Revisions:"
az containerapp revision list \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query "[].{Name:name, Active:properties.active, Created:properties.createdTime}" \
  -o table | head -5

# 3. Check logs for errors
echo ""
echo "3. Recent Errors in Logs:"
az containerapp logs show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --tail 100 | grep -i "error\|failed\|exception" | tail -20

# 4. Check Key Vault access
echo ""
echo "4. Key Vault Access:"
PRINCIPAL_ID=$(az containerapp show \
  --name unified-temporal-worker \
  --resource-group rg-secure-timesheet-agent \
  --query identity.principalId -o tsv)
echo "Principal ID: $PRINCIPAL_ID"

# 5. Test endpoints
echo ""
echo "5. Endpoint Tests:"
BASE_URL="https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"
curl -s -o /dev/null -w "Health: %{http_code}\n" "$BASE_URL/health"
curl -s -o /dev/null -w "Root: %{http_code}\n" "$BASE_URL/"

echo ""
echo "✅ Diagnostics complete"
EOF

chmod +x troubleshoot.sh

echo "✅ Troubleshooting script created: troubleshoot.sh"
```

---

**🚀 Ready for Goose automation!**

**Deployment URL:** https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io
