#!/bin/bash

# 🔍 PRISM - Complete Verification Script
# This script verifies all changes and helps restart the server

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🔍 PRISM - PROJECT VERIFICATION & STATUS 🔍        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1️⃣  REBRANDING VERIFICATION${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check README
if grep -q "# 🔍 PRISM - Open Source Intelligence Platform" README.md 2>/dev/null; then
    echo -e "${GREEN}✓${NC} README.md updated to PRISM"
else
    echo -e "${RED}✗${NC} README.md not updated"
fi

# Check LICENSE
if grep -q "PRISM Team" LICENSE 2>/dev/null; then
    echo -e "${GREEN}✓${NC} LICENSE updated with PRISM Team"
else
    echo -e "${RED}✗${NC} LICENSE not updated"
fi

# Check Authors in LICENSE
if grep -q "Yash Patil" LICENSE 2>/dev/null && \
   grep -q "Soumitra Bapat" LICENSE 2>/dev/null && \
   grep -q "Sharvari Jadhav" LICENSE 2>/dev/null; then
    echo -e "${GREEN}✓${NC} All three authors listed in LICENSE"
else
    echo -e "${YELLOW}⚠${NC}  Authors might not all be listed in LICENSE"
fi

# Check HEADER template
if grep -q "PRISM v" spiderfoot/templates/HEADER.tmpl 2>/dev/null; then
    echo -e "${GREEN}✓${NC} HEADER.tmpl updated with PRISM branding"
else
    echo -e "${RED}✗${NC} HEADER.tmpl not updated"
fi

# Check FOOTER template
if grep -q "PRISM" spiderfoot/templates/FOOTER.tmpl 2>/dev/null; then
    echo -e "${GREEN}✓${NC} FOOTER.tmpl updated with PRISM branding"
else
    echo -e "${RED}✗${NC} FOOTER.tmpl not updated"
fi

echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2️⃣  DOWNLOAD FUNCTIONALITY FIX${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check download helper function
if grep -q "sf.downloadFile" spiderfoot/static/js/spiderfoot.js 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Download helper function added to spiderfoot.js"
else
    echo -e "${RED}✗${NC} Download helper not found in spiderfoot.js"
fi

# Check scanlist.js
if grep -q "sf.downloadFile" spiderfoot/static/js/spiderfoot.scanlist.js 2>/dev/null; then
    echo -e "${GREEN}✓${NC} scanlist.js updated to use new download method"
else
    echo -e "${YELLOW}⚠${NC}  scanlist.js not using new download method"
fi

# Check scaninfo.tmpl
if grep -q "sf.downloadFile" spiderfoot/templates/scaninfo.tmpl 2>/dev/null; then
    echo -e "${GREEN}✓${NC} scaninfo.tmpl updated to use new download method"
else
    echo -e "${YELLOW}⚠${NC}  scaninfo.tmpl not using new download method"
fi

# Check opts.js
if grep -q "sf.downloadFile" spiderfoot/static/js/spiderfoot.opts.js 2>/dev/null; then
    echo -e "${GREEN}✓${NC} spiderfoot.opts.js updated to use new download method"
else
    echo -e "${YELLOW}⚠${NC}  spiderfoot.opts.js not using new download method"
fi

echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3️⃣  DARK MODE & UI ENHANCEMENTS${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check CSS variables
if grep -q "data-theme='dark'" spiderfoot/static/css/spiderfoot.css 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Dark mode CSS variables implemented"
else
    echo -e "${RED}✗${NC} Dark mode CSS not found"
fi

# Check theme toggle in JS
if grep -q "data-theme" spiderfoot/static/js/spiderfoot.js 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Theme toggle JavaScript implemented"
else
    echo -e "${RED}✗${NC} Theme toggle JS not found"
fi

echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4️⃣  SERVER STATUS${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if ps aux | grep -q "[p]ython3.*sf.py"; then
    PID=$(ps aux | grep "[p]ython3.*sf.py" | awk '{print $2}')
    echo -e "${GREEN}✓${NC} PRISM server is running (PID: $PID)"
    echo -e "${GREEN}  → Access at: http://127.0.0.1:5001${NC}"
else
    echo -e "${YELLOW}⚠${NC}  PRISM server is not running"
    echo ""
    echo -e "${BLUE}To start the server, run:${NC}"
    echo "  cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot"
    echo "  ./start.sh"
    echo ""
    echo -e "${BLUE}Or manually:${NC}"
    echo "  python3 sf.py -l 127.0.0.1:5001"
fi

echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}5️⃣  DOCUMENTATION FILES${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

docs=(
    "README.md:Main project documentation"
    "LICENSE:MIT License with PRISM Team"
    "PRISM_REBRANDING.md:Rebranding summary"
    "DOWNLOAD_FIX.md:Download functionality fix"
    "CSS_VARIABLES_IMPLEMENTATION.md:CSS variables guide"
    "UI_MODERNIZATION_SUMMARY.md:UI changes summary"
    "PROJECT_COMPLETE.md:Project completion summary"
)

for doc in "${docs[@]}"; do
    file="${doc%%:*}"
    desc="${doc#*:}"
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file - $desc"
    else
        echo -e "${RED}✗${NC} $file - Missing"
    fi
done

echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}6️⃣  QUICK ACTIONS${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}Start PRISM:${NC}"
echo "  ./start.sh"
echo ""

echo -e "${BLUE}Stop PRISM:${NC}"
echo "  pkill -f 'python3.*sf.py'"
echo ""

echo -e "${BLUE}View Logs:${NC}"
echo "  tail -f spiderfoot.log"
echo ""

echo -e "${BLUE}Access Application:${NC}"
echo "  http://127.0.0.1:5001"
echo ""

echo -e "${BLUE}Read Documentation:${NC}"
echo "  cat README.md"
echo "  cat PRISM_REBRANDING.md"
echo ""

echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}7️⃣  TESTING CHECKLIST${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "After starting the server, verify:"
echo ""
echo "  □ Browser tab shows 'PRISM v4.0 - OSINT Platform'"
echo "  □ Navigation bar displays 'PRISM' logo/text"
echo "  □ Footer shows 'PRISM' and team names"
echo "  □ About modal shows PRISM information"
echo "  □ Dark/Light theme toggle works (☀️/🌙 icon)"
echo "  □ Download buttons work (CSV, Excel, JSON, GEXF)"
echo "  □ Export logs button works"
echo "  □ Export API keys button works"
echo ""

echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}8️⃣  PROJECT SUMMARY${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}✨ PRISM - Project Complete ✨${NC}"
echo ""
echo "Project Name: PRISM (Open Source Intelligence Platform)"
echo "Authors: Yash Patil, Soumitra Bapat, Sharvari Jadhav"
echo "License: MIT License"
echo "Year: 2025"
echo ""
echo "Key Features:"
echo "  • 200+ OSINT modules"
echo "  • Modern purple gradient UI"
echo "  • Dark/Light theme support"
echo "  • Fixed download functionality"
echo "  • CSS variables system"
echo "  • Professional branding"
echo ""
echo -e "${BLUE}Base Technology:${NC} Built upon SpiderFoot framework"
echo -e "${BLUE}Enhancements:${NC} Modern UI, Dark mode, Download fixes, Rebranding"
echo ""

echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🎉 All verifications complete! 🎉${NC}"
echo ""
echo -e "${BLUE}💡 Pro Tip:${NC} Open README.md for comprehensive documentation"
echo ""
echo -e "${PURPLE}Made with 💜 by the PRISM Team${NC}"
echo ""
