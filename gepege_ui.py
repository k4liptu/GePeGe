# SPDX-License-Identifier: GPL-3.0-only
"""Estilos, iconos y componentes compartidos de la interfaz de GePeGe."""
from pathlib import Path
from PySide6.QtCore import QByteArray, QObject, QRunnable, Signal, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPushButton, QStyle,
                               QTextEdit, QToolButton, QWidget)

STYLE = '''
QWidget { font-family: sans-serif; font-size: 14px; color: #182536; }
QMainWindow, QScrollArea, QScrollArea > QWidget > QWidget { background: #edf2f7; }
QScrollArea { border: 0; }
QGroupBox { background: #f8fafc; border: 1px solid #9eafc1; border-radius: 9px; margin-top: 16px; padding: 14px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; color: #182536; }
QTextEdit, QLineEdit, QComboBox, QListWidget { color: #172536; background: #ffffff; border: 1px solid #91a3b5; border-radius: 5px; padding: 7px; selection-background-color: #2854a1; selection-color: #ffffff; }
QTextEdit:read-only { background: #f1f5f9; color: #172536; }
QTextEdit:focus, QLineEdit:focus, QComboBox:focus, QListWidget:focus { border: 2px solid #2854a1; }
QComboBox QAbstractItemView { color: #172536; background: #ffffff; selection-background-color: #2854a1; selection-color: #ffffff; }
QComboBox:disabled, QLineEdit:disabled { color: #526274; background: #dce4ec; }
QPushButton { color: #173457; background: #d5e2f1; border: 1px solid #91a9c4; border-radius: 5px; padding: 9px 14px; }
QPushButton:hover { background: #c1d5eb; }
QPushButton:pressed { background: #acc5e1; }
QPushButton:focus { border: 2px solid #2854a1; }
QPushButton#primary { color: #ffffff; background: #254e9c; border: 1px solid #254e9c; font-weight: bold; }
QPushButton#primary:hover { background: #193b7c; }
QPushButton:disabled { color: #526274; background: #dce4ec; }
QTabWidget::pane { border: 0; }
QTabBar::tab { color: #263b54; background: #dce6f1; border: 1px solid #afbdcb; padding: 10px 18px; }
QTabBar::tab:selected { color: #183759; background: #b8d2ec; border-color: #6e91b5; font-weight: bold; }
QTabBar::tab:!selected:hover { background: #cad9e9; }
QWidget#keyRow { background: #ffffff; border-radius: 4px; }
QWidget#keyRow[selected="true"] { background: #2854a1; border: 1px solid #2854a1; }
QWidget#keyRow QLabel { background: transparent; color: #172536; }
QWidget#keyRow[selected="true"] QLabel { color: #ffffff; }
QToolButton#keyAction { background: #f5f9ff; border: 1px solid #829bb8; border-radius: 5px; padding: 5px; }
QToolButton#keyAction:hover { background: #bdd4ef; }
QToolButton#deleteKey { background: #fff0ef; border: 1px solid #b52929; border-radius: 5px; padding: 5px; }
QToolButton#deleteKey:hover { background: #ffd3cf; }
QToolButton#lessonHeader { background: #dce6f1; border: 1px solid #afbdcb; border-radius: 5px; padding: 10px; text-align: left; font-weight: bold; }
QToolButton#lessonHeader:hover { background: #cad9e9; }
'''

APP_ICON = Path(__file__).resolve().parent / 'packaging' / 'GePeGe.svg'

TAB_SYMBOLS = (
    '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><path d="M12 14v3"/>',
    '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 7-2.6"/><path d="M12 14v3"/>',
    '<circle cx="8" cy="9" r="4"/><path d="M11 12l8 8m-3-3 2-2m-5-1 2-2"/>',
    '<circle cx="8" cy="9" r="4"/><path d="M11 12l7 7m-3-3 2-2M18 3v6m-3-3h6"/>',
    '<path d="M9 3 6 21M17 3l-3 18M4 9h17M3 15h17"/>',
    '<path d="M12 6c-2-2-5-3-9-2v14c4-1 7 0 9 2 2-2 5-3 9-2V4c-4-1-7 0-9 2zm0 0v14"/>'
)

def tab_icon(index, selected):
    color = '#183759' if selected else '#243f64'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{TAB_SYMBOLS[index]}</svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')))
    pixmap = QPixmap(48, 48); pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap); renderer.render(painter); painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)

def delete_icon():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#b21d27" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v5M14 11v5"/></svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')))
    pixmap = QPixmap(48, 48); pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap); renderer.render(painter); painter.end(); pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)

def export_icon():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#173457" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m-4-4 4 4 4-4M4 16v4h16v-4"/></svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')))
    pixmap = QPixmap(48, 48); pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap); renderer.render(painter); painter.end(); pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)

class KeyRow(QWidget):
    def __init__(self, owner, item, text):
        super().__init__(); self.owner = owner; self.item = item; self.setObjectName('keyRow')
        row = QHBoxLayout(self); row.setContentsMargins(8, 5, 8, 5)
        row.addWidget(label(text), 1)
        self.info = QToolButton(); self.info.setObjectName('keyAction'); self.info.setIcon(owner.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)); self.info.setToolTip('Información de la clave'); self.info.setAccessibleName('Información de la clave'); self.info.clicked.connect(self.show_info); row.addWidget(self.info)
        self.export = QToolButton(); self.export.setObjectName('keyAction'); self.export.setIcon(export_icon()); self.export.setToolTip('Exportar clave pública'); self.export.setAccessibleName('Exportar clave pública'); self.export.clicked.connect(self.export_key); row.addWidget(self.export)
        self.delete = QToolButton(); self.delete.setObjectName('deleteKey'); self.delete.setIcon(delete_icon()); self.delete.setToolTip('Borrar esta clave'); self.delete.setAccessibleName('Borrar esta clave'); self.delete.clicked.connect(self.delete_key); row.addWidget(self.delete)
        self.set_selected(False)
    def mousePressEvent(self, event):
        self.owner.key_list.setCurrentItem(self.item)
        super().mousePressEvent(event)
    def set_selected(self, selected):
        self.setProperty('selected', selected); self.info.setVisible(selected); self.export.setVisible(selected); self.delete.setVisible(selected)
        self.style().unpolish(self); self.style().polish(self); self.update()
    def show_info(self):
        self.owner.key_list.setCurrentItem(self.item); self.owner.key_info()
    def export_key(self):
        self.owner.key_list.setCurrentItem(self.item); self.owner.export_selected_key()
    def delete_key(self):
        self.owner.key_list.setCurrentItem(self.item); self.owner.delete_key()

class Signals(QObject):
    done = Signal(object)

class Task(QRunnable):
    def __init__(self, fn):
        super().__init__(); self.fn = fn; self.signals = Signals()
    def run(self):
        try: result = self.fn()
        except Exception as exc: result = {'ok': False, 'detail': str(exc)}
        self.signals.done.emit(result)

def label(text):
    w = QLabel(text); w.setWordWrap(True); return w

def button(text, callback, primary=False):
    b = QPushButton(text); b.clicked.connect(callback)
    if primary: b.setObjectName('primary')
    return b

def textedit(placeholder, height=110):
    w = QTextEdit(); w.setPlaceholderText(placeholder); w.setMinimumHeight(height); return w

def password():
    w = QLineEdit(); w.setEchoMode(QLineEdit.EchoMode.Password); return w
