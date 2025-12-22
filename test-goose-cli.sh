#!/bin/bash
# Test Goose CLI with DeepSeek-R1 8B

cd /Users/dongshulin/Library/CloudStorage/OneDrive-2ai.cx/Desktop/GitHub/multi_Agent_Conversation_System

# Set environment variables for Goose
export GOOSE_PROVIDER=ollama
export GOOSE_MODEL=deepseek-r1:8b
export OLLAMA_HOST=http://localhost:11434

echo "🧪 Testing Goose CLI with DeepSeek-R1 8B"
echo "Provider: $GOOSE_PROVIDER"
echo "Model: $GOOSE_MODEL"
echo "Host: $OLLAMA_HOST"
echo ""

# Test with a simple command
echo "Read tests/e2e/test_complete_conversation_flow.py and count the test methods." | goose session start --profile default

echo ""
echo "✅ Test complete!"
