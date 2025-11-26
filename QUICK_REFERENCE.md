# 🎨 Quick Reference Guide - OSINT Investigator UI

## 🚀 Quick Start Commands

### Start Server
```bash
cd /home/yash/Desktop/MEGA_PROJECT/spiderfoot
./start.sh
```

### Manual Start
```bash
python3 sf.py -l 127.0.0.1:5001
```

### Access URL
```
http://127.0.0.1:5001
```

---

## 🎨 CSS Variables Quick Reference

### Text Colors

#### Light Mode
```css
--text-primary: #000000   /* Pure Black */
--text-secondary: #333333
--text-tertiary: #666666
--text-muted: #999999
--text-inverse: #ffffff
```

#### Dark Mode
```css
--text-primary: #ffffff   /* Pure White */
--text-secondary: #e0e0e0
--text-tertiary: #b0b0b0
--text-muted: #808080
--text-inverse: #000000
```

### Accent Colors
```css
--accent-color: #667eea
--primary-color: #667eea
--secondary-color: #764ba2
```

### Status Colors
```css
--success-color: #22c55e / #4ade80
--warning-color: #f59e0b / #fbbf24
--error-color: #ef4444 / #f87171
--info-color: #3b82f6 / #60a5fa
```

---

## 📁 Project Structure

```
spiderfoot/
├── sf.py                       # Main entry point
├── sfwebui.py                  # Web UI server
├── start.sh                    # Quick start script ⭐
├── RUN_PROJECT.md              # Detailed instructions
├── CSS_VARIABLES_IMPLEMENTATION.md  # CSS guide
├── UI_MODERNIZATION_SUMMARY.md      # Full summary
│
├── spiderfoot/
│   ├── templates/              # HTML templates (modernized)
│   │   ├── HEADER.tmpl
│   │   ├── FOOTER.tmpl
│   │   ├── newscan.tmpl
│   │   ├── scanlist.tmpl
│   │   ├── opts.tmpl
│   │   └── scaninfo.tmpl
│   │
│   └── static/
│       ├── css/
│       │   ├── spiderfoot.css  # Main CSS with variables ⭐
│       │   └── dark.css        # Legacy (not used)
│       │
│       └── js/
│           └── spiderfoot.js   # Theme toggle logic ⭐
│
└── modules/                    # 200+ OSINT modules
```

---

## 🎯 Key Features

### ✨ Modern UI
- Purple gradient theme
- Glassmorphism effects
- Smooth animations
- Responsive design

### 🌓 Theme System
- Light/Dark mode toggle
- Instant switching (no reload)
- LocalStorage persistence
- Pure black/white text

### ♿ Accessibility
- WCAG AAA contrast
- Maximum readability
- Screen reader friendly
- Keyboard navigation

---

## 🎨 Using CSS Variables

### In Your CSS
```css
/* Use existing variables */
.my-element {
    color: var(--text-primary);
    background: var(--card-bg);
    border-color: var(--accent-color);
}
```

### Add New Variables
```css
:root {
    --my-custom-color: #ff6b6b;
}

[data-theme='dark'] {
    --my-custom-color: #ff8787;
}
```

### Use in HTML (inline styles)
```html
<div style="color: var(--text-primary)">
    Hello World
</div>
```

---

## 🌓 Theme Toggle

### Via UI
Click the ☀️/🌙 icon in the navigation bar

### Via JavaScript
```javascript
// Get current theme
const theme = document.documentElement.getAttribute('data-theme');

// Set light mode
document.documentElement.removeAttribute('data-theme');

// Set dark mode
document.documentElement.setAttribute('data-theme', 'dark');
```

### Via LocalStorage
```javascript
// Save preference
localStorage.setItem('theme', 'dark');

// Read preference
const savedTheme = localStorage.getItem('theme');
```

---

## 📊 Common Selectors

### Text Elements
```css
body, p, span, div        → var(--text-primary)
h1, h2, h3, h4, h5, h6    → var(--text-primary)
ul, ol, li                → var(--text-primary)
```

### Forms
```css
input, textarea, select   → var(--text-primary)
label                     → var(--text-primary)
::placeholder             → var(--text-muted)
```

### Tables
```css
table                     → var(--text-primary)
table th                  → var(--text-inverse)
table td                  → var(--text-primary)
```

### Components
```css
.navbar                   → var(--text-inverse)
.btn                      → var(--text-inverse)
.modal-header             → var(--text-inverse)
.modal-body               → var(--text-primary)
```

---

## 🐛 Troubleshooting

### Text not visible in dark mode?
```css
/* Force text color */
.my-element {
    color: var(--text-primary) !important;
}
```

### Theme not switching?
1. Check browser console for errors
2. Verify JavaScript is enabled
3. Clear LocalStorage: `localStorage.clear()`
4. Hard refresh: `Ctrl+Shift+R`

### Colors not updating?
1. Check CSS variable definition
2. Verify no hardcoded colors override
3. Check specificity (`!important` if needed)
4. Inspect element in DevTools

---

## 💡 Pro Tips

### 1. **Use DevTools**
- Right-click → Inspect
- View computed styles
- See which rules apply
- Test CSS changes live

### 2. **Check Contrast**
- Use browser DevTools contrast checker
- Aim for 7:1 ratio (WCAG AAA)
- Test with actual users

### 3. **Test Both Modes**
- Always test light AND dark
- Check all pages
- Verify forms and inputs
- Test with real data

### 4. **Use CSS Variables**
- Don't hardcode colors
- Use semantic names
- Keep variables organized
- Document custom variables

### 5. **Performance**
- CSS variables are fast
- No JavaScript needed for colors
- Hardware accelerated transitions
- Minimal reflow/repaint

---

## 📚 Documentation

### Main Guides
- `RUN_PROJECT.md` - How to run the project
- `CSS_VARIABLES_IMPLEMENTATION.md` - CSS variable details
- `UI_MODERNIZATION_SUMMARY.md` - Complete UI changes

### Code Comments
- CSS: Organized by section with headers
- JS: Inline comments explain logic
- Templates: Template syntax documented

---

## 🎓 Key Concepts

### CSS Variables (Custom Properties)
```css
/* Define */
:root {
    --my-var: value;
}

/* Use */
.element {
    property: var(--my-var);
}

/* Fallback */
.element {
    property: var(--my-var, fallback-value);
}
```

### Data Attributes for Theming
```html
<!-- Light mode (default) -->
<html>

<!-- Dark mode -->
<html data-theme="dark">
```

### LocalStorage for Persistence
```javascript
// Save
localStorage.setItem('key', 'value');

// Get
const value = localStorage.getItem('key');

// Remove
localStorage.removeItem('key');
```

---

## ⚡ Performance Tips

### CSS
- Use CSS variables (no JS overhead)
- Minimize `!important` usage
- Group similar selectors
- Use efficient selectors

### JavaScript
- Use event delegation
- Debounce theme toggles
- Cache DOM queries
- Use `requestAnimationFrame` for animations

### Images
- Use SVG when possible
- Optimize PNG/JPG
- Lazy load images
- Use proper image formats

---

## 🔧 Customization

### Change Primary Color
```css
:root {
    --accent-color: #your-color;
    --primary-color: #your-color;
}
```

### Change Text Color
```css
:root {
    --text-primary: #your-color;
}
```

### Add New Theme
```css
[data-theme='blue'] {
    --accent-color: #3b82f6;
    --primary-color: #3b82f6;
    /* ... more colors */
}
```

---

## 📞 Support

### Issues?
1. Check browser console
2. Review error logs
3. Verify file paths
4. Check permissions

### Need Help?
1. Read documentation
2. Check CSS comments
3. Inspect with DevTools
4. Test in isolation

---

## ✅ Checklist

### Before Deployment
- [ ] Test light mode
- [ ] Test dark mode
- [ ] Test theme switching
- [ ] Test all pages
- [ ] Test responsive design
- [ ] Check contrast ratios
- [ ] Verify accessibility
- [ ] Test in multiple browsers
- [ ] Check performance
- [ ] Review documentation

---

## 🎉 Quick Wins

1. **Start server:** `./start.sh`
2. **Open browser:** `http://127.0.0.1:5001`
3. **Toggle theme:** Click ☀️/🌙 icon
4. **See results:** Instant theme switching!
5. **Verify:** Text is black in light, white in dark

---

**🚀 You're all set! Enjoy your modernized OSINT Investigator!**

Last Updated: November 24, 2025
