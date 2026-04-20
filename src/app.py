#!/usr/bin/env python3
"""la-toolhive-thv-ui — Main application entry point.

Cross-desktop GUI application supporting GNOME, Xfce, and KDE.
Replace la-toolhive-thv-ui and all TODO markers before use.
"""
# TODO: Replace la-toolhive-thv-ui with your application name throughout this file
# TODO: Replace com.vai-int.la-toolhive-thv-ui with your reverse-domain app ID (e.g. com.example.myapp)

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

la-toolhive-thv-ui = "la-toolhive-thv-ui"
com.vai-int.la-toolhive-thv-ui = "com.vai-int.la-toolhive-thv-ui"
APP_VERSION = "1.0.0"
ICON_PATH = f"/usr/share/icons/hicolor/scalable/apps/{la-toolhive-thv-ui}.svg"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(la-toolhive-thv-ui)
        self.setMinimumSize(400, 300)

        # TODO: Replace placeholder UI with your application's interface
        central = QWidget()
        layout = QVBoxLayout(central)
        label = QLabel(f"{la-toolhive-thv-ui} is running.", central)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setCentralWidget(central)

    def closeEvent(self, event):
        # TODO: Decide whether closing should quit the app or minimise to tray.
        # To minimise to tray instead of quitting:
        #   event.ignore()
        #   self.hide()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(la-toolhive-thv-ui)
    app.setApplicationVersion(APP_VERSION)
    app.setDesktopFileName(com.vai-int.la-toolhive-thv-ui)          # Links to .desktop file for GNOME/KDE
    app.setWindowIcon(QIcon(ICON_PATH))
    app.setQuitOnLastWindowClosed(True)     # Set False if using a system tray

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
