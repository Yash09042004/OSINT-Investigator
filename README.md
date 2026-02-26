# 🔍 PRISM - Open Source Intelligence Platform

<div align="center">

![PRISM Logo](https://img.shields.io/badge/PRISM-OSINT%20Platform-purple?style=for-the-badge)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.7+-green?style=flat-square)](https://www.python.org)
[![Status](https://img.shields.io/badge/status-active-success?style=flat-square)]()

**A modern, elegant OSINT automation platform for comprehensive intelligence gathering**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [License](#-license)

</div>

---

## 📖 About PRISM

PRISM is an advanced Open Source Intelligence (OSINT) automation platform designed to streamline and enhance digital investigations. With over 200 integrated data sources and a modern, intuitive interface, PRISM makes complex intelligence gathering simple and efficient.

Built on proven technology and enhanced with modern web design, PRISM provides investigators, researchers, and security professionals with a powerful tool for comprehensive target analysis.

### 🎯 Key Highlights

- **200+ Data Sources** - Comprehensive integration with major intelligence databases
- **Modern UI/UX** - Beautiful purple gradient theme with dark mode support
- **Multiple Export Formats** - CSV, JSON, Excel, and GEXF visualization
- **Intelligent Correlation** - YAML-based correlation engine with 37+ pre-defined rules
- **Flexible Deployment** - Web UI, CLI, or Docker-based deployments
- **Privacy Focused** - Most modules work without API keys

---

## ✨ Features

### 🌐 Web Interface
- Clean, modern purple gradient interface
- Real-time scan monitoring and visualization
- Dark/Light theme toggle
- Responsive design for all devices
- Interactive data exploration

### 🔎 Intelligence Gathering
- **Host Enumeration** - Subdomain discovery and DNS analysis
- **Email Intelligence** - Address extraction and breach checking
- **Social Media** - Profile discovery across 500+ platforms
- **Threat Intelligence** - Malicious IP and domain detection
- **Document Analysis** - Metadata extraction from files
- **Network Mapping** - Port scanning and service identification
- **Dark Web Search** - TOR integration for deep web intelligence

### 📊 Data Analysis
- Advanced correlation engine
- Custom correlation rules (YAML-based)
- Visual relationship mapping
- False positive filtering
- Historical data tracking

### 🛠️ Technical Features
- Python 3.7+ compatibility
- SQLite database backend
- RESTful API support
- Module-based architecture
- Docker support
- CLI and Web interfaces

---

## 🚀 Installation

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd spiderfoot

# Install dependencies
pip3 install -r requirements.txt

# Start PRISM
python3 sf.py -l 127.0.0.1:5001
```

### Using Start Script

```bash
# Make start script executable
chmod +x start.sh

# Launch PRISM
./start.sh
```

The web interface will be available at: **http://127.0.0.1:5001**

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

---

## 📱 Usage

### Starting a New Investigation

1. **Launch PRISM** - Open http://127.0.0.1:5001 in your browser
2. **New Investigation** - Click "New Investigation" in the navigation
3. **Configure Target** - Enter your target (domain, IP, email, etc.)
4. **Select Modules** - Choose intelligence gathering modules
5. **Start Scan** - Launch your investigation
6. **Analyze Results** - Browse, search, and export findings

### Target Types Supported

- 🌐 Domain names and subdomains
- 🔢 IP addresses and network ranges
- 📧 Email addresses
- 📞 Phone numbers
- 👤 Human names and usernames
- 💰 Bitcoin/Ethereum addresses
- 🏢 Organizations and ASNs

### Command Line Interface

```bash
# Run CLI version
python3 sfcli.py

# Get help
python3 sf.py --help
```

---

## 📚 Documentation

### Project Structure

```
spiderfoot/
├── sf.py                    # Main entry point
├── sfwebui.py              # Web interface server
├── sfcli.py                # Command-line interface
├── start.sh                # Quick start script
├── requirements.txt        # Python dependencies
├── spiderfoot/
│   ├── templates/          # HTML templates
│   └── static/            # CSS, JS, and assets
└── modules/               # 200+ OSINT modules
```

### Key Configuration Files

- **requirements.txt** - Python package dependencies
- **docker-compose.yml** - Docker deployment configuration
- **correlations/** - Custom correlation rule definitions

### Exporting Data

PRISM supports multiple export formats:
- **CSV** - Spreadsheet-compatible format
- **Excel** - XLSX format with formatting
- **JSON** - Structured data format
- **GEXF** - Graph visualization format

---

## 🎨 Modern UI Features

### Purple Gradient Theme
- Professional purple (#667eea) and deep purple (#764ba2) gradient
- Glassmorphism effects for depth
- Smooth animations and transitions

### Dark Mode Support
- Toggle between light and dark themes
- Automatic theme persistence
- WCAG AAA accessibility compliance
- Pure black cards with white text in dark mode

### Enhanced User Experience
- Intuitive navigation
- Real-time progress indicators
- Interactive data tables
- Advanced search and filtering
- One-click exports

---

## 🛡️ Privacy & Security

- **No Data Collection** - All processing happens locally
- **API Key Protection** - Secure credential storage
- **Open Source** - Fully auditable codebase
- **Community Driven** - Transparent development

---

## 🤝 Contributing

We welcome contributions to PRISM! Whether it's:
- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🔧 Code contributions

Please feel free to open issues or submit pull requests.

---

## 👥 Authors

**PRISM** is developed and maintained by:

- **Mr. Yash Patil**
- **Mr. Soumitra Bapat**
- **Mr. Sharvari Jadhav**

---

## 📄 License

This project is licensed under the **MIT License** - see below for details:

```
MIT License

Copyright (c) 2025 PRISM Team
(Yash Patil, Soumitra Bapat, Sharvari Jadhav)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🌟 Acknowledgments

PRISM is built upon the foundation of SpiderFoot, an excellent OSINT automation tool. We extend our gratitude to the SpiderFoot community and contributors.

This project has been enhanced with:
- Modern UI/UX design
- Purple gradient theming
- Enhanced dark mode support
- Improved download functionality
- CSS variable system for easy customization

---

## 📞 Support

For questions, issues, or suggestions:
- 📧 Open an issue on the repository
- 💬 Check existing documentation
- 🔍 Review the correlation rules guide

---

## 🚀 Quick Reference

### Start Server
```bash
./start.sh
```

### Access Application
```
http://127.0.0.1:5001
```

### Theme Toggle
Click the ☀️/🌙 icon in the top-right corner to switch themes

### Export Data
Select scans → Click Export → Choose format (CSV/Excel/JSON/GEXF)

---

<div align="center">

**Made with 💜 by the PRISM Team**

*Empowering Intelligence Gathering Through Open Source Technology*

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)

</div>
