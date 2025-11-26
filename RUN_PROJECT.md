# 🚀 OSINT Investigator - Running Instructions

## ✅ Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git (already installed)

## 📦 Installation Steps

### 1. Navigate to Project Directory
```bash
cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
# Check if all packages are installed
pip list
```

## 🎯 Running the Application

### Method 1: Run Web Interface (Recommended)
```bash
# Make sure you're in the spiderfoot directory
cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot

# Start the web server
python3 sf.py -l 127.0.0.1:5001
```

**Access the application:**
- Open your browser and navigate to: `http://127.0.0.1:5001`
- The modern purple gradient UI will load automatically
- Use the theme toggle (☀️/🌙) in the top-right to switch between Light/Dark modes

### Method 2: Run with Custom Port
```bash
# Run on a different port (e.g., 8080)
python3 sf.py -l 127.0.0.1:8080
```

### Method 3: Run Accessible from Network
```bash
# Allow access from other devices on your network
python3 sf.py -l 0.0.0.0:5001
```

### Method 4: Command Line Interface
```bash
# Run CLI version
python3 sfcli.py -h
```

## 🎨 UI Features (Modernized)

### ✨ What's New:
- **Modern Purple Gradient Theme** - Beautiful gradient backgrounds
- **CSS Variables System** - Easy theme customization
- **High Contrast Text**:
  - ☀️ Light Mode: Pure black text (#000000) on light backgrounds
  - 🌙 Dark Mode: Pure white text (#ffffff) on dark backgrounds
- **Glassmorphism Effects** - Modern card designs with blur effects
- **Smooth Animations** - Transitions and hover effects
- **Responsive Design** - Works on all screen sizes
- **Theme Toggle** - Switch between light/dark modes instantly

### 🎯 Color Palette:
- Primary: `#667eea` (Purple)
- Secondary: `#764ba2` (Deep Purple)
- Accent: Various purple gradients
- Success: Green tones
- Warning: Orange tones
- Error: Red tones

## 🔧 Configuration

### Default Settings
- Host: `127.0.0.1`
- Port: `5001`
- Database: SQLite (auto-created)
- Log File: `spiderfoot.log`

### Environment Variables (Optional)
```bash
# Set custom configuration
export SPIDERFOOT_HOST=127.0.0.1
export SPIDERFOOT_PORT=5001
```

## 📝 Common Commands

### Start Server (Basic)
```bash
python3 sf.py
```

### Start Server with Debug Mode
```bash
python3 sf.py -d
```

### View Help
```bash
python3 sf.py -h
```

### Check Version
```bash
python3 sf.py -v
```

## 🛑 Stopping the Server
- Press `Ctrl + C` in the terminal
- Or close the terminal window

## 🔍 Testing the UI Improvements

1. **Start the server:**
   ```bash
   python3 sf.py -l 127.0.0.1:5001
   ```

2. **Open browser:** `http://127.0.0.1:5001`

3. **Test Light Mode:**
   - Text should be pure black (#000000)
   - Backgrounds should be light with purple gradient overlay
   - Cards should have glassmorphism effect

4. **Test Dark Mode:**
   - Click the theme toggle (☀️/🌙 icon in navbar)
   - Text should be pure white (#ffffff)
   - Backgrounds should be dark with purple gradient
   - All elements should maintain proper contrast

5. **Test Navigation:**
   - New Scan page - Modern form layouts
   - Scans list - Updated alerts and cards
   - Settings - Improved module configuration UI
   - All pages should have consistent styling

## 📊 Project Structure
```
spiderfoot/
├── sf.py                    # Main entry point
├── sfwebui.py              # Web UI server
├── sfcli.py                # CLI interface
├── requirements.txt         # Dependencies
├── spiderfoot/
│   ├── templates/          # HTML templates (modernized)
│   └── static/
│       ├── css/
│       │   ├── spiderfoot.css  # Main CSS (with CSS variables)
│       │   └── dark.css        # Legacy (no longer needed)
│       └── js/
│           └── spiderfoot.js   # Theme toggle logic
└── modules/                # OSINT modules
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>

# Or use a different port
python3 sf.py -l 127.0.0.1:5002
```

### Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Permission Issues
```bash
# Make sf.py executable
chmod +x sf.py

# Run with explicit python
python3 sf.py
```

### Database Issues
```bash
# Remove old database
rm spiderfoot.db

# Restart the application
python3 sf.py
```

## 📚 Additional Resources
- Full Documentation: Check `docs/` folder
- Module List: 200+ OSINT modules available
- API Documentation: Available when server is running

## 🎉 Success Indicators
- Server starts without errors
- Browser loads the UI at http://127.0.0.1:5001
- Theme toggle works (☀️ ↔️ 🌙)
- Text is readable in both modes
- Purple gradient theme is visible
- All navigation works smoothly

## 💡 Pro Tips
1. **Use virtual environment** to avoid dependency conflicts
2. **Check logs** in `spiderfoot.log` if issues occur
3. **Test theme switching** to see CSS variables in action
4. **Try responsive design** by resizing browser window
5. **Explore all pages** to see complete UI modernization

---

**Enjoy your modernized OSINT Investigator! 🎨🔍**
