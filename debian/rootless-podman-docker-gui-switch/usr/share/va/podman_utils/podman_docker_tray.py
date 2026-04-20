#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer

# Import our custom CLI logic
import la_toolhive_thv_ui as cli

class PodmanDockerTray:
    def __init__(self, app):
        self.app = app
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Determine paths to icons
        script_dir = os.path.dirname(os.path.realpath(__file__))
        local_icon_dir = os.path.join(script_dir, "icons")
        system_icon_dir = "/usr/share/va/podman_utils/icons"
        
        icon_dir = local_icon_dir if os.path.isdir(local_icon_dir) else system_icon_dir
        
        self.icon_paths = {
            "none": os.path.join(icon_dir, "none-active.svg"),
            "podman": os.path.join(icon_dir, "podman-active.svg"),
            "docker": os.path.join(icon_dir, "docker-active.ico"),
            "both": os.path.join(icon_dir, "both_active.ico"),
        }

        self.menu = QMenu()
        
        self.podman_action = QAction("Toggle Podman")
        self.podman_action.triggered.connect(self.toggle_podman)
        self.menu.addAction(self.podman_action)
        
        self.docker_action = QAction("Toggle Docker")
        self.docker_action.triggered.connect(self.toggle_docker)
        self.menu.addAction(self.docker_action)
        
        self.menu.addSeparator()
        
        self.all_on_action = QAction("All On")
        self.all_on_action.triggered.connect(self.all_on)
        self.menu.addAction(self.all_on_action)
        
        self.all_off_action = QAction("All Off")
        self.all_off_action.triggered.connect(self.all_off)
        self.menu.addAction(self.all_off_action)

        self.menu.addSeparator()
        
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)

        self.about_action = QAction("About")
        self.about_action.triggered.connect(self.show_about)
        self.menu.addAction(self.about_action)
        
        self.tray_icon.setContextMenu(self.menu)
        
        self.podman_active = False
        self.docker_active = False
        
        # Init state and icons
        self.update_state()
        self.tray_icon.show()
        
        # Poll state every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_state)
        self.timer.start(5000)

    def update_state(self):
        status = cli.get_status()
        self.podman_active = status["podman"]
        self.docker_active = status["docker"]
        
        self.podman_action.setText(f"Podman: {'ON' if self.podman_active else 'OFF'}")
        self.docker_action.setText(f"Docker: {'ON' if self.docker_active else 'OFF'}")
        
        if self.podman_active and self.docker_active:
            state = "both"
            tooltip = "Podman: ON | Docker: ON"
        elif self.podman_active:
            state = "podman"
            tooltip = "Podman: ON | Docker: OFF"
        elif self.docker_active:
            state = "docker"
            tooltip = "Podman: OFF | Docker: ON"
        else:
            state = "none"
            tooltip = "Podman: OFF | Docker: OFF"
            
        icon = QIcon(self.icon_paths[state])
        if icon.isNull():
            # Fallback to standard theme icons if our SVGs fail to load or are missing
            if state == "both":
                icon = QIcon.fromTheme("network-server")
            elif state == "podman":
                icon = QIcon.fromTheme("application-x-executable")
            elif state == "docker":
                icon = QIcon.fromTheme("application-x-archive")
            else:
                icon = QIcon.fromTheme("application-x-zerosize")
                
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(tooltip)

    def toggle_podman(self):
        if self.podman_active:
            cli.disable_podman()
        else:
            cli.enable_podman()
        self.update_state()
        
    def toggle_docker(self):
        if self.docker_active:
            cli.disable_docker()
        else:
            cli.enable_docker()
        self.update_state()

    def all_on(self):
        cli.action_both_enabled()
        self.update_state()

    def all_off(self):
        cli.action_both_disabled()
        self.update_state()

    def show_about(self):
        QMessageBox.information(
            None,
            "About VA Tray",
            "This utility lets you gracefully toggle your user-land Podman and Docker socket endpoints.\n\n"
            "- Toggle Podman: Switches your Podman socket ON/OFF\n"
            "- Toggle Docker: Switches your Docker socket ON/OFF\n"
            "- All On: Turns both socket instances ON simultaneously\n"
            "- All Off: Turns both socket instances OFF simultaneously\n\n"
            "This ensures you do not waste system resources or face port conflicts."
        )

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Needs a real system tray icon or app indicator support in the desktop environment
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("System tray is not available on this desktop environment.")
        sys.exit(1)
        
    tray = PodmanDockerTray(app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
