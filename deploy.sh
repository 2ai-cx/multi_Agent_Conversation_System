#!/bin/bash

# 🚀 Multi-Agent System - Build and Deploy Script
# This script builds the Docker image and deploys to Azure Container Apps

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="multi-agent-system"
VERSION="1.0.0"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG="${VERSION}-${TIMESTAMP}"

echo -e "${BLUE}🚀 Multi-Agent System - Build and Deploy${NC}"
echo "=================================================="
echo ""

# Step 1: Get Azure configuration
echo -e "${YELLOW}📋 Step 1: Azure Configuration${NC}"
echo "Please provide your Azure details:"
echo ""

read -p "Azure Container Registry name (e.g., myregistry): " ACR_NAME
read -p "Resource Group name: " RESOURCE_GROUP
read -p "Container App name: " CONTAINER_APP
read -p "Container App Environment name: " ENVIRONMENT

# Validate inputs
if [ -z "$ACR_NAME" ] || [ -z "$RESOURCE_GROUP" ] || [ -z "$CONTAINER_APP" ] || [ -z "$ENVIRONMENT" ]; then
    echo -e "${RED}❌ Error: All fields are required${NC}"
    exit 1
fi

REGISTRY="${ACR_NAME}.azurecr.io"
IMAGE_NAME="${REGISTRY}/${APP_NAME}"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
LATEST_IMAGE="${IMAGE_NAME}:latest"

echo ""
echo "Configuration:"
echo "  Registry: ${REGISTRY}"
echo "  Image: ${FULL_IMAGE}"
echo "  Resource Group: ${RESOURCE_GROUP}"
echo "  Container App: ${CONTAINER_APP}"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Deployment cancelled${NC}"
    exit 0
fi

# Step 2: Check prerequisites
echo ""
echo -e "${YELLOW}🔍 Step 2: Checking Prerequisites${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker installed${NC}"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Please install Azure CLI.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Azure CLI installed${NC}"

# Check Azure login
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure. Running 'az login'...${NC}"
    az login
fi
echo -e "${GREEN}✅ Azure CLI authenticated${NC}"

# Step 3: Build Docker image
echo ""
echo -e "${YELLOW}🔨 Step 3: Building Docker Image${NC}"
echo "Building: ${FULL_IMAGE}"
echo ""

docker build --platform linux/amd64 \
    -t "${FULL_IMAGE}" \
    -t "${LATEST_IMAGE}" \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Step 4: Login to Azure Container Registry
echo ""
echo -e "${YELLOW}🔐 Step 4: Logging in to Azure Container Registry${NC}"

az acr login --name "${ACR_NAME}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Logged in to ACR${NC}"
else
    echo -e "${RED}❌ ACR login failed${NC}"
    exit 1
fi

# Step 5: Push image to registry
echo ""
echo -e "${YELLOW}📤 Step 5: Pushing Image to Registry${NC}"
echo "Pushing: ${FULL_IMAGE}"
echo ""

docker push "${FULL_IMAGE}"
docker push "${LATEST_IMAGE}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Image pushed successfully${NC}"
else
    echo -e "${RED}❌ Image push failed${NC}"
    exit 1
fi

# Step 6: Check if Container App exists
echo ""
echo -e "${YELLOW}🔍 Step 6: Checking Container App${NC}"

if az containerapp show --name "${CONTAINER_APP}" --resource-group "${RESOURCE_GROUP}" &> /dev/null; then
    echo -e "${GREEN}✅ Container App exists - will update${NC}"
    DEPLOY_MODE="update"
else
    echo -e "${YELLOW}⚠️  Container App does not exist - will create${NC}"
    DEPLOY_MODE="create"
fi

# Step 7: Deploy to Azure Container Apps
echo ""
echo -e "${YELLOW}🚀 Step 7: Deploying to Azure Container Apps${NC}"

if [ "$DEPLOY_MODE" = "update" ]; then
    echo "Updating existing container app..."
    
    az containerapp update \
        --name "${CONTAINER_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --image "${FULL_IMAGE}" \
        --set-env-vars \
            AZURE_KEY_VAULT_URL=https://kv-secure-agent-2ai.vault.azure.net/
    
else
    echo "Creating new container app..."
    
    az containerapp create \
        --name "${CONTAINER_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --environment "${ENVIRONMENT}" \
        --image "${FULL_IMAGE}" \
        --target-port 8003 \
        --ingress external \
        --min-replicas 1 \
        --max-replicas 10 \
        --cpu 1.0 \
        --memory 2.0Gi \
        --env-vars \
            AZURE_KEY_VAULT_URL=https://kv-secure-agent-2ai.vault.azure.net/
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Step 8: Enable Managed Identity (if creating new app)
if [ "$DEPLOY_MODE" = "create" ]; then
    echo ""
    echo -e "${YELLOW}🔐 Step 8: Enabling Managed Identity${NC}"
    
    az containerapp identity assign \
        --name "${CONTAINER_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --system-assigned
    
    echo -e "${GREEN}✅ Managed Identity enabled${NC}"
    
    # Get the identity
    IDENTITY_ID=$(az containerapp identity show \
        --name "${CONTAINER_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --query principalId -o tsv)
    
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Grant Key Vault access${NC}"
    echo "Run this command to grant access:"
    echo ""
    echo "az keyvault set-policy \\"
    echo "  --name kv-secure-agent-2ai \\"
    echo "  --object-id ${IDENTITY_ID} \\"
    echo "  --secret-permissions get list"
    echo ""
fi

# Step 9: Get app URL
echo ""
echo -e "${YELLOW}🌐 Step 9: Getting Application URL${NC}"

APP_URL=$(az containerapp show \
    --name "${CONTAINER_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query properties.configuration.ingress.fqdn -o tsv)

echo -e "${GREEN}✅ Application URL: https://${APP_URL}${NC}"

# Step 10: Test health endpoint
echo ""
echo -e "${YELLOW}🏥 Step 10: Testing Health Endpoint${NC}"
echo "Waiting 30 seconds for app to start..."
sleep 30

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://${APP_URL}/health" || echo "000")

if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned: ${HEALTH_STATUS}${NC}"
    echo "The app may still be starting. Check logs with:"
    echo "az containerapp logs show --name ${CONTAINER_APP} --resource-group ${RESOURCE_GROUP} --follow"
fi

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "📊 Deployment Summary:"
echo "  Image: ${FULL_IMAGE}"
echo "  Container App: ${CONTAINER_APP}"
echo "  URL: https://${APP_URL}"
echo ""
echo "🔍 Next Steps:"
echo "  1. Check logs: az containerapp logs show --name ${CONTAINER_APP} --resource-group ${RESOURCE_GROUP} --follow"
echo "  2. Test health: curl https://${APP_URL}/health"
echo "  3. Update Twilio webhooks:"
echo "     - SMS: https://${APP_URL}/webhook/sms"
echo "     - WhatsApp: https://${APP_URL}/webhook/whatsapp"
echo ""
echo "📚 Documentation:"
echo "  - FINAL_CHECKLIST.md - Complete deployment checklist"
echo "  - DEPLOYMENT_READY.md - Deployment guide"
echo ""
echo -e "${GREEN}✅ Ready to receive messages!${NC}"
echo ""
