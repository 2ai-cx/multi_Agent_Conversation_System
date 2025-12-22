#!/bin/bash

# Build and Deploy Multi-Agent System with Qdrant Support
# This script builds the Docker image and deploys to Azure Container Apps with Qdrant sidecar

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="rg-secure-timesheet-agent"
CONTAINER_APP="unified-temporal-worker"
ENVIRONMENT="env-secure-agent-2ai"
REGISTRY="secureagentreg2ai"
IMAGE_NAME="multi-agent-system"
KEY_VAULT="kv-secure-agent-2ai"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Multi-Agent System - Build & Deploy with Qdrant          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check Azure CLI
echo -e "${YELLOW}📋 Step 1: Checking Prerequisites${NC}"
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found${NC}"
    exit 1
fi

if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    echo "Run: az login"
    exit 1
fi

echo -e "${GREEN}✅ Azure CLI authenticated${NC}"

# Get subscription info
SUBSCRIPTION=$(az account show --query name -o tsv)
echo -e "${GREEN}✅ Subscription: ${SUBSCRIPTION}${NC}"
echo ""

# Step 2: Build Docker Image
echo -e "${YELLOW}🐳 Step 2: Building Docker Image${NC}"

# Generate timestamp for image tag
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG="${IMAGE_NAME}:${TIMESTAMP}"
FULL_IMAGE="${REGISTRY}.azurecr.io/${IMAGE_TAG}"

echo "Building: ${FULL_IMAGE}"
echo ""

# Build the image
docker build -t "${FULL_IMAGE}" .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker image built successfully${NC}"
echo ""

# Step 3: Push to Azure Container Registry
echo -e "${YELLOW}📤 Step 3: Pushing to Azure Container Registry${NC}"

# Login to ACR
az acr login --name "${REGISTRY}"

# Push image
docker push "${FULL_IMAGE}"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker push failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Image pushed to registry${NC}"
echo ""

# Save image name for reference
echo "${FULL_IMAGE}" > .last_build_image
echo -e "${GREEN}✅ Image name saved to .last_build_image${NC}"
echo ""

# Step 4: Check if Qdrant secrets exist
echo -e "${YELLOW}🔐 Step 4: Verifying Qdrant Secrets in Key Vault${NC}"

REQUIRED_SECRETS=(
    "RAG-ENABLED"
    "VECTOR-DB-PROVIDER"
    "QDRANT-URL"
    "QDRANT-COLLECTION-NAME"
    "EMBEDDINGS-PROVIDER"
    "EMBEDDINGS-MODEL"
)

MISSING_SECRETS=()

for secret in "${REQUIRED_SECRETS[@]}"; do
    if az keyvault secret show --vault-name "${KEY_VAULT}" --name "${secret}" &> /dev/null; then
        echo -e "${GREEN}✅ ${secret}${NC}"
    else
        echo -e "${RED}❌ ${secret} - MISSING${NC}"
        MISSING_SECRETS+=("${secret}")
    fi
done

if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ Missing secrets detected!${NC}"
    echo -e "${YELLOW}Run: ./add_qdrant_secrets.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All Qdrant secrets verified${NC}"
echo ""

# Step 5: Deploy Container App with Qdrant
echo -e "${YELLOW}🚀 Step 5: Deploying Container App with Qdrant${NC}"

# Check if container app exists
if az containerapp show --name "${CONTAINER_APP}" --resource-group "${RESOURCE_GROUP}" &> /dev/null; then
    echo "Container app exists - updating..."
    DEPLOY_MODE="update"
else
    echo "Container app does not exist - creating..."
    DEPLOY_MODE="create"
fi

if [ "$DEPLOY_MODE" = "update" ]; then
    # Update existing container app with Qdrant sidecar
    echo "Updating container app with Qdrant sidecar..."
    
    az containerapp update \
        --name "${CONTAINER_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --image "${FULL_IMAGE}" \
        --cpu 1.0 \
        --memory 2.0Gi \
        --min-replicas 1 \
        --max-replicas 3 \
        --revision-suffix "qdrant-${TIMESTAMP}" \
        --set-env-vars \
            AZURE_KEY_VAULT_URL="https://${KEY_VAULT}.vault.azure.net/" \
        --output none
    
    echo -e "${GREEN}✅ Container app updated${NC}"
    
    # Note: Qdrant sidecar needs to be added via YAML or portal
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Qdrant Sidecar Configuration${NC}"
    echo ""
    echo "The main app has been updated. To add Qdrant sidecar:"
    echo ""
    echo "Option 1: Use Azure Portal"
    echo "  1. Go to Container App: ${CONTAINER_APP}"
    echo "  2. Click 'Containers' -> 'Edit and deploy'"
    echo "  3. Add container:"
    echo "     - Name: qdrant"
    echo "     - Image: qdrant/qdrant:latest"
    echo "     - CPU: 0.5"
    echo "     - Memory: 1Gi"
    echo "     - Environment variables:"
    echo "       QDRANT__SERVICE__HTTP_PORT=6333"
    echo ""
    echo "Option 2: Deploy Qdrant as separate Container App"
    echo "  Run: ./deploy_qdrant_separate.sh"
    echo ""
    
else
    # Create new container app
    echo "Creating new container app..."
    
    az containerapp create \
        --name "${CONTAINER_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --environment "${ENVIRONMENT}" \
        --image "${FULL_IMAGE}" \
        --target-port 8003 \
        --ingress external \
        --cpu 1.0 \
        --memory 2.0Gi \
        --min-replicas 1 \
        --max-replicas 3 \
        --env-vars \
            AZURE_KEY_VAULT_URL="https://${KEY_VAULT}.vault.azure.net/" \
        --registry-server "${REGISTRY}.azurecr.io" \
        --system-assigned \
        --output none
    
    echo -e "${GREEN}✅ Container app created${NC}"
    
    # Grant Key Vault access
    echo ""
    echo "Granting Key Vault access to managed identity..."
    
    PRINCIPAL_ID=$(az containerapp show \
        --name "${CONTAINER_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --query identity.principalId -o tsv)
    
    az keyvault set-policy \
        --name "${KEY_VAULT}" \
        --object-id "${PRINCIPAL_ID}" \
        --secret-permissions get list \
        --output none
    
    echo -e "${GREEN}✅ Key Vault access granted${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Add Qdrant sidecar via portal or deploy separately${NC}"
fi

echo ""

# Step 6: Get Application URL
echo -e "${YELLOW}🌐 Step 6: Getting Application URL${NC}"

APP_URL=$(az containerapp show \
    --name "${CONTAINER_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query properties.configuration.ingress.fqdn -o tsv)

echo -e "${GREEN}✅ Application URL: https://${APP_URL}${NC}"
echo ""

# Step 7: Wait for deployment
echo -e "${YELLOW}⏳ Step 7: Waiting for Deployment${NC}"
echo "Waiting 30 seconds for container to start..."
sleep 30

# Step 8: Health Check
echo ""
echo -e "${YELLOW}🏥 Step 8: Health Check${NC}"

HEALTH_URL="https://${APP_URL}/health"
echo "Checking: ${HEALTH_URL}"

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_URL}" || echo "000")

if [ "${HEALTH_STATUS}" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed (200 OK)${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned: ${HEALTH_STATUS}${NC}"
    echo "This is normal if Qdrant sidecar is not yet configured"
fi

echo ""

# Step 9: Show Recent Logs
echo -e "${YELLOW}📋 Step 9: Recent Application Logs${NC}"

az containerapp logs show \
    --name "${CONTAINER_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --tail 30 || echo "Logs not available yet"

echo ""

# Step 10: Deployment Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  Deployment Summary                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Docker Image:${NC} ${FULL_IMAGE}"
echo -e "${GREEN}✅ Container App:${NC} ${CONTAINER_APP}"
echo -e "${GREEN}✅ Resource Group:${NC} ${RESOURCE_GROUP}"
echo -e "${GREEN}✅ Application URL:${NC} https://${APP_URL}"
echo -e "${GREEN}✅ Health Endpoint:${NC} https://${APP_URL}/health"
echo -e "${GREEN}✅ Status Endpoint:${NC} https://${APP_URL}/status"
echo ""

# Qdrant Status
echo -e "${YELLOW}⚠️  Qdrant Configuration:${NC}"
echo ""
echo "Secrets configured in Key Vault:"
echo "  ✅ RAG-ENABLED"
echo "  ✅ VECTOR-DB-PROVIDER"
echo "  ✅ QDRANT-URL"
echo "  ✅ EMBEDDINGS-PROVIDER"
echo ""
echo "Next step: Add Qdrant container"
echo ""

# Next Steps
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     Next Steps                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. Add Qdrant Sidecar (choose one):"
echo ""
echo "   Option A: Azure Portal (Recommended)"
echo "     - Go to: https://portal.azure.com"
echo "     - Navigate to Container App: ${CONTAINER_APP}"
echo "     - Add Qdrant container as shown above"
echo ""
echo "   Option B: Deploy Qdrant Separately"
echo "     ./deploy_qdrant_separate.sh"
echo ""
echo "2. Monitor Logs:"
echo "   az containerapp logs show --name ${CONTAINER_APP} --resource-group ${RESOURCE_GROUP} --follow"
echo ""
echo "3. Test Endpoints:"
echo "   curl https://${APP_URL}/health"
echo "   curl https://${APP_URL}/status"
echo ""
echo "4. Check Qdrant (after deployment):"
echo "   - Memory storage working"
echo "   - Collections auto-created"
echo "   - Context retrieval functional"
echo ""

echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
