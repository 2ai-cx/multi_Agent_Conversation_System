#!/bin/bash

# Test webhook endpoint directly
echo "🧪 Testing SMS webhook endpoint..."
echo ""

curl -X POST https://unified-temporal-worker.kindcoast-5a2a34c6.australiaeast.azurecontainerapps.io/webhook/sms \
  -d "From=+61400000000" \
  -d "To=+61488886084" \
  -d "Body=Check my timesheet" \
  -d "MessageSid=TEST123" \
  -v

echo ""
echo ""
echo "✅ If you see a 200 OK response above, the webhook is working!"
echo "📱 Now send a real SMS to test the full flow"
