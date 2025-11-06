"""
This is made and maintained by Tijul Kabir Toha (Visit tijulkabir.me for more projects).

This is intentionally a single-file starter app. You can extend it (authentication, notifications, recurring logic) as needed.
"""

import sys
import sqlite3
from datetime import date, datetime
from pathlib import Path
import pandas as pd

from PySide6.QtCore import QDate
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QDateEdit, QMessageBox, QFileDialog, QHeaderView, QAbstractItemView
)



DB_FILE = "subscriptions.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_date TEXT NOT NULL, -- ISO format yyyy-mm-dd
    end_date TEXT NOT NULL,
    notes TEXT
);
"""


def init_db(path=DB_FILE):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()
    return conn


class SubscriptionDB:
    def __init__(self, path=DB_FILE):
        self.path = path
        self.conn = init_db(path)

    def add(self, name, start_iso, end_iso, notes=""):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO subscriptions (name, start_date, end_date, notes) VALUES (?, ?, ?, ?)",
                    (name, start_iso, end_iso, notes))
        self.conn.commit()
        return cur.lastrowid

    def update(self, sid, name, start_iso, end_iso, notes=""):
        cur = self.conn.cursor()
        cur.execute("UPDATE subscriptions SET name=?, start_date=?, end_date=?, notes=? WHERE id=?",
                    (name, start_iso, end_iso, notes, sid))
        self.conn.commit()

    def delete(self, sid):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM subscriptions WHERE id=?", (sid,))
        self.conn.commit()

    def list_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, start_date, end_date, notes FROM subscriptions ORDER BY end_date")
        return cur.fetchall()

    def import_from_dataframe(self, df):
        # Expect columns: Name, Start Date, End Date, Notes (optional)
        for _, row in df.iterrows():
            name = str(row.get('Name') or row.get('name') or '')
            sd = row.get('Start Date') or row.get('start_date')
            ed = row.get('End Date') or row.get('end_date')
            notes = row.get('Notes') or ''
            try:
                sd_iso = pd.to_datetime(sd).date().isoformat()
                ed_iso = pd.to_datetime(ed).date().isoformat()
            except Exception:
                continue
            self.add(name, sd_iso, ed_iso, str(notes))

    def export_to_dataframe(self):
        rows = self.list_all()
        df = pd.DataFrame(rows, columns=['ID', 'Name', 'Start Date', 'End Date', 'Notes'])
        return df


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subscription Manager — ByteFroster Edition")
        self.db = SubscriptionDB()
        self._editing_id = None
        self._setup_ui()
        self._load_table()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)

        # Form row
        form_h = QHBoxLayout()

        self.name_in = QLineEdit(); self.name_in.setPlaceholderText('Service name (e.g. Netflix)')
        self.start_in = QDateEdit(); self.start_in.setCalendarPopup(True); self.start_in.setDate(QDate.currentDate())
        self.end_in = QDateEdit(); self.end_in.setCalendarPopup(True); self.end_in.setDate(QDate.currentDate().addDays(30))
        self.notes_in = QLineEdit(); self.notes_in.setPlaceholderText('Notes (optional)')

        form_h.addWidget(QLabel('Name:'))
        form_h.addWidget(self.name_in)
        form_h.addWidget(QLabel('Start:'))
        form_h.addWidget(self.start_in)
        form_h.addWidget(QLabel('End:'))
        form_h.addWidget(self.end_in)
        form_h.addWidget(QLabel('Notes:'))
        form_h.addWidget(self.notes_in)

        v.addLayout(form_h)

        # Buttons
        btn_h = QHBoxLayout()
        self.add_btn = QPushButton('Add')
        self.add_btn.clicked.connect(self.add_subscription)
        self.update_btn = QPushButton('Save')
        self.update_btn.clicked.connect(self.save_edit)
        self.update_btn.setEnabled(False)
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.cancel_btn.setEnabled(False)

        btn_h.addWidget(self.add_btn)
        btn_h.addWidget(self.update_btn)
        btn_h.addWidget(self.cancel_btn)

        btn_h.addStretch()

        self.import_btn = QPushButton('Import Excel')
        self.import_btn.clicked.connect(self.import_excel)
        self.export_btn = QPushButton('Export Excel')
        self.export_btn.clicked.connect(self.export_excel)

        btn_h.addWidget(self.import_btn)
        btn_h.addWidget(self.export_btn)

        v.addLayout(btn_h)

        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Start Date', 'End Date', 'Days Remaining', 'Notes'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Use enum from QAbstractItemView for edit triggers
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_cell_double)

        v.addWidget(self.table)

        # Lower buttons
        lower_h = QHBoxLayout()
        self.delete_btn = QPushButton('Delete Selected')
        self.delete_btn.clicked.connect(self.delete_selected)
        lower_h.addWidget(self.delete_btn)

        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.clicked.connect(self._load_table)
        lower_h.addWidget(self.refresh_btn)

        lower_h.addStretch()
        v.addLayout(lower_h)

    def _on_cell_double(self, row, col):
        # open edit mode for that row
        item = self.table.item(row, 0)  # ID column
        if not item:
            return
        sid = int(item.text())
        name = self.table.item(row, 1).text()
        sd = self.table.item(row, 2).text()
        ed = self.table.item(row, 3).text()
        notes = self.table.item(row, 5).text()
        # Fill form
        self._editing_id = sid
        self.name_in.setText(name)
        try:
            sd_dt = datetime.fromisoformat(sd).date()
            ed_dt = datetime.fromisoformat(ed).date()
            self.start_in.setDate(QDate(sd_dt.year, sd_dt.month, sd_dt.day))
            self.end_in.setDate(QDate(ed_dt.year, ed_dt.month, ed_dt.day))
        except Exception:
            pass
        self.notes_in.setText(notes)
        # toggle buttons
        self.add_btn.setEnabled(False)
        self.update_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

    def cancel_edit(self):
        self._editing_id = None
        self.name_in.clear(); self.notes_in.clear()
        self.start_in.setDate(QDate.currentDate()); self.end_in.setDate(QDate.currentDate().addDays(30))
        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

    def save_edit(self):
        if not self._editing_id:
            return
        name = self.name_in.text().strip()
        sd = self.start_in.date().toPython()
        ed = self.end_in.date().toPython()
        notes = self.notes_in.text().strip()
        if not name:
            QMessageBox.warning(self, 'Validation', 'Name is required')
            return
        if ed < sd:
            QMessageBox.warning(self, 'Validation', 'End date must be after start date')
            return
        self.db.update(self._editing_id, name, sd.isoformat(), ed.isoformat(), notes)
        self.cancel_edit()
        self._load_table()

    def add_subscription(self):
        name = self.name_in.text().strip()
        sd = self.start_in.date().toPython()
        ed = self.end_in.date().toPython()
        notes = self.notes_in.text().strip()
        if not name:
            QMessageBox.warning(self, 'Validation', 'Name is required')
            return
        if ed < sd:
            QMessageBox.warning(self, 'Validation', 'End date must be after start date')
            return
        self.db.add(name, sd.isoformat(), ed.isoformat(), notes)
        self.name_in.clear(); self.notes_in.clear()
        self.start_in.setDate(QDate.currentDate()); self.end_in.setDate(QDate.currentDate().addDays(30))
        self._load_table()

    def _load_table(self):
        rows = self.db.list_all()
        self.table.setRowCount(0)
        today_d = date.today()
        for r in rows:
            sid, name, sd_raw, ed_raw, notes = r
            try:
                sd = datetime.fromisoformat(sd_raw).date()
                ed = datetime.fromisoformat(ed_raw).date()
            except Exception:
                sd = ed = today_d
            days_remaining = (ed - today_d).days
            if days_remaining < 0:
                days_str = f"Expired ({-days_remaining} days ago)"
            else:
                days_str = f"{days_remaining} days"
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(sid)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(sd.isoformat()))
            self.table.setItem(row_idx, 3, QTableWidgetItem(ed.isoformat()))
            self.table.setItem(row_idx, 4, QTableWidgetItem(days_str))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(notes)))
        # show ID column (change to True to hide it)
        self.table.setColumnHidden(0, False)
        self.table.resizeColumnsToContents()

    def delete_selected(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.information(self, 'Delete', 'No row selected')
            return
        ids = [int(self.table.item(r.row(), 0).text()) for r in sel]
        ok = QMessageBox.question(self, 'Confirm delete', f'Delete {len(ids)} subscription(s)?')
        if ok != QMessageBox.StandardButton.Yes:
            return
        for sid in ids:
            self.db.delete(sid)
        self._load_table()

    def import_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Import Excel or CSV', str(Path.home()), 'Excel Files (*.xlsx *.xls);;CSV Files (*.csv)')
        if not path:
            return
        try:
            if path.lower().endswith('.csv'):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            self.db.import_from_dataframe(df)
            QMessageBox.information(self, 'Import', 'Import complete')
            self._load_table()
        except Exception as e:
            QMessageBox.critical(self, 'Import error', str(e))

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Export to Excel', str(Path.home() / 'subscriptions.xlsx'), 'Excel Files (*.xlsx);;CSV Files (*.csv)')
        if not path:
            return
        df = self.db.export_to_dataframe()
        try:
            if path.lower().endswith('.csv'):
                df.to_csv(path, index=False)
            else:
                df.to_excel(path, index=False)
            QMessageBox.information(self, 'Export', f'Exported to {path}')
        except Exception as e:
            QMessageBox.critical(self, 'Export error', str(e))


if __name__ == '__main__':
    # Ensure Windows treats this process as our app (helps taskbar icon)
    try:
        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"com.bytefroster.subscriptionmanager")
    except Exception:
        pass

    app = QApplication(sys.argv)

    base_folder = Path(__file__).resolve().parent
    icon_path = base_folder / "bytefroster.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    mw = MainWindow()
    if icon_path.exists():
        mw.setWindowIcon(QIcon(str(icon_path)))

    mw.resize(1100, 600)
    mw.show()
    sys.exit(app.exec())
