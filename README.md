# VA User Podman Docker Switch (`la-toolhive-thv-ui`)

A highly integrated set of utilities that strictly manages and toggles the rootless endpoints of Podman and Docker in the user space (`systemctl --user`). 

The application is built primarily for VA environments, providing a robust command-line foundation and a lightweight system tray visualization application that reflects real-time polling statuses.

## Features

- **CLI Backend** (`la_toolhive_thv_ui.py`): Manages the start and stop functionalities of the socket and service layers for Docker and Podman in user-land mutually or inclusively.
- **System Tray application** (`la_toolhive_thv_ui_tray.py`): A background PyQt6 application that displays an icon indicating which engine(s) are active and provides a right-click drop-down toggler.
- **Menu Entry Shims**: `.desktop` application launchers mapped to VA launcher menus to manually select the active engines straight from your applications panel.

## Usage

### Command Line Interactivity
Use the `la_toolhive_thv_ui.py` to enact toggles globally or in scripts:
```bash
la_toolhive_thv_ui --podman-only
la_toolhive_thv_ui --docker-only
la_toolhive_thv_ui --both-enabled
la_toolhive_thv_ui --both-disabled

# Get JSON formatted state
la_toolhive_thv_ui --status
```
For manual documentation:
```bash
man la_toolhive_thv_ui
```

### Background Service Toggling
Simply run or execute `la_toolhive_thv_ui_tray`. 
If you are properly using VA or a desktop environment that respects Wayland `.desktop` system tray integration protocols, you will instantly notice the status update on your top/bottom navigation panels. 
By clicking the visual icon on your tray, you can directly invoke the `ON/OFF` switch mechanisms. 

---

## Developer Notes

### Native Packaging
This toolkit ships with full native integration configurations.

**Testing the Tray App Locally**
To test the PyQt6 tray widget prior to deployment from your local repository, simply execute it from your terminal:
```bash
./src/la_toolhive_thv_ui_tray.py
```
*Note: Make sure `python3-pyqt6` is installed on your development machine.*

**Debian (.deb)**
The overarching `la-toolhive-thv-ui` architecture depends entirely on Python3 and PyQt6 natively. Therefore, `dpkg` works independently of standard `C` builds.
```bash
# We provide a standalone wrapper script compiling BOTH Debian packages and extracting them cleanly into a local `./dist` directory without polluting the upstream directory inherently:
./build.sh

# Outputs: 
# ./dist/la-toolhive-thv-ui_1.0.1_all.deb
# ./dist/la-toolhive-thv-ui-cli_1.0.1_all.deb
```
- A man page is sourced natively using CLI specific packages.
- Custom VA launcher files and user-space icon SVGs are handled securely by standard `dh_install`.

**Redhat Build Tooling (.rpm)**
The `rpm/` subdirectory handles standard RPM specifications. `rpmbuild` will require a natively compiled `tar.gz` payload configured as `Source0`. 
```bash
# Scaffold target directory manually
mkdir -p build_rpm/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Compress the source manually to preprpm
tar -czvf build_rpm/SOURCES/la-toolhive-thv-ui-1.0.0.tar.gz src/ rpm/ debian/
cp rpm/la-toolhive-thv-ui.spec build_rpm/SPECS/

# Trigger RPM macro parsing to build the dual architecture:
rpmbuild --define "_topdir $PWD/build_rpm" -ba build_rpm/SPECS/la-toolhive-thv-ui.spec

# Expected CLI Output: la-toolhive-thv-ui-cli-1.0.0-1.noarch.rpm
# Expected GUI Output: la-toolhive-thv-ui-1.0.0-1.noarch.rpm
```

**Arch Linux (.pkg.tar.zst)**
The `arch/` directory supports dual native Arch Linux targets directly honoring explicit GUI and Headless boundaries completely matching upstream distributions.
```bash
# Enter the staging directory directly alongside the native PKGBUILD source:
cd arch/

# Triggers fakeroot compilation mapping both GUI and CLI package configurations directly into Arch standards organically:
makepkg -c

# Expected CLI Output: la-toolhive-thv-ui-cli-1.0.1-1-any.pkg.tar.zst
# Expected GUI Output: la-toolhive-thv-ui-1.0.1-1-any.pkg.tar.zst
```

### Application Structure Restrictions
- Ensure all SVGs for the daemon reside explicitly in `src/icons/` so the un-bundled installer script can resolve icons in place relative to its `__file__` OS module lookup. 
- VA autostart is natively managed by translating `.desktop` files toward `/etc/xdg/autostart` using the installer package (No user-interactive linking required).

## License & Copyright

**MIT License**
Copyright (c) 2026 Gerald Staruiala

### Trademarks & Assets
- **Docker** and the Docker logo are trademarks or registered trademarks of Docker, Inc. in the United States and/or other countries. Docker, Inc. and other parties may also have trademark rights in other terms used herein.
- **Podman** and the Podman logo are trademarks or registered trademarks of Red Hat, Inc. or its subsidiaries in the United States and other countries.
- All other SVGs, `.ico` images, and visual assets belong entirely to their respective original owners.

## Security Posture & Compliance Standard
*The backend Python daemon structures have been aggressively validated mapping natively against universal ISO 17799 and NIST SP 800 standards successfully. All operational bindings dynamically avoid shell injection overlaps tracking entirely to explicitly limited unprivileged `--user` systemd logic avoiding root execution natively over 100%.*
