#!/bin/bash

# 🔐 Azure Key Vault Secret Checker
# Checks which secrets exist in Key Vault

set -e

KV_NAME="kv-secure-agent-2ai"

echo "🔐 Checking Azure Key Vault: $KV_NAME"
echo "=================================================="
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not installed"
    echo "Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure"
    echo "Run: az login"
    exit 1
fi

echo "✅ Azure CLI ready"
echo ""

# Required secrets for multi-agent system
REQUIRED_SECRETS=(
    "OPENROUTER-API-KEY"
    "OPENROUTER-MODEL"
    "USE-OPENROUTER"
    "PROVIDER"
    "SUPABASE-URL"
    "SUPABASE-KEY"
    "HARVEST-ACCESS-TOKEN"
    "HARVEST-ACCOUNT-ID"
    "TEMPORAL-HOST"
    "TEMPORAL-NAMESPACE"
    "TWILIO-ACCOUNT-SID"
    "TWILIO-AUTH-TOKEN"
    "TWILIO-PHONE-NUMBER"
)

# Optional secrets
OPTIONAL_SECRETS=(
    "CACHE-ENABLED"
    "USE-IMPROVED-RATE-LIMITER"
    "FALLBACK-ENABLED"
    "OPIK-ENABLED"
    "OPIK-API-KEY"
    "OPIK-WORKSPACE"
    "OPIK-PROJECT"
    "OPENAI-TEMPERATURE"
    "OPENAI-MAX-TOKENS"
    "GMAIL-USER"
    "GMAIL-PASSWORD"
)

echo "📋 Checking Required Secrets (${#REQUIRED_SECRETS[@]}):"
echo "=================================================="

REQUIRED_FOUND=0
REQUIRED_MISSING=0

for secret in "${REQUIRED_SECRETS[@]}"; do
    if az keyvault secret show --vault-name "$KV_NAME" --name "$secret" &> /dev/null; then
        echo "✅ $secret"
        ((REQUIRED_FOUND++))
    else
        echo "❌ $secret (MISSING)"
        ((REQUIRED_MISSING++))
    fi
done

echo ""
echo "📋 Checking Optional Secrets (${#OPTIONAL_SECRETS[@]}):"
echo "=================================================="

OPTIONAL_FOUND=0
OPTIONAL_MISSING=0

for secret in "${OPTIONAL_SECRETS[@]}"; do
    if az keyvault secret show --vault-name "$KV_NAME" --name "$secret" &> /dev/null; then
        echo "✅ $secret"
        ((OPTIONAL_FOUND++))
    else
        echo "⚠️  $secret (not set)"
        ((OPTIONAL_MISSING++))
    fi
done

echo ""
echo "=================================================="
echo "📊 Summary:"
echo "=================================================="
echo "Required: $REQUIRED_FOUND/${#REQUIRED_SECRETS[@]} found"
echo "Optional: $OPTIONAL_FOUND/${#OPTIONAL_SECRETS[@]} found"
echo "Total: $((REQUIRED_FOUND + OPTIONAL_FOUND))/$((${#REQUIRED_SECRETS[@]} + ${#OPTIONAL_SECRETS[@]})) secrets"
echo ""

if [ $REQUIRED_MISSING -eq 0 ]; then
    echo "✅ All required secrets are present!"
    echo "🚀 System is ready to deploy"
else
    echo "❌ Missing $REQUIRED_MISSING required secrets"
    echo "⚠️  Add missing secrets before deploying"
    echo ""
    echo "See AZURE_KEYVAULT_CHECKLIST.md for details"
fi

echo ""
echo "=================================================="
echo "💡 Tip: To add a secret, run:"
echo "   az keyvault secret set --vault-name $KV_NAME --name SECRET-NAME --value 'secret-value'"
echo "=================================================="
