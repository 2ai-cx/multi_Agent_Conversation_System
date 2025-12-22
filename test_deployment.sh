#!/bin/bash

# Test Deployment - Verify RAG/Qdrant Integration
# This script performs comprehensive tests to verify the deployment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_URL="https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"
RESOURCE_GROUP="rg-secure-timesheet-agent"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Deployment Verification Tests                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
HEALTH_RESPONSE=$(curl -s "${APP_URL}/health")
HEALTH_STATUS=$(echo $HEALTH_RESPONSE | jq -r '.status' 2>/dev/null || echo "error")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ PASS: Application is healthy${NC}"
    echo "   Response: $(echo $HEALTH_RESPONSE | jq -c '.' 2>/dev/null || echo $HEALTH_RESPONSE)"
else
    echo -e "${RED}❌ FAIL: Application health check failed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
fi
echo ""

# Test 2: Check Container Status
echo -e "${YELLOW}Test 2: Container Status${NC}"
MAIN_APP_STATUS=$(az containerapp show --name unified-temporal-worker --resource-group $RESOURCE_GROUP --query "properties.runningStatus" -o tsv 2>/dev/null)
QDRANT_STATUS=$(az containerapp show --name qdrant-service --resource-group $RESOURCE_GROUP --query "properties.runningStatus" -o tsv 2>/dev/null)

if [ "$MAIN_APP_STATUS" = "Running" ]; then
    echo -e "${GREEN}✅ PASS: Main app is running${NC}"
else
    echo -e "${RED}❌ FAIL: Main app status: $MAIN_APP_STATUS${NC}"
fi

if [ "$QDRANT_STATUS" = "Running" ]; then
    echo -e "${GREEN}✅ PASS: Qdrant service is running${NC}"
else
    echo -e "${RED}❌ FAIL: Qdrant status: $QDRANT_STATUS${NC}"
fi
echo ""

# Test 3: Check Key Vault Secrets
echo -e "${YELLOW}Test 3: RAG Secrets in Key Vault${NC}"
SECRETS_TO_CHECK=("RAG-ENABLED" "VECTOR-DB-PROVIDER" "QDRANT-URL" "EMBEDDINGS-PROVIDER")
SECRETS_OK=true

for secret in "${SECRETS_TO_CHECK[@]}"; do
    if az keyvault secret show --vault-name kv-secure-agent-2ai --name "$secret" &>/dev/null; then
        VALUE=$(az keyvault secret show --vault-name kv-secure-agent-2ai --name "$secret" --query value -o tsv 2>/dev/null)
        echo -e "${GREEN}✅ $secret = $VALUE${NC}"
    else
        echo -e "${RED}❌ $secret - NOT FOUND${NC}"
        SECRETS_OK=false
    fi
done

if [ "$SECRETS_OK" = true ]; then
    echo -e "${GREEN}✅ PASS: All RAG secrets configured${NC}"
else
    echo -e "${RED}❌ FAIL: Some secrets missing${NC}"
fi
echo ""

# Test 4: Check if LLMConfig loads RAG settings
echo -e "${YELLOW}Test 4: Check Application Configuration${NC}"
echo "Checking if RAG configuration is loaded..."

# Try to find RAG-related logs
RAG_LOGS=$(az containerapp logs show --name unified-temporal-worker --resource-group $RESOURCE_GROUP --tail 300 2>/dev/null | grep -i "rag\|qdrant" || echo "")

if [ -n "$RAG_LOGS" ]; then
    echo -e "${GREEN}✅ PASS: RAG-related logs found${NC}"
    echo "$RAG_LOGS" | head -5
else
    echo -e "${YELLOW}⚠️  WARNING: No RAG logs found in recent output${NC}"
    echo "   This might mean:"
    echo "   1. RAG is not enabled (RAG_ENABLED=false)"
    echo "   2. No RAG operations have occurred yet"
    echo "   3. Logs have rotated"
fi
echo ""

# Test 5: Check Qdrant Service
echo -e "${YELLOW}Test 5: Qdrant Service Health${NC}"
QDRANT_URL=$(az keyvault secret show --vault-name kv-secure-agent-2ai --name "QDRANT-URL" --query value -o tsv 2>/dev/null)
echo "Qdrant URL: $QDRANT_URL"

if [ -n "$QDRANT_URL" ]; then
    echo -e "${GREEN}✅ PASS: Qdrant URL configured${NC}"
else
    echo -e "${RED}❌ FAIL: Qdrant URL not found${NC}"
fi
echo ""

# Test 6: Check Docker Image
echo -e "${YELLOW}Test 6: Docker Image Verification${NC}"
CURRENT_IMAGE=$(az containerapp show --name unified-temporal-worker --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].image" -o tsv 2>/dev/null)
echo "Current image: $CURRENT_IMAGE"

if [[ "$CURRENT_IMAGE" == *"20251211"* ]]; then
    echo -e "${GREEN}✅ PASS: Running latest image (today's build)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: Image might not be latest${NC}"
fi
echo ""

# Test 7: Check Environment Variables
echo -e "${YELLOW}Test 7: Environment Variables${NC}"
ENV_VARS=$(az containerapp show --name unified-temporal-worker --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].env[].name" -o tsv 2>/dev/null)

if echo "$ENV_VARS" | grep -q "AZURE_KEY_VAULT_URL"; then
    echo -e "${GREEN}✅ PASS: AZURE_KEY_VAULT_URL configured${NC}"
else
    echo -e "${RED}❌ FAIL: AZURE_KEY_VAULT_URL not found${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Test Summary                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Count results
TOTAL_TESTS=7
echo "Total Tests: $TOTAL_TESTS"
echo ""

# Recommendations
echo -e "${YELLOW}📋 Recommendations:${NC}"
echo ""
echo "1. Check if RAG is actually enabled:"
echo "   - Verify RAG_ENABLED=true in Key Vault"
echo "   - Check application logs for RAG initialization"
echo ""
echo "2. Test RAG functionality manually:"
echo "   - Send a conversation via API"
echo "   - Check if it's stored in Qdrant"
echo "   - Verify context retrieval works"
echo ""
echo "3. Monitor logs for errors:"
echo "   az containerapp logs show --name unified-temporal-worker --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "4. Check Qdrant logs:"
echo "   az containerapp logs show --name qdrant-service --resource-group $RESOURCE_GROUP --follow"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
