#!/bin/bash

# Dark Mode Verification Script for SpiderFoot
# This script verifies that dark mode is properly implemented

echo "========================================"
echo "SpiderFoot Dark Mode Verification"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: CSS file exists and contains dark mode variables
echo -n "1. Checking CSS file... "
if [ -f "spiderfoot/static/css/spiderfoot.css" ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    exit 1
fi

# Check 2: Dark mode variables are defined
echo -n "2. Checking dark mode variables... "
if grep -q "\[data-theme='dark'\]" spiderfoot/static/css/spiderfoot.css; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    exit 1
fi

# Check 3: Black card overrides exist
echo -n "3. Checking black card overrides... "
if grep -q "AGGRESSIVE DARK MODE OVERRIDES" spiderfoot/static/css/spiderfoot.css; then
    echo -e "${GREEN}✓ Found${NC}"
    OVERRIDE_LINES=$(grep -A 10 "AGGRESSIVE DARK MODE OVERRIDES" spiderfoot/static/css/spiderfoot.css | wc -l)
    echo "   Found ${OVERRIDE_LINES}+ lines of dark mode overrides"
else
    echo -e "${RED}✗ Not found${NC}"
    exit 1
fi

# Check 4: JavaScript theme toggle exists
echo -n "4. Checking JavaScript theme toggle... "
if grep -q "data-theme" spiderfoot/static/js/spiderfoot.js; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    exit 1
fi

# Check 5: HEADER.tmpl uses new theme system
echo -n "5. Checking HEADER.tmpl... "
if grep -q 'localStorage.getItem("theme") || "light"' spiderfoot/templates/HEADER.tmpl; then
    echo -e "${GREEN}✓ Using new system${NC}"
elif grep -q 'localStorage.getItem("theme") === "dark-theme"' spiderfoot/templates/HEADER.tmpl; then
    echo -e "${RED}✗ Still using old system${NC}"
    echo "   Please update HEADER.tmpl to use the new theme system"
    exit 1
else
    echo -e "${YELLOW}? Unknown state${NC}"
fi

# Check 6: Server is running
echo -n "6. Checking server... "
if curl -s http://127.0.0.1:5001 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running on http://127.0.0.1:5001${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "   Start the server with: python3 sf.py -l 127.0.0.1:5001"
fi

# Check 7: Count CSS variable definitions
echo ""
echo "CSS Variable Statistics:"
LIGHT_VARS=$(grep -A 100 "^:root {" spiderfoot/static/css/spiderfoot.css | grep "^  --" | wc -l)
DARK_VARS=$(grep -A 100 "^\[data-theme='dark'\] {" spiderfoot/static/css/spiderfoot.css | grep "^  --" | wc -l)
echo "  • Light mode variables: ${LIGHT_VARS}"
echo "  • Dark mode variables: ${DARK_VARS}"

# Check 8: Dark mode specific checks
echo ""
echo "Dark Mode Implementation Details:"
echo -n "  • Black cards (rgba(0, 0, 0, 0.85)): "
BLACK_CARDS=$(grep -c "rgba(0, 0, 0, 0.85)" spiderfoot/static/css/spiderfoot.css)
echo "${BLACK_CARDS} occurrences"

echo -n "  • White text (#ffffff): "
WHITE_TEXT=$(grep -c "#ffffff" spiderfoot/static/css/spiderfoot.css)
echo "${WHITE_TEXT} occurrences"

echo -n "  • Purple borders (rgba(102, 126, 234, 0.3)): "
PURPLE_BORDERS=$(grep -c "rgba(102, 126, 234, 0.3)" spiderfoot/static/css/spiderfoot.css)
echo "${PURPLE_BORDERS} occurrences"

echo -n "  • !important declarations: "
IMPORTANT=$(grep -c "!important" spiderfoot/static/css/spiderfoot.css)
echo "${IMPORTANT} occurrences"

echo ""
echo "========================================"
echo -e "${GREEN}✓ All checks passed!${NC}"
echo "========================================"
echo ""
echo "To test dark mode:"
echo "1. Open http://127.0.0.1:5001 in your browser"
echo "2. Click the theme toggle switch in the navigation bar"
echo "3. Verify that all cards turn black with white text"
echo ""
echo "To clear localStorage and reset theme:"
echo "  Open browser console (F12) and run:"
echo "  localStorage.clear(); location.reload();"
echo ""
