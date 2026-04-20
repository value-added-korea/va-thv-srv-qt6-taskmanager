# Architecture — Directory Structure

> Every file and folder explained. For an AI reading this cold: after
> `python3 scaffold.py` the `APP_*` tokens and legacy names are replaced
> and the tree below reflects the live project state.

---

## Full directory tree (template state)

```
va_project_scafold/
│
├── CLAUDE.md                        ← AI context root (Claude Code reads this)
├── .ai/                             ← AI onboarding documentation (this folder)
│   ├── CONTEXT.md                   ← Project purpose, design, technology stack
│   ├── ARCHITECTURE.md              ← This file: every directory and file explained
│   ├── PACKAGING.md                 ← deb / rpm / arch packaging deep-dive
│   ├── TEMPLATES.md                 ← Placeholder system and scaffold.py reference
│   ├── ONBOARDING.md                ← Post-scaffold TODO checklist
│   └── SKILLS.md                    ← Reusable patterns and codebase knowledge
│
├── scaffold.py                      ← One-time project initialisation script
├── Makefile                         ← Unified build: make deb / rpm / arch / clean
├── VERSION                          ← Single source of truth: "1.0.0" (one line)
├── build.sh                         ← Legacy shell build script (superseded by Makefile)
│
├── src/                             ← ALL application source lives here
│   ├── app.py                       ← Main GUI entry point (PyQt6 QMainWindow)
│   ├── tray.py                      ← System tray entry point (QSystemTrayIcon)
│   ├── app.1                        ← Man page (troff format)
│   ├── desktop/
│   │   ├── app.desktop              ← XDG application launcher (menus)
│   │   └── app-autostart.desktop    ← XDG autostart (starts tray on login)
│   ├── systemd/
│   │   └── app.service              ← User systemd service unit
│   ├── metainfo/
│   │   └── app.metainfo.xml         ← AppStream component metadata
│   └── icons/                       ← Application icons (SVG, PNG, ICO)
│       └── .gitkeep                 ← Preserves dir; replace with real icons
│
├── tests/
│   └── .gitkeep                     ← Add test_*.py files here
│
├── debian/                          ← Debhelper packaging metadata
│   ├── control                      ← Source + binary package declarations ★
│   ├── rules                        ← Build rules override (icons, systemd, metainfo)
│   ├── changelog                    ← Debian-format version history (rewritten by scaffold.py)
│   ├── copyright                    ← DEP-5 copyright declaration (required by policy)
│   ├── watch                        ← Upstream release tracking for uscan
│   ├── source/format                ← "3.0 (native)" — no upstream tarball separation
│   ├── la-toolhive-thv-ui.install     ← File→destination maps for GUI package ★
│   └── la-toolhive-thv-ui.links       ← /usr/bin symlink declarations ★
│       (pre-scaffold these are named la-toolhive-thv-ui.*)
│
├── build_cli_deb/                   ← Staging tree for standalone CLI .deb
│   └── DEBIAN/
│       └── control                  ← CLI package control file (dpkg-deb --build)
│       (build_cli_deb/usr/ is gitignored — populated at build time)
│
├── rpm/
│   └── la-toolhive-thv-ui.spec         ← RPM spec (renamed to la-toolhive-thv-ui.spec by scaffold.py) ★
│
├── arch/
│   └── PKGBUILD                     ← Arch Linux build script (split package: GUI + CLI) ★
│
├── dist/                            ← BUILD OUTPUT — gitignored
│   ├── *.deb
│   ├── *.rpm
│   └── *.pkg.tar.zst
│
├── .github/
│   └── workflows/
│       └── build.yml                ← CI: build deb (ubuntu), rpm (fedora), arch (archlinux)
│
├── .editorconfig                    ← Per-file-type indent/encoding rules
├── .gitignore                       ← Excludes dist/, build_rpm/, arch/pkg/, .venv/
├── CHANGELOG.md                     ← Human-readable changelog (Keep a Changelog format)
├── CONTRIBUTING.md                  ← Developer guide: layout, DEs, autostart, substitution table
├── LICENSE                          ← MIT licence
└── README.md                        ← Project overview (update after scaffolding)
```

Files marked ★ contain `APP_*` placeholder tokens replaced by `scaffold.py`.

---

## Gitignore categories

```
dist/                    Built packages — never commit
build_rpm/               rpmbuild working tree
build_cli_deb/usr/       Populated at build time from src/
build_cli_deb/tmp/
debian/.debhelper/       Debhelper state files
debian/files
debian/debhelper-build-stamp
debian/*.substvars
debian/*.log
debian/la-toolhive-thv-ui/ Debhelper staging tree (per binary package)
arch/pkg/                makepkg staging tree
arch/src/
arch/*.zst
arch/*.gz
arch/*.tar.xz
__pycache__/
*.pyc
.venv/                   Added by scaffold.py if venv is requested
```

---

## Key file details

### `debian/control`

Declares the **source package** and all **binary packages** produced from it.
Critical fields:

```
Source: la-toolhive-thv-ui          ← used by dpkg-buildpackage to name artefacts
Package: la-toolhive-thv-ui        ← binary package name (GUI)
Package: la-toolhive-thv-ui-cli    ← binary package name (CLI)
Depends: python3, python3-pyqt6, python3-dbus
Suggests: gnome-shell-extension-appindicator
```

### `debian/rules`

Extends the standard debhelper recipe with three overrides:
1. `override_dh_install` — fans icons into the hicolor theme tree; installs
   systemd user service and AppStream metainfo (these cannot be expressed in
   the `.install` file without wildcards).
2. `override_dh_installsystemduser` — installs the user service with
   `--no-enable --no-start` so the package never auto-enables it.

### `debian/la-toolhive-thv-ui.install`

Maps source-tree files to their installed destinations. Format:
```
src/app.py        usr/share/la-toolhive-thv-ui/
src/tray.py       usr/share/la-toolhive-thv-ui/
src/desktop/app.desktop       usr/share/applications/
src/desktop/app-autostart.desktop    etc/xdg/autostart/
```
Paths are relative to `/`. Populated further by `scaffold.py` if static
config or tmpfiles.d entries are requested.

### `debian/la-toolhive-thv-ui.links`

Creates `/usr/bin/` entry points as symlinks:
```
usr/share/la-toolhive-thv-ui/app.py    usr/bin/la-toolhive-thv-ui
usr/share/la-toolhive-thv-ui/tray.py   usr/bin/la-toolhive-thv-ui-tray
```

### `rpm/la-toolhive-thv-ui.spec`

Single file controls the entire RPM build. Key sections:
- `%package -n` — defines sub-packages (GUI and CLI)
- `%install` — copies files into `%{buildroot}` staging tree
- `%post` / `%postun` — runs `update-desktop-database` and `gtk-update-icon-cache`
- `%files -n` — declares which files belong to which package

### `arch/PKGBUILD`

Uses split-package pattern: `pkgname=('la-toolhive-thv-ui' 'la-toolhive-thv-ui-cli')`.
Two `package_*()` functions install the GUI and CLI subsets respectively.
`backup=()` array protects `/etc/` config files from being overwritten on upgrade.

### `src/app.py`

Template PyQt6 main window. Key patterns to preserve:
- `app.setDesktopFileName(com.vai-int.la-toolhive-thv-ui)` — links the running app to its `.desktop`
  file for GNOME/KDE taskbar grouping and dock integration.
- `app.setQuitOnLastWindowClosed(True)` — set `False` when tray is used,
  so closing the window doesn't quit the process.

### `src/tray.py`

Template `QSystemTrayIcon` tray app. Key patterns:
- `app.setQuitOnLastWindowClosed(False)` — must be False for persistent tray.
- `QSystemTrayIcon.isSystemTrayAvailable()` check on startup — prints a
  GNOME-specific help message if no tray is detected.
- `showMessage()` is the cross-DE notification method (no extra deps needed).

### `src/systemd/app.service`

User service targeting `graphical-session.target`. Users enable it with:
```bash
systemctl --user enable --now la-toolhive-thv-ui.service
```
`PartOf=graphical-session.target` means it stops when the DE session ends.

### `src/metainfo/app.metainfo.xml`

AppStream component metadata. Required fields:
- `<id>` — must match the `.desktop` file basename (without `.desktop`)
- `<launchable type="desktop-id">` — links to `.desktop` file
- `<content_rating type="oars-1.1" />` — required by Flathub and many repos

### `VERSION`

Contains exactly one line: the version string (e.g. `1.0.0`).
The Makefile reads it with `$(shell cat VERSION)`.
`debian/changelog` is kept in sync manually (or via `dch`).

### `Makefile`

Four public targets:
- `make deb` — builds CLI .deb via dpkg-deb, then full build via dpkg-buildpackage
- `make rpm` — stages spec + source tarball, calls rpmbuild
- `make arch` — calls makepkg in arch/
- `make clean` — removes all gitignored build artefacts

---

## Generated files (created by scaffold.py on request)

| File | Created when |
|---|---|
| `src/config.py` | User config = dynamic |
| `src/data.py` | User data dir = yes |
| `src/config/config.ini` | User config = static OR system config = yes |
| `src/tmpfiles.d/la-toolhive-thv-ui.conf` | Var directory = yes |
| `.venv/` | Virtual env = yes (gitignored) |
| `debian/conffiles` | Static config or system config (via debhelper auto) |
