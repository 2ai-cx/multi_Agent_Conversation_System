#!/bin/bash

# SMS Memory Testing Script
# This script simulates SMS messages to test the Mem0 memory system

BASE_URL="https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io"
WEBHOOK_URL="$BASE_URL/webhook/sms"

# Replace with your test phone number (must be registered in Supabase users table)
TEST_PHONE="+61412345678"  # CHANGE THIS TO YOUR PHONE NUMBER

echo "📱 SMS Memory Testing"
echo "===================="
echo "Phone: $TEST_PHONE"
echo ""

# Test 1: Store personal information
echo "Test 1: Storing personal information"
echo "-------------------------------------"
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=$TEST_PHONE" \
  -d "Body=I work as a software engineer at Google." \
  -d "MessageSid=TEST$(date +%s)001"

echo ""
echo "⏳ Waiting 10 seconds for processing and indexing..."
sleep 10

# Test 2: Retrieve information
echo ""
echo "Test 2: Retrieving stored information"
echo "--------------------------------------"
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=$TEST_PHONE" \
  -d "Body=What is my job?" \
  -d "MessageSid=TEST$(date +%s)002"

echo ""
echo "⏳ Waiting 10 seconds..."
sleep 10

# Test 3: Store numeric data
echo ""
echo "Test 3: Storing numeric data"
echo "-----------------------------"
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=$TEST_PHONE" \
  -d "Body=I worked 847 hours last month." \
  -d "MessageSid=TEST$(date +%s)003"

echo ""
echo "⏳ Waiting 10 seconds..."
sleep 10

# Test 4: Retrieve numeric data
echo ""
echo "Test 4: Retrieving numeric data"
echo "--------------------------------"
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=$TEST_PHONE" \
  -d "Body=How many hours did I work?" \
  -d "MessageSid=TEST$(date +%s)004"

echo ""
echo ""
echo "✅ Tests completed!"
echo ""
echo "Check your phone for SMS responses."
echo "Check Azure logs for detailed processing:"
echo "  az containerapp logs show --name unified-temporal-worker --tail 50"
