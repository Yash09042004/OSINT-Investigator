#!/bin/bash

# 🌙 Dark Mode Black Cards - Verification Script
# This script helps verify that dark mode is working correctly

echo "╔════════════════════════════════════════════════════╗"
echo "║  🌙 DARK MODE BLACK CARDS - VERIFICATION TOOL 🌙 ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if server is running
echo "1️⃣  Checking Server Status..."
if ps aux | grep -q "[s]f.py.*5001"; then
    echo -e "${GREEN}✅ Server is running on port 5001${NC}"
    SERVER_RUNNING=true
else
    echo -e "${RED}❌ Server is NOT running${NC}"
    SERVER_RUNNING=false
fi
echo ""

# Check CSS file exists
echo "2️⃣  Checking CSS File..."
CSS_FILE="/home/yash/Desktop/MEGA_PROJECT/spiderfoot/spiderfoot/static/css/spiderfoot.css"
if [ -f "$CSS_FILE" ]; then
    echo -e "${GREEN}✅ CSS file found${NC}"
    
    # Check for dark mode rules
    if grep -q "\[data-theme='dark'\]" "$CSS_FILE"; then
        echo -e "${GREEN}✅ Dark mode rules present${NC}"
        
        # Count dark mode rules
        DARK_RULES=$(grep -c "data-theme='dark'" "$CSS_FILE")
        echo -e "${BLUE}   Found $DARK_RULES dark mode rule sets${NC}"
    else
        echo -e "${RED}❌ Dark mode rules NOT found${NC}"
    fi
    
    # Check for black card rules
    if grep -q "rgba(0, 0, 0, 0.85)" "$CSS_FILE"; then
        echo -e "${GREEN}✅ Black card background rules present${NC}"
    else
        echo -e "${YELLOW}⚠️  Black card rules might be missing${NC}"
    fi
    
else
    echo -e "${RED}❌ CSS file NOT found${NC}"
fi
echo ""

# Check JavaScript file
echo "3️⃣  Checking JavaScript Theme Toggle..."
JS_FILE="/home/yash/Desktop/MEGA_PROJECT/spiderfoot/spiderfoot/static/js/spiderfoot.js"
if [ -f "$JS_FILE" ]; then
    echo -e "${GREEN}✅ JavaScript file found${NC}"
    
    if grep -q "data-theme" "$JS_FILE"; then
        echo -e "${GREEN}✅ Theme toggle code present${NC}"
    else
        echo -e "${RED}❌ Theme toggle code NOT found${NC}"
    fi
else
    echo -e "${RED}❌ JavaScript file NOT found${NC}"
fi
echo ""

# Check test file
echo "4️⃣  Checking Test Page..."
TEST_FILE="/home/yash/Desktop/MEGA_PROJECT/spiderfoot/test_dark_mode.html"
if [ -f "$TEST_FILE" ]; then
    echo -e "${GREEN}✅ Test page created${NC}"
else
    echo -e "${YELLOW}⚠️  Test page not found (optional)${NC}"
fi
echo ""

# Provide access URLs
echo "5️⃣  Access URLs..."
if [ "$SERVER_RUNNING" = true ]; then
    echo -e "${GREEN}🌐 Main Application:${NC}"
    echo "   http://127.0.0.1:5001"
    echo ""
    echo -e "${BLUE}📝 Instructions:${NC}"
    echo "   1. Open the URL above in your browser"
    echo "   2. Click the theme toggle icon (☀️/🌙) in the top right"
    echo "   3. Verify:"
    echo "      - Cards turn BLACK"
    echo "      - Text turns WHITE"
    echo "      - Purple borders visible"
    echo ""
else
    echo -e "${YELLOW}⚠️  Server not running. Start it with:${NC}"
    echo "   cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot"
    echo "   ./start.sh"
    echo ""
fi

# Check if test server can be started
echo "6️⃣  Test Page Server..."
if [ -f "$TEST_FILE" ]; then
    echo -e "${BLUE}💡 To test with standalone page:${NC}"
    echo "   cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot"
    echo "   python3 -m http.server 8000"
    echo ""
    echo "   Then open: http://localhost:8000/test_dark_mode.html"
else
    echo -e "${YELLOW}⚠️  Test page not available${NC}"
fi
echo ""

# Browser console verification
echo "7️⃣  Browser Console Verification..."
echo -e "${BLUE}📊 Copy and paste this in browser console (F12):${NC}"
echo ""
echo "const theme = document.documentElement.getAttribute('data-theme');"
echo "const card = document.querySelector('.panel, .card');"
echo "if (card && theme === 'dark') {"
echo "  const bg = window.getComputedStyle(card).backgroundColor;"
echo "  const text = card.querySelector('p, div');"
echo "  const color = text ? window.getComputedStyle(text).color : null;"
echo "  console.log('Card BG:', bg, '(should be black)');"
echo "  console.log('Text:', color, '(should be white)');"
echo "} else {"
echo "  console.log('Not in dark mode or no cards found');"
echo "}"
echo ""

# Summary
echo "══════════════════════════════════════════════════════"
echo "📋 VERIFICATION SUMMARY"
echo "══════════════════════════════════════════════════════"

CHECKS_PASSED=0
TOTAL_CHECKS=4

if [ "$SERVER_RUNNING" = true ]; then
    ((CHECKS_PASSED++))
fi

if [ -f "$CSS_FILE" ] && grep -q "\[data-theme='dark'\]" "$CSS_FILE"; then
    ((CHECKS_PASSED++))
fi

if [ -f "$JS_FILE" ] && grep -q "data-theme" "$JS_FILE"; then
    ((CHECKS_PASSED++))
fi

if grep -q "rgba(0, 0, 0, 0.85)" "$CSS_FILE" 2>/dev/null; then
    ((CHECKS_PASSED++))
fi

echo "Checks Passed: $CHECKS_PASSED / $TOTAL_CHECKS"
echo ""

if [ $CHECKS_PASSED -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}🎉 Dark mode with black cards is ready to use!${NC}"
    echo ""
    echo "🚀 Quick Start:"
    echo "   1. Open: http://127.0.0.1:5001"
    echo "   2. Toggle theme with ☀️/🌙 icon"
    echo "   3. Enjoy black cards with white text!"
elif [ $CHECKS_PASSED -ge 2 ]; then
    echo -e "${YELLOW}⚠️  PARTIAL SUCCESS${NC}"
    echo "Some checks passed. Review warnings above."
else
    echo -e "${RED}❌ ISSUES DETECTED${NC}"
    echo "Please review errors above."
fi

echo ""
echo "══════════════════════════════════════════════════════"
echo ""

# Documentation references
echo "📚 Documentation:"
echo "   • DARK_MODE_COMPLETE.md - Full implementation guide"
echo "   • DARK_MODE_FIX_GUIDE.md - Troubleshooting guide"
echo "   • CSS_VARIABLES_IMPLEMENTATION.md - CSS details"
echo "   • QUICK_REFERENCE.md - Quick commands"
echo ""

# Offer to open browser
if [ "$SERVER_RUNNING" = true ]; then
    echo -e "${BLUE}🌐 Would you like to open the browser? (y/n)${NC}"
    read -t 10 -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Opening browser..."
        if command -v xdg-open > /dev/null; then
            xdg-open "http://127.0.0.1:5001" 2>/dev/null &
        elif command -v firefox > /dev/null; then
            firefox "http://127.0.0.1:5001" 2>/dev/null &
        elif command -v google-chrome > /dev/null; then
            google-chrome "http://127.0.0.1:5001" 2>/dev/null &
        else
            echo "Please open http://127.0.0.1:5001 manually"
        fi
    fi
fi

echo ""
echo "🌙 Dark Mode Verification Complete! 🌙"
