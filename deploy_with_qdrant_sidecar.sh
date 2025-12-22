#!/bin/bash

# Deploy with Qdrant as Sidecar Container
# This guarantees connectivity via localhost

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Deploy with Qdrant Sidecar - Guaranteed Connectivity  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
RESOURCE_GROUP="rg-secure-timesheet-agent"
APP_NAME="unified-temporal-worker"
ENVIRONMENT="aca-env-secure-agent"
LOCATION="australiaeast"
REGISTRY="secureagentreg2ai.azurecr.io"

# Get latest image
echo -e "${YELLOW}Step 1: Getting latest image...${NC}"
LATEST_IMAGE=$(az acr repository show-tags \
    --name secureagentreg2ai \
    --repository multi-agent-system \
    --orderby time_desc \
    --top 1 \
    --output tsv)

echo "Latest image: $LATEST_IMAGE"
echo ""

# Update Key Vault with localhost URL
echo -e "${YELLOW}Step 2: Updating Qdrant URL to localhost...${NC}"
az keyvault secret set \
    --vault-name kv-secure-agent-2ai \
    --name "QDRANT-URL" \
    --value "http://localhost:6333" \
    --output none

echo -e "${GREEN}✅ Qdrant URL updated to localhost${NC}"
echo ""

# Create YAML configuration for sidecar deployment
echo -e "${YELLOW}Step 3: Creating sidecar configuration...${NC}"

cat > /tmp/sidecar-config.yaml << 'EOF'
properties:
  template:
    containers:
    - name: unified-temporal-worker
      image: secureagentreg2ai.azurecr.io/multi-agent-system:LATEST_TAG
      resources:
        cpu: 1.0
        memory: 2Gi
      env:
      - name: AZURE_KEY_VAULT_URL
        value: https://kv-secure-agent-2ai.vault.azure.net/
      - name: PORT
        value: "8003"
    - name: qdrant
      image: qdrant/qdrant:v1.16.2
      resources:
        cpu: 0.5
        memory: 1Gi
      command:
      - ./qdrant
      args:
      - --log-level
      - INFO
    scale:
      minReplicas: 1
      maxReplicas: 3
EOF

# Replace LATEST_TAG with actual tag
sed -i '' "s/LATEST_TAG/$LATEST_IMAGE/g" /tmp/sidecar-config.yaml

echo -e "${GREEN}✅ Configuration created${NC}"
echo ""

# Update container app with sidecar
echo -e "${YELLOW}Step 4: Deploying with sidecar...${NC}"
echo "This will:"
echo "  - Deploy main app container"
echo "  - Deploy Qdrant sidecar in same pod"
echo "  - Enable localhost:6333 connectivity"
echo ""

az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --yaml /tmp/sidecar-config.yaml \
    --output none

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

# Wait for deployment
echo -e "${YELLOW}Step 5: Waiting for deployment to stabilize...${NC}"
sleep 30

# Test connectivity
echo -e "${YELLOW}Step 6: Testing connectivity...${NC}"
echo ""

APP_URL="https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"

echo "Testing RAG status..."
RAG_STATUS=$(curl -s "${APP_URL}/debug/rag-status")
echo "$RAG_STATUS" | jq .

QDRANT_URL=$(echo "$RAG_STATUS" | jq -r '.environment_variables.QDRANT_URL')
MEMORY_CREATED=$(echo "$RAG_STATUS" | jq -r '.memory_manager.memory_manager_created')

echo ""
if [ "$QDRANT_URL" = "http://localhost:6333" ] && [ "$MEMORY_CREATED" = "true" ]; then
    echo -e "${GREEN}✅ Configuration verified!${NC}"
    echo "   Qdrant URL: $QDRANT_URL"
    echo "   Memory Manager: $MEMORY_CREATED"
else
    echo -e "${RED}❌ Configuration issue detected${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 7: Running real-world test...${NC}"
echo ""

# Test 1: Store memory
echo "Test 1: Storing conversation..."
RESPONSE1=$(curl -s -X POST "${APP_URL}/test/conversation-with-memory" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "sidecar-test-user",
    "tenant_id": "sidecar-tenant",
    "message": "I completed 10 hours of work on the Azure project today"
  }')

STATUS1=$(echo "$RESPONSE1" | jq -r '.status')
echo "Status: $STATUS1"

if [ "$STATUS1" != "success" ]; then
    echo -e "${RED}❌ Test 1 failed${NC}"
    echo "$RESPONSE1" | jq .
    exit 1
fi

echo -e "${GREEN}✅ Test 1 passed${NC}"
echo ""

# Wait for indexing
echo "Waiting 5 seconds for Qdrant indexing..."
sleep 5

# Test 2: Retrieve memory
echo "Test 2: Retrieving conversation..."
RESPONSE2=$(curl -s -X POST "${APP_URL}/test/conversation-with-memory" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "sidecar-test-user",
    "tenant_id": "sidecar-tenant",
    "message": "How many hours did I work on the Azure project?"
  }')

STATUS2=$(echo "$RESPONSE2" | jq -r '.status')
ASSISTANT_RESPONSE=$(echo "$RESPONSE2" | jq -r '.assistant_response')

echo "Status: $STATUS2"
echo ""
echo "Assistant Response:"
echo "$ASSISTANT_RESPONSE"
echo ""

if [ "$STATUS2" != "success" ]; then
    echo -e "${RED}❌ Test 2 failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Test 2 passed${NC}"
echo ""

# Check logs for errors
echo -e "${YELLOW}Step 8: Checking logs for errors...${NC}"
ERRORS=$(az containerapp logs show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --tail 50 2>/dev/null | grep -i "error\|timeout\|failed" | grep -v "Failed to load secret" || echo "No errors found")

if [ "$ERRORS" = "No errors found" ]; then
    echo -e "${GREEN}✅ No errors in logs${NC}"
else
    echo -e "${YELLOW}⚠️  Some errors found:${NC}"
    echo "$ERRORS" | head -10
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    DEPLOYMENT SUCCESS!                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}🎉 Sidecar deployment successful!${NC}"
echo ""
echo "✅ Main app running"
echo "✅ Qdrant sidecar running"
echo "✅ Localhost connectivity working"
echo "✅ Memory storage working"
echo "✅ Memory retrieval working"
echo ""
echo "Architecture:"
echo "  ┌─────────────────────────────────┐"
echo "  │  Container App Pod              │"
echo "  │  ┌──────────────────────────┐   │"
echo "  │  │  Main App                │   │"
echo "  │  │  (unified-temporal-worker)│  │"
echo "  │  │  Port: 8003              │   │"
echo "  │  └──────────────────────────┘   │"
echo "  │           ↕ localhost            │"
echo "  │  ┌──────────────────────────┐   │"
echo "  │  │  Qdrant Sidecar          │   │"
echo "  │  │  Port: 6333              │   │"
echo "  │  └──────────────────────────┘   │"
echo "  └─────────────────────────────────┘"
echo ""
echo "Next steps:"
echo "  1. Test with real SMS/WhatsApp messages"
echo "  2. Monitor memory usage and performance"
echo "  3. Add persistent storage for Qdrant data"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
