#!/bin/bash
# Monitor Goose's autonomous test generation progress

echo "🤖 Goose Autonomous Test Generation Monitor"
echo "=========================================="
echo ""

# Check test count
echo "📊 Test Count:"
pytest tests/ --collect-only -q 2>&1 | grep "tests collected" || echo "No tests collected yet"
echo ""

# Check test status
echo "✅ Test Status:"
pytest tests/ -q --tb=no 2>&1 | tail -3
echo ""

# Check coverage
echo "📈 Coverage:"
pytest tests/ --cov --cov-report=term-missing -q 2>&1 | grep "TOTAL" || echo "Coverage not available"
echo ""

# Check warnings
echo "⚠️  Warnings:"
pytest tests/ -q 2>&1 | grep "warnings" || echo "No warnings info"
echo ""

# Check new files
echo "📁 New Test Files Created:"
find tests/ -name "*.py" -type f -newer GOOSE-AUTONOMOUS-TEST-GENERATION.md 2>/dev/null | wc -l | xargs echo "New files:"
echo ""

# List test directories
echo "📂 Test Directory Structure:"
tree tests/ -L 2 2>/dev/null || find tests/ -type d | head -20
echo ""

# Check if report exists
echo "📝 Final Report:"
if [ -f "AUTONOMOUS-TEST-REPORT.md" ]; then
    echo "✅ Report generated!"
    echo "Preview:"
    head -20 AUTONOMOUS-TEST-REPORT.md
else
    echo "⏳ Report not yet generated (Goose still working...)"
fi
echo ""

echo "=========================================="
echo "Run this script periodically to check progress"
echo "Usage: bash monitor_goose_progress.sh"
