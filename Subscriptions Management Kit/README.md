# Subscription Manager — ByteFroster Edition

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-00E676?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)

**A sleek desktop app to manage your digital subscriptions**

*Built with Python + PySide6 by [Tijul Kabir Toha](https://tijulkabir.me)*

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📋 **CRUD Operations** | Add, edit, and delete subscriptions with ease |
| 📅 **Date Tracking** | Track start dates, end dates, and days remaining |
| 🏷️ **Categories** | Organize subscriptions by type (Streaming, Music, Software, etc.) |
| 🔍 **Search & Filter** | Quickly find subscriptions by name or category |
| 🎨 **Status Colors** | Visual indicators — 🟢 Active, 🟡 Expiring Soon, 🔴 Expired |
| 📥 **Import/Export** | Excel and CSV support for bulk operations |
| 💾 **SQLite Backend** | Local database, no cloud required |
| ⌨️ **Keyboard Shortcuts** | Ctrl+N, Delete, F5, and more |
| 📝 **Logging** | Debug logs stored in AppData |

---

## 🚀 Quick Start

### One-Click Installation (Windows)

1. **Download** or clone this repository
2. **Double-click** `install.bat`
3. **Done!** A desktop shortcut will be created

```batch
# Or from command line:
install.bat
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/tijulkabir/personal_projects.git
cd "personal_projects/Subscriptions Management Kit"

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the app
python subscription_manager.py
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New subscription |
| `Ctrl+I` | Import Excel/CSV |
| `Ctrl+E` | Export to Excel |
| `Delete` | Delete selected |
| `F5` | Refresh table |
| `F1` | About dialog |
| `Escape` | Cancel editing |

---

## 📁 Project Structure

```
Subscriptions Management Kit/
├── subscription_manager.py   # Main application (v2.0.0)
├── install.bat               # One-click Windows installer
├── run_silent.vbs            # Silent launcher (no console)
├── run.cmd                    # Command-line launcher
├── create_shortcut.ps1       # PowerShell shortcut creator
├── requirements.txt          # Python dependencies
├── bytefroster.ico          # Custom application icon
└── README.md                 # This file
```

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **GUI Framework:** PySide6 (Qt for Python)
- **Database:** SQLite
- **Data Handling:** Pandas, OpenPyXL

---

## 📊 Data Location

Your subscription data is stored locally:

| OS | Location |
|----|----------|
| Windows | `%LOCALAPPDATA%\SubscriptionManager\` |
| macOS | `~/Library/Application Support/SubscriptionManager/` |
| Linux | `~/.local/share/SubscriptionManager/` |

Files stored:
- `subscriptions.db` — SQLite database
- `config.json` — User preferences
- `app.log` — Application logs

---

## 👨‍💻 Author

**Tijul Kabir Toha** (Froster)

- 🎓 BSc in CSE @ PUST, Bangladesh
- 💀 Cybersecurity & Competitive Programming Enthusiast
- 🌐 [tijulkabir.me](https://tijulkabir.me)
- 📂 [GitHub](https://github.com/tijulkabir)

---

## 📜 License

This project is open-source under the **MIT License**.  
You are free to modify and distribute it — just give credit to the original author.

---

<div align="center">

Made with 💚 by ByteFroster

</div>
