#!/usr/bin/env python3
"""la-toolhive-thv-ui — System tray entry point.

Provides a persistent system tray icon with desktop notification support.
Works natively on Xfce and KDE via QSystemTrayIcon (StatusNotifierItem).

GNOME note: GNOME removed the legacy system tray. To display this tray icon
on GNOME the user must install the 'AppIndicator and KStatusNotifierItem
Support' GNOME Shell extension (package: gnome-shell-extension-appindicator).
"""
# TODO: Replace la-toolhive-thv-ui with your application name throughout this file

import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer

la-toolhive-thv-ui = "la-toolhive-thv-ui"
ICON_ACTIVE = f"/usr/share/{la-toolhive-thv-ui}/icons/tray-active.svg"
ICON_INACTIVE = f"/usr/share/{la-toolhive-thv-ui}/icons/tray-inactive.svg"


class TrayApp(QSystemTrayIcon):
    def __init__(self, app: QApplication):
        super().__init__(QIcon(ICON_ACTIVE), parent=app)
        self._app = app
        self._build_menu()
        self.setToolTip(la-toolhive-thv-ui)
        self.activated.connect(self._on_activated)

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _build_menu(self):
        menu = QMenu()

        # TODO: Add application-specific actions here
        action_open = QAction("Open", menu)
        action_open.triggered.connect(self._on_open)
        menu.addAction(action_open)

        menu.addSeparator()

        action_quit = QAction("Quit", menu)
        action_quit.triggered.connect(self._app.quit)
        menu.addAction(action_quit)

        self.setContextMenu(menu)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def notify(self, title: str, message: str,
               icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
               duration_ms: int = 4000):
        """Send a desktop notification bubble via the system tray."""
        self.showMessage(title, message, icon, duration_ms)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left-click: toggle main window or perform primary action
            self._on_open()

    def _on_open(self):
        # TODO: Import and show/raise the MainWindow from app.py, or
        # perform the primary action for a left-click on the tray icon.
        self.notify(la-toolhive-thv-ui, "Application opened.")


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(la-toolhive-thv-ui)
    app.setQuitOnLastWindowClosed(False)    # Keep alive when all windows close

    if not QSystemTrayIcon.isSystemTrayAvailable():
        print(
            f"{la-toolhive-thv-ui}: No system tray available.\n"
            "On GNOME, install the 'AppIndicator and KStatusNotifierItem Support' extension.",
            file=sys.stderr,
        )
        sys.exit(1)

    tray = TrayApp(app)
    tray.show()

    # Optional: send a startup notification
    # QTimer.singleShot(500, lambda: tray.notify(la-toolhive-thv-ui, "Running in the system tray."))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
