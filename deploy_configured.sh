#!/bin/bash

# 🚀 Multi-Agent System - Build and Deploy Script (Pre-configured)
# This script builds the Docker image and deploys to Azure Container Apps

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Pre-configured Azure settings
ACR_NAME="secureagentreg2ai"
RESOURCE_GROUP="rg-secure-timesheet-agent"
CONTAINER_APP="unified-temporal-worker"
ENVIRONMENT="secure-timesheet-env"
KEY_VAULT_URL="https://kv-secure-agent-2ai.vault.azure.net/"

# Application configuration
APP_NAME="multi-agent-system"
VERSION="1.0.0"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG="${VERSION}-${TIMESTAMP}"

REGISTRY="${ACR_NAME}.azurecr.io"
IMAGE_NAME="${REGISTRY}/${APP_NAME}"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
LATEST_IMAGE="${IMAGE_NAME}:latest"

echo -e "${BLUE}🚀 Multi-Agent System - Build and Deploy${NC}"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  Registry: ${REGISTRY}"
echo "  Image: ${FULL_IMAGE}"
echo "  Resource Group: ${RESOURCE_GROUP}"
echo "  Container App: ${CONTAINER_APP}"
echo "  Key Vault: ${KEY_VAULT_URL}"
echo ""
echo -e "${GREEN}✅ Starting automated deployment...${NC}"
echo ""

# Step 1: Check prerequisites
echo ""
echo -e "${YELLOW}🔍 Step 1: Checking Prerequisites${NC}"

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

# Step 2: Build Docker image
echo ""
echo -e "${YELLOW}🔨 Step 2: Building Docker Image${NC}"
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

# Step 3: Login to Azure Container Registry
echo ""
echo -e "${YELLOW}🔐 Step 3: Logging in to Azure Container Registry${NC}"

az acr login --name "${ACR_NAME}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Logged in to ACR${NC}"
else
    echo -e "${RED}❌ ACR login failed${NC}"
    exit 1
fi

# Step 4: Push image to registry
echo ""
echo -e "${YELLOW}📤 Step 4: Pushing Image to Registry${NC}"
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

# Step 5: Deploy to Azure Container Apps
echo ""
echo -e "${YELLOW}🚀 Step 5: Deploying to Azure Container Apps${NC}"
echo "Updating container app: ${CONTAINER_APP}"
echo ""

az containerapp update \
    --name "${CONTAINER_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --image "${FULL_IMAGE}" \
    --set-env-vars \
        AZURE_KEY_VAULT_URL="${KEY_VAULT_URL}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Step 6: Get app URL
echo ""
echo -e "${YELLOW}🌐 Step 6: Getting Application URL${NC}"

APP_URL=$(az containerapp show \
    --name "${CONTAINER_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query properties.configuration.ingress.fqdn -o tsv)

echo -e "${GREEN}✅ Application URL: https://${APP_URL}${NC}"

# Step 7: Wait for deployment
echo ""
echo -e "${YELLOW}⏳ Step 7: Waiting for Deployment${NC}"
echo "Waiting 45 seconds for container to start..."
sleep 45

# Step 8: Test health endpoint
echo ""
echo -e "${YELLOW}🏥 Step 8: Testing Health Endpoint${NC}"

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://${APP_URL}/health" || echo "000")

if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned: ${HEALTH_STATUS}${NC}"
    echo "Checking logs for errors..."
    echo ""
    az containerapp logs show \
        --name "${CONTAINER_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --tail 50
fi

# Step 9: Show recent logs
echo ""
echo -e "${YELLOW}📋 Step 9: Recent Logs${NC}"
az containerapp logs show \
    --name "${CONTAINER_APP}" \
    --resource-group "${RESOURCE_GROUP}" \
    --tail 30

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
echo "  Health: ${HEALTH_STATUS}"
echo ""
echo "🔍 Next Steps:"
echo ""
echo "1. Check logs:"
echo "   az containerapp logs show --name ${CONTAINER_APP} --resource-group ${RESOURCE_GROUP} --follow"
echo ""
echo "2. Test health endpoint:"
echo "   curl https://${APP_URL}/health"
echo ""
echo "3. Update Twilio webhooks:"
echo "   SMS: https://${APP_URL}/webhook/sms"
echo "   WhatsApp: https://${APP_URL}/webhook/whatsapp"
echo ""
echo "4. Send test SMS to your Twilio number:"
echo "   'Check my timesheet'"
echo ""
echo "5. Monitor workflows:"
echo "   Temporal: https://cloud.temporal.io"
echo "   Opik: https://www.comet.com/opik"
echo ""
echo -e "${GREEN}✅ Multi-Agent System is Live!${NC}"
echo ""
