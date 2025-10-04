#!/bin/bash

# Comprehensive Domain Analysis and Merge Script
# Usage: ./scripts/run_comprehensive_analysis.sh <url> [domain_name]

if [ $# -lt 1 ]; then
    echo "Usage: $0 <url> [domain_name]"
    echo "Example: $0 https://example.com example"
    exit 1
fi

URL="$1"
DOMAIN_NAME="${2:-$(echo "$URL" | sed 's|https\?://||' | sed 's|/.*||' | sed 's|\.|_|g')}"

echo "=== COMPREHENSIVE DOMAIN ANALYSIS ==="
echo "URL: $URL"
echo "Domain: $DOMAIN_NAME"
echo ""

# Run comprehensive analysis
echo "Running comprehensive analysis with multiple configurations..."
python scripts/comprehensive_domain_analysis.py "$URL" "$DOMAIN_NAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "=== ANALYSIS COMPLETE ==="
    echo "All reports have been generated and merged successfully!"
    echo "Check the generated JSON files for comprehensive results."
else
    echo ""
    echo "=== ANALYSIS FAILED ==="
    echo "Some analysis runs may have failed. Check the output above for details."
    exit 1
fi
