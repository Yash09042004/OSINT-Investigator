#!/bin/bash

# 🧪 Download Functionality Test Script
# This script helps test the download fixes

echo "╔══════════════════════════════════════════════════╗"
echo "║  📥 DOWNLOAD FUNCTIONALITY - TEST SCRIPT 📥    ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1️⃣  Checking Modified Files...${NC}"
echo "════════════════════════════════════════════════"

FILES=(
    "spiderfoot/static/js/spiderfoot.js"
    "spiderfoot/static/js/spiderfoot.scanlist.js"
    "spiderfoot/static/js/spiderfoot.opts.js"
    "spiderfoot/templates/scaninfo.tmpl"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (NOT FOUND)"
    fi
done

echo ""
echo -e "${BLUE}2️⃣  Checking for Download Helper Function...${NC}"
echo "════════════════════════════════════════════════"

if grep -q "sf.downloadFile" "spiderfoot/static/js/spiderfoot.js"; then
    echo -e "${GREEN}✓${NC} Download helper function added"
else
    echo -e "${RED}✗${NC} Download helper function NOT found"
fi

echo ""
echo -e "${BLUE}3️⃣  Checking Usage in Files...${NC}"
echo "════════════════════════════════════════════════"

if grep -q "sf.downloadFile" "spiderfoot/static/js/spiderfoot.scanlist.js"; then
    echo -e "${GREEN}✓${NC} scanlist.js updated to use new method"
else
    echo -e "${YELLOW}⚠${NC}  scanlist.js NOT using new method"
fi

if grep -q "sf.downloadFile" "spiderfoot/templates/scaninfo.tmpl"; then
    echo -e "${GREEN}✓${NC} scaninfo.tmpl updated to use new method"
else
    echo -e "${YELLOW}⚠${NC}  scaninfo.tmpl NOT using new method"
fi

if grep -q "sf.downloadFile" "spiderfoot/static/js/spiderfoot.opts.js"; then
    echo -e "${GREEN}✓${NC} spiderfoot.opts.js updated to use new method"
else
    echo -e "${YELLOW}⚠${NC}  spiderfoot.opts.js NOT using new method"
fi

echo ""
echo -e "${BLUE}4️⃣  Server Status...${NC}"
echo "════════════════════════════════════════════════"

if ps aux | grep -q "[s]f.py.*5001"; then
    echo -e "${GREEN}✓${NC} Server is running on http://127.0.0.1:5001"
    echo ""
    echo -e "${YELLOW}📝 To restart server with changes:${NC}"
    echo "   pkill -f 'python3.*sf.py'"
    echo "   ./start.sh"
else
    echo -e "${YELLOW}⚠${NC}  Server is not running"
    echo ""
    echo -e "${GREEN}🚀 To start server:${NC}"
    echo "   ./start.sh"
fi

echo ""
echo -e "${BLUE}5️⃣  Manual Testing Checklist...${NC}"
echo "════════════════════════════════════════════════"
echo "Open http://127.0.0.1:5001 and test:"
echo ""
echo "□ Investigations page → Select scan → Export → CSV"
echo "□ Investigations page → Select scan → Export → Excel"
echo "□ Investigations page → Select scan → Export → JSON"
echo "□ Investigations page → Select scan → Export → GEXF"
echo "□ Scan details page → Download Logs button"
echo "□ Scan details page → Export → CSV"
echo "□ Scan details page → Export → Excel"
echo "□ Settings page → Export API Keys"
echo ""
echo -e "${GREEN}✓ All downloads should trigger immediately!${NC}"
echo -e "${GREEN}✓ Files should save to your Downloads folder!${NC}"
echo ""
echo "════════════════════════════════════════════════"
echo -e "${BLUE}💡 Tip: Open browser console (F12) to see download logs${NC}"
echo "════════════════════════════════════════════════"
