# Subscription Manager — ByteFroster Edition

A sleek desktop app to **manage your digital subscriptions** — built with **Python + PySide6**, by [Tijul Kabir Toha](https://tijulkabir.me).  
Easily track your services, renewal dates, and remaining days with a minimal, modern UI.

---

## 🚀 Features
- ✅ Add, edit, and delete subscriptions  
- ✅ Track start date, end date, and remaining days  
- ✅ SQLite storage (no setup required)  
- ✅ Import / export Excel or CSV  
- ✅ Custom **ByteFroster** green-black theme + icon  
- ✅ One-click silent startup (no console pop-up)

---

## ⚙️ Requirements

- **Python 3.10+**
- Install dependencies:
```bash
pip install -r requirements.txt
---

##  Run Instructions

###  Option 1 — Direct Run
```bash
python subscription_manager.py
Option 2 — Silent Mode (no CMD popup)

Step 1 — Allow local scripts:

Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned


Step 2 — Create a shortcut:

.\create_shortcut.ps1


This creates a desktop shortcut: Subscription Manager.lnk
Double-click it to launch your app silently with your custom icon.
Folder Layout
Subscription_Management/
├── subscription_manager.py     # Main application
├── run_silent.vbs              # Silent launcher (no CMD)
├── create_shortcut.ps1         # Shortcut creator script
├── bytefroster.ico             # Custom icon
├── requirements.txt            # Dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore rules
```
```bash
Language: Python
GUI Framework: PySide6 (Qt for Python)
Database: SQLite
Data Handling: Pandas, OpenPyXL
Launcher: VBS + PowerShell integration

👨‍💻 Author

Tijul Kabir Toha (Froster)
🎓 BSc in CSE @ PUST, Bangladesh
💀 Cybersecurity & Competitive Programming Enthusiast

🪪 License

This project is open-source under the MIT License.
You are free to modify and distribute it — just give credit to the original author.
