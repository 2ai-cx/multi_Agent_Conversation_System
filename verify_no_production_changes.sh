#!/bin/bash
# Verify Goose didn't modify any production code

echo "🔒 Production Code Safety Check"
echo "================================"
echo ""

# Check git status
echo "📋 Git Status:"
git status --short
echo ""

# Check for changes outside tests/
echo "⚠️  Changes Outside tests/ Directory:"
CHANGES=$(git status --short | grep -v "^?? tests/" | grep -v "^M  tests/" | grep -v "\.md$" | grep -v "^?? htmlcov/" | grep -v "^?? \.coverage")

if [ -z "$CHANGES" ]; then
    echo "✅ SAFE: No production code modified!"
else
    echo "❌ WARNING: Production code may have been modified:"
    echo "$CHANGES"
    echo ""
    echo "🚨 ALERT: Goose modified files outside tests/ directory!"
fi
echo ""

# List modified production files
echo "🔍 Modified Production Files:"
git diff --name-only | grep -v "^tests/" | grep -v "\.md$" | grep -v "htmlcov" | grep -v "\.coverage" || echo "None"
echo ""

# List new test files
echo "✅ New Test Files Created:"
find tests/ -name "*.py" -type f -newer GOOSE-AUTONOMOUS-TEST-GENERATION.md 2>/dev/null || echo "None yet"
echo ""

# List modified test files
echo "📝 Modified Test Files:"
git diff --name-only tests/ 2>/dev/null || echo "None"
echo ""

echo "================================"
echo "✅ = Safe | ❌ = Needs Review"
