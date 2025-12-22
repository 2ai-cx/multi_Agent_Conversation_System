#!/bin/bash

# Fix Qdrant Service with Health Probes
# Health probes are required for ingress to route traffic properly

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Fix Qdrant Service - Add Health Probes                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

RESOURCE_GROUP="rg-secure-timesheet-agent"
QDRANT_APP="qdrant-service"

echo -e "${YELLOW}Step 1: Current Configuration${NC}"
echo "Checking current Qdrant configuration..."
echo ""

az containerapp show \
    --name $QDRANT_APP \
    --resource-group $RESOURCE_GROUP \
    --query "properties.template.containers[0].{Image:image,Probes:probes,Resources:resources}" \
    -o json

echo ""
echo -e "${YELLOW}Step 2: Creating Configuration with Health Probes${NC}"
echo ""

# Create YAML with health probes
cat > /tmp/qdrant-with-probes.yaml << 'EOF'
properties:
  template:
    containers:
    - name: qdrant-service
      image: qdrant/qdrant:v1.16.2
      resources:
        cpu: 1.0
        memory: 2Gi
      probes:
      - type: liveness
        httpGet:
          path: /
          port: 6333
          scheme: HTTP
        initialDelaySeconds: 10
        periodSeconds: 10
        timeoutSeconds: 5
        failureThreshold: 3
      - type: readiness
        httpGet:
          path: /
          port: 6333
          scheme: HTTP
        initialDelaySeconds: 5
        periodSeconds: 5
        timeoutSeconds: 3
        failureThreshold: 3
      - type: startup
        httpGet:
          path: /
          port: 6333
          scheme: HTTP
        initialDelaySeconds: 0
        periodSeconds: 5
        timeoutSeconds: 3
        failureThreshold: 30
    scale:
      minReplicas: 1
      maxReplicas: 1
EOF

echo "Configuration created with:"
echo "  - Liveness probe: HTTP GET / on port 6333"
echo "  - Readiness probe: HTTP GET / on port 6333"
echo "  - Startup probe: HTTP GET / on port 6333"
echo ""

echo -e "${YELLOW}Step 3: Updating Qdrant Service${NC}"
echo ""

az containerapp update \
    --name $QDRANT_APP \
    --resource-group $RESOURCE_GROUP \
    --yaml /tmp/qdrant-with-probes.yaml

echo ""
echo -e "${GREEN}✅ Qdrant service updated with health probes${NC}"
echo ""

echo -e "${YELLOW}Step 4: Waiting for deployment...${NC}"
sleep 30

echo ""
echo -e "${YELLOW}Step 5: Checking Status${NC}"
echo ""

STATUS=$(az containerapp show \
    --name $QDRANT_APP \
    --resource-group $RESOURCE_GROUP \
    --query "properties.runningStatus" \
    -o tsv)

echo "Status: $STATUS"
echo ""

if [ "$STATUS" = "Running" ]; then
    echo -e "${GREEN}✅ Qdrant is running${NC}"
else
    echo -e "${YELLOW}⚠️  Status: $STATUS (waiting for Running)${NC}"
fi

echo ""
echo -e "${YELLOW}Step 6: Testing Connectivity${NC}"
echo ""

echo "Test 1: HTTP without port (ingress default)"
curl --max-time 5 -s "http://qdrant-service.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/" | head -5 || echo "Failed or timeout"

echo ""
echo "Test 2: HTTPS without port"
curl --max-time 5 -s -k "https://qdrant-service.internal.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/" | head -5 || echo "Failed or timeout"

echo ""
echo -e "${YELLOW}Step 7: Checking Qdrant Logs${NC}"
echo ""

az containerapp logs show \
    --name $QDRANT_APP \
    --resource-group $RESOURCE_GROUP \
    --tail 20 \
    --format text 2>/dev/null | tail -10

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Next Steps                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "1. Wait 1-2 minutes for health probes to stabilize"
echo "2. Test from main app container:"
echo "   az containerapp exec --name unified-temporal-worker \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --command 'curl -v http://qdrant-service:6333/collections'"
echo ""
echo "3. If still failing, check revision health:"
echo "   az containerapp revision list --name $QDRANT_APP \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --query '[].{Name:name,Health:properties.healthState,Active:properties.active}'"
echo ""

