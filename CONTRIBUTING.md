# Contributing

## Project layout

```
.
├── src/
│   ├── app.py                      # Main GUI application (PyQt6)
│   ├── tray.py                     # System tray + desktop notifications
│   ├── app.1                       # Man page (troff format)
│   ├── desktop/
│   │   ├── app.desktop             # XDG application launcher (menus)
│   │   └── app-autostart.desktop   # XDG autostart entry (tray on login)
│   ├── systemd/
│   │   └── app.service             # User systemd service unit
│   ├── metainfo/
│   │   └── app.metainfo.xml        # AppStream metadata (software centres)
│   └── icons/
│       ├── la-toolhive-thv-ui.svg            # Main app icon → hicolor theme
│       ├── tray-active.svg         # Tray icon, active state → app data dir
│       └── tray-inactive.svg       # Tray icon, inactive state
├── tests/                          # Test suite
├── debian/                         # Debhelper packaging metadata (apt)
│   ├── control                     # Source + binary package declarations
│   ├── rules                       # Build rules (icons, systemd, metainfo)
│   ├── changelog                   # Debian-format version history
│   ├── copyright                   # DEP-5 copyright declaration (required)
│   ├── watch                       # Upstream release tracking (uscan)
│   ├── *.install                   # File→destination install mappings
│   └── *.links                     # /usr/bin symlink declarations
├── build_cli_deb/
│   └── DEBIAN/control              # Standalone CLI .deb control file
├── rpm/
│   └── *.spec                      # RPM spec (dnf/yum)
├── arch/
│   └── PKGBUILD                    # Arch Linux package build (pacman)
├── Makefile                        # make deb / rpm / arch / clean
├── VERSION                         # Single source of truth for version
└── dist/                           # Build output — gitignored
```

## Desktop environment support

| Feature | GNOME | Xfce | KDE |
|---|---|---|---|
| Application launcher | ✓ | ✓ | ✓ |
| System tray icon | ✓ (needs AppIndicator extension) | ✓ | ✓ |
| Desktop notifications | ✓ | ✓ | ✓ |
| XDG autostart | ✓ | ✓ | ✓ |
| User systemd service | ✓ | ✓ | ✓ |

**GNOME tray note:** GNOME removed the legacy system tray. The `QSystemTrayIcon`
in `tray.py` uses the StatusNotifierItem D-Bus protocol. GNOME users need the
[AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/)
shell extension (`gnome-shell-extension-appindicator` on Debian/Ubuntu).

## Autostart mechanisms

Two complementary mechanisms are provided — include both for maximum compatibility:

| Mechanism | File installed | How to control |
|---|---|---|
| **XDG autostart** | `/etc/xdg/autostart/la-toolhive-thv-ui-tray.desktop` | DE session settings, or copy to `~/.config/autostart/` with `Hidden=true` to disable |
| **systemd user service** | `/usr/lib/systemd/user/la-toolhive-thv-ui.service` | `systemctl --user enable --now la-toolhive-thv-ui.service` |

The systemd service is installed but **not auto-enabled** by the package.
Users opt in with `systemctl --user enable --now la-toolhive-thv-ui.service`.
The XDG autostart entry IS active for all users by default (place in
`/etc/xdg/autostart/`); disable per-user via the DE's session settings.

## Setting up a new project from this template

1. **Set the version** in `VERSION`.

2. **Rename package files** in `debian/`:
   ```bash
   git mv debian/la-toolhive-thv-ui.install debian/la-toolhive-thv-ui.install
   git mv debian/la-toolhive-thv-ui.links   debian/la-toolhive-thv-ui.links
   ```
   Also rename the RPM spec:
   ```bash
   git mv rpm/la-toolhive-thv-ui.spec rpm/la-toolhive-thv-ui.spec
   ```

3. **Replace all placeholders** — search for `APP_` across the tree:
   ```bash
   grep -r "APP_" --include="*.py" --include="*.desktop" \
       --include="*.service" --include="*.xml" --include="*.spec" \
       --include="PKGBUILD" --include="control" --include="*.install" \
       --include="*.links" --include="*.1" .
   ```
   | Placeholder | Replace with |
   |---|---|
   | `la-toolhive-thv-ui` | Debian source package name (e.g. `my-app`) |
   | `la-toolhive-thv-ui` | Binary package name (e.g. `my-app`) |
   | `la-toolhive-thv-ui` | Display name / executable name (e.g. `my-app`) |
   | `com.vai-int.la-toolhive-thv-ui` | Reverse-domain ID (e.g. `com.example.my-app`) |
   | `A user UI to start, stop toolhive mcp-optimizer using thv command line` | One-line description |
   | `thv command line has more features and options than Toolhive UI, additionally it is more stable.  The package is to give simular administrative functions to the user for thv but using the users UI (KDE, Gnome, XFCE) and has a system tray notification to indicate the state of the users thv service and the running mcp servers.  The package is adress short comings with Linux and Podman Rootless use cases.` | Multi-sentence description |
   | `Utility` | Generic category name (e.g. `System Monitor`) |
   | `Gerald Staruiala` | Your full name |
   | `value.added.kr@gmail.com` | Your email address |
   | `OWNER/la-toolhive-thv-ui` | GitHub owner/repo slug |
   | `2026-04-13` | Release date |

4. **Add application icons** to `src/icons/`:
   - `la-toolhive-thv-ui.svg` — main app icon (installed to hicolor theme)
   - `tray-active.svg`, `tray-inactive.svg` — tray state icons

5. **Update `src/app.py` and `src/tray.py`** with your application logic.

6. **Update install mappings** in `debian/la-toolhive-thv-ui.install`,
   `rpm/la-toolhive-thv-ui.spec`, and `arch/PKGBUILD` if you add files.

7. **Write tests** in `tests/`.

## Building packages locally

Prerequisites: `debhelper`, `devscripts`, `dpkg-dev`, `rpm-build`, `base-devel` (Arch)

```bash
make deb      # Build .deb packages
make rpm      # Build .rpm package
make arch     # Build .pkg.tar.zst via makepkg
make all      # Build all three
make clean    # Remove all build artifacts
```

All output lands in `dist/`.

## Versioning

Version is the single value in `VERSION`. When releasing:

1. Update `VERSION`.
2. Add a dated entry to `CHANGELOG.md`.
3. Update `debian/changelog` (use `dch -v VERSION` or edit manually).
4. Tag: `git tag v$(cat VERSION) && git push --tags`.

## Submitting changes

1. Fork and create a feature branch.
2. Make changes; verify packages build with `make all`.
3. Open a pull request against `main`.
