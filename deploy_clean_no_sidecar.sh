#!/bin/bash

# Deploy clean - remove sidecar, use separate Qdrant service

set -e

echo "=== Deploying Clean Configuration (No Sidecar) ==="
echo ""

# Get latest image
LATEST_IMAGE=$(az acr repository show-tags \
    --name secureagentreg2ai \
    --repository multi-agent-system \
    --orderby time_desc \
    --top 1 \
    --output tsv)

echo "Latest image: $LATEST_IMAGE"
echo ""

# Create clean YAML (single container only)
cat > /tmp/clean-config.yaml << EOF
properties:
  template:
    containers:
    - name: unified-temporal-worker
      image: secureagentreg2ai.azurecr.io/multi-agent-system:$LATEST_IMAGE
      resources:
        cpu: 1.0
        memory: 2Gi
      env:
      - name: AZURE_KEY_VAULT_URL
        value: https://kv-secure-agent-2ai.vault.azure.net/
      - name: PORT
        value: "8003"
    scale:
      minReplicas: 1
      maxReplicas: 3
EOF

echo "Deploying..."
az containerapp update \
    --name unified-temporal-worker \
    --resource-group rg-secure-timesheet-agent \
    --yaml /tmp/clean-config.yaml

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Configuration:"
echo "  - Single container (no sidecar)"
echo "  - Qdrant URL: http://qdrant-service:6333"
echo "  - Secrets loaded from Key Vault"
echo ""
