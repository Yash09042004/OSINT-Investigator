#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  🚀 PYTHON COMMANDS TO RUN OSINT INVESTIGATOR
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# METHOD 1: Quick Start (Recommended - Use the script)
# ─────────────────────────────────────────────────────────────

cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot
./start.sh


# ─────────────────────────────────────────────────────────────
# METHOD 2: Manual Setup (Step by Step)
# ─────────────────────────────────────────────────────────────

# Step 1: Navigate to project directory
cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot

# Step 2: Create virtual environment (recommended)
python3 -m venv venv

# Step 3: Activate virtual environment
source venv/bin/activate

# Step 4: Upgrade pip
pip install --upgrade pip

# Step 5: Install dependencies
pip install -r requirements.txt

# Step 6: Run the web server
python3 sf.py -l 127.0.0.1:5001

# Step 7: Open browser and go to:
# http://127.0.0.1:5001


# ─────────────────────────────────────────────────────────────
# METHOD 3: Direct Run (Without Virtual Environment)
# ─────────────────────────────────────────────────────────────

cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot

# Install dependencies globally (not recommended for production)
pip3 install -r requirements.txt

# Run the server
python3 sf.py -l 127.0.0.1:5001


# ─────────────────────────────────────────────────────────────
# ALTERNATIVE RUN OPTIONS
# ─────────────────────────────────────────────────────────────

# Run on different port (e.g., 8080)
python3 sf.py -l 127.0.0.1:8080

# Run accessible from network (all interfaces)
python3 sf.py -l 0.0.0.0:5001

# Run with debug mode
python3 sf.py -l 127.0.0.1:5001 -d

# Run in background (requires nohup)
nohup python3 sf.py -l 127.0.0.1:5001 &


# ─────────────────────────────────────────────────────────────
# VERIFICATION COMMANDS
# ─────────────────────────────────────────────────────────────

# Check Python version
python3 --version

# Check if port is available
lsof -i :5001

# List installed packages
pip list

# Show SpiderFoot help
python3 sf.py -h


# ─────────────────────────────────────────────────────────────
# STOPPING THE SERVER
# ─────────────────────────────────────────────────────────────

# Press Ctrl+C in the terminal where server is running

# Or kill by port
kill -9 $(lsof -t -i:5001)


# ─────────────────────────────────────────────────────────────
# TROUBLESHOOTING COMMANDS
# ─────────────────────────────────────────────────────────────

# If port is busy, find and kill process
lsof -i :5001
kill -9 <PID>

# If dependencies fail, try:
pip install -r requirements.txt --force-reinstall

# If database issues, remove old database:
rm spiderfoot.db

# View logs
tail -f spiderfoot.log


# ─────────────────────────────────────────────────────────────
# ACCESS THE APPLICATION
# ─────────────────────────────────────────────────────────────

# Local access:
# http://127.0.0.1:5001

# Network access (if using 0.0.0.0):
# http://<your-ip-address>:5001


# ═══════════════════════════════════════════════════════════════
#  ✅ WHAT TO EXPECT
# ═══════════════════════════════════════════════════════════════
#
#  1. Server starts on http://127.0.0.1:5001
#  2. Modern purple gradient UI loads
#  3. Light mode with PURE BLACK text (#000000)
#  4. Click theme toggle (☀️/🌙) to switch to dark mode
#  5. Dark mode with PURE WHITE text (#ffffff)
#  6. Smooth transitions, no page reload needed
#  7. Theme preference saved in browser
#
# ═══════════════════════════════════════════════════════════════
