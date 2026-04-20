# Claude Code — Project Context

> **Read this file first.** It gives you full working context for this repository
> without requiring codebase exploration. All detail is in `.ai/`.

---

## What this repository is

This is a **reusable packaging scaffold** (not a finished application).
Its purpose is to be cloned once and then transformed into a real Linux GUI
application project by running `python3 scaffold.py`.

After scaffolding, the result is a fully wired project that builds installable
packages for **three Linux package managers simultaneously**:

| Target | Tool | Format | Distros |
|---|---|---|---|
| Debian / Ubuntu | `dpkg-buildpackage` + `dpkg-deb` | `.deb` (apt) | Debian, Ubuntu, Mint, Pop!\_OS |
| Red Hat / Fedora / RHEL | `rpmbuild` | `.rpm` (dnf/yum) | Fedora, RHEL, CentOS, Rocky, AlmaLinux |
| Arch Linux | `makepkg` | `.pkg.tar.zst` (pacman) | Arch, Manjaro, EndeavourOS |

Applications built from this template are **PyQt6 GUI apps** with optional:
- System tray icon (GNOME / Xfce / KDE)
- Desktop notifications
- XDG autostart on login
- User systemd service on login
- Per-user config (`~/.config/`), data (`~/.local/share/`), or system config (`/etc/`)
- System var directory (`/var/lib/`, `/var/cache/`, `/var/log/`)

---

## Key commands

```bash
python3 scaffold.py     # One-time: answer questions, wire the project
make deb                # Build .deb packages
make rpm                # Build .rpm packages
make arch               # Build Arch .pkg.tar.zst
make all                # Build all three
make clean              # Remove all build artefacts (dist/, build_rpm/, arch/pkg/)
```

---

## Repository state

This repo has **two phases**:

1. **Template phase** (current) — all source files contain `APP_*` placeholder
   tokens. The packaging files are named with legacy strings
   (`la-toolhive-thv-ui`, `la-toolhive-thv-ui`) that `scaffold.py`
   replaces. Do not refactor these names manually.

2. **Project phase** (after `python3 scaffold.py`) — all tokens are replaced,
   files are renamed, unneeded feature files are removed, and the project is
   ready for development.

---

## Placeholder token table

| Token | Replaced with |
|---|---|
| `la-toolhive-thv-ui` | Debian source package name (kebab-case) |
| `la-toolhive-thv-ui` | Binary package name |
| `la-toolhive-thv-ui-cli` | CLI-only binary package name |
| `la-toolhive-thv-ui` | Executable / short name |
| `com.vai-int.la-toolhive-thv-ui` | Reverse-domain ID (`com.example.pkg`) |
| `A user UI to start, stop toolhive mcp-optimizer using thv command line` | One-line description |
| `thv command line has more features and options than Toolhive UI, additionally it is more stable.  The package is to give simular administrative functions to the user for thv but using the users UI (KDE, Gnome, XFCE) and has a system tray notification to indicate the state of the users thv service and the running mcp servers.  The package is adress short comings with Linux and Podman Rootless use cases.` | Multi-sentence description |
| `Utility` | XDG generic category name |
| `Gerald Staruiala` | Full maintainer name |
| `value.added.kr@gmail.com` | Maintainer email address |
| `OWNER/la-toolhive-thv-ui` | GitHub `owner/repo` slug |
| `OWNER` | GitHub owner |
| `la-toolhive-thv-ui` | GitHub repository name |
| `la-toolhive-thv-ui` | Same as `la-toolhive-thv-ui` (used in copyright/watch) |
| `2026-04-13` | Release date |
| `2026` | Copyright year |

---

## File map (quick reference)

```
scaffold.py                ← Run this once to initialise a new project
src/app.py                 ← Main PyQt6 GUI window (template)
src/tray.py                ← QSystemTrayIcon tray app (template)
src/desktop/app.desktop    ← XDG application launcher (template)
src/desktop/app-autostart.desktop  ← XDG autostart for tray (template)
src/systemd/app.service    ← Systemd user service unit (template)
src/metainfo/app.metainfo.xml      ← AppStream metadata (template)
src/app.1                  ← Man page in troff format (template)
debian/control             ← Debian source + binary package declarations
debian/rules               ← Debhelper build rules (icons, systemd, metainfo)
debian/*.install           ← File→destination install maps (per binary package)
debian/*.links             ← /usr/bin symlink declarations
rpm/la-toolhive-thv-ui.spec   ← RPM spec (renamed by scaffold.py)
arch/PKGBUILD              ← Arch package build script
build_cli_deb/DEBIAN/control ← Standalone CLI .deb control (manual dpkg-deb)
Makefile                   ← Unified deb/rpm/arch/clean build interface
VERSION                    ← Single source of truth for version number
```

---

## Important conventions

- **Never** hardcode the version number anywhere except `VERSION`.
  The Makefile, debhelper, rpmbuild, and makepkg all read it from there
  (or from `debian/changelog` which scaffold.py generates).
- **Icons** go to `/usr/share/icons/hicolor/scalable/apps/` (SVG) and
  `/usr/share/icons/hicolor/256x256/apps/` (PNG) — not to a custom path —
  so that all three DEs pick them up automatically.
- **User systemd services** are installed to `/usr/lib/systemd/user/` but
  **never auto-enabled** by the package. Users opt in with
  `systemctl --user enable --now la-toolhive-thv-ui.service`.
- **XDG autostart** entries in `/etc/xdg/autostart/` apply to all users.
  Per-user disabling is done by copying to `~/.config/autostart/` with
  `Hidden=true`.

---

## Full documentation index

| File | Contents |
|---|---|
| `.ai/CONTEXT.md` | Project purpose, design decisions, technology stack |
| `.ai/ARCHITECTURE.md` | Complete directory tree with every file explained |
| `.ai/PACKAGING.md` | deb / rpm / arch packaging details and conventions |
| `.ai/TEMPLATES.md` | Template token system, scaffold.py feature flags, naming rules |
| `.ai/ONBOARDING.md` | Post-scaffold TODO checklist with validation commands |
| `.ai/SKILLS.md` | Reusable patterns: adding deps, files, config options, features |
