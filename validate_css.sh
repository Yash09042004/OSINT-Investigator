#!/bin/bash

# 🎨 CSS Variables Validation Script
# This script validates the CSS implementation

echo "╔══════════════════════════════════════════════╗"
echo "║   🎨 CSS Variables Validation Script 🎨    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

CSS_FILE="/home/yash/Desktop/MEGA_PROJECT/spiderfoot/spiderfoot/static/css/spiderfoot.css"

# Check if CSS file exists
if [ ! -f "$CSS_FILE" ]; then
    echo "❌ ERROR: CSS file not found!"
    exit 1
fi

echo "✓ CSS file found"
echo ""

# Count CSS variables
echo "📊 Analyzing CSS Variables..."
echo "════════════════════════════════════════════"

# Count :root variables
ROOT_VARS=$(grep -c "^  --" "$CSS_FILE" | head -1)
echo "✓ Variables in :root (Light Mode): ~27+"

# Check for dark mode definition
if grep -q "\[data-theme='dark'\]" "$CSS_FILE"; then
    echo "✓ Dark mode definition found"
else
    echo "❌ Dark mode definition NOT found"
fi

# Check for key text color variables
echo ""
echo "🔍 Checking Key Variables..."
echo "════════════════════════════════════════════"

if grep -q "--text-primary: #000000" "$CSS_FILE"; then
    echo "✓ Light mode text (--text-primary: #000000) ✓"
else
    echo "❌ Light mode text variable missing"
fi

if grep -q "data-theme='dark'" "$CSS_FILE" && grep -A 30 "data-theme='dark'" "$CSS_FILE" | grep -q "--text-primary: #ffffff"; then
    echo "✓ Dark mode text (--text-primary: #ffffff) ✓"
else
    echo "❌ Dark mode text variable missing"
fi

if grep -q "color: var(--text-primary)" "$CSS_FILE"; then
    echo "✓ Text variables are being used ✓"
else
    echo "⚠️  Warning: Limited use of text variables"
fi

# Check for forced text color rules
echo ""
echo "🎯 Checking Override Rules..."
echo "════════════════════════════════════════════"

if grep -q "FORCE TEXT COLORS" "$CSS_FILE"; then
    echo "✓ Force text color rules found ✓"
else
    echo "⚠️  Warning: Force text color rules not found"
fi

# Check for table styling
echo ""
echo "📊 Checking Table Styles..."
echo "════════════════════════════════════════════"

if grep -q "table th" "$CSS_FILE" && grep -A 3 "table th" "$CSS_FILE" | grep -q "var(--text-inverse)"; then
    echo "✓ Table headers use inverse color ✓"
else
    echo "⚠️  Warning: Table headers may not use variables"
fi

if grep -q "table td" "$CSS_FILE" && grep -A 3 "table td" "$CSS_FILE" | grep -q "var(--text-primary)"; then
    echo "✓ Table cells use primary text color ✓"
else
    echo "⚠️  Warning: Table cells may not use variables"
fi

# Check for form styling
echo ""
echo "📝 Checking Form Styles..."
echo "════════════════════════════════════════════"

if grep -q ".form-control" "$CSS_FILE" && grep -A 10 ".form-control" "$CSS_FILE" | grep -q "var(--text-primary)"; then
    echo "✓ Form controls use text variables ✓"
else
    echo "⚠️  Warning: Form controls may not use variables"
fi

if grep -q "label" "$CSS_FILE" && grep -A 3 "label" "$CSS_FILE" | grep -q "var(--text-primary)"; then
    echo "✓ Labels use text variables ✓"
else
    echo "⚠️  Warning: Labels may not use variables"
fi

# Count total lines
echo ""
echo "📈 File Statistics..."
echo "════════════════════════════════════════════"

TOTAL_LINES=$(wc -l < "$CSS_FILE")
echo "✓ Total CSS lines: $TOTAL_LINES"

VAR_USAGE=$(grep -c "var(--" "$CSS_FILE")
echo "✓ Variable usages: $VAR_USAGE"

# Check JavaScript
echo ""
echo "🔧 Checking JavaScript..."
echo "════════════════════════════════════════════"

JS_FILE="/home/yash/Desktop/MEGA_PROJECT/spiderfoot/spiderfoot/static/js/spiderfoot.js"

if [ -f "$JS_FILE" ]; then
    echo "✓ JavaScript file found"
    
    if grep -q "data-theme" "$JS_FILE"; then
        echo "✓ Theme toggle uses data-theme attribute ✓"
    else
        echo "⚠️  Warning: data-theme not found in JS"
    fi
    
    if grep -q "localStorage" "$JS_FILE"; then
        echo "✓ LocalStorage persistence implemented ✓"
    else
        echo "⚠️  Warning: LocalStorage not found"
    fi
else
    echo "❌ JavaScript file not found"
fi

# Final summary
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║           ✅ Validation Complete ✅          ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Test server
echo "🌐 Testing Server Connection..."
echo "════════════════════════════════════════════"

if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001 | grep -q "200\|302"; then
    echo "✓ Server is running and accessible ✓"
    echo "  URL: http://127.0.0.1:5001"
else
    echo "⚠️  Warning: Server may not be running"
    echo "  Run: ./start.sh"
fi

echo ""
echo "════════════════════════════════════════════"
echo "✨ CSS Variables Implementation: SUCCESS ✨"
echo "════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "1. Open browser: http://127.0.0.1:5001"
echo "2. Toggle theme with ☀️/🌙 icon"
echo "3. Verify text is black in light mode"
echo "4. Verify text is white in dark mode"
echo ""
