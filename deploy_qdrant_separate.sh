#!/bin/bash

# Deploy Qdrant as Separate Azure Container App
# This creates a dedicated Qdrant service that your main app can connect to

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
RESOURCE_GROUP="rg-secure-timesheet-agent"
ENVIRONMENT="secure-timesheet-env"
QDRANT_APP="qdrant-service"
KEY_VAULT="kv-secure-agent-2ai"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Deploy Qdrant as Separate Service               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if already exists
if az containerapp show --name "${QDRANT_APP}" --resource-group "${RESOURCE_GROUP}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Qdrant service already exists${NC}"
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled"
        exit 0
    fi
    DEPLOY_MODE="update"
else
    DEPLOY_MODE="create"
fi

if [ "$DEPLOY_MODE" = "create" ]; then
    echo -e "${YELLOW}🚀 Creating Qdrant Container App${NC}"
    
    az containerapp create \
        --name "${QDRANT_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --environment "${ENVIRONMENT}" \
        --image qdrant/qdrant:latest \
        --target-port 6333 \
        --ingress internal \
        --cpu 0.5 \
        --memory 1.0Gi \
        --min-replicas 1 \
        --max-replicas 1 \
        --env-vars \
            QDRANT__SERVICE__HTTP_PORT=6333 \
        --output none
    
    echo -e "${GREEN}✅ Qdrant service created${NC}"
else
    echo -e "${YELLOW}🔄 Updating Qdrant Container App${NC}"
    
    az containerapp update \
        --name "${QDRANT_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --image qdrant/qdrant:latest \
        --cpu 0.5 \
        --memory 1.0Gi \
        --output none
    
    echo -e "${GREEN}✅ Qdrant service updated${NC}"
fi

echo ""

# Get Qdrant URL
echo -e "${YELLOW}🌐 Getting Qdrant Service URL${NC}"

QDRANT_FQDN=$(az containerapp show \
    --name "${QDRANT_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query properties.configuration.ingress.fqdn -o tsv)

QDRANT_URL="http://${QDRANT_FQDN}"

echo -e "${GREEN}✅ Qdrant URL: ${QDRANT_URL}${NC}"
echo ""

# Update Key Vault secret
echo -e "${YELLOW}🔐 Updating QDRANT-URL in Key Vault${NC}"

az keyvault secret set \
    --vault-name "${KEY_VAULT}" \
    --name "QDRANT-URL" \
    --value "${QDRANT_URL}" \
    --description "Qdrant service URL (separate container app)" \
    --output none

echo -e "${GREEN}✅ Key Vault secret updated${NC}"
echo ""

# Wait for Qdrant to start
echo -e "${YELLOW}⏳ Waiting for Qdrant to start (30 seconds)${NC}"
sleep 30

# Test Qdrant health (from within Azure network)
echo -e "${YELLOW}🏥 Testing Qdrant Health${NC}"
echo "Note: Health check may fail if testing from outside Azure network"
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  Deployment Summary                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Qdrant Service:${NC} ${QDRANT_APP}"
echo -e "${GREEN}✅ Resource Group:${NC} ${RESOURCE_GROUP}"
echo -e "${GREEN}✅ Internal URL:${NC} ${QDRANT_URL}"
echo -e "${GREEN}✅ Key Vault Updated:${NC} QDRANT-URL"
echo ""
echo -e "${YELLOW}📝 Configuration:${NC}"
echo "  - CPU: 0.5 vCPU"
echo "  - Memory: 1 GB"
echo "  - Replicas: 1 (fixed)"
echo "  - Ingress: Internal only"
echo "  - Port: 6333"
echo ""

# Next Steps
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     Next Steps                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. Restart your main application to load new QDRANT-URL:"
echo "   az containerapp update --name unified-temporal-worker --resource-group ${RESOURCE_GROUP}"
echo ""
echo "2. Check Qdrant logs:"
echo "   az containerapp logs show --name ${QDRANT_APP} --resource-group ${RESOURCE_GROUP} --follow"
echo ""
echo "3. Check main app logs for Qdrant connection:"
echo "   az containerapp logs show --name unified-temporal-worker --resource-group ${RESOURCE_GROUP} --follow"
echo ""
echo "4. Test memory functionality:"
echo "   - Send a conversation"
echo "   - Check if memory is stored"
echo "   - Verify context retrieval"
echo ""

echo -e "${GREEN}🎉 Qdrant Deployment Complete!${NC}"
echo ""
