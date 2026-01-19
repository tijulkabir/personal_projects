"""
Subscription Manager — ByteFroster Edition v2.0.0
Industrial-Grade Desktop Application

Maintained by Tijul Kabir Toha (Visit tijulkabir.me for more projects).
https://github.com/tijulkabir/personal_projects

Features:
- Track subscriptions with start/end dates and categories
- Import/Export Excel/CSV
- Search and filter
- Color-coded status indicators
- Keyboard shortcuts
- Logging and error handling
"""

__version__ = "2.0.0"
__author__ = "Tijul Kabir Toha"

import sys
import os
import sqlite3
import logging
from datetime import date, datetime
from pathlib import Path
import json

import pandas as pd
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon, QAction, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QDateEdit, QMessageBox, QFileDialog, QHeaderView, QAbstractItemView,
    QComboBox, QMenuBar, QMenu, QDialog, QTextBrowser, QDialogButtonBox,
    QSystemTrayIcon, QStyle
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_app_data_dir() -> Path:
    """Get appropriate application data directory for the OS."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    app_dir = base / "SubscriptionManager"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

APP_DIR = get_app_data_dir()
DB_FILE = APP_DIR / "subscriptions.db"
CONFIG_FILE = APP_DIR / "config.json"
LOG_FILE = APP_DIR / "app.log"

# Default categories
DEFAULT_CATEGORIES = [
    "Streaming", "Music", "Software", "Gaming", "Cloud Storage",
    "News", "Fitness", "Education", "Productivity", "Other"
]

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════════════

def setup_logging():
    """Configure rotating file handler and console logging."""
    logger = logging.getLogger("SubscriptionManager")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Console handler (only warnings and above in production)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(file_format)
    logger.addHandler(console_handler)
    
    return logger

log = setup_logging()

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class ConfigManager:
    """Handles application configuration with JSON storage."""
    
    DEFAULTS = {
        "categories": DEFAULT_CATEGORIES.copy(),
        "warn_days": 7,  # Days before expiry to show warning
        "window_width": 1200,
        "window_height": 700,
    }
    
    def __init__(self, path: Path = CONFIG_FILE):
        self.path = path
        self.data = self._load()
    
    def _load(self) -> dict:
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    return {**self.DEFAULTS, **loaded}
            except Exception as e:
                log.error(f"Failed to load config: {e}")
        return self.DEFAULTS.copy()
    
    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            log.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value):
        self.data[key] = value
        self.save()

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

SCHEMA = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    category TEXT DEFAULT 'Other',
    notes TEXT
);
"""

def init_db(path: Path = DB_FILE) -> sqlite3.Connection:
    """Initialize database with schema, adding category column if needed."""
    log.info(f"Initializing database at {path}")
    conn = sqlite3.connect(str(path))
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    
    # Migration: add category column if it doesn't exist
    cur.execute("PRAGMA table_info(subscriptions)")
    columns = [col[1] for col in cur.fetchall()]
    if "category" not in columns:
        log.info("Migrating database: adding 'category' column")
        cur.execute("ALTER TABLE subscriptions ADD COLUMN category TEXT DEFAULT 'Other'")
    
    conn.commit()
    return conn


class SubscriptionDB:
    """Database access layer for subscriptions."""
    
    def __init__(self, path: Path = DB_FILE):
        self.path = path
        self.conn = init_db(path)
        log.info("Database connection established")

    def add(self, name: str, start_iso: str, end_iso: str, category: str = "Other", notes: str = "") -> int:
        """Add a new subscription and return its ID."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO subscriptions (name, start_date, end_date, category, notes) VALUES (?, ?, ?, ?, ?)",
                (name, start_iso, end_iso, category, notes)
            )
            self.conn.commit()
            log.info(f"Added subscription: {name}")
            return cur.lastrowid
        except Exception as e:
            log.error(f"Failed to add subscription: {e}")
            raise

    def update(self, sid: int, name: str, start_iso: str, end_iso: str, category: str = "Other", notes: str = ""):
        """Update an existing subscription."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE subscriptions SET name=?, start_date=?, end_date=?, category=?, notes=? WHERE id=?",
                (name, start_iso, end_iso, category, notes, sid)
            )
            self.conn.commit()
            log.info(f"Updated subscription ID {sid}")
        except Exception as e:
            log.error(f"Failed to update subscription: {e}")
            raise

    def delete(self, sid: int):
        """Delete a subscription by ID."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM subscriptions WHERE id=?", (sid,))
            self.conn.commit()
            log.info(f"Deleted subscription ID {sid}")
        except Exception as e:
            log.error(f"Failed to delete subscription: {e}")
            raise

    def list_all(self) -> list:
        """Return all subscriptions ordered by end date."""
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, start_date, end_date, category, notes FROM subscriptions ORDER BY end_date")
        return cur.fetchall()

    def search(self, query: str) -> list:
        """Search subscriptions by name or category."""
        cur = self.conn.cursor()
        pattern = f"%{query}%"
        cur.execute(
            "SELECT id, name, start_date, end_date, category, notes FROM subscriptions "
            "WHERE name LIKE ? OR category LIKE ? ORDER BY end_date",
            (pattern, pattern)
        )
        return cur.fetchall()

    def import_from_dataframe(self, df: pd.DataFrame) -> int:
        """Import subscriptions from a DataFrame. Returns count of imported rows."""
        count = 0
        for _, row in df.iterrows():
            name = str(row.get("Name") or row.get("name") or "")
            sd = row.get("Start Date") or row.get("start_date")
            ed = row.get("End Date") or row.get("end_date")
            category = str(row.get("Category") or row.get("category") or "Other")
            notes = str(row.get("Notes") or row.get("notes") or "")
            
            if not name:
                continue
            
            try:
                sd_iso = pd.to_datetime(sd).date().isoformat()
                ed_iso = pd.to_datetime(ed).date().isoformat()
                self.add(name, sd_iso, ed_iso, category, notes)
                count += 1
            except Exception as e:
                log.warning(f"Skipped row during import: {e}")
                continue
        
        log.info(f"Imported {count} subscriptions")
        return count

    def export_to_dataframe(self) -> pd.DataFrame:
        """Export all subscriptions to a DataFrame."""
        rows = self.list_all()
        return pd.DataFrame(rows, columns=["ID", "Name", "Start Date", "End Date", "Category", "Notes"])


# ═══════════════════════════════════════════════════════════════════════════════
# ABOUT DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class AboutDialog(QDialog):
    """About dialog showing version and author info."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Subscription Manager")
        self.setFixedSize(420, 300)
        
        layout = QVBoxLayout(self)
        
        info_html = f"""
        <div style="text-align: center; font-family: Segoe UI, Arial;">
            <h2 style="color: #00E676;">📋 Subscription Manager</h2>
            <h3>ByteFroster Edition</h3>
            <p><b>Version:</b> {__version__}</p>
            <hr>
            <p><b>Author:</b> {__author__}</p>
            <p>🎓 BSc in CSE @ PUST, Bangladesh</p>
            <p>💀 Cybersecurity & Competitive Programming Enthusiast</p>
            <hr>
            <p>🌐 <a href="https://tijulkabir.me">tijulkabir.me</a></p>
            <p>📂 <a href="https://github.com/tijulkabir/personal_projects">GitHub Repository</a></p>
            <hr>
            <p style="font-size: 11px; color: #888;">
                Open-source under MIT License
            </p>
        </div>
        """
        
        text_browser = QTextBrowser()
        text_browser.setHtml(info_html)
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Subscription Manager — ByteFroster Edition v{__version__}")
        
        self.config = ConfigManager()
        self.db = SubscriptionDB()
        self._editing_id = None
        
        self._setup_menu()
        self._setup_ui()
        self._setup_shortcuts()
        self._load_table()
        
        log.info("Application started successfully")
    
    def _setup_menu(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        import_action = QAction("&Import Excel/CSV...", self)
        import_action.setShortcut(QKeySequence("Ctrl+I"))
        import_action.triggered.connect(self.import_excel)
        file_menu.addAction(import_action)
        
        export_action = QAction("&Export to Excel...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_excel)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        add_action = QAction("&New Subscription", self)
        add_action.setShortcut(QKeySequence("Ctrl+N"))
        add_action.triggered.connect(self._focus_name_input)
        edit_menu.addAction(add_action)
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._load_table)
        edit_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setShortcut(QKeySequence("F1"))
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        data_folder_action = QAction("Open &Data Folder", self)
        data_folder_action.triggered.connect(self._open_data_folder)
        help_menu.addAction(data_folder_action)
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # ── Search Bar ──
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by name or category...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # ── Form Row ──
        form_layout = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Service name (e.g., Netflix)")
        
        self.start_input = QDateEdit()
        self.start_input.setCalendarPopup(True)
        self.start_input.setDate(QDate.currentDate())
        
        self.end_input = QDateEdit()
        self.end_input.setCalendarPopup(True)
        self.end_input.setDate(QDate.currentDate().addDays(30))
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(self.config.get("categories", DEFAULT_CATEGORIES))
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Notes (optional)")
        
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input, 2)
        form_layout.addWidget(QLabel("Start:"))
        form_layout.addWidget(self.start_input)
        form_layout.addWidget(QLabel("End:"))
        form_layout.addWidget(self.end_input)
        form_layout.addWidget(QLabel("Category:"))
        form_layout.addWidget(self.category_input, 1)
        form_layout.addWidget(QLabel("Notes:"))
        form_layout.addWidget(self.notes_input, 1)
        
        layout.addLayout(form_layout)
        
        # ── Action Buttons ──
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Add")
        self.add_btn.clicked.connect(self.add_subscription)
        self.add_btn.setStyleSheet("background-color: #00C853; color: white; font-weight: bold; padding: 8px 16px;")
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_edit)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px 16px;")
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet("padding: 8px 16px;")
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self.import_excel)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_excel)
        
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.export_btn)
        
        layout.addLayout(btn_layout)
        
        # ── Table ──
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Start Date", "End Date", "Days Left", "Category"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_row_double_click)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # ── Footer Buttons ──
        footer_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setStyleSheet("background-color: #F44336; color: white; padding: 8px 16px;")
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._load_table)
        
        footer_layout.addWidget(self.delete_btn)
        footer_layout.addWidget(self.refresh_btn)
        footer_layout.addStretch()
        
        # Status label
        self.status_label = QLabel()
        footer_layout.addWidget(self.status_label)
        
        layout.addLayout(footer_layout)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Delete key to remove selected
        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        delete_shortcut.activated.connect(self.delete_selected)
        
        # Escape to cancel edit
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.cancel_edit)
    
    def _focus_name_input(self):
        """Focus the name input field for new entry."""
        self.cancel_edit()
        self.name_input.setFocus()
    
    def _show_about(self):
        """Show the about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def _open_data_folder(self):
        """Open the application data folder in file explorer."""
        import subprocess
        if sys.platform == "win32":
            subprocess.run(["explorer", str(APP_DIR)])
        elif sys.platform == "darwin":
            subprocess.run(["open", str(APP_DIR)])
        else:
            subprocess.run(["xdg-open", str(APP_DIR)])
    
    def _on_search(self, text: str):
        """Filter table based on search text."""
        self._load_table(search_query=text)
    
    def _on_row_double_click(self, row: int, col: int):
        """Handle double-click to edit a subscription."""
        item = self.table.item(row, 0)
        if not item:
            return
        
        sid = int(item.text())
        name = self.table.item(row, 1).text()
        sd = self.table.item(row, 2).text()
        ed = self.table.item(row, 3).text()
        category = self.table.item(row, 5).text()
        
        # Get notes from database since we don't display it in table
        rows = self.db.list_all()
        notes = ""
        for r in rows:
            if r[0] == sid:
                notes = r[5] or ""
                break
        
        self._editing_id = sid
        self.name_input.setText(name)
        self.notes_input.setText(notes)
        self.category_input.setCurrentText(category)
        
        try:
            sd_date = datetime.fromisoformat(sd).date()
            ed_date = datetime.fromisoformat(ed).date()
            self.start_input.setDate(QDate(sd_date.year, sd_date.month, sd_date.day))
            self.end_input.setDate(QDate(ed_date.year, ed_date.month, ed_date.day))
        except Exception:
            pass
        
        # Toggle buttons
        self.add_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.name_input.setFocus()
    
    def cancel_edit(self):
        """Cancel editing and reset form."""
        self._editing_id = None
        self.name_input.clear()
        self.notes_input.clear()
        self.start_input.setDate(QDate.currentDate())
        self.end_input.setDate(QDate.currentDate().addDays(30))
        self.category_input.setCurrentIndex(0)
        
        self.add_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
    
    def save_edit(self):
        """Save changes to existing subscription."""
        if not self._editing_id:
            return
        
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required!")
            return
        
        sd = self.start_input.date().toPython()
        ed = self.end_input.date().toPython()
        
        if ed < sd:
            QMessageBox.warning(self, "Validation", "End date must be after start date!")
            return
        
        category = self.category_input.currentText().strip() or "Other"
        notes = self.notes_input.text().strip()
        
        try:
            self.db.update(self._editing_id, name, sd.isoformat(), ed.isoformat(), category, notes)
            self.cancel_edit()
            self._load_table()
            self._update_status("✅ Subscription updated successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update: {e}")
    
    def add_subscription(self):
        """Add a new subscription."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required!")
            return
        
        sd = self.start_input.date().toPython()
        ed = self.end_input.date().toPython()
        
        if ed < sd:
            QMessageBox.warning(self, "Validation", "End date must be after start date!")
            return
        
        category = self.category_input.currentText().strip() or "Other"
        notes = self.notes_input.text().strip()
        
        try:
            self.db.add(name, sd.isoformat(), ed.isoformat(), category, notes)
            self.name_input.clear()
            self.notes_input.clear()
            self.start_input.setDate(QDate.currentDate())
            self.end_input.setDate(QDate.currentDate().addDays(30))
            self._load_table()
            self._update_status("✅ Subscription added successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add: {e}")
    
    def _load_table(self, search_query: str = None):
        """Load subscriptions into the table."""
        if search_query and search_query.strip():
            rows = self.db.search(search_query.strip())
        else:
            rows = self.db.list_all()
        
        self.table.setRowCount(0)
        today = date.today()
        warn_days = self.config.get("warn_days", 7)
        
        for r in rows:
            sid, name, sd_raw, ed_raw, category, notes = r
            
            try:
                ed = datetime.fromisoformat(ed_raw).date()
            except Exception:
                ed = today
            
            days_remaining = (ed - today).days
            
            if days_remaining < 0:
                days_str = f"Expired ({-days_remaining}d ago)"
                row_color = QColor(255, 200, 200)  # Light red
            elif days_remaining <= warn_days:
                days_str = f"⚠️ {days_remaining} days"
                row_color = QColor(255, 255, 200)  # Light yellow
            else:
                days_str = f"{days_remaining} days"
                row_color = QColor(200, 255, 200)  # Light green
            
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            items = [
                QTableWidgetItem(str(sid)),
                QTableWidgetItem(name),
                QTableWidgetItem(sd_raw),
                QTableWidgetItem(ed_raw),
                QTableWidgetItem(days_str),
                QTableWidgetItem(category or "Other"),
            ]
            
            for col, item in enumerate(items):
                item.setBackground(row_color)
                self.table.setItem(row_idx, col, item)
        
        # Hide ID column
        self.table.setColumnHidden(0, True)
        
        # Update status
        self._update_status(f"📊 {len(rows)} subscription(s)")
    
    def _update_status(self, text: str):
        """Update the status label."""
        self.status_label.setText(text)
    
    def delete_selected(self):
        """Delete selected subscriptions."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Delete", "No subscription selected!")
            return
        
        ids = [int(self.table.item(r.row(), 0).text()) for r in selected]
        
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(ids)} subscription(s)? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            for sid in ids:
                self.db.delete(sid)
            self._load_table()
            self._update_status(f"🗑️ Deleted {len(ids)} subscription(s)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete: {e}")
    
    def import_excel(self):
        """Import subscriptions from Excel or CSV."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Excel or CSV",
            str(Path.home()),
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*.*)"
        )
        
        if not path:
            return
        
        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            
            count = self.db.import_from_dataframe(df)
            QMessageBox.information(self, "Import", f"✅ Successfully imported {count} subscription(s)!")
            self._load_table()
        except Exception as e:
            log.error(f"Import failed: {e}")
            QMessageBox.critical(self, "Import Error", f"Failed to import:\n{e}")
    
    def export_excel(self):
        """Export subscriptions to Excel or CSV."""
        default_path = Path.home() / "subscriptions.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export to Excel",
            str(default_path),
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        
        if not path:
            return
        
        df = self.db.export_to_dataframe()
        
        try:
            if path.lower().endswith(".csv"):
                df.to_csv(path, index=False)
            else:
                df.to_excel(path, index=False)
            
            QMessageBox.information(self, "Export", f"✅ Exported to:\n{path}")
            log.info(f"Exported to {path}")
        except Exception as e:
            log.error(f"Export failed: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{e}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Application entry point."""
    # Windows: Set app ID for taskbar grouping
    try:
        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "com.bytefroster.subscriptionmanager.v2"
            )
    except Exception:
        pass
    
    app = QApplication(sys.argv)
    app.setApplicationName("Subscription Manager")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("ByteFroster")
    
    # Set application icon
    base_folder = Path(__file__).resolve().parent
    icon_path = base_folder / "bytefroster.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show main window
    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    
    config = ConfigManager()
    window.resize(config.get("window_width", 1200), config.get("window_height", 700))
    window.show()
    
    log.info("Main window displayed")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
