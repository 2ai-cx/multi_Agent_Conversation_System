#!/bin/bash

# Script to add Qdrant/RAG secrets to Azure Key Vault
# Run this to configure Qdrant for production deployment

set -e

KV_NAME="kv-secure-agent-2ai"

echo "🔐 Adding Qdrant/RAG secrets to Azure Key Vault: $KV_NAME"
echo "=" | head -c 60
echo ""

# Check if Azure CLI is logged in
if ! az account show &>/dev/null; then
    echo "❌ Not logged in to Azure CLI"
    echo "   Run: az login"
    exit 1
fi

echo "✅ Azure CLI authenticated"
echo ""

# RAG Configuration
echo "📝 Adding RAG configuration..."

az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "RAG-ENABLED" \
    --value "true" \
    --description "Enable RAG (Retrieval-Augmented Generation) with vector store" \
    > /dev/null

echo "   ✅ RAG-ENABLED = true"

az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "VECTOR-DB-PROVIDER" \
    --value "qdrant" \
    --description "Vector database provider (qdrant, pinecone, weaviate)" \
    > /dev/null

echo "   ✅ VECTOR-DB-PROVIDER = qdrant"

# Qdrant Configuration
echo ""
echo "📝 Adding Qdrant configuration..."

# For production, you might want to use Qdrant Cloud
# For now, we'll set it to localhost (will work in Docker network)
az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "QDRANT-URL" \
    --value "http://qdrant:6333" \
    --description "Qdrant server URL (use service name in Docker/K8s)" \
    > /dev/null

echo "   ✅ QDRANT-URL = http://qdrant:6333"

# API key is optional for local Qdrant (set to space character for empty)
az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "QDRANT-API-KEY" \
    --value " " \
    --description "Qdrant API key (optional, leave empty for local)" \
    > /dev/null

echo "   ✅ QDRANT-API-KEY = (empty - local deployment)"

az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "QDRANT-COLLECTION-NAME" \
    --value "timesheet_memory" \
    --description "Qdrant collection name prefix" \
    > /dev/null

echo "   ✅ QDRANT-COLLECTION-NAME = timesheet_memory"

# Embeddings Configuration
echo ""
echo "📝 Adding embeddings configuration..."

az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "EMBEDDINGS-PROVIDER" \
    --value "openai" \
    --description "Embeddings provider (openai, cohere, huggingface)" \
    > /dev/null

echo "   ✅ EMBEDDINGS-PROVIDER = openai"

az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "EMBEDDINGS-MODEL" \
    --value "text-embedding-3-small" \
    --description "Embeddings model name" \
    > /dev/null

echo "   ✅ EMBEDDINGS-MODEL = text-embedding-3-small"

az keyvault secret set \
    --vault-name "$KV_NAME" \
    --name "EMBEDDINGS-DIMENSION" \
    --value "1536" \
    --description "Embedding vector dimension" \
    > /dev/null

echo "   ✅ EMBEDDINGS-DIMENSION = 1536"

echo ""
echo "=" | head -c 60
echo ""
echo "🎉 All Qdrant/RAG secrets added successfully!"
echo ""
echo "📋 Secrets added (8 total):"
echo "   1. RAG-ENABLED"
echo "   2. VECTOR-DB-PROVIDER"
echo "   3. QDRANT-URL"
echo "   4. QDRANT-API-KEY"
echo "   5. QDRANT-COLLECTION-NAME"
echo "   6. EMBEDDINGS-PROVIDER"
echo "   7. EMBEDDINGS-MODEL"
echo "   8. EMBEDDINGS-DIMENSION"
echo ""
echo "✅ Your application will now use Qdrant for long-term memory!"
echo ""
echo "📝 Next steps:"
echo "   1. Deploy Qdrant container alongside your app"
echo "   2. Restart your application to load new secrets"
echo "   3. Memory will automatically work!"
echo ""
echo "🐳 To deploy Qdrant in Azure Container Apps:"
echo "   - Add Qdrant as a sidecar container"
echo "   - Or deploy as separate container app"
echo "   - Update QDRANT-URL if using separate service"
echo ""
