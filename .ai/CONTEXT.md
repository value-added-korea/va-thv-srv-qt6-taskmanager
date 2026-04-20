# Project Context

> **Audience:** AI assistants and developers reading this cold.
> Read this file before touching any code. Then read `ARCHITECTURE.md`.

---

## Purpose

This repository is a **Linux packaging template** for PyQt6 GUI desktop
applications. It is not itself an application — it is a scaffold that is
cloned once and transformed into a real project by running `python3 scaffold.py`.

The scaffold handles all three major Linux packaging ecosystems in parallel:

| Ecosystem | Package manager | Build tool | File format |
|---|---|---|---|
| Debian / Ubuntu / Mint | apt | `dpkg-buildpackage`, `dpkg-deb` | `.deb` |
| Red Hat / Fedora / RHEL / Rocky / AlmaLinux | dnf / yum | `rpmbuild` | `.rpm` |
| Arch Linux / Manjaro / EndeavourOS | pacman | `makepkg` | `.pkg.tar.zst` |

---

## Application profile

Projects built from this template are **user-space GUI applications** with
the following feature set (each feature is optional and toggled by `scaffold.py`):

| Feature | Default | Description |
|---|---|---|
| Main GUI window | Always | PyQt6 `QMainWindow`-based application |
| System tray icon | Optional | `QSystemTrayIcon` — works natively on Xfce and KDE; requires AppIndicator extension on GNOME |
| Desktop notifications | With tray | `QSystemTrayIcon.showMessage()` (D-Bus backed) |
| XDG autostart | Optional | `/etc/xdg/autostart/` entry starts tray on login for all DEs |
| Systemd user service | Optional | `/usr/lib/systemd/user/` unit, users enable manually |
| User config | Optional | `~/.config/la-toolhive-thv-ui/config.ini` via `configparser` |
| User data dir | Optional | `~/.local/share/la-toolhive-thv-ui/` and `~/.cache/la-toolhive-thv-ui/` |
| System-wide config | Optional | `/etc/la-toolhive-thv-ui/config.ini` installed by package |
| System var directory | Optional | `/var/lib/la-toolhive-thv-ui/` via `systemd-tmpfiles.d` |
| AppStream metainfo | Always | `/usr/share/metainfo/*.xml` for software centres |
| Man page | Always | troff `.1` man page for the main executable |

---

## Technology stack

| Layer | Technology | Why |
|---|---|---|
| GUI toolkit | PyQt6 | Cross-DE (Gnome, Xfce, KDE); ships its own Qt; no DE-specific bindings needed |
| System tray | `QSystemTrayIcon` | StatusNotifierItem protocol; native on KDE/Xfce, extension-backed on GNOME |
| Notifications | `QSystemTrayIcon.showMessage()` | D-Bus-backed; works on all DEs without extra dependencies |
| Config | Python `configparser` (stdlib) | No extra deps; INI format is universally readable |
| Packaging (deb) | debhelper 13 | Modern helper-based approach; handles changelogs, icons, systemd, metainfo |
| Packaging (rpm) | rpmbuild spec | Standard RPM build; includes `%post` hooks for icon and desktop cache refresh |
| Packaging (arch) | PKGBUILD | Split package (`GUI` + `CLI`) via `package_*()` functions |
| CI/CD | GitHub Actions | Matrix: Ubuntu (deb), Fedora container (rpm), Arch container (pkg) |

---

## Two-package structure

Every project produces **two binary packages** from one source:

```
SOURCE_NAME
├── la-toolhive-thv-ui          (GUI package)
│   ├── src/app.py        → /usr/share/la-toolhive-thv-ui/app.py
│   ├── src/tray.py       → /usr/share/la-toolhive-thv-ui/tray.py
│   ├── /usr/bin/la-toolhive-thv-ui        (symlink → app.py)
│   ├── /usr/bin/la-toolhive-thv-ui-tray   (symlink → tray.py)
│   ├── XDG desktop entry, autostart entry
│   ├── hicolor icon tree
│   ├── systemd user service
│   └── AppStream metainfo
└── la-toolhive-thv-ui-cli      (headless CLI package, no GUI deps)
    ├── src/app.py        → /usr/share/la-toolhive-thv-ui/app.py
    ├── /usr/bin/la-toolhive-thv-ui        (symlink)
    └── man page
```

The CLI package can be installed on headless servers without pulling in PyQt6.

There is also a **separate standalone CLI .deb** built via `dpkg-deb --build`
(not debhelper) from `build_cli_deb/`. This is for quick distribution of the
CLI without requiring a full debhelper build environment.

---

## XDG standard path conventions

All installed paths follow XDG and FHS conventions. This is critical — deviating
from these paths breaks DE integration:

| Purpose | Install path | Why |
|---|---|---|
| Main app icon | `/usr/share/icons/hicolor/scalable/apps/NAME.svg` | GNOME, Xfce, KDE all search hicolor |
| Tray icons | `/usr/share/NAME/icons/` | Non-standard names; app-private |
| App launcher | `/usr/share/applications/NAME.desktop` | All DEs search here |
| Autostart | `/etc/xdg/autostart/NAME-tray.desktop` | All DEs search here on login |
| Man page | `/usr/share/man/man1/NAME.1.gz` | Standard man path |
| AppStream | `/usr/share/metainfo/com.vai-int.la-toolhive-thv-ui.metainfo.xml` | GNOME Software, KDE Discover |
| Systemd user unit | `/usr/lib/systemd/user/NAME.service` | User service template location |
| System config | `/etc/NAME/config.ini` (if requested) | FHS: config files in /etc |
| System data | `/var/lib/NAME/` (if requested) | FHS: persistent app state |
| User config | `~/.config/NAME/` | XDG_CONFIG_HOME |
| User data | `~/.local/share/NAME/` | XDG_DATA_HOME |
| User cache | `~/.cache/NAME/` | XDG_CACHE_HOME |

---

## GNOME tray caveat

GNOME removed the legacy system tray in GNOME 3.26. `QSystemTrayIcon` uses
the `org.kde.StatusNotifierItem` D-Bus protocol, which GNOME does not support
natively. Users must install the
`AppIndicator and KStatusNotifierItem Support` extension
(package: `gnome-shell-extension-appindicator`).

This dependency is listed as `Suggests:` (Debian) — not `Depends:` — because
it is optional and only relevant for GNOME users. Xfce and KDE support
`StatusNotifierItem` natively.

---

## Scaffold.py workflow

```
Clone template repo
        ↓
python3 scaffold.py
        ↓ (answers questions)
 ┌──────────────────────────────────────────┐
 │ 1. Replace all APP_* tokens in all files  │
 │ 2. Rename debian/*.install → PKG.install  │
 │ 3. Rename debian/*.links   → PKG.links    │
 │ 4. Rename rpm/*.spec       → PKG.spec     │
 │ 5. Remove unused feature files            │
 │ 6. Patch packaging refs for removed files │
 │ 7. Rewrite debian/changelog               │
 │ 8. Generate src/config.py (if dynamic)   │
 │ 9. Generate src/data.py (if user data)   │
 │ 10. Generate src/tmpfiles.d/ (if var/)   │
 │ 11. Create .venv + install PyQt6 (opt.)  │
 │ 12. Update git remote origin (opt.)      │
 └──────────────────────────────────────────┘
        ↓
 Implement application logic in src/
        ↓
 make deb / make rpm / make arch
        ↓
 dist/ contains installable packages
```
