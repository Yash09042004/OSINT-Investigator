#!/bin/bash

# 🚀 PRISM - OSINT Platform Quick Start Script
# This script sets up and runs the PRISM web application

echo "╔════════════════════════════════════════════╗"
echo "║      🔷 PRISM - OSINT Platform 🔷         ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/.requirements_installed" ]; then
    echo "📥 Installing dependencies (this may take a few minutes)..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    
    # Mark requirements as installed
    touch venv/.requirements_installed
    echo "✓ Dependencies installed successfully"
    echo ""
else
    echo "✓ Dependencies already installed"
    echo ""
fi

# Display information
echo "╔════════════════════════════════════════════╗"
echo "║           Starting Web Server...          ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "🌐 Server will be available at:"
echo "   👉 http://127.0.0.1:5001"
echo ""
echo "🎨 UI Features:"
echo "   ☀️  Light Mode: Pure black text (#000000)"
echo "   🌙 Dark Mode: Pure white text (#ffffff)"
echo "   🎨 Modern purple gradient theme"
echo "   ✨ Glassmorphism effects"
echo ""
echo "💡 Tips:"
echo "   • Use the theme toggle (☀️/🌙) in the navbar"
echo "   • Press Ctrl+C to stop the server"
echo "   • Check spiderfoot.log for debug info"
echo ""
echo "════════════════════════════════════════════"
echo ""

# Start the server on port 5001
python3 sf.py -l 127.0.0.1:5001

# Cleanup on exit
echo ""
echo "👋 Server stopped. Goodbye!"
deactivate 2>/dev/null || true