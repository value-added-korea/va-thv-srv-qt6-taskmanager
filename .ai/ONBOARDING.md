# Post-Scaffold Onboarding Checklist

> This is the definitive TODO list for a developer (or AI) taking over a project
> that was just initialised from this template. Work through phases in order.
> Each item has a verification command where applicable.

---

## Phase 0 — Confirm scaffold ran successfully

```bash
# 1. No APP_* placeholder tokens should remain in any tracked file
grep -rn 'la-toolhive-thv-ui\|la-toolhive-thv-ui\|la-toolhive-thv-ui\|com.vai-int.la-toolhive-thv-ui\|A user UI to start, stop toolhive mcp-optimizer using thv command line\|Gerald Staruiala\|OWNER/la-toolhive-thv-ui\|2026-04-13' \
    --include="*.py" --include="*.desktop" --include="*.service" \
    --include="*.xml" --include="*.spec" --include="PKGBUILD" \
    --include="control" --include="*.install" --include="*.links" \
    --include="*.md" .

# 2. Package-specific files should be renamed
ls debian/*.install debian/*.links rpm/*.spec
# Should show PKG.install, PKG.links, PKG.spec — not the legacy names

# 3. Version file contains your version
cat VERSION

# 4. debian/changelog shows your package name and maintainer
head -3 debian/changelog
```

---

## Phase 1 — Complete TODO markers in source files

```bash
# Find all TODO markers left by the template
grep -rn 'TODO' src/ debian/ rpm/ arch/ --include="*.py" \
    --include="*.desktop" --include="*.service" --include="*.xml" \
    --include="*.spec" --include="PKGBUILD" --include="*.install" \
    --include="*.1"
```

### `src/app.py`
- [ ] Build your main window UI in `MainWindow.__init__()`
- [ ] Decide close behaviour: quit vs minimise to tray
      Set `app.setQuitOnLastWindowClosed(False)` if using tray

### `src/tray.py` (if tray enabled)
- [ ] Add application-specific menu actions in `_build_menu()`
- [ ] Implement `_on_open()` to show/raise the main window
- [ ] Update tray icon path to match your actual icon filename

### `src/desktop/app.desktop`
- [ ] Set `Categories=` to appropriate XDG categories
- [ ] Set `Keywords=` for application launcher search
- [ ] Set `GenericName=` to a clear category description
- [ ] If restricting DEs: uncomment and set `OnlyShowIn=GNOME;XFCE;KDE;`

### `src/desktop/app-autostart.desktop` (if XDG autostart enabled)
- [ ] Verify `Exec=` matches the tray executable name
- [ ] Adjust `X-GNOME-Autostart-Delay` if needed (seconds before starting)

### `src/systemd/app.service` (if systemd service enabled)
- [ ] Verify `ExecStart=` matches the tray executable path
- [ ] Adjust `RestartSec` and `StartLimitBurst` to taste

### `src/metainfo/app.metainfo.xml`
- [ ] Write a real `<description>` (software centres display this)
- [ ] Set a real `<url type="homepage">`
- [ ] Add `<screenshots>` (hosted PNG/WebP, recommended by Flathub)
- [ ] Generate an OARS rating at https://hughsie.github.io/oars/
- [ ] Update `<release version=… date=…>`

### `src/app.1` (man page)
- [ ] Write `DESCRIPTION` and `OPTIONS` sections
- [ ] Set correct date and version in `.TH` header
- [ ] Add `FILES`, `ENVIRONMENT`, `BUGS`, `AUTHOR` sections

### `src/config.py` (if dynamic config generated)
- [ ] Add application-specific sections and keys to `DEFAULTS`

### `src/config/config.ini` (if static config generated)
- [ ] Add application-specific sections and keys

---

## Phase 2 — Add application icons

Icons are not included in the template (they are application-specific).
All three packaging targets expect them at these source paths:

| File | Install destination | Usage |
|---|---|---|
| `src/icons/PKG_NAME.svg` | `/usr/share/icons/hicolor/scalable/apps/` | App launcher icon (all DEs) |
| `src/icons/PKG_NAME.png` | `/usr/share/icons/hicolor/256x256/apps/` | PNG fallback |
| `src/icons/tray-active.svg` | `/usr/share/PKG_NAME/icons/` | Tray icon — active state |
| `src/icons/tray-inactive.svg` | `/usr/share/PKG_NAME/icons/` | Tray icon — inactive state |

```bash
# After adding icons, remove the .gitkeep
rm src/icons/.gitkeep
git add src/icons/

# Verify the hicolor install rule finds them
find src/icons/ -name "*.svg" -o -name "*.png"
```

**Icon naming requirement:** The main icon filename (without extension)
**must match** the `Icon=` value in the `.desktop` file and the
`<icon>` element in the metainfo XML.

---

## Phase 3 — Validate all metadata

```bash
# Desktop entry validation (requires desktop-file-utils)
desktop-file-validate src/desktop/PKG_NAME.desktop

# AppStream metainfo validation (requires appstream)
appstreamcli validate src/metainfo/app.metainfo.xml
# or:
appstream-util validate src/metainfo/app.metainfo.xml

# Man page formatting check
man --warnings -l src/app.1 > /dev/null
```

---

## Phase 4 — Implement and test the application

- [ ] Write the application logic in `src/app.py` and `src/tray.py`
- [ ] Test that `QSystemTrayIcon.isSystemTrayAvailable()` returns `True`
      on your target DEs before shipping
- [ ] Test the tray icon on each DE:
  - Xfce: native (no extension needed)
  - KDE Plasma: native (StatusNotifierItem)
  - GNOME: requires `gnome-shell-extension-appindicator`
- [ ] Test XDG autostart: log out and back in, verify tray starts
- [ ] Test systemd service: `systemctl --user enable --now PKG_NAME.service`
- [ ] Write unit tests in `tests/`
- [ ] Remove `tests/.gitkeep` once real test files exist

---

## Phase 5 — Build and install locally

```bash
# Build all package formats
make all

# Install the .deb locally for testing
sudo dpkg -i dist/PKG_NAME_VERSION_all.deb
sudo apt-get install -f       # Fix any missing dependencies

# Verify installation paths
ls /usr/share/PKG_NAME/
ls /usr/share/applications/PKG_NAME.desktop
ls /usr/share/icons/hicolor/scalable/apps/
ls /usr/lib/systemd/user/PKG_NAME.service
ls /usr/share/metainfo/

# Test the man page
man PKG_NAME

# Test the executables
PKG_NAME --help
PKG_NAME-tray &

# Lint the .deb
lintian --no-tag-display-limit dist/PKG_NAME_VERSION_all.deb
```

---

## Phase 6 — Update top-level documentation

- [ ] Rewrite `README.md` — it still contains the original project description
- [ ] Update `CHANGELOG.md` — set the release date in the `[1.0.0]` entry
- [ ] Update `.github/workflows/build.yml` if you need additional build deps
- [ ] Check `CONTRIBUTING.md` — the placeholder table may need adjustment
      if you added extra features beyond the scaffold

---

## Phase 7 — CI and release

```bash
# Push the branch; CI builds all three package formats
git add -A
git commit -m "feat: initialise PKG_NAME from template"
git push -u origin main

# Tag a release (triggers the GitHub Release job)
git tag v1.0.0
git push origin v1.0.0
```

Verify on GitHub:
- [ ] `build-deb` job passes → `.deb` artefact uploaded
- [ ] `build-rpm` job passes → `.rpm` artefact uploaded
- [ ] `build-arch` job passes → `.pkg.tar.zst` artefact uploaded
- [ ] `release` job creates a GitHub Release with all three files attached

---

## Common mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Icon filename doesn't match `Icon=` in .desktop | App shows generic icon in launcher | Rename icon file or update `Icon=` |
| `app.setQuitOnLastWindowClosed(True)` with tray | Process exits when main window closes | Set to `False` in `app.py` |
| `usr/` prefix in `.install` file | debhelper install fails | Paths in `.install` are relative to `/` — no leading `/` |
| Tray on GNOME without AppIndicator extension | Icon invisible | Document in README; list in `Suggests:` |
| systemd service auto-enabled in `%post` | Package overrides user preference | Never auto-enable; use `--no-enable` |
| Version in `VERSION` out of sync with `debian/changelog` | `make deb` names files with wrong version | Update both; use `dch -v VERSION` |
| Forgetting `%config(noreplace)` in RPM spec | RPM overwrites `/etc/` edits on upgrade | Add `%config(noreplace)` in `%files` |
